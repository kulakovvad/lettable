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

from agent import gates
from agent.config import Config
from agent.policy import policy_topics
from agent.schema import ACTIONS
from agent.timeline import Case, Event

PRIORITIES = ("P0", "P1", "P2", "P3")
PARTIES = ("tenant", "landlord", "provider")
PURPOSES = ("chase", "request_info", "reminder", "update", "safety_advice", "instruct_provider")
INVOICE_STATES = ("sent_to_landlord", "landlord_pays_directly", "no_charge", "unknown")
# Numbers a safety message may always contain: gas emergency, emergency services, NHS 111, power cut 105.
SAFE_NUMBERS = {"08001119999", "999", "111", "105"}

_PHONE_RE = re.compile(r"(?:\+44\s?\(?0?\)?|\b0)\d(?:[\s-]?\d){8,10}\b")
_MONEY_RE = re.compile(r"£\s?(\d[\d,]*(?:\.\d{1,2})?)|\b(\d[\d,]*(?:\.\d{1,2})?)\s?(?:GBP|pounds)\b", re.I)
_APPROVAL_RE = re.compile(r"\b(go ahead|approved?|proceed|yes,? please|happy (?:for|to)|ok to|okay to|fine to|authori[sz]e)\b", re.I)
_AGENCY_APPROVAL_RE = re.compile(r"\b(landlord approval confirmed|estimate approved|quote approved|landlord (?:has )?approved)\b", re.I)
_APPOINTMENT_RE = re.compile(r"\b(appointment|booked|attend(?:ing|ance)?|visit|scheduled|between \d{1,2}(?::\d\d)? ?(?:am|pm)?(?: and| -| to) \d)", re.I)
_REOPEN_RE = re.compile(r"\b(still|again|not working|isn't working|is not working|came back|is back|broken|leak(?:ing)?|worse|not fixed|hasn't been)\b", re.I)
_SECTION_RE = re.compile(r"^## (Overview|Outcome|Summary|Resolution)\b.*?(?=^## |\Z)", re.M | re.S | re.I)


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


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def _amounts(text: str) -> List[float]:
    out = []
    for m in _MONEY_RE.finditer(text):
        raw = (m.group(1) or m.group(2) or "").replace(",", "")
        try:
            out.append(round(float(raw), 2))
        except ValueError:
            pass
    return out


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
    {"name": "search_case", "description": "Case-insensitive search across events, the request and attachment text. Returns refs and snippets.",
     "parameters": _schema({"query": _STR}, ["query"])},
    {"name": "read_attachment", "description": "Extracted text of one attachment by file name, or a note that its contents are unavailable.",
     "parameters": _schema({"name": _STR}, ["name"])},
    {"name": "list_case_files", "description": "List files in the case folder (for unusual case formats).",
     "parameters": _schema({}, [])},
    {"name": "read_case_file", "description": "Read a text file in the case folder by relative path (capped). Summary/outcome sections are removed.",
     "parameters": _schema({"path": _STR}, ["path"])},
    {"name": "check_policy", "description": "Read the agency operating policy. Topics: authority, chasing, safety, closing, communication, escalation, scope, data, or 'all'.",
     "parameters": _schema({"topic": _STR}, ["topic"])},
    {"name": "send_message", "description": "Stage a message to a party. Gates check the party exists in the case, chase timing, landlord approval before instructing a provider, appointment evidence for reminders, and that every phone number and amount in the body appears in the case. Returns staged or blocked with a reason.",
     "parameters": _schema({
         "to": {"type": "string", "enum": list(PARTIES)},
         "purpose": {"type": "string", "enum": list(PURPOSES)},
         "body": _STR,
         "evidence_refs": _STRS,
         "priority": _PRIORITY,
     }, ["to", "purpose", "body", "evidence_refs", "priority"])},
    {"name": "route_for_approval", "description": "Stage a request to the landlord to approve a quote or cost. The amount must appear in the case. Blocked if the landlord already approved it.",
     "parameters": _schema({"amount_gbp": {"type": "number"}, "scope": _STR, "body": _STR, "evidence_refs": _STRS},
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
    {"name": "close_case", "description": "Stage closing the case. Requires completion confirmed by provider, tenant or landlord (event refs), no later report reopening it, and a known invoice position.",
     "parameters": _schema({"completion_refs": _STRS, "invoice_status": {"type": "string", "enum": list(INVOICE_STATES)},
                            "keys_status": {"type": "string", "enum": ["returned", "not_applicable", "unknown"]}, "reason": _STR},
                           ["completion_refs", "invoice_status", "keys_status", "reason"])},
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
     }, ["action", "priority", "reason", "confidence", "evidence_refs", "unknowns", "options", "unrelated_issues", "amount_gbp"])},
]

