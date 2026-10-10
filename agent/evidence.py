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
    r"(?:have|has|had) (?:now )?(?:been )?(?:fixed|repaired|replaced|resolved|sorted|cleared|unblocked)|"
    r"(?:has|have) (?:now )?been (?:done|carried out)|is (?:now )?fixed|fixed (?:it|the)\b|"
    r"(?:this|that|the) (?:one|job|work|repair) is (?:now )?(?:done|sorted|finished)|all (?:sorted|fixed|working)|"
    r"(?:work|works|job|clean(?:ing)?|repairs?) (?:that )?(?:was|were) done|"
    r"(?:is|are|it's|its) (?:now )?(?:clear|unblocked)\b(?! (?:that|whether|how|what|why|to)\b)|now (?:clear|unblocked)\b|"
    r"draining (?:fine|properly|normally|well)|"
    r"(?:is|are|it's|its) (?:now )?working (?:again|now|fine|properly)|working again|"
    r"(?:that|this|it|plunger|fix|advice) (?:has )?worked\b)",
    re.I)
# A completion word after one of these in its sentence is reported or asked about, not affirmed.
UNCERTAIN_RE = re.compile(r"\b(whether|if|inquir\w*|enquir\w*|hope|hopefully|expected|should be|once)\b", re.I)
APPROVAL_RE = re.compile(
    r"\b(go ahead|approved?|proceed|yes,? please|happy (?:for|to)|ok(?:ay)? to|fine to|authori[sz]e)\b", re.I)
AGENCY_APPROVAL_RE = re.compile(
    r"\b(landlord approval confirmed|estimate approved|quote approved|landlord (?:has )?approved)\b", re.I)
INVOICE_RE = re.compile(
    r"\b(invoice\w*|paid|payment|no charge|without payment|free of charge|at no cost|pays? (?:the )?(?:contractor|provider) directly)\b",
    re.I)
KEYS_RE = re.compile(r"\bkeys?\b", re.I)
MONEY_RE = re.compile(r"£\s?(\d[\d,]*(?:\.\d{1,2})?)|\b(\d[\d,]*(?:\.\d{1,2})?)\s?(?:GBP|pounds)\b|\bGBP\s?(\d[\d,]*(?:\.\d{1,2})?)", re.I)
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
        raw = (m.group(1) or m.group(2) or m.group(3) or "").replace(",", "")
        try:
            out.append(round(float(raw), 2))
        except ValueError:
            pass
    return out


def affirmed(pattern: "re.Pattern[str]", text: str,
             hedges: Optional["re.Pattern[str]"] = None) -> Optional["re.Match[str]"]:
    """First match that is not negated (or hedged) in its sentence and not part of a question."""
    for m in pattern.finditer(text or ""):
        start = max(text.rfind(c, 0, m.start()) for c in ".!?\n") + 1
        ends = [i for i in (text.find(c, m.end()) for c in ".!\n?") if i >= 0]
        end = min(ends) if ends else len(text)
        if NEGATION_RE.search(text[start:m.start()][-40:]):
            continue
        if hedges is not None and hedges.search(text[start:m.start()][-60:]):
            continue
        if end < len(text) and text[end] == "?":
            continue
        return m
    return None


def reports_completion(e: Event) -> bool:
    """A provider, tenant or landlord says the job is done. Agency/system notes do not count."""
    return role_of(e.sender) in PARTIES and affirmed(DONE_RE, e.body, UNCERTAIN_RE) is not None


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
    # (ref, text, advisory): agency messages and documents also give advice ("if you smell gas, call ...")
    # and ask questions ("can you smell gas?"); in them a conditional or a question is not a report.
    sources: List[Tuple[str, str, bool]] = [("request", case.request, False)]
    sources += [(a.name, a.text, True) for a in case.attachments if a.text]
    sources += [("event-%03d" % e.index, e.body, role_of(e.sender) == "agency") for j, e in enumerate(events)
                if j >= split or completion_index is None or completion_index < j]
    hits = []
    for pattern in cfg.hazard_patterns:
        for ref, text, advisory in sources:
            for m in re.finditer(pattern, text or "", re.I):
                if not _is_compliance_line(text, m.start(), m.end()) and not _not_a_report(text, m, advisory):
                    hits.append((ref, m.group(0)))
                    break
    return hits


# A hazard phrase right after a denial, with only filler words between ("no smell of gas", "there is no
# sign of a leak", "not flooding"), is denied. Action negations ("can't stop the flooding", "didn't fix
# the gas leak") are not in the list, so they still count.
_DENIAL_RE = re.compile(
    r"\b(?:no|not|nor|never|without|none|isn't|wasn't|aren't|weren't|don't|doesn't|ruled out|no longer|free of)"
    r"(?:\s+(?:a|an|any|the|longer|more|real|sign|signs|evidence|trace|risk|of|smell|smelling|been|be|is|was|"
    r"there|further|obvious|actual|apparent))*\s*$", re.I)
