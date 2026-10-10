"""Plain-code checks on a model proposal.

Rule: a gate may only make the outcome stricter (WAIT or ESCALATE). It never
invents a new action, and it never overrides an escalation.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional

from lettable.config import Config
from lettable.schema import (
    MAX_TEXT,
    NEEDS_MESSAGE,
    Decision,
    Proposal,
    idempotency_key,
)
from lettable.timeline import Case, WaitState

_DONE_RE = re.compile(r"\b(completed|all done|job complete|works? complete|finished the work)\b", re.I)
_SPEND_OK = ("ROUTE_FOR_APPROVAL", "ESCALATE")


def find_hazard(case: Case, cfg: Config) -> Optional[str]:
    """Return the matched phrase if recent events mention a safety hazard."""
    window = case.events[-cfg.hazard_window:] if cfg.hazard_window > 0 else case.events
    text = "\n".join(e.body for e in window) + "\n" + case.request
    for pattern in cfg.hazard_patterns:
        m = re.search(pattern, text, re.I)
        if m:
            return m.group(0)
    return None


def wait_days(wait: Optional[WaitState], now: datetime) -> Optional[float]:
    if wait is None:
        return None
    return max(0.0, (now - wait.since).total_seconds() / 86400.0)


def apply(case: Case, proposal: Proposal, cfg: Config, now: datetime) -> Decision:
    action = proposal.action
    message = proposal.message
    notes: List[str] = []
    wait = case.waiting()
    days = wait_days(wait, now)
    hazard = find_hazard(case, cfg)

    def stricter(new: str, note: str) -> None:
        nonlocal action
        action = new
        notes.append(note)

    if hazard and action != "ESCALATE":
        stricter("ESCALATE", "possible hazard in recent events (%r); a person must decide" % hazard)

    if action != "ESCALATE" and proposal.confidence < cfg.min_confidence and action != "WAIT":
        stricter("ESCALATE", "model confidence %.2f is below %.2f" % (proposal.confidence, cfg.min_confidence))

    if action != "ESCALATE" and action in NEEDS_MESSAGE and not message:
        stricter("ESCALATE", "%s proposed without a message to send" % action)

    if action in ("CHASE_LANDLORD", "CHASE_PROVIDER"):
        party = "landlord" if action == "CHASE_LANDLORD" else "provider"
        if wait is None or wait.party != party:
            stricter("ESCALATE", "model wants to chase the %s but the timeline is not waiting on them" % party)
        elif days is not None and days < cfg.chase_after_days:
            stricter("WAIT", "waiting on the %s for %.1f days; chase after %.1f" % (party, days, cfg.chase_after_days))

    if action == "CLOSE" and not any(_DONE_RE.search(e.body) for e in case.events):
        stricter("ESCALATE", "close proposed but no completion is recorded in the timeline")

    if (
        proposal.amount_gbp is not None
        and proposal.amount_gbp > cfg.approval_limit_gbp
        and action not in _SPEND_OK
    ):
        stricter(
            "ESCALATE",
            "amount GBP %.2f is above the approval limit GBP %.2f" % (proposal.amount_gbp, cfg.approval_limit_gbp),
        )

    if action not in NEEDS_MESSAGE:
        message = ""

    reason = proposal.reason
    if notes:
        reason = "%s [gate: %s]" % (reason, "; ".join(notes))
    options = proposal.options
    if action == "ESCALATE" and not options:
        options = ("Review the timeline and decide the next step", "Contact the party we are waiting on directly")

    return Decision(
        case_id=case.case_id,
        action=action,
        reason=reason[: MAX_TEXT * 2],
        source="model",
        message=message,
        unknowns=proposal.unknowns,
        options=options,
        confidence=proposal.confidence,
        hazard=bool(hazard),
        waiting_on=wait.party if wait else None,
        waiting_days=round(days, 2) if days is not None else None,
        events_seen=len(case.events),
        gate_notes=tuple(notes),
        proposed_action=proposal.action if action != proposal.action else None,
        idempotency_key=idempotency_key(case.case_id, len(case.events), action, message),
        decided_at=now.isoformat(),
        warnings=case.warnings,
    )
