"""The case card: everything the case tells us, as structured data with where each value came from.

Deterministic code only (no model, no network), conservative on purpose: a value is filled in only when the text
says so, names are never guessed, and every value carries `refs` (event-NNN, an attachment name, or "index") so a
reader can check it. Every key is always present (null or an empty list when unknown), so a dashboard can rely on
the shape. The card is stored in decision.json under `details`, and shown in ANSWER.md.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Callable, Dict, List, Optional, Tuple

from agent import evidence
from agent.timeline import Case

SCHEMA = "case-card/1"
CAP = 10  # entries kept per list

_CAP_WORD = r"[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’-]+"
_NOT_NAMES = {"there", "all", "team", "sir", "madam", "both", "everyone", "everybody", "tenant", "landlord", "landlady",
              "customer", "contractor", "provider", "agent", "colleague", "sirs", "support", "sorry", "thanks", "thank", "please",
              "apologies", "morning", "afternoon", "evening"}
_GREETING = re.compile(r"\A\s*(?i:hi|hello|dear|hey|good (?:morning|afternoon|evening))[ ,]+(%s(?: %s)?)\s*[,!.\n]" % (_CAP_WORD, _CAP_WORD))
_LABEL = re.compile(r"^[ \t>*-]*((?i:tenant|landlord))(?i: name)?[ \t]*:[ \t]*(%s(?: %s){0,2})[ \t]*$" % (_CAP_WORD, _CAP_WORD), re.M)
_PHONE = re.compile(r"(?:\+44\s?\(?0?\)?|\b0)\d(?:[\s-]?\d){8,10}\b")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_LABELLED_PHONE = re.compile(r"(?i)\b(tenant|landlord)(?:'s|’s)?\s+(?:phone|mobile|telephone|tel|contact number|number)\b[^\d+]{0,12}((?:\+44|\b0)\d[\d\s-]{8,13}\d)")
_AGENCY_CONTACT = re.compile(r"(?i)\b(?:call|ring|phone|contact|reach|text) us (?:on|at)\s+((?:\+44|\b0)\d[\d\s-]{8,13}\d|[\w.+-]+@[\w-]+(?:\.[\w-]+)+)")
_SIGN_WORD = re.compile(r"\s*(?i:kind regards|best regards|warm regards|regards|many thanks|thanks|thank you|sincerely|best wishes|best|cheers)\s*,?\s*\Z")
_STAFF = re.compile(r"[ \t]*(%s(?: %s){0,2})[ \t]*\Z" % (_CAP_WORD, _CAP_WORD))
_AGENCY_WORD = re.compile(r"\b(Lettings?|Estates?|Agents?|Properties|Property|Management|Homes|Residential|Services|Ltd|Limited)\b")
_PROVIDER = re.compile(r"(?i:\b(?:maintenance )?provider(?: assigned)?)[ \t]*:?[ \t]*(?:\*\*)?([A-Z][\w&'’-]*(?: [A-Z][\w&'’-]*){0,3})(?:\*\*)?[ \t]*(?i:will be attending|will attend|has been assigned|is attending|\.|$)", re.M)
_REFERENCE = re.compile(r"(?i)\b(job id|job ref(?:erence)?|reference|ref|po number|order number|invoice (?:no|number)|case id)[ \t]*[:#][ \t]*([A-Z0-9][A-Z0-9/_-]{2,29})\b")
_ADDRESS_LINE = re.compile(r"^[ \t>*-]*(?:property )?address[ \t]*:[ \t]*(.+?)[ \t]*$", re.I | re.M)
_VAT_EXCL = re.compile(r"(?i)\+\s*vat|plus vat|ex(?:cl(?:uding|usive)?|\.)?\.?\s+vat|before vat|net of vat")
_VAT_INCL = re.compile(r"(?i)incl(?:uding|usive|\.)?\s+(?:of\s+)?vat|inc\.?\s+vat|vat included|with vat|and vat|parts, labour and vat")
_INVOICE_WORD = re.compile(r"\binvoice\w*", re.I)
_DATE_OR_TIME = re.compile(
    r"(?i)\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b|\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b|"
    r"\b(?:mon|tues?|wed(?:nes)?|thu(?:rs)?|fri|sat(?:ur)?|sun)(?:day)?\b|\b\d{1,2}(?::\d\d)?\s?(?:am|pm)\b|\bbetween \d")
_APPOINTMENT = re.compile(r"(?i)\b(?:booked|scheduled|appointment|attending|attend|visit(?:ing)?|engineer will|arrive|arrival)\b")
_PAYMENT_KINDS = (
    ("bank_details", re.compile(r"(?i)\bbank details\b|\bsort code\b|\baccount number\b|\biban\b")),
    ("direct_debit", re.compile(r"(?i)\bdirect debit\b")),
    ("paid_directly", re.compile(r"(?i)\bpa(?:id|ys|y)\b[^.]{0,30}\bdirectly\b|\bdirectly\b[^.]{0,20}\bpa(?:id|ys|y)\b")),
    ("no_charge", re.compile(r"(?i)\bno charge\b|\bwithout payment\b|\bfree of charge\b|\bat no cost\b")),
    ("payment", re.compile(r"(?i)\bpayment\b|\bpaid\b|\bpay\b")),
)
_DEPOSIT = re.compile(r"(?i)\bdeposit\b")
_AUDIO = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".webm"}
_IMAGE = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".heic"}
_TEXT = {".txt", ".md", ".csv", ".json", ".eml"}


def _ref(e: Any) -> str:
    return "event-%03d" % e.index


def _get(decision: Any, key: str, default: Any = None) -> Any:
    return decision.get(key, default) if isinstance(decision, dict) else getattr(decision, key, default)


class _Bag:
    """Distinct values (by a normalised key), each with the references where it was seen."""

    def __init__(self, norm: Callable[[str], str] = lambda s: " ".join(s.lower().split())) -> None:
        self._norm, self._items = norm, {}

    def add(self, value: str, ref: str) -> None:
        value = " ".join(str(value).split())
        key = self._norm(value)
        if not key:
            return
        item = self._items.setdefault(key, {"value": value, "refs": []})
        if ref not in item["refs"]:
            item["refs"].append(ref)

    def items(self) -> List[Dict[str, Any]]:
        return list(self._items.values())[:CAP]

    def single(self) -> Optional[str]:
        """The value when there is exactly one, or when the others are only shorter forms of the longest ("Freya" and
        "Freya Bennett"); None when there is none or the case disagrees with itself."""
        values = [i["value"] for i in self._items.values()]
        if not values:
            return None
        longest = max(values, key=lambda v: len(v.split()))
        words = {w.lower() for w in longest.split()}
        return longest if all({w.lower() for w in v.split()} <= words for v in values) else None


_HEADER_LINE = re.compile(r"(?i)\s*(?:address|job id|job ref(?:erence)?|reference|subject|ref)\s*:")
_FORWARDED = re.compile(r"(?i)(?:begin forwarded|forwarded message|original message)")
# A contact named with another role is not this party's own number ("the contractor asked me to call ...").
_OTHER_ROLE = {
    "tenant": re.compile(r"\b(?:contractors?|providers?|engineers?|landlords?|owners?|agenc(?:y|ies))\b", re.I),
    "landlord": re.compile(r"\b(?:contractors?|providers?|engineers?|tenants?|agenc(?:y|ies))\b", re.I),
    "provider": re.compile(r"\b(?:landlords?|owners?|tenants?|agenc(?:y|ies))\b", re.I),
}


def _greeting_name(body: str) -> Optional[str]:
    """The name in the opening greeting ("Hi Rowan,"), after any Address / Job Id header lines. Only the first line
    counts, so a greeting quoted further down (another person's) is never taken."""
    lines = [l for l in body.splitlines() if l.strip()]
    i = 0
    while i < len(lines) and _HEADER_LINE.match(lines[i]):
        i += 1
    m = _GREETING.match(lines[i] + "\n") if i < len(lines) else None
    return m.group(1) if m and m.group(1).split()[0].lower() not in _NOT_NAMES else None


def _digits(value: str) -> str:
    d = re.sub(r"\D", "", value)
    return "0" + d[2:] if d.startswith("44") else d


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text or "") if len(s.strip()) > 8]


