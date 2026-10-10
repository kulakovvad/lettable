"""The escalation used when anything fails. Plain code, no model call, never raises."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from lettable.config import Config
from lettable.gates import find_hazard, wait_days
from lettable.schema import Decision, idempotency_key
from lettable.timeline import Case


def fallback_decision(
    case_id: str,
    cause: str,
    detail: str,
    now: datetime,
    case: Optional[Case] = None,
    cfg: Optional[Config] = None,
) -> Decision:
    cfg = cfg or Config()
    known = []
    unknowns = ["The system could not finish this case (%s)." % cause]
    hazard = None
    waiting_on = None
    waiting_days = None
    events_seen = 0
    warnings = ()
    if case is not None:
        try:
            events_seen = len(case.events)
            warnings = case.warnings
            if case.title:
                known.append("Case: %s" % case.title)
            if case.request:
                known.append("Request: %s" % case.request[:300])
            known.append("%d events recorded" % events_seen)
            wait = case.waiting()
            if wait:
                waiting_on = wait.party
                d = wait_days(wait, now)
                waiting_days = round(d, 2) if d is not None else None
                known.append("Waiting on the %s since %s" % (wait.party, wait.since.strftime("%Y-%m-%d")))
            hazard = find_hazard(case, cfg)
        except Exception:
            pass
    reason = "Automatic escalation: %s. %s" % (cause, detail[:300])
    if known:
        reason += " Known: " + "; ".join(known) + "."
    if hazard:
        reason += " Possible hazard mentioned (%r): treat as urgent." % hazard
    return Decision(
        case_id=case_id,
        action="ESCALATE",
        reason=reason,
        source="fallback",
        unknowns=tuple(unknowns),
        options=("Take over the case and read the timeline", "Re-run the case once the cause is fixed"),
        hazard=bool(hazard),
        waiting_on=waiting_on,
        waiting_days=waiting_days,
        events_seen=events_seen,
        cause=cause,
        idempotency_key=idempotency_key(case_id, events_seen, "ESCALATE", cause),
        decided_at=now.isoformat(),
        warnings=tuple(warnings),
    )
