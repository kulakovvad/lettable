"""What a phone call said and what was agreed on it, as data a dashboard can read.

Pure functions, no I/O and no model. The raw record of a call lives in out/<case>/calls/<conversation>.json
(written by agent/calls.py); this module turns it into the shape stored in decision.json:

    action["call_result"]   one call: status, summary, outcome, decisions, duration and a capped transcript
    decision["calls"]       one entry per call action, so a dashboard does not have to walk `actions`
    decision["details"]["calls"]   the same calls on the case card, without the transcript (a reference instead)

Transcript text is untrusted third-party speech: it is only ever copied as text, capped, never interpreted.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

MAX_TURNS = 60
MAX_MESSAGE = 500
_ISO_DATE = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")
_ROLES = {"agent": "agent", "assistant": "agent"}  # anything else is the person who was called
_DECISION_KEYS = ("confirmed_date", "confirmed_date_iso", "quoted_amount_gbp", "callback_number", "outcome", "notes")


def _text(value: Any, limit: int = 500) -> Optional[str]:
    if value is None:
        return None
    text = " ".join(str(value).split())
    return text[:limit] or None


def _number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def decisions_from(data: Any) -> Dict[str, Any]:
    """The facts the call produced, copied from the extracted data only. Missing or unusable values are null."""
    data = data if isinstance(data, dict) else {}
    out: Dict[str, Any] = {k: _text(data.get(k)) for k in _DECISION_KEYS}
    out["quoted_amount_gbp"] = _number(data.get("quoted_amount_gbp"))
    if out["confirmed_date_iso"] is not None and not _ISO_DATE.match(out["confirmed_date_iso"]):
        out["confirmed_date_iso"] = None  # only an exact YYYY-MM-DD is kept; anything else stays in confirmed_date
    return out


def transcript_from(raw: Any) -> Dict[str, Any]:
    """{"transcript": [{role, message}], "transcript_turns": n, "truncated": bool}; roles are agent / other_party."""
    turns = [t for t in (raw if isinstance(raw, list) else []) if isinstance(t, dict) and t.get("message")]
    kept = []
    truncated = len(turns) > MAX_TURNS
    for t in turns[:MAX_TURNS]:
        message = " ".join(str(t["message"]).split())
        if len(message) > MAX_MESSAGE:
            message, truncated = message[:MAX_MESSAGE].rstrip() + "…", True
        entry = {"role": _ROLES.get(str(t.get("role", "")).lower(), "other_party"), "message": message}
        if isinstance(t.get("time_s"), (int, float)) and not isinstance(t.get("time_s"), bool):
            entry["time_s"] = t["time_s"]
        kept.append(entry)
    return {"transcript": kept, "transcript_turns": len(turns), "truncated": truncated}


def shape_result(record: Dict[str, Any], record_path: Optional[str] = None) -> Dict[str, Any]:
    """The `call_result` stored in decision.json, from the full record in calls/<conversation>.json."""
    data = record.get("data") if isinstance(record.get("data"), dict) else {}
    decisions = decisions_from(data)
    duration = _number(record.get("duration_s"))
    return {
        "status": record.get("status"), "success": record.get("success"), "summary": record.get("summary"), "data": data,
        "outcome": decisions["outcome"], "decisions": decisions, "duration_s": duration,
        **transcript_from(record.get("transcript")),
        "record": record_path,
    }


def call_entry(action: Dict[str, Any]) -> Dict[str, Any]:
    """One entry of decision["calls"] from a call action. Always the same keys."""
    result = action.get("call_result") if isinstance(action.get("call_result"), dict) else None
    conversation = action.get("conversation_id")
    return {
        "id": action.get("id"), "party": action.get("to"), "purpose": action.get("purpose"), "priority": action.get("priority"),
        "number": action.get("number"), "state": action.get("state"), "call_status": action.get("call_status"),
        "dry_run": action.get("call_status") == "dry_run" or str(conversation or "").startswith("dryrun-"),
        "conversation_id": conversation, "placed_at": action.get("placed_at"), "objective": action.get("objective"),
        "detail": action.get("call_detail"), "result": result,
    }


def call_entries(actions: Any) -> List[Dict[str, Any]]:
    return [call_entry(a) for a in actions or [] if isinstance(a, dict) and a.get("kind") == "call"]


def card_entry(action: Dict[str, Any]) -> Dict[str, Any]:
    """One entry of the case card's `calls` group: no transcript, a reference to the stored record instead."""
    result = action.get("call_result") if isinstance(action.get("call_result"), dict) else {}
    decisions = result.get("decisions") if isinstance(result.get("decisions"), dict) else decisions_from(result.get("data"))
    return {
        "party": action.get("to"), "status": action.get("call_status") or action.get("state"),
        "conversation_id": action.get("conversation_id"), "result_summary": result.get("summary"),
        "outcome": result.get("outcome") or decisions.get("outcome"), "decisions": decisions,
        "duration_s": result.get("duration_s"), "transcript_ref": result.get("record"),
    }


def sync(decision: Dict[str, Any]) -> None:
    """Refresh decision["calls"] and the case card's calls group from the call actions. Never raises."""
    try:
        actions = decision.get("actions") or []
        decision["calls"] = call_entries(actions)
        card = decision.get("details")
        if isinstance(card, dict) and "calls" in card:
            card["calls"] = [card_entry(a) for a in actions if isinstance(a, dict) and a.get("kind") == "call"][:10]
    except Exception:  # noqa: BLE001 - this is a convenience view; the call actions stay the source of truth
        pass
