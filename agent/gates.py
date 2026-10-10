"""Plain-code checks on a model proposal.

Rule: a gate may only make the outcome stricter (WAIT or ESCALATE). It never
invents a new action, and it never overrides an escalation.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from agent import consistency, evidence, redflags
from agent.config import Config
from agent.schema import (
    MAX_TEXT,
    NEEDS_MESSAGE,
    Decision,
    Proposal,
    idempotency_key,
)
from agent.timeline import Case, WaitState

# A later tenant message blocks a close unless every sentence is a clear all-clear.
# A sentence about another household subject (parking, rent, a different appliance) is a
# side issue: policy says the case does not close while that message is unanswered.
# A sentence saying the fault is back, or that names this job, reopens it.
_HARMLESS_RE = re.compile(
    r"\b(thank(?:s| you)|all (?:fixed|good|fine|sorted|done)|fixed|resolved|sorted|working (?:now|fine|well)|"
    r"works (?:now|fine)|perfect|great|happy with|(?:now )?clear)\b",
    re.I,
)
_REGRESSION_RE = re.compile(
    r"\b(again|still|leak\w*|broken|damp|mould|smell\w*|worse|stopped|(?:came|come|coming|is|it's) back|not yet|"
    r"not (?:been )?(?:fixed|done|sorted|working|resolved|repaired))\b|n't (?:been )?(?:fixed|done|sorted|working|resolved|repaired)",
    re.I,
)
_PROBLEM_RE = re.compile(r"\b(noise|wrong|issue|problem|another|however|why)\b|\?|n't|\bnot\b|\bno\b", re.I)
_SETTLED_RE = re.compile(
    r"\b(thanks again|thank you again|no (?:more |further )?(?:issues?|problems?|leaks?)|no worries|not a problem|"
    r"nothing (?:else|further))\b", re.I)
_TOPIC_STOP = frozenset((
    "request", "repair", "repairs", "issue", "problem", "report", "reported", "property", "please", "thanks",
    "hello", "tenant", "landlord", "maintenance", "check", "with", "from", "that", "this", "have", "there",
    "their", "would", "could", "about", "been", "will", "your", "when", "what", "which", "since", "just",
    "some", "into", "they", "them", "were", "also", "very", "still", "need", "needs", "work", "works", "job",
    "after", "before", "come", "coming", "become", "currently", "days", "last", "make", "made", "even", "below",
    "above", "shown", "photo", "photos", "cause", "arrived", "here", "every", "keep", "never", "over", "enough",
    "following", "follow", "anything", "something", "does", "doesn", "other", "being", "because", "mind", "case",
    "according", "during", "appear", "appears", "mostly", "quote", "estimate", "flat", "road", "lane", "street",
    "thank", "dear", "regards", "kind", "morning", "afternoon", "evening", "today", "week", "should", "into",
    "customer", "reports", "reporting", "inquiring", "enquiring", "requesting", "requests", "informs", "confirms",
    "mentioned", "says", "asked", "asking", "wants", "like", "able", "help", "space", "register",
))
_SUBJECT_RE = re.compile(
    r"\b(parking|garage|bins?|rent|deposit|council|neighbou?rs?|parcels?|broadband|internet|wifi|aerial|"
    r"windows?|doors?|locks?|boiler|heating|radiators?|shower|bath|toilet|sink|taps?|oven|cooker|hob|fridge|"
    r"freezer|dishwasher|washing machine|dryer|lights?|bulbs?|sockets?|fuse|garden|fence|gate|shed|gutters?|roof|"
    r"ceiling|walls?|floor|carpets?|stairs|pests?|mice|extractor|fan|blinds?|curtains?|wardrobe|furniture|"
    r"inventory|tenancy|renewal|viewing|inspection)\b", re.I)
_SPEND_OK = ("ROUTE_FOR_APPROVAL", "ESCALATE")


def _is_harmless(body: str) -> bool:
    body = _SETTLED_RE.sub(" ", body)
    return (len(body) <= 200 and bool(_HARMLESS_RE.search(body)) and not _PROBLEM_RE.search(body)
            and not _REGRESSION_RE.search(body))


def _words(text: str) -> set:
    return {w.rstrip("s") for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in _TOPIC_STOP}


def _subjects(text: str) -> set:
    return {m.lower().rstrip("s") for m in _SUBJECT_RE.findall(text)}


def job_topic(case: Case) -> set:
    """Content words and subjects of the job (title and the start of the request), for telling side issues apart."""
    text = "%s %s" % (case.title, case.request[:300])
    return _words(text) | _subjects(text)


def followup(body: str, topic: set) -> str:
    """How a tenant message after completion relates to the job: clear, side, or reopen.

    clear: a short all-clear. side: only other household subjects, still unanswered.
    reopen: a defect, a question about this job, or anything that does not name another subject.
    """
    if _is_harmless(body):
        return "clear"
    kind = "clear"
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", body):
        if not sentence.strip() or _is_harmless(sentence):
            continue
        if _REGRESSION_RE.search(sentence):
            return "reopen"
        subjects = _subjects(sentence)
        if not subjects or subjects & topic or _words(sentence) & topic:
            return "reopen"
        kind = "side"
    return kind


def reopens(body: str, topic: set) -> bool:
    """Whether a tenant message after a completion blocks the close (see the comment above _HARMLESS_RE)."""
    return followup(body, topic) != "clear"


def later_followup(case: Case) -> Optional[str]:
    """clear, side, or reopen for tenant messages after the latest completion report, or None if none exists."""
    events = case.events
    topic = job_topic(case)
    for i in range(len(events) - 1, -1, -1):
        if not evidence.reports_completion(events[i]):
            continue
        kind = "clear"
        for later in events[i + 1:]:
            if "tenant" not in later.sender.lower():
                continue
            step = followup(later.body, topic)
            if step == "reopen":
                return "reopen"
            if step == "side":
                kind = "side"
        return kind
    return None


def confirmed_completion(case: Case) -> Optional[int]:
    """Position of the latest event in which a provider, tenant or landlord reports the job done, or None.

    Agency/system notes, negated mentions ("not completed") and questions ("has it
    been completed?") do not count. A later tenant message blocks the close when it
    reopens the job or leaves a side issue unanswered.
    This is the single definition of completion; the close_case tool uses it too.
    """
    if later_followup(case) != "clear":
        return None
    events = case.events
    for i in range(len(events) - 1, -1, -1):
        if evidence.reports_completion(events[i]):
            return i
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

    flags = redflags.scan(case)
    for flag in flags:
        if flag["force"] and action != "ESCALATE":
            stricter("ESCALATE", "red flag %s at %s; %s" % (flag["category"], flag["ref"], flag["guidance"]))

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
            stricter("WAIT", "not waiting on the %s, so there is nothing to chase yet" % party)
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
        if later_followup(case) == "side":
            stricter("WAIT", "a later message is about something else and is still unanswered; list it in "
                     "unrelated_issues and do not close yet")
        else:
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
        red_flags=flags,
    )
