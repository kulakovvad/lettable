"""The escalation packet a person can act on without re-reading the case.

Filled by code when the model omits a field. Existing text is kept. Route and
priority only move stricter: a payment flag becomes accounts at P1 or above,
and an on-call emergency route is left in place.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence

from agent.timeline import Case

_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
_HOURS = {"P0": 1, "P1": 4, "P2": 24, "P3": 72}
_DEFAULTS = (
    "A person reads the conflicts and decides the next step",
    "Contact the relevant party on a number already in the case",
    "Leave the case with the named route if more information is needed",
)


def more_urgent(a: Optional[str], b: Optional[str]) -> str:
    if a not in _RANK:
        return b if b in _RANK else "P2"
    if b not in _RANK:
        return a
    return a if _RANK[a] <= _RANK[b] else b


def event_digest(case: Optional[Case], limit: int = 6) -> List[str]:
    """One line per recent event, for a fallback answer."""
    if case is None or not case.events:
        return []
    events = case.events
    start = max(0, len(events) - limit)
    lines = ["%d earlier events not listed" % start] if start else []
    for e in events[start:]:
        when = e.ts.strftime("%Y-%m-%d %H:%M") if e.ts else "unknown time"
        body = re.sub(r"\s+", " ", e.body or "").strip()
        if len(body) > 140:
            body = body[:140] + "..."
        lines.append("event-%03d %s %s -> %s: %s" % (e.index, when, e.sender, e.recipient, body))
    return lines


def conflicts_from(report: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for c in (report or {}).get("checks") or []:
        if c.get("tier") not in ("flag", "escalate"):
            continue
        values = []
        for value, refs in zip(c.get("values") or [], c.get("refs") or []):
            values.append({"value": value, "refs": list(refs)})
        out.append({"field": c.get("field"), "values": values})
    return out


def _route(current: Optional[str], flags: Sequence[Dict[str, Any]], hazard: bool) -> str:
    route = current or ("on_call_emergency" if hazard else "property_manager")
    payment = any(f.get("force") and f.get("category") == "payment" for f in flags)
    if payment and route != "on_call_emergency":
        return "accounts"
    return route


def _priority(current: Optional[str], flags: Sequence[Dict[str, Any]], hazard: bool) -> str:
    priority = current if current in _RANK else "P2"
    if hazard:
        priority = more_urgent(priority, "P1")
    for f in flags:
        if f.get("force") and f.get("priority"):
            priority = more_urgent(priority, f["priority"])
    return priority


def _options(existing: Sequence[Any], fallback: Sequence[Any]) -> List[str]:
    opts = [str(o).strip() for o in list(existing) or list(fallback) if str(o).strip()]
    for line in _DEFAULTS:
        if len(opts) >= 2:
            break
        if line not in opts:
            opts.append(line)
    opts = opts[:3]
    if opts and not any(o.lower().startswith("recommended:") for o in opts):
        opts[0] = "Recommended: " + opts[0]
    return opts


def enrich(ticket: Dict[str, Any], case: Optional[Case], now: datetime, *, reason: str = "",
           unknowns: Sequence[str] = (), options: Sequence[str] = (), gate_notes: Sequence[str] = (),
           proposed: Optional[str] = None, flags: Sequence[Dict[str, Any]] = (),
           consistency_report: Optional[Dict[str, Any]] = None, hazard: bool = False,
           digest: bool = False) -> Dict[str, Any]:
    """Fill a staged escalation so it has a route, a deadline, conflicts, and a recommendation."""
    priority = _priority(ticket.get("priority"), flags, hazard)
    ticket["priority"] = priority
    ticket["route"] = _route(ticket.get("route"), flags, hazard)
    if not ticket.get("respond_by"):
        ticket["respond_by"] = (now + timedelta(hours=_HOURS.get(priority, 24))).isoformat()
    if not ticket.get("summary"):
        ticket["summary"] = (reason or "Escalated for a person to decide.")[:1500]
    if not ticket.get("conflicts"):
        ticket["conflicts"] = conflicts_from(consistency_report)

    known = [str(k) for k in ticket.get("known") or [] if str(k).strip()]
    if case is not None:
        if case.title and not any(case.title in k for k in known):
            known.insert(0, "Title: %s (index)" % case.title)
        if case.property and not any(case.property in k for k in known):
            known.append("Property: %s (index)" % case.property)
        request = re.sub(r"\s+", " ", case.request or "").strip()
        if request and not any(k.startswith("Request:") for k in known):
            known.append("Request: %s (request)" % request[:300])
    if digest:
        for line in event_digest(case):
            if line not in known:
                known.append(line)
    ticket["known"] = known[:14]

    missing = [str(k) for k in ticket.get("unknowns") or [] if str(k).strip()]
    for item in unknowns:
        if item and item not in missing:
            missing.append(item)
    if ticket["conflicts"] and not any("conflict" in m.lower() for m in missing):
        missing.append("Which conflicting value is right (see conflicts)")
    ticket["unknowns"] = missing[:8]

    tried = [str(k) for k in ticket.get("tried") or [] if str(k).strip()]
    if proposed and not any(proposed in t for t in tried):
        tried.append("Agent proposed %s" % proposed)
    for note in gate_notes:
        if note and note not in tried:
            tried.append(note)
    ticket["tried"] = tried[:8]

    failed = [str(k) for k in ticket.get("failed") or [] if str(k).strip()]
    for f in flags:
        if f.get("category") == "failed_action":
            line = "%s: %s" % (f.get("ref"), f.get("excerpt"))
            if line not in failed:
                failed.append(line)
    ticket["failed"] = failed[:6]

    opts = _options(ticket.get("options") or (), options)
    ticket["options"] = opts
    ticket["recommended"] = next((o for o in opts if o.lower().startswith("recommended:")), opts[0] if opts else "")

    refs = list(ticket.get("evidence_refs") or [])
    for f in flags:
        ref = f.get("ref")
        if ref and ref not in refs and ref != "request":
            refs.append(ref)
    ticket["evidence_refs"] = refs[:20]
    return ticket
