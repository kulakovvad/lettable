"""Phone calls through ElevenLabs agents (Twilio outbound call), standard library only.

place() returns at once with a conversation id; the call finishes later and
fetch() reads its transcript and extracted fields.

Safety, all enforced here so no caller can skip it:
- the same idempotency key never dials twice, even across processes (a file ledger under a lock);
- only E.164 numbers, only inside cfg.call_hours (UK local time), at most cfg.max_calls_per_run per run;
- a request the API clearly refused (4xx) is not recorded, so it can be tried again;
- a request that may have gone through (timeout, dropped connection, 5xx) stays "pending" in the ledger
  and is never retried automatically: a person checks ElevenLabs, then clears the entry.
Only reads are retried on transport problems. A POST is retried on 429 only: dialling twice is worse than failing once.
"""

from __future__ import annotations

import json
import os
import re
import socket
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, Optional

from agent.config import Config
from agent.files import atomic_write
from agent.voice import STAFF_PARTY, CallRequest, CallResult, Conversation
from agent.voice_prompt import dynamic_variables

API = "https://api.elevenlabs.io"
E164 = re.compile(r"^\+\d{8,15}$")


def _acquire_lock(lock) -> None:
    """Exclusive lock. flock on macOS and Linux; a byte lock on Windows, which has no fcntl."""
    if os.name == "nt":
        import msvcrt
        lock.seek(0, os.SEEK_END)
        if lock.tell() == 0:
            lock.write(b"\0")
            lock.flush()
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
        return
    import fcntl
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX)


def _release_lock(lock) -> None:
    if os.name == "nt":
        import msvcrt
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
        return
    import fcntl
    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


class VoiceError(RuntimeError):
    def __init__(self, message: str, ambiguous: bool = False) -> None:
        super().__init__(message)
        self.ambiguous = ambiguous  # the request may have been processed