ACTION_TOOLS = {"send_message", "route_for_approval", "schedule_followup", "escalate_to_human", "close_case"}
_PRIMARY_NEEDS = {
    "CHASE_LANDLORD": ("message", "landlord"),
    "CHASE_PROVIDER": ("message", "provider"),
    "ASK_TENANT": ("message", "tenant"),
    "SEND_REMINDER": ("message", None),
    "ROUTE_FOR_APPROVAL": ("approval", "landlord"),
    "INSTRUCT_PROVIDER": ("message", "provider"),
    "CLOSE": ("close", None),
}


class Toolbox:
    def __init__(self, case: Case, cfg: Config, now: datetime, folder: Optional[Path] = None) -> None:
        self.case, self.cfg, self.now, self.folder = case, cfg, now, folder
        self.staged: List[Dict[str, Any]] = []
        self.blocked: List[Dict[str, Any]] = []
        self.decision: Optional[Dict[str, Any]] = None
        self._by_index = {e.index: e for e in case.events}
        self._corpus = "\n".join([case.request] + [e.body for e in case.events] + [a.text or "" for a in case.attachments])
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

    def _stage(self, kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        key = hashlib.sha256(("%s|%d|%s|%s" % (self.case.case_id, len(self.case.events), kind,
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

    def latest_quote(self) -> Optional[Event]:
        for e in reversed(self.case.events):
            if role_of(e.sender) == "provider" and _amounts(e.body):
                return e
        return None

    def landlord_approval(self) -> Optional[Event]:
        """Latest landlord approval that postdates the latest provider quote (approving a visit is not approving a quote)."""
        quote = self.latest_quote()
        for e in reversed(self.case.events):
            if quote is not None and e.index <= quote.index:
                return None
            if role_of(e.sender) == "landlord" and _APPROVAL_RE.search(e.body):
                return e
            if role_of(e.sender) in ("agency", "other") and _AGENCY_APPROVAL_RE.search(e.body):
                return e
        return None

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
        hazards = []
        for p in self.cfg.hazard_patterns:
            for e in self.case.events:
                m = re.search(p, e.body, re.I)
                if m:
                    hazards.append({"ref": ref(e), "match": m.group(0)})
            for a in self.case.attachments:
                m = re.search(p, a.text or "", re.I)
                if m:
                    hazards.append({"ref": a.name, "match": m.group(0)})
        done = gates.confirmed_completion(self.case)
        approval = self.landlord_approval()
        return {
            "as_of": self.now.isoformat(),
            "waiting_on": {"party": wait.party, "since": wait.since.isoformat(), "since_event": "event-%03d" % wait.event_index,
                           "days": round((self.now - wait.since).total_seconds() / 86400, 1)} if wait else None,
            "parties": parties,
            "money_mentions": money[:30],
            "latest_provider_quote": ref(self.latest_quote()) if self.latest_quote() else None,
            "landlord_approval_after_latest_quote": ref(approval) if approval else None,
            "hazard_keyword_hits": hazards[:15],
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
        try:
            pat = re.compile(q, re.I)
        except re.error:
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
            text = _SECTION_RE.sub("", text)
        return {"status": "ok", "path": str(target.relative_to(root)), "text": text[:20000], "note": "Untrusted case text."}

    def _t_check_policy(self, args):
        topics = policy_topics(self.cfg)
        topic = _s(args.get("topic"), 40).lower()
        if topic in topics:
            return {"status": "ok", "topic": topic, "policy": topics[topic]}
        return {"status": "ok", "policy": topics}

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
        urgent = priority in ("P0", "P1")
        if purpose == "chase":
            if to == "tenant":
                return self._blocked("wrong_purpose", "chasing applies to landlords and providers",
                                     "Use purpose request_info to ask the tenant.")
            out, inn = self._last(to, True), self._last(to, False)
            if out is None:
                return self._blocked("nothing_to_chase", "we have not sent the %s anything yet" % to,
                                     "Use purpose request_info or update for a first message.")
            if inn is not None and inn.index > out.index:
                return self._blocked("already_replied", "the %s replied at %s after our last message %s" % (to, ref(inn), ref(out)),
                                     "Act on their reply instead of chasing.")
            days = (self.now - out.ts).total_seconds() / 86400 if out.ts else None
            if days is not None and days < self.cfg.chase_after_days and not urgent:
                return self._blocked("too_early", "only %.1f days since we wrote to the %s (%s); policy is %.0f days" %
                                     (days, to, ref(out), self.cfg.chase_after_days),
                                     "Schedule a follow-up and WAIT, unless the risk is P0/P1.")
        if purpose == "instruct_provider":
            if to != "provider":
                return {"status": "error", "error": "instruct_provider messages go to the provider"}
            approval = self.landlord_approval()
            if approval is None and not urgent:
                return self._blocked("no_landlord_approval", "no landlord approval is recorded for this work",
                                     "Route the quote to the landlord first, or escalate.")
        if purpose == "reminder":
            evidence = [self._by_index[int(re.search(r"\d+", r).group())] for r in refs if r.startswith("event-")]
            if not any(_APPOINTMENT_RE.search(e.body) for e in evidence):
                return self._blocked("no_appointment", "evidence_refs do not include an event that records the appointment",
                                     "Cite the event that books the appointment, or do not send a reminder.")
        result = self._stage("message", {"to": to, "purpose": purpose, "priority": priority, "body": body, "evidence_refs": refs})
        if bad:
            result["ignored_refs"] = bad
        return result

    def _t_route_for_approval(self, args):
        try:
            amount = round(float(args.get("amount_gbp")), 2)
        except (TypeError, ValueError):
            return {"status": "error", "error": "amount_gbp must be a number"}
        body = _s(args.get("body"), 3000)
        refs, bad = self._resolve_refs(args.get("evidence_refs"))
        known = set(_amounts(self._corpus))
        if amount not in known and round(amount / 1.2, 2) not in known:
            return self._blocked("amount_not_in_case", "GBP %.2f does not appear in the case" % amount,
                                 "Use the exact quoted amount from the case, or ask the provider for a written quote.")
        if not self.party_exists("landlord"):
            return self._blocked("unknown_party", "no landlord appears in this case", "Escalate to the property manager.")
        fab = self._fabrication(body)
        if fab:
            return self._blocked("unverified_detail", fab, "Only use numbers and amounts from the case.")
        first = next((e for e in self.case.events if amount in _amounts(e.body)), None)
        if first is not None:
            for e in self.case.events:
                if e.index > first.index and role_of(e.sender) == "landlord" and _APPROVAL_RE.search(e.body):
                    return self._blocked("already_approved", "the landlord approved at %s after the amount appeared at %s" % (ref(e), ref(first)),
                                         "Instruct the provider or wait for the work instead of asking again.")
        result = self._stage("approval_request", {"to": "landlord", "amount_gbp": amount, "scope": _s(args.get("scope"), 500),
                                                  "body": body, "evidence_refs": refs,
                                                  "above_limit": amount > self.cfg.approval_limit_gbp})
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

    def _t_close_case(self, args):
        refs, bad = self._resolve_refs(args.get("completion_refs"))
        events = [self._by_index[int(re.search(r"\d+", r).group())] for r in refs if r.startswith("event-")]
        confirmers = [e for e in events if role_of(e.sender) in PARTIES]
        if not confirmers:
            return self._blocked("no_confirmation", "none of the cited events is a completion confirmation from the provider, tenant or landlord",
                                 "Ask the provider or tenant to confirm completion.")
        latest = max(e.index for e in confirmers)
        later = [e for e in self.case.events if e.index > latest and role_of(e.sender) == "tenant" and _REOPEN_RE.search(e.body)]
        if later:
            return self._blocked("possibly_reopened", "the tenant wrote %s after the confirmation and it may report the problem continues" % ref(later[0]),
                                 "Check with the tenant before closing.")
        invoice = _s(args.get("invoice_status"), 30)
        if invoice not in INVOICE_STATES or invoice == "unknown":
            return self._blocked("invoice_unknown", "the invoice position is not known",
                                 "Ask the provider for the invoice or confirm with the landlord how it is paid.")
        if _s(args.get("keys_status"), 20) == "unknown":
            return self._blocked("keys_unknown", "key return is not confirmed", "Confirm keys were returned, or mark not_applicable if no keys were held.")
        return self._stage("closure", {"completion_refs": [ref(e) for e in confirmers], "invoice_status": invoice,
                                       "keys_status": _s(args.get("keys_status"), 20), "reason": _s(args.get("reason"), 800)})

    # ---------- finish ----------

    def _t_submit_decision(self, args):
        action = _s(args.get("action"), 30).upper()
        if action not in ACTIONS:
            return {"status": "error", "error": "action must be one of %s" % (ACTIONS,)}
        need = _PRIMARY_NEEDS.get(action)
        if need:
            kind, party = need
            kinds = {"message": "message", "approval": "approval_request", "close": "closure"}
            match = [s for s in self.staged if s["kind"] == kinds[kind] and (party is None or s.get("to") == party)]
            if action == "SEND_REMINDER":
                match = [s for s in match if s.get("purpose") == "reminder"]
            if action.startswith("CHASE"):
                match = [s for s in match if s.get("purpose") == "chase"]
            if action == "INSTRUCT_PROVIDER":
                match = [s for s in match if s.get("purpose") == "instruct_provider"]
            if not match:
                return self._blocked("action_not_staged", "%s needs a staged %s%s first" % (action, kinds[kind], " to the %s" % party if party else ""),
                                     "Call the matching action tool, or choose WAIT/ESCALATE if it was blocked.")
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
        }
        return {"status": "accepted", "ignored_refs": bad} if bad else {"status": "accepted"}
