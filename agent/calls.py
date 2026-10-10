"""Place the calls a case staged, and bring their results back into the case.

The loop only stages a call. After the final gates have passed, the runner (in the
parent process, so the run-wide cap and the exactly-once rule are race-free) hands
the committed calls to a Dialer. A call takes minutes, so nothing waits for it:
`collect` fetches finished calls later and a re-run of the case reads them as events.
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from agent.config import Config
from agent.report import atomic_write, write_case
from agent.timeline import Case, Event
import os

from agent.voice import CALL_RECORD_TAG, ONCALL_PURPOSE, STAFF_PARTY, CallRequest, CallResult, Dialer

_NAMES = {"provider": "Contractor", "landlord": "Landlord", "tenant": "Tenant"}
_UNSAFE = re.compile(r"[^A-Za-z0-9_.-]")


class CallBudget:
    """Run-wide cap on calls placed. Thread-safe."""

    def __init__(self, limit: int) -> None:
        self._left, self._lock = limit, threading.Lock()

    def take(self) -> bool:
        with self._lock:
            if self._left <= 0:
                return False
            self._left -= 1
            return True


def _in_hours(cfg: Config, now: datetime) -> bool:
    from zoneinfo import ZoneInfo

    return cfg.call_hours[0] <= now.astimezone(ZoneInfo("Europe/London")).hour < cfg.call_hours[1]


def allowlist(cfg: Config) -> tuple:
    """Numbers a live call may dial: the config list, else LETTABLE_CALL_ALLOWLIST (comma separated). Empty = no list."""
    if cfg.call_allowlist:
        return tuple(cfg.call_allowlist)
    return tuple(n.strip() for n in os.environ.get("LETTABLE_CALL_ALLOWLIST", "").split(",") if n.strip())


def _tell_a_person(decision: Dict[str, Any], action: Dict[str, Any], code: str, why: str) -> None:
    """The decision stays valid, but a person is told the call did not happen (a case always ends with an output)."""
    decision.setdefault("blocked", []).append({"tool": "place_call", "status": "blocked", "code": code, "why": why,
                                               "hint": "A person should make the call or send a message."})
    tickets = [a for a in decision.get("actions", []) if a.get("kind") == "escalation"]
    if tickets:
        tickets[0].setdefault("unknowns", []).append(why)
        return
    decision.setdefault("actions", []).append({
        "id": "escalation-%d" % (len(decision.get("actions", [])) + 1), "kind": "escalation",
        "idempotency_key": hashlib.sha256((decision["case_id"] + action["idempotency_key"]).encode()).hexdigest()[:12],
        "state": "committed", "priority": "P2", "route": "property_manager", "summary": why,
        "known": [action.get("objective", "")], "unknowns": [why], "tried": ["Phone call"],
        "options": ["Call the %s" % action.get("to"), "Send them a message"], "evidence_refs": [],
        "note": "Created automatically because a phone call could not be placed.",
    })


def _hold(decision: Dict[str, Any], action: Dict[str, Any], why: str) -> None:
    action["state"], action["call_status"], action["note"] = "held_for_review", "not_placed", "Held: " + why
    _tell_a_person(decision, action, "call_held", "The phone call to the %s was not placed: %s" % (action.get("to"), why))


def _record_failure(decision: Dict[str, Any], action: Dict[str, Any]) -> None:
    action["state"] = "call_failed"
    _tell_a_person(decision, action, "call_failed", "The phone call to the %s could not be placed (%s)." % (
        action.get("to"), action.get("call_detail")))


def _canonical_number(number: Any) -> str:
    """'+' and digits, so '+44 7700 900555' and '447700900555' are the same number."""
    digits = re.sub(r"\D", "", str(number or ""))
    return "+" + digits if digits else ""


def _on_list(number: Any, allowed: tuple) -> bool:
    want = _canonical_number(number)
    return bool(want) and want in {_canonical_number(n) for n in allowed}


def _not_allowed(action: Dict[str, Any], cfg: Config) -> bool:
    """A live call to a number off the allow-list is held. The list is optional for ordinary calls (empty = no list),
    but an on-call briefing is only ever dialled to a number that is on it."""
    allowed = allowlist(cfg)
    if action.get("purpose") == ONCALL_PURPOSE:
        return not _on_list(action.get("number"), allowed)
    return bool(allowed) and not _on_list(action.get("number"), allowed)


def _already_placed(previous: List[Dict[str, Any]], action: Dict[str, Any], cfg: Config) -> Optional[Dict[str, Any]]:
    """An earlier run already placed this call. One on-call briefing per case, even if its old key included events_seen."""
    for p in previous:
        cid = p.get("conversation_id")
        if not cid or (cfg.call_backend != "dry_run" and str(cid).startswith("dryrun-")):
            continue
        same_key = p.get("idempotency_key") == action.get("idempotency_key")
        same_briefing = action.get("purpose") == ONCALL_PURPOSE and p.get("purpose") == ONCALL_PURPOSE
        if same_key or same_briefing:
            return p
    return None


def place_pending(decision: Dict[str, Any], get_dialer: Callable[[], Dialer], cfg: Config, budget: CallBudget,
                  previous: List[Dict[str, Any]], now: datetime) -> None:
    """Place each committed call that is still pending. Mutates the decision; never raises."""
    for a in decision.get("actions", []):
        if a.get("kind") != "call" or a.get("state") != "committed" or a.get("call_status") != "pending":
            continue
        earlier = _already_placed(previous, a, cfg)
        if earlier:  # the same call was already placed by an earlier run: never dial twice
            for k in ("call_status", "conversation_id", "call_detail", "call_result"):
                if k in earlier:
                    a[k] = earlier[k]
            a["note"] = "Already placed by an earlier run."
        elif cfg.call_backend != "dry_run" and _not_allowed(a, cfg):
            _hold(decision, a, "the number is not on the call allow-list.")
        elif cfg.call_backend != "dry_run" and a.get("purpose") != ONCALL_PURPOSE and not _in_hours(cfg, now):
            _hold(decision, a, "outside UK calling hours (%02d:00 to %02d:00)." % cfg.call_hours)
        elif not budget.take():
            _hold(decision, a, "the run's call limit (%d) is reached." % cfg.max_calls_per_run)
        else:
            try:
                result = get_dialer().place(CallRequest(decision["case_id"], a["to"], a["number"], a["objective"],
                                                        dict(a.get("facts") or {}), a["idempotency_key"]))
            except Exception as exc:  # a dialer problem must never lose the decision
                result = CallResult("failed", None, "%s: %s" % (type(exc).__name__, str(exc)[:200]))
            a["call_status"], a["conversation_id"], a["call_detail"] = result.status, result.conversation_id, result.detail
            if result.status == "failed":
                _record_failure(decision, a)
            else:
                a["placed_at"] = now.isoformat()
                a["note"] = "Call %s." % ("recorded, nothing dialled (dry run)" if result.status == "dry_run" else "placed")


def _result_path(case_out: Path, conversation_id: str) -> Path:
    return case_out / "calls" / (_UNSAFE.sub("_", conversation_id) + ".json")


def _collect_case(case_out: Path, out_dir: Path, get_dialer, summary: Dict[str, Any], skip_dry_run: bool = False) -> None:
    f = case_out / "decision.json"
    if not f.is_file():
        return
    decision = json.loads(f.read_text(encoding="utf-8"))
    changed = False
    for a in decision.get("actions", []):
        cid = a.get("conversation_id")
        if a.get("kind") != "call" or not cid or a.get("call_status") not in ("dry_run", "started") or a.get("call_result"):
            continue
        if skip_dry_run and str(cid).startswith("dryrun-"):
            continue  # a rehearsal has nothing to fetch from the real service
        path = _result_path(case_out, cid)
        if path.is_file():
            record = json.loads(path.read_text(encoding="utf-8"))
        else:
            try:
                conv = get_dialer().fetch(cid)
            except Exception as exc:  # one failed fetch must not drop the other calls of this case
                summary["errors"].append({"case_id": decision["case_id"], "conversation_id": cid,
                                          "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])})
                continue
            if conv.status not in ("done", "failed"):
                summary["pending"].append({"case_id": decision["case_id"], "conversation_id": cid, "status": conv.status})
                continue
            record = {"conversation_id": cid, "case_id": decision["case_id"], "party": a.get("to"), "status": conv.status,
                      "success": conv.success, "summary": conv.summary, "data": conv.data, "duration_s": conv.duration_s,
                      "dry_run": cid.startswith("dryrun-"), "placed_at": a.get("placed_at"),
                      "transcript": [{"role": r, "message": m} for r, m in conv.transcript]}
            atomic_write(path, json.dumps(record, indent=2, ensure_ascii=False) + "\n")
            summary["collected"].append({"case_id": decision["case_id"], "conversation_id": cid})
        a["call_result"] = {k: record.get(k) for k in ("status", "success", "summary", "data")}
        changed = True
    if changed:
        write_case(out_dir, decision)


def collect(out_dir: Path, get_dialer: Callable[[], Dialer], skip_dry_run: bool = False) -> Dict[str, Any]:
    """Fetch the result of every placed call that has none yet. Idempotent; one bad case never stops the rest."""
    out_dir = Path(out_dir)
    summary: Dict[str, Any] = {"collected": [], "pending": [], "errors": []}
    for case_out in sorted(p for p in out_dir.iterdir() if p.is_dir()):
        try:
            _collect_case(case_out, out_dir, get_dialer, summary, skip_dry_run)
        except Exception as exc:
            summary["errors"].append({"case_id": case_out.name, "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])})
    return summary


def with_call_events(case: Case, case_out: Path) -> Case:
    """Append finished call records to the case as automatic Call events, so the next decision sees them.

    The record is logged as the agency's own contact (sender 'Agency / system'), not as a reply: a call that
    reached voicemail must not clear the wait on that party.
    """
    fallback_ts = case.last_ts() or datetime.now(timezone.utc)
    index = max([e.index for e in case.events] or [0])
    events: List[Event] = []
    for f in sorted((case_out / "calls").glob("*.json")) if (case_out / "calls").is_dir() else []:
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if r.get("dry_run") or r.get("status") not in ("done", "failed") or r.get("party") == STAFF_PARTY:
            continue  # a briefing to our own on-call person is not contact with a party of the case
        excerpt = " / ".join("%s: %s" % ("Agency" if t["role"] == "agent" else "Other party", t["message"]) for t in r.get("transcript", [])[:8])
        data = "; ".join("%s=%s" % kv for kv in (r.get("data") or {}).items())
        body = CALL_RECORD_TAG + ", untrusted third-party speech] Call to the %s%s. Outcome: %s. Summary: %s%s Excerpt: %s" % (
            r.get("party"), " (did not connect)" if r.get("status") == "failed" else "", r.get("success") or "unknown",
            r.get("summary") or "(none)", " Extracted: %s." % data if data else "", excerpt)
        index += 1
        try:  # the call happened when it was placed, not when the case last changed
            ts = datetime.fromisoformat(r["placed_at"])
        except (KeyError, TypeError, ValueError):
            ts = fallback_ts
        events.append(Event(index, ts, "Call", "Agency / system", _NAMES.get(r.get("party"), "Other"), body[:1500]))
    return replace(case, events=case.events + tuple(events)) if events else case
