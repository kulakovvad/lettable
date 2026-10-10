"""Who decides to phone: the code.

The model decides WHAT to do and says it (a message, or a call objective, to a party, with a purpose). Whether the
PHONE is the right channel is a deterministic policy, so it is testable, cost-controlled and the same every time:
a call is for when writing has failed or the matter is urgent. The model may suggest a call; this module decides.

Pure functions of the case, the party, the clock and the config. Nothing here reads files, calls a service or
changes a case.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional, Tuple

from agent.config import Config
from agent.evidence import role_of
from agent.timeline import Case, Event

WRITTEN = ("Email", "SMS")
# "not delivered" on its own is ordinary language ("the part was not delivered"), not a mailer bounce.
_BOUNCE = re.compile(
    r"\b(bounced|undeliverable|undelivered|could not be delivered|delivery (?:failed|failure|status: failed)|"
    r"failed to (?:send|deliver)|message failed|mailbox (?:full|unavailable)|returned to sender|no such (?:user|address))\b", re.I)
_SYSTEM_OR_MAILER = re.compile(r"\b(system|mailer(?:-daemon)?|mailer daemon|postmaster|mail delivery)\b", re.I)
_PARTY_NAME = {
    "provider": re.compile(r"\b(providers?|contractors?|suppliers?|engineers?)\b", re.I),
    "landlord": re.compile(r"\b(landlords?|owners?)\b", re.I),
    "tenant": re.compile(r"\b(tenants?|residents?)\b", re.I),
}


def _written_to(case: Case, party: str) -> List[Event]:
    """Our own emails and texts to this party (calls and notes are not written contact)."""
    return [e for e in case.events
            if e.channel in WRITTEN and role_of(e.sender) == "agency" and role_of(e.recipient) == party]


def unanswered(case: Case, party: str) -> List[Event]:
    """Our written messages to the party since their last reply, oldest first."""
    last_reply = max((e.index for e in case.events if role_of(e.sender) == party), default=0)
    return [e for e in _written_to(case, party) if e.index > last_reply]


def _names_recipient(event: Event, party: str, message: Event) -> bool:
    """The bounce is about this party or this message, not a later note that happens to use bounce wording."""
    if role_of(event.recipient) == party:
        return True
    if re.search(r"\bevent[- ]0*%d\b" % message.index, event.body or "", re.I):
        return True
    named = _PARTY_NAME.get(party)
    return named is not None and named.search(event.body or "") is not None


def _bounced(case: Case, party: str) -> Optional[Event]:
    """The latest written message to the party, if a later system or mailer bounce says that message did not arrive."""
    sent = _written_to(case, party)
    if not sent:
        return None
    last = sent[-1]
    for e in case.events:
        if e.index <= last.index or not _SYSTEM_OR_MAILER.search(e.sender or ""):
            continue
        if _BOUNCE.search(e.body or "") and _names_recipient(e, party, last):
            return last
    return None


def _tenant_phoned_in(case: Case) -> bool:
    return any(e.channel == "Call" and role_of(e.sender) == "tenant" for e in case.events)


def phone_allowed(case: Case, party: str, purpose: str, now: datetime, cfg: Config,
                  urgent: bool = False) -> Tuple[bool, str, str]:
    """(allowed, reason, hint). The reason and hint are shown to the model when it asks for a call too early.

    Allowed when: the matter is urgent (a hazard found by code); or written contact has failed (at least
    cfg.call_after_unanswered of our emails/texts to the party are unanswered and the latest is at least
    cfg.call_after_hours old; or the latest one bounced); or, for the tenant, a safety_advice call (the caller of
    this function applies the hazard rule) or a request_info to a tenant who phoned in themselves.
    """
    if urgent:
        return True, "urgent: a hazard was found in the case", ""
    if party == "tenant" and purpose == "request_info" and _tenant_phoned_in(case):
        return True, "the tenant phoned in, so phoning back is the same channel", ""
    bounced = _bounced(case, party)
    if bounced is not None:
        return True, "our last written message to the %s (event-%03d) did not arrive" % (party, bounced.index), ""
    pending = unanswered(case, party)
    need = cfg.call_after_unanswered
    if len(pending) < need:
        return (False,
                "only %d unanswered written message(s) to the %s so far; a call is for when %d go unanswered, "
                "written contact bounces, or the matter is urgent" % (len(pending), party, need),
                "Send a message first (send_message), or WAIT until a reply is overdue.")
    latest = pending[-1]
    if latest.ts is None or now is None:
        return False, "the time of our latest message to the %s is unknown" % party, "Send a message, or escalate."
    hours = (now - latest.ts).total_seconds() / 3600.0
    if hours < cfg.call_after_hours:
        return (False,
                "our latest message to the %s (event-%03d) is only %.0f hours old; a call waits until it is %g hours "
                "old unanswered" % (party, latest.index, max(hours, 0.0), cfg.call_after_hours),
                "WAIT and schedule a follow-up; the code will allow a call once that time has passed.")
    return (True, "%d written messages to the %s went unanswered, the latest %.0f hours ago" % (len(pending), party, hours), "")
