"""Things in a case that do not match each other, found by plain code (no model call).

Each detector is conservative on purpose: a wrong item sends a person looking for a problem that is not there, while
a missed one is still covered by the model's own reading and the policy checks. A detector never raises; on odd
input it simply reports nothing. The result is shown in ANSWER.md under "Inconsistencies and mismatches".
"""

from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from agent import evidence
from agent.timeline import Case, Event

MAX_ITEMS = 20
CHECKED = "addresses, invoice amounts against quotes and approval, completion against later reports, contact details"

_ADDRESS_LINE = re.compile(r"^[ \t>*-]*(?:property )?address[ \t]*:[ \t]*(.+?)[ \t]*$", re.I | re.M)
_POSTCODE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b", re.I)
_GENERIC_WORDS = {"flat", "apartment", "apt", "unit", "house", "road", "rd", "street", "st", "lane", "ln", "avenue", "ave",
                  "close", "court", "drive", "way", "walk", "mews", "row", "place", "the", "and", "of", "floor", "room"}
_PHONE = re.compile(r"(?:\+44\s?\(?0?\)?|\b0)\d(?:[\s-]?\d){8,10}\b")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_INVOICE_WORD = re.compile(r"\binvoice\w*", re.I)
_THANKS_AGAIN = re.compile(r"(?i)\b(?:thanks|thank you) again\b")
# "again" alone is not a fault ("working again", "check again"). It counts only next to one, or as "back" / "started again".
_FAULT = r"leak\w*|drip\w*|broken|broke|block\w*|fault|problem|issue|smell|flood\w*|damp|mould|mold"
_PROBLEM = re.compile(
    r"(?i)\b(?:%s)\b(?:\W+\w+){0,6}\W+again\b|\bagain\b(?:\W+\w+){0,4}\W+\b(?:%s)\b|"
    r"\b(?:started|happening|returned)\s+again\b|"
    r"\b(?:came|come|coming|is|it's|its|has) back\b|\bstill (?:not|leak\w*|broken|dripping|blocked|"
    r"doesn't|isn't|won't|has|have)\b|\bnot (?:been )?(?:fixed|done|sorted|working|resolved|repaired)\b|"
    r"\b(?:isn't|is not|doesn't|won't) (?:work|working|fixed|flush|flushing|drain|draining|heating)\b|\bleak\w*|\bbroken\b|\bworse\b"
    % (_FAULT, _FAULT))


def _ref(e: Event) -> str:
    return "event-%03d" % e.index


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _address_parts(text: str) -> Tuple[Set[str], Set[str], Optional[str]]:
    """(house/flat numbers, street words, postcode) of an address, ignoring case and punctuation."""
    pc = _POSTCODE.search(text)
    postcode = re.sub(r"\s+", "", pc.group(0)).upper() if pc else None
    rest = _POSTCODE.sub(" ", text)
    toks = _tokens(rest)
    numbers = {t.lstrip("0") or "0" for t in toks if t.isdigit()}
    words = {t for t in toks if not t.isdigit() and t not in _GENERIC_WORDS and len(t) > 2}
    return numbers, words, postcode


def _same_address(prop: str, other: str) -> bool:
    """True unless the two clearly name different places. A longer or shorter form of one address is the same."""
    n1, w1, p1 = _address_parts(prop)
    n2, w2, p2 = _address_parts(other)
    if p1 and p2 and p1 != p2:
        return False
    if n1 and n2 and not (n1 <= n2 or n2 <= n1):
        return False
    if w1 and w2 and not (w1 & w2):
        return False
    return True


def _address(case: Case) -> List[Dict[str, Any]]:
    prop = (case.property or "").strip()
    if not prop:
        return []
    found: Dict[str, List[str]] = {}
    shown: Dict[str, str] = {}
    sources: List[Tuple[str, str]] = [(_ref(e), e.body) for e in case.events]
    sources += [(a.name, a.text) for a in case.attachments if a.text]
    for ref, text in sources:
        for m in _ADDRESS_LINE.finditer(text or ""):
            line = re.sub(r"\s+", " ", m.group(1)).strip(" *_`\"'")  # markdown emphasis is not part of the address
            if line and not _same_address(prop, line):
                key = " ".join(_tokens(line))
                shown.setdefault(key, line)
                refs = found.setdefault(key, [])
                if ref not in refs:
                    refs.append(ref)
    return [{"kind": "address", "severity": "flag", "refs": refs,
             "summary": "The case is for %s, but %s give the address as %s." % (
                 prop, "a message" if len(refs) == 1 else "%d messages" % len(refs), shown[key])}
            for key, refs in found.items()]


def _quote_values(e: Event) -> Set[float]:
    return set(evidence.amounts(e.body))


def _matches_a_quote(amount: float, quotes: Set[float]) -> bool:
    return any(abs(amount - q) < 0.015 or abs(amount - round(q * evidence.VAT, 2)) < 0.015
               or abs(amount - round(q / evidence.VAT, 2)) < 0.015 for q in quotes)


def _matches_approval(amount: float, cap: Optional[float]) -> bool:
    """The amount is the approved figure (same VAT basis), not merely under the cap."""
    return cap is not None and _matches_a_quote(amount, {cap})


