"""Plain-code checks on a model proposal.

Rule: a gate may only make the outcome stricter (WAIT or ESCALATE). It never
invents a new action, and it never overrides an escalation.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional

from agent.config import Config
from agent.schema import (
    MAX_TEXT,
    NEEDS_MESSAGE,
    Decision,
    Proposal,
    idempotency_key,
)
from agent.timeline import Case, WaitState

_DONE_RE = re.compile(r"\b(completed|all done|job complete|works? complete|finished the work)\b", re.I)
_NEGATION_RE = re.compile(r"\b(not|never|no|yet to|still|incomplete|unfinished)\b|n't", re.I)
_SPEND_OK = ("ROUTE_FOR_APPROVAL", "ESCALATE")


def confirmed_completion(case: Case) -> Optional[int]:
    """Position of the latest event that reports the job done, or None.

    A mention does not count when it is negated ("not completed") or when the
    tenant wrote again afterwards (the job was reopened).
    """
    events = case.events
    for i in range(len(events) - 1, -1, -1):
        for m in _DONE_RE.finditer(events[i].body):
            before = re.split(r"[.!?\n]", events[i].body[: m.start()])[-1][-40:]
            if _NEGATION_RE.search(before):
                continue
            reopened = any("tenant" in later.sender.lower() for later in events[i + 1:])
            return None if reopened else i
    return None


def find_hazard(case: Case, cfg: Config) -> Optional[str]:
    """Return the matched phrase if the case mentions a safety hazard that is still open.

    Checked: the request, the text of every attachment, the latest events, and
    any older event unless the job was confirmed done after it.
    """
    events = case.events
    window = cfg.hazard_window if cfg.hazard_window > 0 else len(events)
    split = max(0, len(events) - window)
    done_at = confirmed_completion(case)
    texts = [case.request]
    texts += [a.text for a in case.attachments if a.text]
    texts += [e.body for e in events[split:]]
    texts += [e.body for j, e in enumerate(events[:split]) if done_at is None or done_at < j]
    blob = "\n".join(texts)
    for pattern in cfg.hazard_patterns:
        for m in re.finditer(pattern, blob, re.I):
            if not _is_compliance_line(blob, m.start(), m.end()):
                return m.group(0)
    return None


# Inspection reports routinely say "smoke and carbon monoxide alarms were checked"; that is not a reported hazard.
_COMPLIANCE_RE = re.compile(
    r"\b(alarms?|detectors?)\b.{0,60}\b(checked|tested|test(?:ed)?\s*[:—-]\s*yes|working|fitted|present|in place|will have been)\b"
    r"|\b(checked|tested)\b.{0,40}\b(alarms?|detectors?)\b",
    re.I | re.S,
)


def _is_compliance_line(text: str, start: int, end: int) -> bool:
    """Report lines wrap mid-sentence, so the sentence runs from full stop to full stop."""
    left = max(text.rfind(".", 0, start) + 1, start - 200)
    right = text.find(".", end)
    sentence = text[left:right if 0 <= right < end + 200 else end + 200]
    return bool(_COMPLIANCE_RE.search(sentence)) and not re.search(
        r"\b(sounding|going off|beeping|triggered|activated|smell)\b", sentence, re.I)


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
        stricter("ESCALATE", "possible open hazard (%r); a person must decide" % hazard)

    verified_wait = action == "WAIT" and wait is not None
    if action != "ESCALATE" and proposal.confidence < cfg.min_confidence and not verified_wait:
        stricter("ESCALATE", "model confidence %.2f is below %.2f" % (proposal.confidence, cfg.min_confidence))

    if action != "ESCALATE" and action in NEEDS_MESSAGE and not message:
        stricter("ESCALATE", "%s proposed without a message to send" % action)

    if action in ("CHASE_LANDLORD", "CHASE_PROVIDER"):
        party = "landlord" if action == "CHASE_LANDLORD" else "provider"
        if wait is None or wait.party != party:
            stricter("ESCALATE", "model wants to chase the %s but the timeline is not waiting on them" % party)
        elif days is not None and days < cfg.chase_after_days:
            stricter("WAIT", "waiting on the %s for %.1f days; chase after %.1f" % (party, days, cfg.chase_after_days))

    if action == "CLOSE" and confirmed_completion(case) is None:
        stricter("ESCALATE", "close proposed but no confirmed completion (missing, negated, or reopened by the tenant)")

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
