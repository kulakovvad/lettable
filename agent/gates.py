"""Plain-code checks on a model proposal.

Rule: a gate may only make the outcome stricter (WAIT or ESCALATE). It never
invents a new action, and it never overrides an escalation.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from agent import consistency, evidence
from agent.config import Config
from agent.schema import (
    MAX_TEXT,
    NEEDS_MESSAGE,
    Decision,
    Proposal,
    idempotency_key,
)
from agent.timeline import Case, WaitState

# A tenant message after a completion only keeps CLOSE open if it is short, clearly
# positive, and has no problem or negation words. Anything else escalates.
_HARMLESS_RE = re.compile(
    r"\b(thank(?:s| you)|all (?:fixed|good|fine|sorted|done)|fixed|resolved|sorted|working (?:now|fine|well)|"
    r"works (?:now|fine)|perfect|great|happy with)\b",
    re.I,
)
_PROBLEM_RE = re.compile(
    r"\b(again|back|still|leak\w*|broken|damp|mould|smell\w*|noise|wrong|issue|problem|"
    r"worse|another|but|however|why|when|update|chase)\b|\?|n't|\bnot\b|\bno\b",
    re.I,
)
_SPEND_OK = ("ROUTE_FOR_APPROVAL", "ESCALATE")


def _is_harmless(body: str) -> bool:
    return len(body) <= 200 and bool(_HARMLESS_RE.search(body)) and not _PROBLEM_RE.search(body)


def confirmed_completion(case: Case) -> Optional[int]:
    """Position of the latest event in which a provider, tenant or landlord reports the job done, or None.

    Agency/system notes, negated mentions ("not completed") and questions ("has it
    been completed?") do not count. A tenant writing again afterwards with anything
    other than a short, clearly positive reply means the job may have been reopened.
    This is the single definition of completion; the close_case tool uses it too.
    """
    events = case.events
    for i in range(len(events) - 1, -1, -1):
        if not evidence.reports_completion(events[i]):
            continue
        reopened = any(
            "tenant" in later.sender.lower() and not _is_harmless(later.body) for later in events[i + 1:]
        )
        return None if reopened else i
    return None


def hazard_hits(case: Case, cfg: Config):
    """Every open hazard mention as (source ref, phrase). Shared with the case_facts tool."""
    return evidence.hazard_hits(case, cfg, confirmed_completion(case))


def find_hazard(case: Case, cfg: Config) -> Optional[str]:
    """Return the matched phrase if the case mentions a safety hazard that is still open."""
    hits = hazard_hits(case, cfg)
    return hits[0][1] if hits else None


def wait_days(wait: Optional[WaitState], now: datetime) -> Optional[float]:
    if wait is None:
        return None
    return max(0.0, (now - wait.since).total_seconds() / 86400.0)


def apply(case: Case, proposal: Proposal, cfg: Config, now: datetime,
          consistency_report: Optional[Dict[str, Any]] = None) -> Decision:
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

    for c in consistency.escalations(consistency_report):
        if action != "ESCALATE":
            stricter("ESCALATE", "documents disagree on %s (%s); a person must confirm which is right"
                     % (c["field"], " vs ".join(repr(v) for v in c["values"])))

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

    if action in ("ASK_PROVIDER", "ASK_LANDLORD"):
        party = action[len("ASK_"):].lower()
        if wait is not None and wait.party == party and days is not None and days < cfg.chase_after_days:
            stricter("WAIT", "already waiting on the %s for %.1f days; a new question before %.1f days is an early chase"
                     % (party, days, cfg.chase_after_days))

    if action == "INSTRUCT_PROVIDER" and evidence.covering_approval(case)[0] is None:
        stricter("ESCALATE", "instructing the provider without a landlord approval in force (missing, negated, or older than the latest quote)")

    if action == "CLOSE" and confirmed_completion(case) is None:
        stricter("ESCALATE", "close proposed but no confirmed completion (missing, negated, or a tenant follow-up that is not a clear all-clear)")

    landlord_covered = (action == "INSTRUCT_PROVIDER" and proposal.amount_gbp is not None
                        and evidence.approval_covers(case, proposal.amount_gbp))
    if (
        proposal.amount_gbp is not None
        and proposal.amount_gbp > cfg.approval_limit_gbp
        and action not in _SPEND_OK
        and not landlord_covered
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
