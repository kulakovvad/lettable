"""Shared readings of case evidence, used by both the final gates and the tool gates.

One place for: who an event is from, money amounts, affirmative (not negated, not
a question) mentions of approval and completion, which approval covers which
quote, and hazard keyword hits. Keeping this in one module stops the two gate
layers from drifting apart.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from agent.config import Config
from agent.timeline import Case, Event

PARTIES = ("tenant", "landlord", "provider")

NEGATION_RE = re.compile(
    r"\b(not|never|no|yet to|still|incomplete|unfinished|hold off|cannot|won't|wouldn't|unable)\b|n't", re.I)
DONE_RE = re.compile(
    r"\b(completed|all done|job (?:is )?(?:done|complete)|works? (?:is |are )?complete|finished the (?:work|job)|"
    r"(?:have|has|had) (?:now )?(?:been )?(?:fixed|repaired|replaced|resolved)|is (?:now )?fixed|fixed (?:it|the)\b)",
    re.I)
APPROVAL_RE = re.compile(
    r"\b(go ahead|approved?|proceed|yes,? please|happy (?:for|to)|ok(?:ay)? to|fine to|authori[sz]e)\b", re.I)
AGENCY_APPROVAL_RE = re.compile(
    r"\b(landlord approval confirmed|estimate approved|quote approved|landlord (?:has )?approved)\b", re.I)
INVOICE_RE = re.compile(
    r"\b(invoice\w*|paid|payment|no charge|without payment|free of charge|at no cost|pays? (?:the )?(?:contractor|provider) directly)\b",
    re.I)
KEYS_RE = re.compile(r"\bkeys?\b", re.I)
MONEY_RE = re.compile(r"£\s?(\d[\d,]*(?:\.\d{1,2})?)|\b(\d[\d,]*(?:\.\d{1,2})?)\s?(?:GBP|pounds)\b", re.I)
VAT = 1.2


def role_of(name: str) -> str:
    n = (name or "").lower()
    if "landlord" in n or "owner" in n:
        return "landlord"
    if "tenant" in n or "resident" in n:
        return "tenant"
    if any(w in n for w in ("contractor", "provider", "supplier", "engineer", "plumber", "electrician")):
        return "provider"
    if any(w in n for w in ("agency", "lettings", "system", "manager")):
        return "agency"
    return "other"


def amounts(text: str) -> List[float]:
    out = []
    for m in MONEY_RE.finditer(text or ""):
        raw = (m.group(1) or m.group(2) or "").replace(",", "")
        try:
            out.append(round(float(raw), 2))
        except ValueError:
            pass
    return out


def affirmed(pattern: "re.Pattern[str]", text: str) -> Optional["re.Match[str]"]:
    """First match that is not negated in its sentence and not part of a question."""
    for m in pattern.finditer(text or ""):
        start = max(text.rfind(c, 0, m.start()) for c in ".!?\n") + 1
        ends = [i for i in (text.find(c, m.end()) for c in ".!\n?") if i >= 0]
        end = min(ends) if ends else len(text)
        if NEGATION_RE.search(text[start:m.start()][-40:]):
            continue
        if end < len(text) and text[end] == "?":
            continue
        return m
    return None


def reports_completion(e: Event) -> bool:
    """A provider, tenant or landlord says the job is done. Agency/system notes do not count."""
    return role_of(e.sender) in PARTIES and affirmed(DONE_RE, e.body) is not None


def is_approval(e: Event) -> bool:
    if role_of(e.sender) == "landlord":
        return affirmed(APPROVAL_RE, e.body) is not None
    if role_of(e.sender) in ("agency", "other"):
        return affirmed(AGENCY_APPROVAL_RE, e.body) is not None
    return False


def is_quote(e: Event) -> bool:
    return role_of(e.sender) == "provider" and bool(amounts(e.body)) and not INVOICE_RE.search(e.body)


def latest_quote(case: Case) -> Optional[Event]:
    return next((e for e in reversed(case.events) if is_quote(e)), None)


def covering_approval(case: Case) -> Tuple[Optional[Event], Optional[float]]:
    """The latest landlord approval still in force, and the amount it covers (None = no amount stated).

    A later quote only invalidates it when that quote exceeds what was approved; an
    approval of a visit with no amount does not cover a quote that arrives afterwards.
    """
    approval = next((e for e in reversed(case.events) if is_approval(e)), None)
    if approval is None:
        return None, None
    cap_amounts = amounts(approval.body)
    if not cap_amounts:
        prior = next((e for e in reversed(case.events) if e.index < approval.index and is_quote(e)), None)
        cap_amounts = amounts(prior.body) if prior else []
    cap = max(cap_amounts) if cap_amounts else None
    later = [a for e in case.events if e.index > approval.index and is_quote(e) for a in amounts(e.body)]
    if later and (cap is None or max(later) > cap * VAT + 0.01):
        return None, None
    return approval, cap


def approval_covers(case: Case, amount: float) -> bool:
    approval, cap = covering_approval(case)
    return approval is not None and cap is not None and amount <= cap * VAT + 0.01


def hazard_hits(case: Case, cfg: Config, completion_index: Optional[int]) -> List[Tuple[str, str]]:
    """(source ref, matched phrase) for every open hazard mention, in the gate's scan order.

    Scanned: the request, every attachment, the latest hazard_window events, and older
    events unless a confirmed completion came after them. Routine compliance lines in
    reports ("smoke and CO alarms checked") are skipped.
    """
    events = case.events
    window = cfg.hazard_window if cfg.hazard_window > 0 else len(events)
    split = max(0, len(events) - window)
    sources: List[Tuple[str, str]] = [("request", case.request)]
    sources += [(a.name, a.text) for a in case.attachments if a.text]
    sources += [("event-%03d" % e.index, e.body) for e in events[split:]]
    sources += [("event-%03d" % e.index, e.body) for j, e in enumerate(events[:split])
                if completion_index is None or completion_index < j]
    hits = []
    for pattern in cfg.hazard_patterns:
        for ref, text in sources:
            for m in re.finditer(pattern, text or "", re.I):
                if not _is_compliance_line(text, m.start(), m.end()):
                    hits.append((ref, m.group(0)))
                    break
    return hits


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


def agency_name(case: Case) -> str:
    """The agency's own name as it signs in the history (e.g. 'Northbridge Lettings'), else 'the agency'."""
    counts = {}
    for e in case.events:
        name = e.sender.strip()
        if role_of(name) == "agency" and "system" not in name.lower() and "agency" not in name.lower():
            counts[name] = counts.get(name, 0) + 1
    return max(counts, key=counts.get) if counts else "the agency"
