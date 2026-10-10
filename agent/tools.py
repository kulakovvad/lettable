"""Tools the model can call while working one case.

Read tools never change anything. Action tools only *stage* an action after
plain-code gates pass; nothing is committed until the final decision has also
passed agent.gates.apply (see agent.loop). A gate refusal is returned to the
model as a structured result with a reason and a hint, so it can recover.
Every handler returns a JSON-serialisable dict and never raises.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from agent import evidence, gates
from agent.config import Config
from agent.policy import policy_topics
from agent.schema import ACTIONS
from agent.timeline import Case, Event, redact_index
from agent.voice import CALL_RECORD_TAG

PRIORITIES = ("P0", "P1", "P2", "P3")
PARTIES = evidence.PARTIES
PURPOSES = ("chase", "request_info", "reminder", "update", "safety_advice", "instruct_provider")
# A call can also give safety advice, but only to the tenant and only on a hazard found by code.
CALL_PURPOSES = ("chase", "request_info", "instruct_provider", "update", "safety_advice")
INVOICE_STATES = ("sent_to_landlord", "landlord_pays_directly", "no_charge", "unknown")
# Numbers a safety message may always contain: gas emergency, emergency services, NHS 111, power cut 105.
SAFE_NUMBERS = {"0800111999", "999", "111", "105"}

_ELSEWHERE_RE = re.compile(r"\b(colleague|accounts?|alternative|instead|different number|switchboard|out of hours)\b", re.I)
# Premium rate (09), 084/087, directory enquiries (118), personal numbers (070), pagers (076), corporate (055/056).
_UNCALLABLE_RE = re.compile(r"^0(9|84|87|118|70|76|55|56)")
_PHONE_RE = re.compile(r"(?:\+44\s?\(?0?\)?|\b0)\d(?:[\s-]?\d){8,10}\b")
_APPOINTMENT_RE = re.compile(r"\b(appointment|booked|attend(?:ing|ance)?|visit|scheduled|between \d{1,2}(?::\d\d)? ?(?:am|pm)?(?: and| -| to) \d)", re.I)
_KEY_HELD_RE = re.compile(r"\b(collect(?:ed)? (?:the )?keys?|keys? (?:collected|held|from the office)|key collection|return (?:the )?keys?)\b", re.I)
_KEY_BACK_RE = re.compile(
    r"\bkeys? (?:(?:have|has|were|was|are) (?:now |all )?(?:been )?)?(?:returned|dropped (?:off|back)|handed (?:back|in)|"
    r"brought back|posted back|back (?:at|in|to) (?:the |our )?office)\b|"
    r"\b(?:returned|dropped (?:off|back)|handed back|brought back) (?:the |all |both )?keys?\b", re.I)

role_of = evidence.role_of
_amounts = evidence.amounts


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def ref(e: Event) -> str:
    return "event-%03d" % e.index


def _fmt_event(e: Event, cap: int = 4000) -> str:
    when = e.ts.strftime("%Y-%m-%d %H:%M") if e.ts else "unknown time"
    body = e.body if len(e.body) <= cap else e.body[:cap] + " [cut]"
    return "[%s %s %s, %s -> %s]\n%s" % (ref(e), when, e.channel, e.sender, e.recipient, body)


def _s(value: Any, limit: int = 2000) -> str:
    return str(value if value is not None else "").strip()[:limit]


def _list(value: Any, limit: int = 10) -> List[str]:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple)):
        return []
    return [_s(v, 400) for v in value[:limit] if _s(v, 400)]


def _schema(props: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}


_STR = {"type": "string"}
_STRS = {"type": "array", "items": {"type": "string"}}
_PRIORITY = {"type": "string", "enum": list(PRIORITIES)}

TOOL_SPECS: List[Dict[str, Any]] = [
    {"name": "case_facts", "description": "Code-derived facts: who we wait on and since when, last message to/from each party, money amounts with event refs, approvals seen, possible hazard keywords (may be false positives), completion signals, input warnings.",
     "parameters": _schema({}, [])},
    {"name": "read_events", "description": "Read full events by number range (inclusive), max 30 per call. Use when the overview omitted events or cut long bodies.",
     "parameters": _schema({"first": {"type": "integer"}, "last": {"type": "integer"}}, ["first", "last"])},
    {"name": "search_case", "description": "Case-insensitive plain-text search across events, the request and attachment text. Returns refs and snippets.",
     "parameters": _schema({"query": _STR}, ["query"])},
    {"name": "read_attachment", "description": "Extracted text of one attachment by file name, or a note that its contents are unavailable.",
     "parameters": _schema({"name": _STR}, ["name"])},
    {"name": "list_case_files", "description": "List files in the case folder (for unusual case formats).",
     "parameters": _schema({}, [])},
    {"name": "read_case_file", "description": "Read a text file in the case folder by relative path (capped). Recorded endings and status lines are removed from index.md.",
     "parameters": _schema({"path": _STR}, ["path"])},
    {"name": "check_policy", "description": "Read the agency operating policy. topic: one topic, several separated by commas, or 'all'. Topics: %s." % ", ".join(policy_topics(Config())),
     "parameters": _schema({"topic": _STR}, ["topic"])},
    {"name": "send_message", "description": "Stage a message to a party. Gates check the party exists in the case, chase timing, landlord approval before instructing a provider, appointment evidence for reminders, and that every phone number and amount in the body appears in the case. Returns staged or blocked with a reason.",
     "parameters": _schema({
         "to": {"type": "string", "enum": list(PARTIES)},
         "purpose": {"type": "string", "enum": list(PURPOSES)},
         "body": _STR,
         "evidence_refs": _STRS,
         "priority": _PRIORITY,
     }, ["to", "purpose", "body", "evidence_refs", "priority"])},
    {"name": "place_call", "description": "Stage a phone call to a party instead of a message (use when an email has gone unanswered, a voicemail was left, or the matter is urgent). Code finds the number in the case; you never give one. The caller only asks and reports back: it has no authority to approve spend or promise anything. Same gates as send_message, at most one call per case, and during an open hazard only a safety_advice call to the tenant. Returns staged or blocked with a reason.",
     "parameters": _schema({
         "party": {"type": "string", "enum": list(PARTIES)},
         "purpose": {"type": "string", "enum": list(CALL_PURPOSES)},
         "objective": {"type": "string", "description": "What the call must achieve, one or two sentences."},
         "facts": {"type": "object", "additionalProperties": {"type": "string"}, "description": "Short facts the caller may rely on (address, job, dates from the case)."},
         "evidence_refs": _STRS,
         "priority": _PRIORITY,
     }, ["party", "purpose", "objective", "facts", "evidence_refs", "priority"])},
    {"name": "route_for_approval", "description": "Stage a request to the landlord to approve a quote or cost, or (amount_gbp null) to approve a provider attending or quoting when nothing is approved yet. A stated amount must appear in the case. Blocked if the landlord already approved it.",
     "parameters": _schema({"amount_gbp": {"type": ["number", "null"]}, "scope": _STR, "body": _STR, "evidence_refs": _STRS},
                           ["amount_gbp", "scope", "body", "evidence_refs"])},
    {"name": "schedule_followup", "description": "Record when to look at this case again and why (use with a WAIT decision).",
     "parameters": _schema({"after_hours": {"type": "number"}, "waiting_on": {"type": "string", "enum": list(PARTIES) + ["internal"]}, "reason": _STR},
                           ["after_hours", "waiting_on", "reason"])},
    {"name": "escalate_to_human", "description": "Create a handover ticket for a person. Always allowed. Give a complete handover: summary, known facts, unknowns, what was tried, 2-3 options.",
     "parameters": _schema({
         "priority": _PRIORITY,
         "route": {"type": "string", "enum": ["on_call_emergency", "property_manager", "accounts", "complaints"]},
         "summary": _STR, "known": _STRS, "unknowns": _STRS, "tried": _STRS, "options": _STRS, "evidence_refs": _STRS,
     }, ["priority", "route", "summary", "known", "unknowns", "tried", "options", "evidence_refs"])},
    {"name": "close_case", "description": "Stage closing the case. Cite the event where the provider, tenant or landlord says the job is done, the event that shows the invoice position, and (if keys were held) the event confirming key return. Blocked if a later tenant message may reopen it.",
     "parameters": _schema({"completion_refs": _STRS, "invoice_status": {"type": "string", "enum": list(INVOICE_STATES)},
                            "invoice_refs": _STRS,
                            "keys_status": {"type": "string", "enum": ["returned", "not_applicable", "unknown"]},
                            "key_refs": _STRS, "reason": _STR},
                           ["completion_refs", "invoice_status", "invoice_refs", "keys_status", "key_refs", "reason"])},
    {"name": "submit_decision", "description": "Finish the case with ONE primary action. Stage the matching action first (message, approval, close, follow-up or escalation). Ends the loop.",
     "parameters": _schema({
         "action": {"type": "string", "enum": list(ACTIONS)},
         "priority": _PRIORITY,
         "reason": {"type": "string", "description": "2-5 sentences, evidence-based, citing event refs."},
         "confidence": {"type": "number", "description": "0..1 that this is the right next step."},
         "evidence_refs": _STRS,
         "unknowns": _STRS,
         "options": {"type": "array", "items": {"type": "string"}, "description": "2-3 options for a person, for ESCALATE."},
         "unrelated_issues": {"type": "array", "items": {"type": "string"}, "description": "Separate issues raised in the thread that need their own request."},
         "amount_gbp": {"type": ["number", "null"]},
         "answer": {"type": "string", "description": "Direct answer when the case asks an explicit question, task or decision point. Leave empty otherwise."},
     }, ["action", "priority", "reason", "confidence", "evidence_refs", "unknowns", "options", "unrelated_issues", "amount_gbp"])},
]

ACTION_TOOLS = {"send_message", "place_call", "route_for_approval", "schedule_followup", "escalate_to_human", "close_case"}
_PRIMARY_NEEDS = {
    "CHASE_LANDLORD": ("message", "landlord"),
    "CHASE_PROVIDER": ("message", "provider"),
    "ASK_TENANT": ("message", "tenant"),
    "ASK_PROVIDER": ("message", "provider"),
    "ASK_LANDLORD": ("message", "landlord"),
    "SEND_REMINDER": ("message", None),
    "ROUTE_FOR_APPROVAL": ("approval", "landlord"),
    "INSTRUCT_PROVIDER": ("message", "provider"),
    "CLOSE": ("close", None),
}


def staged_action(s: Dict[str, Any]) -> Optional[str]:
    """The primary action that would send this staged outbound request (None for updates, follow-ups, tickets)."""
    if s["kind"] == "approval_request":
        return "ROUTE_FOR_APPROVAL"
    if s["kind"] not in ("message", "call"):
        return None
    purpose, to = s.get("purpose"), s.get("to")
    if purpose == "request_info":
        return "ASK_" + str(to).upper()
    if purpose == "chase" and to in ("landlord", "provider"):
        return "CHASE_" + to.upper()
    return {"instruct_provider": "INSTRUCT_PROVIDER", "reminder": "SEND_REMINDER"}.get(purpose)


class Toolbox:
    def __init__(self, case: Case, cfg: Config, now: datetime, folder: Optional[Path] = None) -> None:
        self.case, self.cfg, self.now, self.folder = case, cfg, now, folder
        self.staged: List[Dict[str, Any]] = []
        self.blocked: List[Dict[str, Any]] = []
        self.decision: Optional[Dict[str, Any]] = None
        self._wait_confirmed = False
        self._by_index = {e.index: e for e in case.events}
        # Urgency comes from code, never from the model's own priority argument.
        self.hazards = gates.hazard_hits(case, cfg)
        self.urgent = bool(self.hazards)
        # Call records are third-party speech: they must not make an amount or number count as "in the case".
        self._corpus = "\n".join([case.request] + [e.body for e in case.events if not e.body.startswith(CALL_RECORD_TAG)]
                                  + [a.text or "" for a in case.attachments])
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
            s["name"]: getattr(self, "_t_" + s["name"]) for s in TOOL_SPECS
        }

    # ---------- dispatch ----------

    def call(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        handler = self._handlers.get(name)
        if handler is None:
            return {"status": "error", "error": "unknown tool %r" % name}
        if not isinstance(args, dict):
            return {"status": "error", "error": "arguments must be a JSON object"}
        try:
            result = handler(args)
        except Exception as exc:  # a tool bug must never kill the case
            result = {"status": "error", "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
        if result.get("status") == "blocked":
            self.blocked.append({"tool": name, **result})
        return result

    def _blocked(self, code: str, why: str, hint: str) -> Dict[str, Any]:
        return {"status": "blocked", "code": code, "why": why, "hint": hint}

    def _stage(self, kind: str, payload: Dict[str, Any], key: Optional[str] = None) -> Dict[str, Any]:
        key = key or hashlib.sha256(("%s|%d|%s|%s" % (self.case.case_id, len(self.case.events), kind,
                                                      sorted(payload.items()))).encode("utf-8")).hexdigest()[:12]
        for s in self.staged:
            if s["idempotency_key"] == key:
                return {"status": "staged", "id": s["id"], "duplicate": True}
        item = {"id": "%s-%d" % (kind, len(self.staged) + 1), "kind": kind, "idempotency_key": key,
                "state": "staged", **payload}
        self.staged.append(item)
        return {"status": "staged", "id": item["id"], "note": "Staged. Committed only if the final decision passes code checks."}

    # ---------- facts ----------

    def _resolve_refs(self, refs: Any) -> Tuple[List[str], List[str]]:
        good, bad = [], []
        names = {a.name for a in self.case.attachments}
        for r in _list(refs, 30):
            m = re.search(r"(\d+)", r)
            if r in names or any(r.startswith(n) for n in names):
                good.append(r)
            elif m and ("event" in r.lower() or r.strip("#e ").isdigit()) and int(m.group(1)) in self._by_index:
                good.append("event-%03d" % int(m.group(1)))
            else:
                bad.append(r)
        return good, bad

    def _last(self, party: str, outbound: bool) -> Optional[Event]:
        for e in reversed(self.case.events):
            if outbound and role_of(e.sender) == "agency" and role_of(e.recipient) == party:
                return e
            if not outbound and role_of(e.sender) == party:
                return e
        return None

    def party_exists(self, party: str) -> bool:
        if party == "landlord":
            return True  # every managed property has a landlord on the agency's books
        if party == "tenant" and "tenant" in (self.case.source_role or "").lower():
            return True
        for e in self.case.events:
            if party in (role_of(e.sender), role_of(e.recipient)):
                return True
            if party == "provider" and re.search(r"provider assigned", e.body, re.I):
                return True
        return False

    def facts(self) -> Dict[str, Any]:
        wait = self.case.waiting()
        parties = {}
        for p in PARTIES:
            out, inn = self._last(p, True), self._last(p, False)
            parties[p] = {
                "present_in_case": self.party_exists(p),
                "last_message_to": ref(out) if out else None,
                "last_message_to_at": out.ts.isoformat() if out and out.ts else None,
                "last_message_from": ref(inn) if inn else None,
                "last_message_from_at": inn.ts.isoformat() if inn and inn.ts else None,
                "replied_after_our_last_message": bool(out and inn and inn.index > out.index),
                "days_since_our_last_message": round((self.now - out.ts).total_seconds() / 86400, 1) if out and out.ts else None,
            }
        money = []
        for e in self.case.events:
            for a in _amounts(e.body):
                money.append({"ref": ref(e), "from": e.sender, "amount_gbp": a})
        for a in self.case.attachments:
            for amt in _amounts(a.text or ""):
                money.append({"ref": a.name, "amount_gbp": amt})
        done = gates.confirmed_completion(self.case)
        approval, approved_cap = evidence.covering_approval(self.case)
        quote = evidence.latest_quote(self.case)
        return {
            "as_of": self.now.isoformat(),
            "waiting_on": {"party": wait.party, "since": wait.since.isoformat(), "since_event": "event-%03d" % wait.event_index,
                           "days": round((self.now - wait.since).total_seconds() / 86400, 1)} if wait else None,
            "parties": parties,
            "money_mentions": money[:30],
            "latest_provider_quote": ref(quote) if quote else None,
            "landlord_approval_in_force": ({"ref": ref(approval), "covers_gbp": approved_cap} if approval else None),
            "open_hazard_hits": [{"ref": r, "match": m} for r, m in self.hazards[:15]],
            "urgent_by_code": self.urgent,
            "completion_signal": ref(self.case.events[done]) if done is not None else None,
            "attachments": [{"name": a.name, "available": bool(a.text)} for a in self.case.attachments],
            "input_warnings": list(self.case.warnings),
            "policy_numbers": {"chase_after_days": self.cfg.chase_after_days, "approval_limit_gbp": self.cfg.approval_limit_gbp},
        }

    # ---------- read tools ----------

    def _t_case_facts(self, args):
        return {"status": "ok", **self.facts()}

    def _t_read_events(self, args):
        try:
            first, last = int(args.get("first", 1)), int(args.get("last", 1))
        except (TypeError, ValueError):
            return {"status": "error", "error": "first and last must be integers"}
        last = min(last, first + 29)
        events = [_fmt_event(e) for e in self.case.events if first <= e.index <= last]
        return {"status": "ok", "events": events, "total_events": len(self.case.events)}

    def _t_search_case(self, args):
        q = _s(args.get("query"), 200)
        if not q:
            return {"status": "error", "error": "empty query"}
        pat = re.compile(re.escape(q), re.I)
        hits = []
        sources = [("request", self.case.request)] + [(ref(e), e.body) for e in self.case.events] + \
                  [(a.name, a.text or "") for a in self.case.attachments]
        for name, text in sources:
            for m in pat.finditer(text):
                hits.append({"ref": name, "snippet": text[max(0, m.start() - 120): m.end() + 120]})
                if len(hits) >= 15:
                    return {"status": "ok", "hits": hits, "truncated": True}
        return {"status": "ok", "hits": hits}

    def _t_read_attachment(self, args):
        name = _s(args.get("name"), 300)
        for a in self.case.attachments:
            if a.name == name or Path(name).name == a.name:
                if a.text:
                    return {"status": "ok", "name": a.name, "text": a.text, "note": "Untrusted document text."}
                return {"status": "unavailable", "name": a.name, "note": "Contents unavailable or unreadable. Do not assume what it says."}
        return {"status": "error", "error": "no attachment named %r" % name, "available": [a.name for a in self.case.attachments]}

    def _t_list_case_files(self, args):
        if not self.folder or not self.folder.is_dir():
            return {"status": "error", "error": "case folder not available"}
        files = [str(p.relative_to(self.folder)) for p in sorted(self.folder.rglob("*")) if p.is_file() and not p.is_symlink()]
        return {"status": "ok", "files": files[:100]}

    def _t_read_case_file(self, args):
        if not self.folder:
            return {"status": "error", "error": "case folder not available"}
        root = self.folder.resolve()
        target = (root / _s(args.get("path"), 300)).resolve()
        if root not in target.parents or not target.is_file() or target.is_symlink():
            return {"status": "error", "error": "path is outside the case folder or not a file"}
        if target.suffix.lower() == ".pdf":
            return self._t_read_attachment({"name": target.name})
        text = target.read_bytes()[:60000].decode("utf-8", errors="replace")
        if target.name == "index.md":
            text = redact_index(text)
        return {"status": "ok", "path": str(target.relative_to(root)), "text": text[:20000], "note": "Untrusted case text."}

    def _t_check_policy(self, args):
        topics = policy_topics(self.cfg)
        asked = [t for t in re.split(r"[\s,]+", _s(args.get("topic"), 200).lower()) if t]
        known = [t for t in asked if t in topics]
        unknown = [t for t in asked if t not in topics and t != "all"]
        if len(known) == 1 and not unknown:
            return {"status": "ok", "topic": known[0], "policy": topics[known[0]]}
        chosen = topics if not known or "all" in asked else {t: topics[t] for t in known}
        result = {"status": "ok", "policy": chosen}
        if unknown:
            result["note"] = "unknown topic(s) %s; known topics: %s" % (", ".join(unknown), ", ".join(topics))
        return result

    # ---------- action tools ----------

    def _fabrication(self, body: str) -> Optional[str]:
        corpus_digits = _digits(self._corpus)
        for m in _PHONE_RE.finditer(body):
            d = _digits(m.group(0))
            if d not in SAFE_NUMBERS and d not in corpus_digits:
                return "phone number %r does not appear in the case" % m.group(0)
        known = set(_amounts(self._corpus))
        for a in _amounts(body):
            if a not in known and round(a / 1.2, 2) not in known:
                return "amount GBP %.2f does not appear in the case" % a
        return None

    def _contact_gates(self, to: str, purpose: str) -> Optional[Dict[str, Any]]:
        """Rules shared by messages and calls: chase timing, already replied, approval before instructing."""
        urgent = self.urgent
        if purpose == "chase":
            if to == "tenant":
                return self._blocked("wrong_purpose", "chasing applies to landlords and providers",
                                     "Use purpose request_info to ask the tenant.")
            out, inn = self._last(to, True), self._last(to, False)
            if out is None:
                return self._blocked("nothing_to_chase", "we have not sent the %s anything yet" % to,
                                     "This is a first message, not a chase: use purpose request_info (ASK_%s)%s."
                                     % (to.upper(), ", or route_for_approval if the landlord must approve a visit or cost"
                                        if to == "landlord" else ""))
            if inn is not None and inn.index > out.index:
                return self._blocked("already_replied", "the %s replied at %s after our last message %s" % (to, ref(inn), ref(out)),
                                     "Act on their reply instead of chasing.")
            days = (self.now - out.ts).total_seconds() / 86400 if out.ts else None
            if days is not None and days < self.cfg.chase_after_days and not urgent:
                return self._blocked("too_early", "only %.1f days since we wrote to the %s (%s); policy is %.0f days" %
                                     (days, to, ref(out), self.cfg.chase_after_days),
                                     "Schedule a follow-up and WAIT. Only an open hazard found by code allows an early chase.")
        if purpose == "request_info" and to != "tenant":
            out, inn = self._last(to, True), self._last(to, False)
            unanswered = out is not None and out.ts is not None and (inn is None or inn.index < out.index)
            days = (self.now - out.ts).total_seconds() / 86400 if unanswered else None
            if days is not None and days < self.cfg.chase_after_days and not urgent:
                return self._blocked("too_early", "we wrote to the %s %.1f days ago (%s) and they have not replied; "
                                     "policy is %g days" % (to, days, ref(out), self.cfg.chase_after_days),
                                     "WAIT for their reply, or add the question to the chase once it is due.")
        if purpose == "instruct_provider":
            if to != "provider":
                return {"status": "error", "error": "instruct_provider messages go to the provider"}
            approval, _ = evidence.covering_approval(self.case)
            if approval is None:
                return self._blocked("no_landlord_approval",
                                     "no landlord approval in force (none recorded, negated, or older than the latest quote)",
                                     "Route the quote to the landlord first, or escalate. Urgency never skips approval.")
        return None

    def number_for(self, party: str) -> Optional[str]:
        """The party's own phone number from the case (E.164), newest first. Never taken from the model.

        Case text is untrusted, so skip quoted lines, lines that point to somebody else ("ring our accounts
        desk"), and premium-rate or non-geographic ranges.
        """
        texts = [e.body for e in reversed(self.case.events) if role_of(e.sender) == party]
        if party == "tenant":
            texts.append(self.case.request)
        for text in texts:
            for line in (text or "").splitlines():
                if line.lstrip().startswith(">") or _ELSEWHERE_RE.search(line):
                    continue
                for m in _PHONE_RE.finditer(line):
                    d = _digits(m.group(0))
                    national = "0" + (d[2:] if d.startswith("44") else d.lstrip("0"))
                    if not _UNCALLABLE_RE.match(national):
                        return "+44" + national[1:]
        return None

    def call_rounds(self) -> int:
        """Calls already made on this case, from the call records in its timeline."""
        return sum(1 for e in self.case.events if e.body.startswith(CALL_RECORD_TAG))

    def _t_place_call(self, args):
        party, purpose = _s(args.get("party"), 20), _s(args.get("purpose"), 30)
        objective, priority = _s(args.get("objective"), 500), _s(args.get("priority"), 3) or "P3"
        raw = args.get("facts")
        facts = {_s(k, 40): _s(v, 200) for k, v in list(raw.items())[:10]} if isinstance(raw, dict) else {}
        if party not in PARTIES or purpose not in CALL_PURPOSES:
            return {"status": "error", "error": "party must be one of %s and purpose one of %s" % (PARTIES, CALL_PURPOSES)}
        if len(objective) < 15:
            return self._blocked("empty_objective", "the call objective is missing or too short", "Say what the call must achieve.")
        refs, bad = self._resolve_refs(args.get("evidence_refs"))
        if not self.party_exists(party):
            return self._blocked("unknown_party", "no %s appears in this case, so there is nobody to call" % party,
                                 "Escalate if this party must be reached.")
        fab = self._fabrication(" ".join([objective] + list(facts.values())))
        if fab:
            return self._blocked("unverified_detail", fab, "Only use numbers and amounts from the case, or leave them out.")
        # Hazards: the final gate turns any other action into an escalation, so the only call that makes
        # sense is safety advice to the tenant. Everything else follows the normal message rules.
        if purpose == "safety_advice" and (party != "tenant" or not self.urgent):
            return self._blocked("no_hazard", "safety_advice calls go to the tenant and need an open hazard found by code",
                                 "Use another purpose, or escalate.")
        if purpose != "safety_advice" and self.urgent and party != "tenant":
            return self._blocked("hazard_escalate", "an open hazard is on this case; a person must decide before the %s is called" % party,
                                 "Escalate, and call the tenant with safety advice if they are at risk.")
        if self.call_rounds() + sum(1 for s in self.staged if s["kind"] == "call") >= self.cfg.max_calls_per_case:
            return self._blocked("call_limit", "this case already has the maximum of %d call(s)" % self.cfg.max_calls_per_case,
                                 "Use send_message or escalate.")
        if purpose != "safety_advice":
            blocked = self._contact_gates(party, purpose)
            if blocked:
                return blocked
        number = self.number_for(party)
        if number is None:
            return self._blocked("no_number", "no phone number for the %s appears in the case" % party,
                                 "Send a message instead, or escalate so a person can find the number.")
        facts["agency_name"] = evidence.agency_name(self.case)  # who the phone agent speaks for is not the model's choice
        # One call per party, purpose and number in each round; rewording the objective must not dial again.
        key = hashlib.sha256(("%s|call|%s|%s|%s|%d" % (self.case.case_id, party, purpose, number, self.call_rounds())).encode()).hexdigest()[:12]
        result = self._stage("call", {"to": party, "purpose": purpose, "priority": priority, "number": number,
                                      "objective": objective, "facts": facts, "evidence_refs": refs,
                                      "body": "Phone call: " + objective}, key=key)
        if bad:
            result["ignored_refs"] = bad
        return result

    def _t_send_message(self, args):
        to, purpose, body = _s(args.get("to"), 20), _s(args.get("purpose"), 30), _s(args.get("body"), 3000)
        priority = _s(args.get("priority"), 3) or "P3"
        if to not in PARTIES or purpose not in PURPOSES:
            return {"status": "error", "error": "to must be one of %s and purpose one of %s" % (PARTIES, PURPOSES)}
        if len(body) < 15:
            return self._blocked("empty_message", "message body is missing or too short", "Write the full message text.")
        refs, bad = self._resolve_refs(args.get("evidence_refs"))
        if not self.party_exists(to):
            return self._blocked("unknown_party", "no %s appears in this case, so there is no recipient on record" % to,
                                 "Escalate if this party must be contacted, or pick a party that is in the case.")
        fab = self._fabrication(body)
        if fab:
            return self._blocked("unverified_detail", fab, "Only use numbers and amounts from the case, or leave them out.")
        blocked = self._contact_gates(to, purpose)
        if blocked:
            return blocked
        if purpose == "reminder":
            booked = self._event_refs(refs)
            if not any(_APPOINTMENT_RE.search(e.body) for e in booked):
                return self._blocked("no_appointment", "evidence_refs do not include an event that records the appointment",
                                     "Cite the event that books the appointment, or do not send a reminder.")
        result = self._stage("message", {"to": to, "purpose": purpose, "priority": priority, "body": body, "evidence_refs": refs})
        if bad:
            result["ignored_refs"] = bad
        return result

    def _t_route_for_approval(self, args):
        raw = args.get("amount_gbp")
        try:
            amount = None if raw in (None, "") else round(float(raw), 2)
        except (TypeError, ValueError):
            return {"status": "error", "error": "amount_gbp must be a number or null"}
        body = _s(args.get("body"), 3000)
        refs, bad = self._resolve_refs(args.get("evidence_refs"))
        known = set(_amounts(self._corpus))
        if amount is not None and amount not in known and round(amount / 1.2, 2) not in known:
            return self._blocked("amount_not_in_case", "GBP %.2f does not appear in the case" % amount,
                                 "Use the exact quoted amount from the case, or amount_gbp null to ask approval for a "
                                 "provider to attend or quote.")
        if not self.party_exists("landlord"):
            return self._blocked("unknown_party", "no landlord appears in this case", "Escalate to the property manager.")
        fab = self._fabrication(body)
        if fab:
            return self._blocked("unverified_detail", fab, "Only use numbers and amounts from the case.")
        approval, cap = evidence.covering_approval(self.case)
        if approval is not None and (amount is None or evidence.approval_covers(self.case, amount)):
            covers = "a provider attending" if cap is None else "GBP %.2f" % cap
            return self._blocked("already_approved", "the landlord approval at %s already covers %s" % (ref(approval), covers),
                                 "Instruct the provider, ask them for a quote, or wait for the work instead of asking again.")
        result = self._stage("approval_request", {"to": "landlord", "amount_gbp": amount, "scope": _s(args.get("scope"), 500),
                                                  "body": body, "evidence_refs": refs,
                                                  "above_limit": amount is not None and amount > self.cfg.approval_limit_gbp})
        if bad:
            result["ignored_refs"] = bad
        return result

    def _t_schedule_followup(self, args):
        try:
            hours = float(args.get("after_hours"))
        except (TypeError, ValueError):
            return {"status": "error", "error": "after_hours must be a number"}
        if not 0 < hours <= 24 * 30:
            return {"status": "error", "error": "after_hours must be between 0 and 720"}
        return self._stage("followup", {"review_at": (self.now + timedelta(hours=hours)).isoformat(),
                                        "waiting_on": _s(args.get("waiting_on"), 20), "reason": _s(args.get("reason"), 500)})

    def _t_escalate_to_human(self, args):
        refs, bad = self._resolve_refs(args.get("evidence_refs"))
        priority = _s(args.get("priority"), 3)
        result = self._stage("escalation", {
            "priority": priority if priority in PRIORITIES else "P2",
            "route": _s(args.get("route"), 40) or "property_manager",
            "summary": _s(args.get("summary"), 1500),
            "known": _list(args.get("known")), "unknowns": _list(args.get("unknowns")),
            "tried": _list(args.get("tried")), "options": _list(args.get("options"), 5), "evidence_refs": refs,
        })
        if bad:
            result["ignored_refs"] = bad
        return result

    def _event_refs(self, refs: List[str]) -> List[Event]:
        return [self._by_index[int(re.search(r"\d+", r).group())] for r in refs if r.startswith("event-")]

    def _keys_out(self) -> Optional[Event]:
        """The latest event saying keys are held, if no later event says they came back."""
        held = [e for e in self.case.events if _KEY_HELD_RE.search(e.body)]
        if not held:
            return None
        back = [e for e in self.case.events if evidence.affirmed(_KEY_BACK_RE, e.body)]
        return None if back and back[-1].index > held[-1].index else held[-1]

    def _t_close_case(self, args):
        """Completion uses the same definition as the final gate (gates.confirmed_completion)."""
        refs, bad = self._resolve_refs(args.get("completion_refs"))
        confirmers = [e for e in self._event_refs(refs) if evidence.reports_completion(e)]
        if not confirmers:
            return self._blocked("no_confirmation",
                                 "none of the cited events is a provider, tenant or landlord saying the job is done "
                                 "(agency notes, quotes, questions and negated mentions do not count)",
                                 "Cite the confirming event, or ask the provider (ASK_PROVIDER) or tenant (ASK_TENANT) "
                                 "to confirm completion.")
        done = gates.confirmed_completion(self.case)
        if done is None or self.case.events[done].index < max(e.index for e in confirmers):
            if gates.later_followup(self.case) == "side":
                return self._blocked("side_unanswered",
                                     "a later tenant message is about something else and nobody has answered it",
                                     "List it in unrelated_issues. The case does not close while that message is "
                                     "unanswered. This is routine, not a reason to escalate.")
            return self._blocked("possibly_reopened",
                                 "a later tenant message reports a fault or asks about this job, so it may be reopened",
                                 "ASK_TENANT whether the fix worked. This is a routine question, not a reason to escalate.")
        invoice = _s(args.get("invoice_status"), 30)
        invoice_refs, _ = self._resolve_refs(args.get("invoice_refs"))
        routine = " This is a routine question, not a reason to escalate."
        if invoice not in INVOICE_STATES or invoice == "unknown":
            return self._blocked("invoice_unknown", "the invoice position is not known",
                                 "Ask the provider for the invoice (ASK_PROVIDER) or the landlord how it is paid "
                                 "(ASK_LANDLORD)." + routine)
        if not any(evidence.INVOICE_RE.search(e.body) for e in self._event_refs(invoice_refs)):
            return self._blocked("invoice_unverified", "no cited event shows the invoice position (%s)" % invoice,
                                 "Cite the event that shows the invoice was sent, paid directly or not charged; an "
                                 "unreadable invoice file still counts as sent if an event says it was sent. If none "
                                 "exists, ASK_PROVIDER for it." + routine)
        keys = _s(args.get("keys_status"), 20)
        key_refs, _ = self._resolve_refs(args.get("key_refs"))
        out = self._keys_out()
        if keys in ("unknown", "not_applicable") and out is not None:
            return self._blocked("keys_unknown", "keys are mentioned as held at %s and no later event shows them returned" % ref(out),
                                 "Ask the provider (ASK_PROVIDER) or tenant (ASK_TENANT) whether the keys came back." + routine)
        if keys == "returned" and not any(evidence.KEYS_RE.search(e.body) for e in self._event_refs(key_refs)):
            return self._blocked("keys_unverified", "no cited event shows the keys were returned", "Cite the event that confirms key return.")
        if keys == "unknown":
            keys = "not_applicable"  # no key was ever held
        result = self._stage("closure", {"completion_refs": [ref(e) for e in confirmers], "invoice_status": invoice,
                                         "invoice_refs": invoice_refs, "keys_status": keys, "key_refs": key_refs,
                                         "reason": _s(args.get("reason"), 800)})
        if bad:
            result["ignored_refs"] = bad
        return result

    # ---------- finish ----------

    def _t_submit_decision(self, args):
        action = _s(args.get("action"), 30).upper()
        if action not in ACTIONS:
            return {"status": "error", "error": "action must be one of %s" % (ACTIONS,)}
        need = _PRIMARY_NEEDS.get(action)
        if need:
            kind, party = need
            kinds = {"message": ("message", "call"), "approval": ("approval_request",), "close": ("closure",)}
            match = [s for s in self.staged if s["kind"] in kinds[kind] and (party is None or s.get("to") == party)]
            if action == "SEND_REMINDER":
                match = [s for s in match if s.get("purpose") == "reminder"]
            if action.startswith("CHASE"):
                match = [s for s in match if s.get("purpose") == "chase"]
            if action.startswith("ASK_"):
                match = [s for s in match if s.get("purpose") == "request_info"]
            if action == "INSTRUCT_PROVIDER":
                match = [s for s in match if s.get("purpose") == "instruct_provider"]
            if not match:
                return self._blocked("action_not_staged", "%s needs a staged %s%s first" % (action, kind, " to the %s" % party if party else ""),
                                     "Call the matching action tool, or choose WAIT/ESCALATE if it was blocked.")
        if action == "WAIT" and not self._wait_confirmed:
            pending = [(s["id"], staged_action(s)) for s in self.staged if staged_action(s)]
            if pending:
                # Refused once: a second WAIT is accepted and the staged requests stay held for a person.
                self._wait_confirmed = True
                names = sorted({a for _, a in pending})
                return self._blocked("staged_not_submitted",
                                     "WAIT holds what you staged (%s), so nothing would be sent" % ", ".join(
                                         "%s as %s" % p for p in pending),
                                     "Submit %s if it should go out now. Submit WAIT again only if it must not be sent yet."
                                     % " or ".join(names))
        refs, bad = self._resolve_refs(args.get("evidence_refs"))
        try:
            confidence = min(1.0, max(0.0, float(args.get("confidence"))))
        except (TypeError, ValueError):
            return {"status": "error", "error": "confidence must be a number from 0 to 1"}
        amount = args.get("amount_gbp")
        try:
            amount = None if amount in (None, "") else max(0.0, float(amount))
        except (TypeError, ValueError):
            amount = None
        priority = _s(args.get("priority"), 3)
        self.decision = {
            "action": action, "priority": priority if priority in PRIORITIES else "P2",
            "reason": _s(args.get("reason"), 2400), "confidence": confidence, "evidence_refs": refs,
            "unknowns": _list(args.get("unknowns")), "options": _list(args.get("options"), 5),
            "unrelated_issues": _list(args.get("unrelated_issues"), 5), "amount_gbp": amount,
            "answer": _s(args.get("answer"), 2000),
        }
        return {"status": "accepted", "ignored_refs": bad} if bad else {"status": "accepted"}
