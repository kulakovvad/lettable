"""Speech-to-text (STT) for audio files in a case, so the agent can read voice messages.

A transcript is attached to the case like any document, labelled as automatic and
untrusted. Anything that goes wrong (no key, too big, network, bad audio) gives
None, which the caller shows as "content not available": the agent must not guess.
Transcripts are cached by file hash so a rerun never pays twice.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from agent.config import Config
from agent.report import atomic_write

AUDIO_SUFFIXES = (".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".webm")
TRANSCRIPT_NOTE = "[Automatic transcript, may contain errors. Untrusted.]"
MAX_TRANSCRIPT_CHARS = 20000
MAX_KEYTERMS = 50
STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"


class SttError(RuntimeError):
    pass


class Transcriber:
    def transcribe(self, path: Path, keyterms: List[str]) -> Optional[str]:
        raise NotImplementedError


class FakeTranscriber(Transcriber):
    """Deterministic and free, for tests and offline runs."""

    def transcribe(self, path: Path, keyterms: List[str]) -> Optional[str]:
        return "Speaker 1: [fake transcript of %s]" % Path(path).name


def _multipart(fields: List[Tuple[str, str]], file_name: str, data: bytes) -> Tuple[bytes, str]:
    boundary = "lettable" + uuid.uuid4().hex
    parts: List[bytes] = []
    for name, value in fields:
        parts.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (boundary, name, value)).encode("utf-8"))
    safe_name = re.sub(r'[^\w.\- ]', "_", file_name)
    parts.append(('--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\n'
                  "Content-Type: application/octet-stream\r\n\r\n" % (boundary, safe_name)).encode("utf-8"))
    parts.append(data + b"\r\n")
    parts.append(("--%s--\r\n" % boundary).encode("utf-8"))
    return b"".join(parts), "multipart/form-data; boundary=%s" % boundary


def _post(url: str, headers: Dict[str, str], body: bytes, content_type: str, cfg: Config) -> Dict[str, Any]:
    """POST and parse JSON. Only transport problems are retried (timeouts, 429, 5xx)."""
    attempt = 0
    while True:
        req = urllib.request.Request(url, data=body, headers={"content-type": content_type, **headers})
        try:
            with urllib.request.urlopen(req, timeout=cfg.stt_timeout_s) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            if not (exc.code == 429 or exc.code >= 500) or attempt >= cfg.max_retries:
                raise SttError("HTTP %d from speech-to-text: %s" % (exc.code, detail))
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as exc:
            if attempt >= cfg.max_retries:
                raise SttError("speech-to-text unreachable: %s" % exc)
        time.sleep(min(2 ** attempt, 8))
        attempt += 1


def format_words(words: Iterable[Dict[str, Any]]) -> str:
    """Diarized words to readable lines: 'Speaker 1: ...' with a new line when the speaker changes."""
    order: Dict[str, int] = {}
    lines: List[List[Any]] = []
    for w in words:
        if w.get("type") not in ("word", "spacing"):
            continue
        speaker = str(w.get("speaker_id") or "speaker_0")
        n = order.setdefault(speaker, len(order) + 1)
        if not lines or lines[-1][0] != n:
            lines.append([n, ""])
        lines[-1][1] += w.get("text", "")
    return "\n".join("Speaker %d: %s" % (n, " ".join(t.split())) for n, t in lines if t.strip())


class ElevenLabsTranscriber(Transcriber):
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg

    def transcribe(self, path: Path, keyterms: List[str]) -> Optional[str]:
        key = os.environ.get("ELEVENLABS_API_KEY")
        if not key:
            return None
        fields = [("model_id", self.cfg.stt_model), ("diarize", "true")] + [("keyterms", k) for k in keyterms]
        body, content_type = _multipart(fields, Path(path).name, Path(path).read_bytes())
        result = _post(STT_URL, {"xi-api-key": key}, body, content_type, self.cfg)
        text = format_words(result.get("words") or []) or str(result.get("text") or "").strip()
        return text or None


def make_transcriber(cfg: Config) -> Optional[Transcriber]:
    """Chosen by cfg.stt_backend; the LETTABLE_STT environment variable applies only while the config says 'off'."""
    name = (cfg.stt_backend or "off").strip()
    if name == "off":
        name = os.environ.get("LETTABLE_STT", "off").strip() or "off"
    if name == "off":
        return None
    if name == "fake":
        return FakeTranscriber()
    if name == "elevenlabs":
        return ElevenLabsTranscriber(cfg)
    raise ValueError("unknown stt backend %r" % name)


def case_keyterms(property_address: str, title: str, bodies: Iterable[str]) -> List[str]:
    """Names and places from the case, to bias the transcript towards them."""
    candidates = [p.strip() for p in property_address.split(",")] + [title.strip()]
    for body in bodies:
        candidates += re.findall(r"\b(?:Hi|Hello|Dear)\s+([A-Z][a-z]+)\b", body)
    out: List[str] = []
    for c in candidates:
        if c and len(c) < 50 and len(c.split()) <= 5 and c not in out:
            out.append(c)
    return out[:MAX_KEYTERMS]


def transcript_for(path: Path, transcriber: Transcriber, cfg: Config, keyterms: List[str]) -> Optional[str]:
    """Transcript text for one audio file, from the cache when possible. Never raises."""
    try:
        path = Path(path)
        if path.stat().st_size > cfg.stt_max_audio_bytes:
            return None
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        cached = Path(cfg.stt_cache_dir) / ("%s-%s.txt" % (digest, re.sub(r"\W", "_", cfg.stt_model)))
        if cached.is_file():
            return cached.read_text(encoding="utf-8")
        text = transcriber.transcribe(path, keyterms)
        if not text:
            return None
        text = "%s\n%s" % (TRANSCRIPT_NOTE, text[:MAX_TRANSCRIPT_CHARS])
    except Exception:
        return None
    try:
        atomic_write(cached, text)
    except Exception:
        pass  # an unwritable cache only costs a repeat call later
    return text