def _safe(fn: Callable[[], Any], default: Any) -> Any:
    try:
        return fn()
    except Exception:  # one extractor failing must not lose the rest of the card
        return default


def _own_lines(body: str, party: str) -> List[str]:
    """Lines where this party is giving their own contact, not a quote, a forward, or someone else's number."""
    forwarded = False
    kept: List[str] = []
    other = _OTHER_ROLE.get(party)
    for raw in (body or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if _FORWARDED.search(line):
            forwarded = True
            continue
        if forwarded or line.startswith(">"):
            continue
        if other is not None and other.search(line):
            continue
        kept.append(line)
    return kept


def _party_block(case: Case, party: str) -> Dict[str, Any]:
    names, phones, emails = _Bag(), _Bag(_digits), _Bag(str.lower)
    for e in case.events:
        sender, recipient = evidence.role_of(e.sender), evidence.role_of(e.recipient)
        if sender == "agency" and recipient == party:
            greeted = _greeting_name(e.body)
            if greeted:
                names.add(greeted, _ref(e))
        for m in _LABEL.finditer(e.body):
            if m.group(1).lower() == party and m.group(2).split()[0].lower() not in _NOT_NAMES:
                names.add(m.group(2), _ref(e))
        for m in _LABELLED_PHONE.finditer(e.body):
            if m.group(1).lower() == party:
                phones.add(m.group(2), _ref(e))
        if sender == party:
            for line in _own_lines(e.body, party):
                for m in _PHONE.finditer(line):
                    phones.add(m.group(0), _ref(e))
                for m in _EMAIL.finditer(line):
                    emails.add(m.group(0), _ref(e))
    return {"name": names.single(), "names": names.items(), "phones": phones.items(), "emails": emails.items()}


def _agency_block(case: Case) -> Dict[str, Any]:
    name = evidence.agency_name(case)
    phones, emails, staff = _Bag(_digits), _Bag(str.lower), _Bag()
    for e in case.events:
        if evidence.role_of(e.sender) != "agency":
            continue
        for m in _AGENCY_CONTACT.finditer(e.body):
            (emails if "@" in m.group(1) else phones).add(m.group(1), _ref(e))
        lines = [l for l in e.body.strip().splitlines() if l.strip()][-4:]
        for i, line in enumerate(lines):
            if _SIGN_WORD.match(line):
                for later in lines[i + 1:i + 2]:
                    m = _STAFF.match(later)
                    if m and not _AGENCY_WORD.search(m.group(1)) and m.group(1).split()[0].lower() not in _NOT_NAMES:
                        staff.add(m.group(1), _ref(e))
                break
    return {"name": None if name == "the agency" else name, "phones": phones.items(), "emails": emails.items(),
            "staff": staff.items()}


def _provider_block(case: Case) -> Dict[str, Any]:
    names = _Bag()
    first_ref: Optional[str] = None
    for e in case.events:
        if evidence.role_of(e.sender) not in ("agency", "other"):
            continue
        m = _PROVIDER.search(e.body)
        if m and m.group(1).split()[0].lower() not in _NOT_NAMES:
            names.add(m.group(1).strip(" .*"), _ref(e))
            first_ref = first_ref or _ref(e)
    phones, emails = _Bag(_digits), _Bag(str.lower)
    for e in case.events:
        if evidence.role_of(e.sender) == "provider":
            for m in _PHONE.finditer(e.body):
                phones.add(m.group(0), _ref(e))
            for m in _EMAIL.finditer(e.body):
                emails.add(m.group(0), _ref(e))
    return {"name": names.single(), "assigned_ref": first_ref if names.single() else None,
            "phones": phones.items(), "emails": emails.items()}


def _property_block(case: Case) -> Dict[str, Any]:
    variants, references = _Bag(), {}
    if case.property:
        variants.add(case.property, "index")
    sources = [(_ref(e), e.body) for e in case.events] + [(a.name, a.text) for a in case.attachments if a.text]
    for ref, text in sources:
        for m in _ADDRESS_LINE.finditer(text):
            variants.add(m.group(1).strip(" *_`\"'"), ref)
        for m in _REFERENCE.finditer(text):
            key = (m.group(1).lower(), m.group(2).upper())
            item = references.setdefault(key, {"kind": m.group(1).lower(), "value": m.group(2), "refs": []})
            if ref not in item["refs"]:
                item["refs"].append(ref)
    return {"address": case.property or None, "address_variants": variants.items(),
            "references": list(references.values())[:CAP]}


def _vat(sentence: str) -> str:
    if _VAT_EXCL.search(sentence):
        return "excl"
    return "incl" if _VAT_INCL.search(sentence) else "unknown"


def _amounts_with_vat(text: str) -> List[Tuple[float, str]]:
    out: List[Tuple[float, str]] = []
    for s in _sentences(text) or [text]:
        for a in evidence.amounts(s):
            if all(a != x for x, _ in out):
                out.append((a, _vat(s)))
    return out


def _money_block(case: Case) -> Dict[str, Any]:
    quotes: List[Dict[str, Any]] = []
    invoices: List[Dict[str, Any]] = []
    payments: List[Dict[str, Any]] = []
    deposit: List[Dict[str, Any]] = []
    seen_pay, seen_dep = set(), set()
    for e in case.events:
        role = evidence.role_of(e.sender)
        is_invoice = role == "provider" and _INVOICE_WORD.search(e.body) is not None
        if evidence.is_quote(e):
            for a, vat in _amounts_with_vat(e.body):
                quotes.append({"amount_gbp": a, "vat": vat, "from": role, "ref": _ref(e)})
        elif is_invoice:
            for a in evidence.amounts(e.body):
                invoices.append({"amount_gbp": a, "from": role, "ref": _ref(e)})
        for s in _sentences(e.body):
            for kind, pattern in _PAYMENT_KINDS:
                if pattern.search(s):
                    key = (kind, s[:80].lower())
                    if key not in seen_pay:
                        seen_pay.add(key)
                        payments.append({"kind": kind, "text": s[:200], "ref": _ref(e)})
                    break
            if _DEPOSIT.search(s) and s[:80].lower() not in seen_dep:
                seen_dep.add(s[:80].lower())
                amounts = evidence.amounts(s)
                deposit.append({"text": s[:200], "amount_gbp": amounts[0] if amounts else None, "ref": _ref(e)})
    for a in case.attachments:
        if not a.text:
            continue
        found = _amounts_with_vat(a.text)
        if re.search(r"(?i)invoice", a.name):
            invoices += [{"amount_gbp": x, "from": "attachment", "ref": a.name} for x, _ in found]
        elif re.search(r"(?i)quot|estimate", a.name):
            quotes += [{"amount_gbp": x, "vat": v, "from": "attachment", "ref": a.name} for x, v in found]
    approval, cap = evidence.covering_approval(case)
    covers = "amount" if approval is not None and cap is not None else ("visit" if approval is not None else "unknown")
    return {"quotes": quotes[:CAP], "invoices": invoices[:CAP],
            "approval": {"amount_gbp": cap, "ref": _ref(approval) if approval is not None else None, "covers": covers},
            "payments": payments[:CAP], "deposit": deposit[:CAP]}


def _appointments(case: Case) -> List[Dict[str, str]]:
    out, seen = [], set()
    for e in case.events:
        for s in _sentences(e.body):
            if _APPOINTMENT.search(s) and _DATE_OR_TIME.search(s) and s[:80].lower() not in seen:
                seen.add(s[:80].lower())
                out.append({"when_text": s[:160], "ref": _ref(e)})
    return out[:CAP]


def _kind(name: str) -> str:
    suffix = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if suffix == ".pdf":
        return "pdf"
    return "image" if suffix in _IMAGE else "audio" if suffix in _AUDIO else "text" if suffix in _TEXT else "other"


def _timeline(case: Case, decision: Any) -> Dict[str, Any]:
    stamps = [e.ts for e in case.events if e.ts is not None]
    wait = case.waiting()
    party = _get(decision, "waiting_on") or (wait.party if wait else None)
    waiting = None
    if party:
        waiting = {"party": party, "since": wait.since.isoformat() if wait else None, "days": _get(decision, "waiting_days")}
    return {"events": len(case.events), "first": min(stamps).isoformat() if stamps else None,
            "last": max(stamps).isoformat() if stamps else None, "waiting_on": waiting,
            "channels": dict(Counter(e.channel for e in case.events))}


def _calls(decision: Any) -> List[Dict[str, Any]]:
    """The calls on the card: party, status, outcome and what was agreed, with a reference to the stored transcript."""
    from agent import call_results

    return [call_results.card_entry(a) for a in _get(decision, "actions") or []
            if isinstance(a, dict) and a.get("kind") == "call"][:CAP]


def build(case: Case, decision: Any) -> Dict[str, Any]:
    """The case card. Always every key; never raises."""
    empty_party = {"name": None, "names": [], "phones": [], "emails": []}
    source = _get(decision, "source") or ""
    card: Dict[str, Any] = {
        "schema": SCHEMA,
        "case": {"id": case.case_id, "title": case.title or None, "source_role": case.source_role or None, "status": None,
                 "request": " ".join((case.request or "").split())[:300] or None},
        "property": _safe(lambda: _property_block(case), {"address": case.property or None, "address_variants": [], "references": []}),
        "tenant": _safe(lambda: _party_block(case, "tenant"), dict(empty_party)),
        "landlord": _safe(lambda: _party_block(case, "landlord"), dict(empty_party)),
        "agency": _safe(lambda: _agency_block(case), {"name": None, "phones": [], "emails": [], "staff": []}),
        "provider": _safe(lambda: _provider_block(case), {"name": None, "assigned_ref": None, "phones": [], "emails": []}),
        "money": _safe(lambda: _money_block(case), {"quotes": [], "invoices": [], "approval": {"amount_gbp": None, "ref": None, "covers": "unknown"},
                                                    "payments": [], "deposit": []}),
        "appointments": _safe(lambda: _appointments(case), []),
        "timeline": _safe(lambda: _timeline(case, decision), {"events": len(case.events), "first": None, "last": None,
                                                              "waiting_on": None, "channels": {}}),
        "attachments": [{"name": a.name, "available": bool(a.text), "kind": _kind(a.name)} for a in case.attachments][:CAP * 3],
        "decision": {"action": _get(decision, "action"), "priority": _get(decision, "priority"),
                     "confidence": _get(decision, "confidence"), "decided_by": "fallback" if source == "fallback" else "model",
                     "cause": _get(decision, "cause"), "as_of": _get(decision, "as_of") or _get(decision, "decided_at") or None,
                     "evidence_refs": list(_get(decision, "evidence_refs") or [])},
        "calls": _safe(lambda: _calls(decision), []),
        "warnings": [str(w) for w in (_get(decision, "warnings") or case.warnings or [])],
    }
    return card


def attach(case: Any, decision: Any, consistency_report: Optional[Dict[str, Any]] = None) -> None:
    """Record the case card and the mismatches on a decision. Every path that produces a decision calls this (the
    tool loop, the single-call backends and the fallback), so decision.json always has them. It never raises and never
    changes the decision itself: on a failure both stay empty and a warning says so."""
    from agent import mismatches

    try:
        report = consistency_report if consistency_report is not None else getattr(decision, "consistency", None)
        decision.details = build(case, decision)
        decision.mismatches = mismatches.find(case, report)
    except Exception as exc:  # noqa: BLE001 - extras must never lose the decision
        decision.details, decision.mismatches = {}, []
        decision.warnings = tuple(decision.warnings) + ("details and mismatches not recorded: %s" % type(exc).__name__,)
