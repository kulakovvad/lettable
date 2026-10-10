"""Phone the agency's own on-call person when a case ends urgently.

The model decides what to do about a case; plain code decides whether and how to phone. This is fully code-driven:
no tool, no model choice, no number from the case. When a case ends with a hazard found by code, or priority P0,
the runner adds one briefing call to the decision. It goes through the same dialer, cap and collect path as other
calls, and only ever to the number in the configuration, which a live run must also find on the allow-list.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent import evidence, gates
from agent.config import Config
from agent.timeline import Case, load_case
from agent.voice import ONCALL_PURPOSE, STAFF_PARTY
from agent.voice_prompt import _MONEY, _prompt_text, _speakable

E164 = re.compile(r"^\+\d{8,15}$")
OBJECTIVE = "Brief the on-call manager and get a spoken acknowledgement."


def number(cfg: Config) -> str:
    """The on-call number: the config, else LETTABLE_ONCALL_NUMBER. Empty means the feature is off."""
    return (cfg.oncall_number or os.environ.get("LETTABLE_ONCALL_NUMBER", "")).strip()


def urgent_reason(decision: Dict[str, Any]) -> Optional[str]:
    """Why this case warrants a briefing, or None. P1 alone does not: only a code-found hazard or P0."""
    if decision.get("hazard"):
        return "a hazard was found by the code checks"
    if decision.get("priority") == "P0":
        return "the case is priority P0"
    return None


def _found(decision: Dict[str, Any], case: Optional[Case], cfg: Config) -> str:
    if case is not None and decision.get("hazard"):
        try:
            hits = gates.hazard_hits(case, cfg)
        except Exception:
            hits = []
        if hits:
            phrase = _speakable(hits[0][1], 60)
            if phrase:
                return "a possible hazard was reported: %s" % phrase
    first = re.split(r"(?<=[.!?])\s", (decision.get("reason") or "").strip(), maxsplit=1)[0]
    return _speakable(first, 140) or "an urgent case needs a person"


def _done(decision: Dict[str, Any]) -> str:
    """Only what is true in the decision: never claim something was sent that was not."""
    parts: List[str] = []
    actions = decision.get("actions") or []
    if any(a.get("kind") == "message" and a.get("to") == "tenant" and a.get("purpose") == "safety_advice"
           and a.get("state") == "committed" for a in actions):
        parts.append("safety advice was sent to the tenant")
    if any(a.get("kind") == "escalation" and a.get("state") == "committed" for a in actions):
        parts.append("an escalation ticket is open")
    return " and ".join(parts) or "nothing has been sent yet"


def _address(case: Optional[Case]) -> str:
    text = _MONEY.sub(" ", case.property if case is not None else "")
    return _prompt_text(text, 100) or "not recorded"


def build_action(decision: Dict[str, Any], case: Optional[Case], cfg: Config, to_number: str) -> Dict[str, Any]:
    case_id = str(decision["case_id"])
    key = hashlib.sha256(("%s|oncall|%s" % (case_id, decision.get("events_seen", 0))).encode("utf-8")).hexdigest()[:12]
    agency = evidence.agency_name(case) if case is not None else "the agency"
    facts = {"agency_name": agency, "job": "an urgent case", "case": _prompt_text(case_id, 40) or "unknown",
             "property": _address(case), "found": _found(decision, case, cfg), "done": _done(decision)}
    return {"id": "call-oncall", "kind": "call", "idempotency_key": key, "state": "committed", "to": STAFF_PARTY,
            "purpose": ONCALL_PURPOSE, "priority": "P0", "number": to_number, "objective": OBJECTIVE, "facts": facts,
            "evidence_refs": [], "body": "Phone call: " + OBJECTIVE, "call_status": "pending",
            "note": "Added by the code checks: %s." % urgent_reason(decision)}


def add_briefing(decision: Dict[str, Any], case_path: Path, cfg: Config) -> bool:
    """Append the briefing call to an urgent decision (one per case). Returns True if one was added. Never raises
    and never changes the decision itself."""
    try:
        to_number = number(cfg)
        if not to_number or not urgent_reason(decision):
            return False
        if any(a.get("purpose") == ONCALL_PURPOSE for a in decision.get("actions") or []):
            return False
        if not E164.match(to_number):
            decision.setdefault("warnings", []).append("on-call number is not a valid E.164 number: no briefing call")
            return False
        try:
            case: Optional[Case] = load_case(case_path, cfg)
        except Exception:
            case = None
        decision.setdefault("actions", []).append(build_action(decision, case, cfg, to_number))
        return True
    except Exception:
        return False