def _amount(case: Case) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    quote_events = [e for e in case.events if evidence.is_quote(e)]
    quotes: Set[float] = set()
    for e in quote_events:
        quotes |= _quote_values(e)
    if not quotes:
        return []
    approval, cap = evidence.covering_approval(case)
    for e in case.events:
        if evidence.role_of(e.sender) != "provider" or not _INVOICE_WORD.search(e.body) or e in quote_events:
            continue
        amounts = evidence.amounts(e.body)
        if not amounts:
            continue
        unmatched = [a for a in amounts if not _matches_a_quote(a, quotes) and not _matches_approval(a, cap)]
        if unmatched:
            refs = [_ref(e)] + ([_ref(approval)] if approval is not None else []) + [_ref(q) for q in quote_events]
            shown = ", ".join("%.2f" % a for a in unmatched)
            if any(_matches_a_quote(a, quotes) for a in amounts):
                summary = "Invoice amount GBP %s (%s) matches neither a quoted amount nor the landlord's approval." % (shown, _ref(e))
            else:
                summary = "Invoice amount GBP %s (%s) matches none of the quoted amounts (%s)." % (
                    shown, _ref(e), ", ".join("GBP %.2f" % q for q in sorted(quotes)))
            items.append({"kind": "amount", "severity": "flag", "refs": refs, "summary": summary})
        elif cap is not None and approval is not None and max(amounts) > cap * evidence.VAT + 0.01:
            items.append({"kind": "amount", "severity": "flag", "refs": [_ref(e), _ref(approval)],
                          "summary": "Invoice of GBP %.2f (%s) is above the GBP %.2f the landlord approved (%s)."
                                     % (max(amounts), _ref(e), cap, _ref(approval))})
    primary = [(e, max(_quote_values(e))) for e in quote_events if _quote_values(e)]
    distinct: List[Tuple[Event, float]] = []
    for e, amount in primary:
        if not any(_matches_a_quote(amount, {other}) for _, other in distinct):
            distinct.append((e, amount))
    if len(distinct) > 1:
        items.append({"kind": "amount", "severity": "info", "refs": [_ref(e) for e, _ in distinct],
                      "summary": "The provider gave different quotes: " + "; ".join(
                          "GBP %.2f (%s)" % (a, _ref(e)) for e, a in distinct) + "."})
    return items


def _completion(case: Case) -> List[Dict[str, Any]]:
    events = case.events
    done = next((i for i in range(len(events) - 1, -1, -1) if evidence.reports_completion(events[i])), None)
    if done is None:
        return []
    for later in events[done + 1:]:
        if "tenant" not in later.sender.lower():
            continue
        text = _THANKS_AGAIN.sub(" ", later.body)
        if evidence.affirmed(_PROBLEM, text) is not None:
            who = evidence.role_of(events[done].sender)
            return [{"kind": "completion", "severity": "flag", "refs": [_ref(events[done]), _ref(later)],
                     "summary": "The %s reports the job done (%s), but the tenant later reports a problem (%s)." % (
                         "provider" if who == "provider" else who, _ref(events[done]), _ref(later))}]
    return []


def _national(number: str) -> str:
    digits = re.sub(r"\D", "", number)
    return "0" + digits[2:] if digits.startswith("44") else digits


def _contact(case: Case) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for party in ("tenant", "landlord"):
        phones: Dict[str, List[str]] = {}
        emails: Dict[str, List[str]] = {}
        for e in case.events:
            if evidence.role_of(e.sender) != party:
                continue
            for m in _PHONE.finditer(e.body):
                phones.setdefault(_national(m.group(0)), []).append(_ref(e))
            for m in _EMAIL.finditer(e.body):
                emails.setdefault(m.group(0).lower(), []).append(_ref(e))
        for label, seen in (("phone numbers", phones), ("email addresses", emails)):
            if len(seen) > 1:
                refs = sorted({r for rs in seen.values() for r in rs})
                items.append({"kind": "contact", "severity": "info", "refs": refs,
                              "summary": "The %s gives %d different %s: %s." % (party, len(seen), label, ", ".join(sorted(seen)))})
    return items


def _consistency(report: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(report, dict) or report.get("status") != "ok":
        return []
    items = []
    for c in report.get("checks") or []:
        if not isinstance(c, dict) or c.get("tier") not in ("flag", "escalate"):
            continue
        values = [str(v) for v in c.get("values") or []]
        refs = sorted({str(r) for group in c.get("refs") or [] for r in (group if isinstance(group, list) else [group])})
        items.append({"kind": "document consistency", "severity": "flag", "refs": refs,
                      "summary": "%s differs between documents: %s (similarity %s)." % (
                          str(c.get("field", "a field")).replace("_", " "), " vs ".join(repr(v) for v in values), c.get("score", "?"))})
    return items


def find(case: Case, consistency_report: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Every mismatch found, flags before notes, at most MAX_ITEMS. Never raises."""
    items: List[Dict[str, Any]] = []
    detectors: List[Callable[[], List[Dict[str, Any]]]] = [
        lambda: _address(case), lambda: _amount(case), lambda: _completion(case), lambda: _contact(case),
        lambda: _consistency(consistency_report)]
    for detect in detectors:
        try:
            items.extend(detect())
        except Exception:  # a detector must never break the answer
            continue
    items.sort(key=lambda i: 0 if i["severity"] == "flag" else 1)
    return items[:MAX_ITEMS]