def request(method: str, path: str, api_key: str, cfg: Config, body: Optional[Dict[str, Any]] = None,
            retry_5xx: bool = True) -> Dict[str, Any]:
    """One JSON call. Retries 429 always; 5xx and timeouts only when retry_5xx (reads)."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    attempt = 0
    while True:
        req = urllib.request.Request(API + path, data=data, method=method,
                                     headers={"xi-api-key": api_key, "content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=cfg.call_timeout_s) as resp:
                return json.loads(resp.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            retryable = exc.code == 429 or (retry_5xx and exc.code >= 500)
            if not retryable or attempt >= cfg.max_retries:
                raise VoiceError("HTTP %d from ElevenLabs: %s" % (exc.code, detail), ambiguous=exc.code >= 500)
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as exc:
            if not retry_5xx or attempt >= cfg.max_retries:
                raise VoiceError("ElevenLabs unreachable: %s" % exc, ambiguous=True)
        time.sleep(min(2 ** attempt, 8))
        attempt += 1


def _uk_now() -> datetime:
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("Europe/London"))
    except Exception:  # no tz database on this machine: fall back to UTC
        return datetime.now()


class ElevenLabsDialer:
    def __init__(self, cfg: Config, clock: Callable[[], datetime] = _uk_now) -> None:
        env = os.environ
        missing = [n for n in ("ELEVENLABS_API_KEY", "ELEVENLABS_AGENT_ID", "ELEVENLABS_PHONE_NUMBER_ID") if not env.get(n)]
        if missing:
            raise RuntimeError("missing environment variable(s): %s" % ", ".join(missing))
        self.cfg, self._clock = cfg, clock
        self._key, self._agent, self._number = env["ELEVENLABS_API_KEY"], env["ELEVENLABS_AGENT_ID"], env["ELEVENLABS_PHONE_NUMBER_ID"]
        self._ledger = Path(env.get("LETTABLE_CALL_LEDGER") or Path.home() / ".cache" / "lettable" / "calls.json")
        # The cap counts calls under one run id. The runner should set LETTABLE_RUN_ID per run; without it every
        # call in the ledger shares one id, so the cap becomes lifetime-of-ledger, which fails safe.
        self._run = env.get("LETTABLE_RUN_ID", "")

    # ---- ledger ----

    @contextmanager
    def _locked(self) -> Iterator[Dict[str, Any]]:
        self._ledger.parent.mkdir(parents=True, exist_ok=True)
        with open(str(self._ledger) + ".lock", "a+b") as lock:
            _acquire_lock(lock)
            try:
                try:
                    ledger = json.loads(self._ledger.read_text(encoding="utf-8")) if self._ledger.exists() else {}
                except ValueError:
                    ledger = {}
                yield ledger
                atomic_write(self._ledger, json.dumps(ledger, indent=1) + "\n")
            finally:
                _release_lock(lock)

    # ---- Dialer ----

    def place(self, req: CallRequest) -> CallResult:
        with self._locked() as ledger:
            done = ledger.get(req.idempotency_key)
            if done and done.get("conversation_id"):
                return CallResult("started", done["conversation_id"], "already placed (idempotent)")
            if done:
                return CallResult("failed", None, "an earlier attempt may have placed this call; check the ElevenLabs "
                                  "conversations, then remove the pending entry from %s" % self._ledger)
            if not E164.match(req.to_number or ""):
                return CallResult("failed", None, "number is not E.164 (+ and 8 to 15 digits)")
            start, end = self.cfg.call_hours
            if req.party != STAFF_PARTY and not start <= self._clock().hour < end:  # an on-call briefing may be night-time
                return CallResult("failed", None, "outside calling hours %02d:00-%02d:00 UK time" % (start, end))
            if sum(1 for v in ledger.values() if v.get("run") == self._run) >= self.cfg.max_calls_per_run:
                return CallResult("failed", None, "call cap of %d per run reached" % self.cfg.max_calls_per_run)
            ledger[req.idempotency_key] = {"status": "pending", "run": self._run, "at": self._clock().isoformat()}
            atomic_write(self._ledger, json.dumps(ledger, indent=1) + "\n")  # on disk before the request, in case we die mid-call
            try:
                data = request("POST", "/v1/convai/twilio/outbound-call", self._key, self.cfg, {
                    "agent_id": self._agent,
                    "agent_phone_number_id": self._number,
                    "to_number": req.to_number,
                    "call_recording_enabled": True,
                    "telephony_call_config": {"ringing_timeout_secs": self.cfg.call_ring_timeout_s},
                    "conversation_initiation_client_data": {"dynamic_variables": dynamic_variables(req)},
                }, retry_5xx=False)
            except VoiceError as exc:
                if exc.ambiguous:
                    return CallResult("failed", None, "%s; the call may have been placed, so it will not be retried automatically" % exc)
                del ledger[req.idempotency_key]
                return CallResult("failed", None, str(exc))
            cid = data.get("conversation_id")
            if not data.get("success") or not cid:
                del ledger[req.idempotency_key]
                return CallResult("failed", None, "ElevenLabs did not start the call: %s" % str(data.get("message"))[:200])
            ledger[req.idempotency_key] = {"conversation_id": cid, "run": self._run, "at": self._clock().isoformat()}
            return CallResult("started", cid, "call placed")

    def fetch(self, conversation_id: str) -> Conversation:
        d = request("GET", "/v1/convai/conversations/" + conversation_id, self._key, self.cfg)
        analysis, meta = d.get("analysis") or {}, d.get("metadata") or {}
        turns = tuple((str(t.get("role") or "unknown"), str(t.get("message") or ""))
                      for t in (d.get("transcript") or []) if isinstance(t, dict) and t.get("message"))
        collected = analysis.get("data_collection_results") or {}
        data = {k: (v.get("value") if isinstance(v, dict) else v) for k, v in collected.items()}
        duration = meta.get("call_duration_secs")
        return Conversation(
            conversation_id=conversation_id,
            status=str(d.get("status") or "unknown"),
            transcript=turns,
            summary=str(analysis.get("transcript_summary") or ""),
            success=analysis.get("call_successful"),
            data=data,
            duration_s=float(duration) if isinstance(duration, (int, float)) else None,
        )