_CONDITIONAL_RE = re.compile(r"\b(?:if|in case|should|whether|in the event)(?:\s+[\w']+){0,3}\s*$", re.I)


def _not_a_report(text: str, m: "re.Match[str]", advisory: bool) -> bool:
    start = max(text.rfind(c, 0, m.start()) for c in ".!?\n;") + 1
    before = text[start:m.start()]
    if _DENIAL_RE.search(before):
        return True
    if not advisory:
        return False
    ends = [i for i in (text.find(c, m.end()) for c in ".!\n?") if i >= 0]
    return bool(_CONDITIONAL_RE.search(before)) or (bool(ends) and text[min(ends)] == "?")


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


# How the agency introduces or signs itself in its own messages. Strict on purpose: the name found here is what the
# agent signs and what the phone agent says aloud, so a wrong guess is worse than "the agency".
_CAP = r"[A-ZÀ-ÖØ-Þ][^\W\d_]*(?:[&'.-][^\W\d_]+)*"  # one capitalised word, accents allowed
_LAST_WORDS = ("Lettings", "Letting", "Estates", "Agents", "Properties", "Property", "Management", "Homes", "Residential")
_GENERIC = {"Lettings", "Letting", "Estates", "Estate", "Agents", "Properties", "Property", "Management", "Homes",
            "Residential", "Ltd", "Limited", "LLP", "Plc"}  # a name made only of these is a department or a job title
_SUFFIX = r"(?: (?:Ltd|Limited|LLP|Plc)\.?)?"
_AGENCY_NAME = r"((?:%s ){1,3}(?:%s)%s)" % (_CAP, "|".join(_LAST_WORDS), _SUFFIX)
# "Hello, this is Northbridge Lettings!": only at the very start of the message, after an optional greeting, so an
# introduction quoted or pasted further down (a contractor's) cannot win. Any capitalisation of "this is";
# the name may end the line, the text, or be followed by punctuation.
_INTRO = re.compile(r"\A\s*(?:(?i:hello|hi|hey|dear|good (?:morning|afternoon|evening))\b[^.!?\n]{0,30}?\s*)?(?i:this is) %s(?=\s*(?:[!.,\n]|\Z))"
                    % _AGENCY_NAME)
_SIGN_WORD = re.compile(r"\s*(?i:kind regards|best regards|warm regards|regards|many thanks|thanks|thank you|sincerely|"
                        r"yours sincerely|best wishes|best|cheers)\s*,?\s*\Z")
_NAME_LINE = re.compile(r"[ \t]*%s[ \t]*\Z" % _AGENCY_NAME)


def _distinctive(name: str) -> bool:
    return any(w.strip(".") not in _GENERIC for w in name.split())


def _signed_name(body: str) -> Optional[str]:
    """The agency named in a sign-off at the end of the message ("Kind regards," then the name, possibly after a
    person's name). Only the last few lines count."""
    lines = [l for l in body.strip().splitlines() if l.strip()][-5:]
    for i, line in enumerate(lines):
        if _SIGN_WORD.match(line):
            for later in lines[i + 1:i + 3]:  # the name, or a person's name and then the firm
                m = _NAME_LINE.match(later)
                if m and _distinctive(m.group(1)):
                    return m.group(1)
            return None
    return None


def _named_in_own_messages(case: Case) -> Optional[str]:
    """An agency-sounding name the agency uses for itself in its own messages (sender 'Agency / system' has none).
    Two different names used equally often are not trusted: the case is ambiguous, so the caller falls back."""
    counts: dict = {}
    for e in case.events:
        if role_of(e.sender) != "agency":
            continue
        m = _INTRO.match(e.body)
        for name in (m.group(1) if m else None, _signed_name(e.body)):
            if name and _distinctive(name):
                counts[name] = counts.get(name, 0) + 1
    if not counts:
        return None
    ranked = sorted(counts.items(), key=lambda kv: -kv[1])
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return None
    return ranked[0][0]


def agency_name(case: Case) -> str:
    """The agency's own name (e.g. 'Northbridge Lettings'): a sender's name, else how it introduces or signs
    itself in its own messages, else 'the agency'."""
    counts = {}
    for e in case.events:
        name = e.sender.strip()
        if role_of(name) == "agency" and "system" not in name.lower() and "agency" not in name.lower():
            counts[name] = counts.get(name, 0) + 1
    if counts:
        return max(counts, key=counts.get)
    return _named_in_own_messages(case) or "the agency"
