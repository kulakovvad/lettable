"""High-precision red flags. They back the agency policy with code.

A forcing flag makes the gates escalate (stricter only). A failed action is shown
to the model with recovery guidance and does not force an escalation: a bounced
email can be recovered on another channel.

Negated mentions are ignored. The patterns are specific on purpose, so ordinary
repairs, "bank holiday", "deposit the keys" and "no smell of gas" do not match.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Pattern, Sequence, Tuple

from agent.timeline import Case

_NEG = re.compile(r"\b(?:no|not|never|without|n't)\b", re.I)

# New bank details. Policy: P1, accounts. A routine Direct Debit with the assigned provider is not this.
_BANK: Tuple[Pattern[str], ...] = (
    re.compile(r"\b(?:changed|new|different|updated)\s+banks?\b", re.I),
    re.compile(r"\b(?:new|changed|different|updated)\s+(?:bank details|account details|sort code|payment details)\b", re.I),
    re.compile(r"\b(?:bank details|account details|sort code)\b.{0,80}\b(?:have changed|has changed|changed|new account|update your records|with immediate effect)\b", re.I),
    re.compile(r"\bpay\b.{0,60}\bnew account\b", re.I),
)
# A Direct Debit request. A confirmation ("confirms receipt", "the setup of") is not a request.
_DD: Tuple[Pattern[str], ...] = (
    re.compile(r"\bdirect debit\b.{0,40}\bmandate\b", re.I),
    re.compile(r"\bmandate\b.{0,40}\bdirect debit\b", re.I),
    re.compile(r"\b(?:set up|complete|sign)\b.{0,50}\bdirect debit\b", re.I),
)
_DD_CONFIRM = re.compile(
    r"\b(?:confirms? receipt|about the setup|has been set up|direct debit (?:is|was) (?:now )?set up)\b",
    re.I,
)
_ASSIGNED_BOLD = re.compile(r"maintenance provider\s+\*\*([^*]{2,80})\*\*", re.I)
_ASSIGNED_LINE = re.compile(r"Maintenance Provider Name:\s*([^\n,]{2,80})", re.I)

# Deposits, notices and legal threats. Policy: never-touch, property manager.
_LEGAL: Tuple[Pattern[str], ...] = (
    re.compile(r"\bsection\s*21\b", re.I),
    re.compile(r"\bsection\s*8\b", re.I),
    re.compile(r"\bnotice to quit\b", re.I),
    re.compile(r"\bevict(?:ion|ed|ing)?\b", re.I),
    re.compile(r"\b(?:solicitor|tribunal|legal action|court proceedings)\b", re.I),
    re.compile(r"\bcompensation\b", re.I),
    re.compile(r"\btake you to court\b", re.I),
    re.compile(r"\bdeposit\b.{0,50}\b(?:deduct|dispute|disputed|protection scheme|withhold|disagree)\b", re.I),
    re.compile(r"\b(?:deduct\w*|dispute\w*|withhold\w*|disagree\w*).{0,40}\bdeposit\b", re.I),
)

_VULN = re.compile(
    r"\b(?:pregnant|pregnancy|baby|infant|newborn|elderly|vulnerable|disabled|disability|wheelchair|toddler)\b",
    re.I,
)
_LOSS = re.compile(
    r"\bno (?:hot )?water\b(?!\s+leak)|"
    r"\bno heating\b(?!\s+(?:problem|issue|fault|complaint))|"
    r"\bwithout (?:any )?(?:heating|hot water|power|electricity|water)\b|"
    r"\bboiler\b.{0,40}\b(?:stopped|not working|broken|failed)\b|"
    r"\b(?:heating|hot water|power)\b.{0,30}\b(?:not working|stopped|has stopped|is off|gone|failed)\b|"
    r"\bpower (?:cut|outage|is off)\b|"
    r"\bno (?:electricity|power)\b",
    re.I,
)

_ABUSE: Tuple[Pattern[str], ...] = (
    re.compile(r"you(?:'ll| will) regret", re.I),
    re.compile(r"\bcoming (?:down|round|over) to (?:your|the) (?:office|branch)\b", re.I),
    re.compile(r"\b(?:kill|hurt|assault|punch|beat) (?:you|your staff)\b", re.I),
    re.compile(r"\bi(?:'ll| will) (?:kill|hurt|smash|come (?:down|round))\b", re.I),
    re.compile(r"\bthreaten(?:ed|ing|s)? (?:you|your|the staff|us)\b", re.I),
)

_BOUNCE = re.compile(
    r"\b(?:undeliverable|delivery has failed|mailbox is full|recipient address rejected|"
    r"bounced|could not be delivered|550 5\.1\.1)\b",
    re.I,
)
_NOSHOW = re.compile(
    r"\b(?:no[- ]show|nobody (?:came|attended|turned up)|did not attend|didn't attend|"
    r"missed (?:the )?appointment)\b",
    re.I,
)
_VOICEMAIL = re.compile(r"\bvoicemail\b", re.I)

_GUIDANCE = {
    "payment": "Suspected payment redirection. Do not reply to the requester, do not change bank details, and do not pay. Escalate P1 to accounts.",
    "legal": "Deposit, notice or legal claim. Do not advise, promise or decide it. Escalate to the property manager; a message may only acknowledge.",
    "vulnerability": "Vulnerable occupant without heating, hot water or power. Escalate P1 to the property manager.",
    "abuse": "Abuse or a threat toward staff. Escalate to the property manager. Do not argue with the sender.",
    "failed_action": "A previous action failed (bounce, no-show or repeated voicemail). Do not repeat it. Recover on another channel or, if every channel has failed, hand the case to a person. This flag does not by itself require an escalation.",
}


def _negated(text: str, start: int, end: int) -> bool:
    """True when a negation applies to this match, not to an earlier clause in the sentence.

    "not sorted, and you'll regret it" is still a threat. "not a Section 21" and
    "bank details have not changed" are not.
    """
    prefix = text[max(0, start - 32):start]
    for sep in (".", "!", "?", "\n", ";"):
        cut = prefix.rfind(sep)
        if cut != -1:
            prefix = prefix[cut + 1:]
    and_at = prefix.lower().rfind(" and ")
    if and_at != -1:
        prefix = prefix[and_at + 5:]
    if _NEG.search(prefix):
        return True
    # A "not" inside the match cancels it ("have not changed"), except findings that
    # are themselves a "no X" ("no heating", "nobody came").
    inside = text[start:end]
    return bool(re.search(r"\b(?:not|never|n't|without)\b", inside, re.I))


def _excerpt(text: str, start: int, end: int) -> str:
    chunk = re.sub(r"\s+", " ", text[max(0, start - 50):end + 70]).strip()
    return chunk[:180]


def _sources(case: Case) -> List[Tuple[str, str]]:
    out = [("request", case.request or "")]
    out += [("event-%03d" % e.index, e.body or "") for e in case.events]
    out += [(a.name, a.text) for a in case.attachments if a.text]
    return out


def _first(sources: Sequence[Tuple[str, str]], patterns: Sequence[Pattern[str]]) -> Optional[Tuple[str, str]]:
    for ref, text in sources:
        for pat in patterns:
            for m in pat.finditer(text):
                if _negated(text, m.start(), m.end()):
                    continue
                return ref, _excerpt(text, m.start(), m.end())
    return None


def _flag(category: str, ref: str, excerpt: str, force: bool, route: Optional[str] = None,
          priority: Optional[str] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {
        "category": category, "force": force, "ref": ref, "excerpt": excerpt, "guidance": _GUIDANCE[category],
    }
    if route:
        item["route"] = route
    if priority:
        item["priority"] = priority
    return item


def _affirmed(pattern: Pattern[str], text: str) -> Optional[re.Match]:
    return next((m for m in pattern.finditer(text or "") if not _negated(text, m.start(), m.end())), None)


def _vulnerability(sources: Sequence[Tuple[str, str]]) -> Optional[Dict[str, Any]]:
    """A vulnerable occupant and a loss of heating, water or power, even in different parts of the case."""
    person = service = None
    for ref, text in sources:
        if person is None:
            match = _affirmed(_VULN, text)
            if match:
                person = (ref, text, match)
        if service is None:
            match = _affirmed(_LOSS, text)
            if match:
                service = (ref, text, match)
        if person and service:
            break
    if person is None or service is None:
        return None
    pref, ptext, pmatch = person
    sref, stext, smatch = service
    if pref == sref:
        start, end = min(pmatch.start(), smatch.start()), max(pmatch.end(), smatch.end())
        return _flag("vulnerability", pref, _excerpt(ptext, start, end), True, "property_manager", "P1")
    excerpt = "%s | %s" % (
        _excerpt(ptext, pmatch.start(), pmatch.end()), _excerpt(stext, smatch.start(), smatch.end()))
    return _flag("vulnerability", "%s, %s" % (pref, sref), excerpt[:180], True, "property_manager", "P1")


def _failed(sources: Sequence[Tuple[str, str]]) -> Optional[Dict[str, Any]]:
    hits: List[Tuple[str, str]] = []
    voicemails: List[Tuple[str, str]] = []
    for ref, text in sources:
        for pat in (_BOUNCE, _NOSHOW):
            for m in pat.finditer(text):
                if not _negated(text, m.start(), m.end()):
                    hits.append((ref, _excerpt(text, m.start(), m.end())))
                    break
        for m in _VOICEMAIL.finditer(text):
            if not _negated(text, m.start(), m.end()):
                voicemails.append((ref, _excerpt(text, m.start(), m.end())))
                break
    if len(voicemails) >= 2:
        hits.append(voicemails[1])
    if not hits:
        return None
    excerpt = " | ".join(h[1] for h in hits[:3])
    return _flag("failed_action", hits[0][0], excerpt[:180], False)


def _assigned_firms(case: Case) -> List[str]:
    """Firm names the agency assigned to the job ("Our maintenance provider **Keystone Works**")."""
    names: List[str] = []
    for e in case.events:
        for rx in (_ASSIGNED_BOLD, _ASSIGNED_LINE):
            m = rx.search(e.body or "")
            if not m:
                continue
            name = re.sub(r"\s+", " ", m.group(1)).strip(" .")
            if name and name not in names:
                names.append(name)
    return names


def _payment(case: Case) -> Optional[Tuple[str, str]]:
    """New bank details, or a Direct Debit request that is not with the assigned provider.

    A confirmation of a Direct Debit (public case 039, event-029) is not a request.
    A request sentence that names the assigned provider is with that provider.
    Naming that provider elsewhere in the same event does not hide a different firm's request.
    """
    sources = _sources(case)
    bank = _first(sources, _BANK)
    if bank:
        return bank
    firms = [n.lower() for n in _assigned_firms(case)]
    for ref, text in sources:
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", text or "") or [text or ""]:
            if not sentence.strip() or _DD_CONFIRM.search(sentence):
                continue
            if any(re.search(r"\b%s\b" % re.escape(firm), sentence, re.I) for firm in firms):
                continue
            hit = _first([(ref, sentence)], _DD)
            if hit:
                return hit
    return None


def scan(case: Case) -> List[Dict[str, Any]]:
    """Flags in the order payment, legal, vulnerability, abuse, failed action. At most one of each."""
    sources = _sources(case)
    found: List[Dict[str, Any]] = []
    payment = _payment(case)
    if payment:
        found.append(_flag("payment", *payment, True, "accounts", "P1"))
    legal = _first(sources, _LEGAL)
    if legal:
        found.append(_flag("legal", *legal, True, "property_manager", "P2"))
    vuln = _vulnerability(sources)
    if vuln:
        found.append(vuln)
    abuse = _first(sources, _ABUSE)
    if abuse:
        found.append(_flag("abuse", *abuse, True, "property_manager", "P1"))
    failed = _failed(sources)
    if failed:
        found.append(failed)
    return found


def describe(flags: Sequence[Dict[str, Any]]) -> str:
    """Block for the loop's first message."""
    if not flags:
        return "None."
    lines = []
    for f in flags:
        mode = "forces ESCALATE" if f.get("force") else "flag only; does not force an escalation"
        route = (" route %s" % f["route"]) if f.get("route") else ""
        pri = (" %s" % f["priority"]) if f.get("priority") else ""
        lines.append("- %s%s%s (%s) at %s: %s" % (f["category"], pri, route, mode, f.get("ref"), f.get("excerpt")))
        lines.append("  %s" % f.get("guidance", ""))
    return "\n".join(lines)

