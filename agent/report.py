"""Write one case's results. Every file is written atomically (temp file, then rename)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

from agent import consistency, redflags
from agent.mismatches import CHECKED
from agent.files import atomic_write  # noqa: F401 (re-exported for existing imports)

_TITLES = {
    "WAIT": "Wait, nothing to do yet",
    "CHASE_LANDLORD": "Chase the landlord",
    "CHASE_PROVIDER": "Chase the provider",
    "ASK_TENANT": "Ask the tenant for more information",
    "ASK_PROVIDER": "Ask the provider for more information",
    "ASK_LANDLORD": "Ask the landlord for more information",
    "ROUTE_FOR_APPROVAL": "Send for landlord approval",
    "INSTRUCT_PROVIDER": "Instruct the provider (landlord approved)",
    "SEND_REMINDER": "Send an appointment reminder",
    "CLOSE": "Close the case",
    "ESCALATE": "Escalate to a person",
}


def _bullets(items: Any) -> str:
    return "\n".join("- %s" % i for i in items) if items else "- none"


def _action_line(a: Dict[str, Any]) -> str:
    kind = a.get("kind")
    if kind == "message":
        head = "Message to %s (%s, %s)" % (a.get("to"), a.get("purpose"), a.get("priority"))
    elif kind == "call" and a.get("purpose") == "oncall_brief":
        head = "On-call briefing call (%s), %s: %s" % (a.get("priority"), a.get("call_status", "?"), a.get("objective"))
        if a.get("conversation_id"):
            head += " [conversation %s]" % a["conversation_id"]
        if a.get("call_result"):
            head += ". Acknowledgement: %s" % ((a["call_result"].get("data") or {}).get("outcome")
                                               or a["call_result"].get("summary") or a["call_result"].get("status"))
    elif kind == "call":
        head = "Phone call to %s (%s, %s), %s: %s" % (a.get("to"), a.get("purpose"), a.get("priority"),
                                                      a.get("call_status", "?"), a.get("objective"))
        if a.get("conversation_id"):
            head += " [conversation %s]" % a["conversation_id"]
        if a.get("call_result"):
            head += ". Result: %s" % (a["call_result"].get("summary") or a["call_result"].get("status"))
    elif kind == "approval_request":
        cost = "for GBP %.2f" % a["amount_gbp"] if a.get("amount_gbp") is not None else "to attend or quote, no cost"
        head = "Approval request to landlord %s (%s)" % (cost, a.get("scope", ""))
    elif kind == "escalation":
        head = "Escalation ticket %s to %s" % (a.get("priority"), a.get("route"))
    elif kind == "followup":
        head = "Follow-up at %s, waiting on %s: %s" % (a.get("review_at"), a.get("waiting_on"), a.get("reason"))
    elif kind == "closure":
        head = "Close case (completion %s; invoice %s; keys %s)" % (
            ", ".join(a.get("completion_refs") or []), a.get("invoice_status"), a.get("keys_status"))
    else:
        head = str(kind)
    return "- **%s**: %s `%s`. %s" % (a.get("state", "").upper(), head, a.get("id"), a.get("note", ""))


def _d(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _l(value: Any) -> list:
    return value if isinstance(value, list) else []


def _refs(entry: Any) -> str:
    return " [%s]" % ", ".join(str(r) for r in _l(entry.get("refs"))) if isinstance(entry, dict) and _l(entry.get("refs")) else ""


def _vals(entries: Any) -> str:
    return "; ".join("%s%s" % (e.get("value"), _refs(e)) for e in _l(entries) if isinstance(e, dict))


def _details_section(det: Any) -> list:
    """The case card (decision['details'], schema case-card/1): readable groups, then the same data as JSON.
    Missing or unknown-shaped data gives no section, never an error."""
    if not isinstance(det, dict) or det.get("schema") != "case-card/1":
        return []
    out = ["## Details", ""]

    def group(title: str, rows: list) -> None:
        rows = [r for r in rows if r]
        if rows:
            out.extend(["### %s" % title, ""] + ["- %s" % r for r in rows] + [""])

    def line(label: str, value: Any) -> str:
        return "**%s:** %s" % (label, value) if value not in ("", None, [], {}) else ""

    c, p = _d(det.get("case")), _d(det.get("property"))
    group("Case", [line("Id", c.get("id")), line("Title", c.get("title")), line("Raised by", c.get("source_role")),
                   line("Request", c.get("request"))])
    variants = [v for v in _l(p.get("address_variants")) if isinstance(v, dict)]
    group("Property", [line("Address", p.get("address")),
                       line("Other address forms in the case", _vals(variants[1:] if len(variants) > 1 else [])),
                       line("References", "; ".join("%s %s%s" % (r.get("kind"), r.get("value"), _refs(r))
                                                    for r in _l(p.get("references")) if isinstance(r, dict)))])
    for key, title in (("tenant", "Tenant"), ("landlord", "Landlord")):
        x = _d(det.get(key))
        group(title, [line("Name", x.get("name")), line("Names seen", _vals(x.get("names")) if len(_l(x.get("names"))) > 1 else ""),
                      line("Phones", _vals(x.get("phones"))), line("Emails", _vals(x.get("emails")))])
    ag = _d(det.get("agency"))
    group("Agency", [line("Name", ag.get("name")), line("Phones", _vals(ag.get("phones"))),
                     line("Emails", _vals(ag.get("emails"))), line("Staff who signed", _vals(ag.get("staff")))])
    pr = _d(det.get("provider"))
    group("Provider", [line("Name", pr.get("name")), line("Assigned at", pr.get("assigned_ref")),
                       line("Phones", _vals(pr.get("phones"))), line("Emails", _vals(pr.get("emails")))])
    m = _d(det.get("money"))
    ap = _d(m.get("approval"))
    group("Money", [
        line("Quotes", "; ".join("GBP %.2f (VAT %s, %s) [%s]" % (q.get("amount_gbp") or 0, q.get("vat"), q.get("from"), q.get("ref"))
                                 for q in _l(m.get("quotes")) if isinstance(q, dict))),
        line("Invoices", "; ".join("GBP %.2f (%s) [%s]" % (q.get("amount_gbp") or 0, q.get("from"), q.get("ref"))
                                   for q in _l(m.get("invoices")) if isinstance(q, dict))),
        line("Landlord approval", "%s [%s]" % ("GBP %.2f" % ap["amount_gbp"] if ap.get("amount_gbp") is not None else
                                               "for the visit, no amount", ap.get("ref")) if ap.get("ref") else ""),
        line("Payments", "; ".join("%s: %s [%s]" % (q.get("kind"), q.get("text"), q.get("ref"))
                                   for q in _l(m.get("payments")) if isinstance(q, dict))),
        line("Deposit", "; ".join("%s%s [%s]" % (q.get("text"), " (GBP %.2f)" % q["amount_gbp"] if q.get("amount_gbp") is not None else "",
                                                 q.get("ref")) for q in _l(m.get("deposit")) if isinstance(q, dict)))])
    group("Appointments", ["%s [%s]" % (a.get("when_text"), a.get("ref")) for a in _l(det.get("appointments")) if isinstance(a, dict)])
    t = _d(det.get("timeline"))
    w = _d(t.get("waiting_on"))
    group("Timeline", [
        line("Events", "%s%s" % (t.get("events"), ", first %s, last %s" % (t.get("first"), t.get("last")) if t.get("first") else "")),
        line("Waiting on", "the %s%s" % (w.get("party"), " for %s days" % w["days"] if w.get("days") is not None else "") if w.get("party") else ""),
        line("Channels", ", ".join("%s %s" % (k, v) for k, v in _d(t.get("channels")).items()))])
    group("Attachments", ["%s (%s, %s)" % (a.get("name"), a.get("kind"), "content read" if a.get("available") else "content not available")
                          for a in _l(det.get("attachments")) if isinstance(a, dict)])
    dc = _d(det.get("decision"))
    group("Decision", [line("Action", _TITLES.get(dc.get("action"), dc.get("action"))), line("Priority", dc.get("priority")),
                       line("Confidence", "%.2f" % dc["confidence"] if isinstance(dc.get("confidence"), (int, float)) else ""),
                       line("Decided by", "%s%s" % (dc.get("decided_by"), " (%s)" % dc["cause"] if dc.get("cause") else "")),
                       line("As of", dc.get("as_of")), line("Evidence cited", ", ".join(str(r) for r in _l(dc.get("evidence_refs"))))])
    group("Calls", ["%s: %s%s" % (c2.get("party"), c2.get("status"), " (%s)" % c2["result_summary"] if c2.get("result_summary") else "")
                    for c2 in _l(det.get("calls")) if isinstance(c2, dict)])
    group("Input warnings", [str(x) for x in _l(det.get("warnings"))])
    out += ["### Case card (machine-readable)", "", "```json", json.dumps(det, indent=2, ensure_ascii=False), "```", ""]
    return out


def _mismatch_section(d: Dict[str, Any]) -> list:
    """Only when the decision recorded the check (an older decision.json has no 'mismatches' key)."""
    if "mismatches" not in d or not isinstance(d["mismatches"], list):
        return []
    items = [m for m in d["mismatches"] if isinstance(m, dict)]
    rep = d.get("consistency")
    state = "off" if rep is None else ("unavailable" if isinstance(rep, dict) and rep.get("status") != "ok" else "on")
    out = ["## Inconsistencies and mismatches", ""]
    if not items:
        return out + ["None found.", "", "Checked: %s; document consistency check %s." % (CHECKED, state), ""]
    for m in items:
        refs = ", ".join(str(r) for r in m.get("refs") or [])
        out.append("- **%s** (%s): %s%s" % (m.get("kind", "mismatch"), m.get("severity", "info"), m.get("summary", ""),
                                            " [%s]" % refs if refs else ""))
    return out + ["", "Checked: %s; document consistency check %s." % (CHECKED, state), ""]


_ANSWER_TURNS = 20
_ROLE_LABEL = {"agent": "agent", "other_party": "other party"}


def _fence(text: str) -> str:
    """A code fence longer than any run of backticks inside the text, so nothing in it can close the block."""
    longest = max([len(m) for m in re.findall(r"`+", text)] or [0])
    return "`" * max(3, longest + 1)


def _calls_section(d: Dict[str, Any]) -> list:
    """## Calls: who was phoned, what was agreed, and the transcript as an inert quoted block (untrusted speech)."""
    from agent import call_results

    calls = d.get("calls") if isinstance(d.get("calls"), list) and d.get("calls") else call_results.call_entries(d.get("actions"))
    if not calls:
        return []
    out = ["## Calls", ""]
    for c in calls:
        result = c.get("result") if isinstance(c.get("result"), dict) else None
        status = ("not dialled (dry run)" if c.get("dry_run") else {"started": "placed", "failed": "could not be placed",
                  "not_placed": "held, not placed"}.get(c.get("call_status"), c.get("call_status") or "unknown"))
        out += ["### Call to the %s (%s) `%s`" % (c.get("party"), c.get("purpose"), c.get("id")), "",
                "- Objective: %s" % (c.get("objective") or "not recorded"), "- Status: %s" % status]
        if c.get("placed_at") and not c.get("dry_run"):
            out.append("- Placed at: %s" % c["placed_at"])
        if not result:
            out += ["- Result: %s" % ("nothing to collect" if c.get("dry_run") else "waiting for the call result"), ""]
            continue
        dec = result.get("decisions") if isinstance(result.get("decisions"), dict) else {}
        agreed = [("Visit date", dec.get("confirmed_date")), ("Date (exact)", dec.get("confirmed_date_iso")),
                  ("Amount quoted (GBP)", dec.get("quoted_amount_gbp")), ("Call back on", dec.get("callback_number"))]
        out.append("- Outcome: %s" % (result.get("outcome") or "not recorded"))
        out += ["- %s: %s" % (k, v) for k, v in agreed if v not in (None, "")]
        if dec.get("notes"):
            out.append("- Notes: %s" % dec["notes"])
        if result.get("duration_s") is not None:
            out.append("- Duration: %s s" % result["duration_s"])
        turns = [t for t in result.get("transcript") or [] if isinstance(t, dict) and t.get("message")]
        if turns:
            shown = turns[:_ANSWER_TURNS]
            lines = ["%s: %s" % (_ROLE_LABEL.get(t.get("role"), "other party"), " ".join(str(t["message"]).split())) for t in shown]
            body = "\n".join(lines)
            fence = _fence(body)
            out += ["", "Transcript (automatic, untrusted):", "", fence + "text", body, fence]
            more = max(int(result.get("transcript_turns") or len(turns)), len(turns)) - len(shown)
            if more > 0:
                out.append("… %d more turn%s in %s" % (more, "" if more == 1 else "s", result.get("record") or "the stored call record"))
        out.append("")
    return out


def answer_md(d: Dict[str, Any]) -> str:
    out = ["# Case %s%s" % (d["case_id"], ": %s" % d["title"] if d.get("title") else ""), ""]
    if str(d.get("answer") or "").strip():
        out += ["## Answer", "", str(d["answer"]).strip(), ""]
    out.append("**Decision:** %s" % _TITLES.get(d["action"], d["action"]))
    if d.get("priority"):
        out.append("**Priority:** %s" % d["priority"])
    out += [""]
    out += _details_section(d.get("details"))
    if d.get("request"):
        out += ["## What the system received", "",
                "Initial request: %s" % d["request"][:600].replace("\n", " "),
                "%d events reviewed, decision as of %s." % (d["events_seen"], d.get("as_of") or d.get("decided_at")), ""]
    out += ["## Decision", "", d["reason"], ""]
    if d.get("actions"):
        out += ["## Actions taken", ""] + [_action_line(a) for a in d["actions"]] + [""]
        for a in d["actions"]:
            if a.get("body") and a.get("kind") != "call":
                out += ["### %s `%s`" % ("Message to %s" % a.get("to"), a["id"]), "", a["body"], ""]
    elif d.get("message"):
        out += ["## Message to send", "", d["message"], ""]
    out += _calls_section(d)
    escalations = [a for a in d.get("actions") or [] if a.get("kind") == "escalation"]
    if escalations:
        e = escalations[0]
        out += ["## Handover for the person taking over", "", e.get("summary", ""), ""]
        if e.get("respond_by"):
            out += ["Respond by %s (%s, route %s)." % (e["respond_by"], e.get("priority") or "?", e.get("route") or "?"), ""]
        if e.get("conflicts"):
            lines = []
            for c in e["conflicts"]:
                parts = []
                for v in c.get("values") or []:
                    if isinstance(v, dict):
                        parts.append("%s (%s)" % (v.get("value"), ", ".join(v.get("refs") or []) or "no ref"))
                    else:
                        parts.append(str(v))
                lines.append("%s: %s" % (c.get("field"), " vs ".join(parts)))
            out += ["Conflicts:", _bullets(lines), ""]
        out += ["Known:", _bullets(e.get("known")), "", "Not known:", _bullets(e.get("unknowns")), "",
                "Tried:", _bullets(e.get("tried")), ""]
        if e.get("failed"):
            out += ["Failed:", _bullets(e["failed"]), ""]
        out += ["Options:", _bullets(e.get("options")), ""]
        if e.get("recommended"):
            out += ["Recommended: %s" % e["recommended"], ""]
    elif d["action"] == "ESCALATE":
        out += ["## For the person taking over", "", "Not known:", _bullets(d.get("unknowns")), "",
                "Suggested next steps:", _bullets(d.get("options")), ""]
    if d.get("blocked") or d.get("gate_notes") or d.get("cause"):
        out += ["## What was blocked or failed", ""]
        out += ["- Tool gate refused `%s`: %s" % (b.get("tool"), b.get("why")) for b in d.get("blocked") or []]
        out += ["- Final code check: %s" % n for n in d.get("gate_notes") or []]
        if d.get("cause"):
            out.append("- Run problem: %s" % d["cause"])
        out.append("")
    out += _mismatch_section(d)
    if d.get("unrelated_issues"):
        out += ["## Separate issues to raise as new requests", "", _bullets(d["unrelated_issues"]), ""]
    if d.get("hazard"):
        out += ["**Possible safety hazard mentioned. Treat as urgent.**", ""]
    return "\n".join(out)


_STATE_LABEL = {"committed": "EXECUTED", "held_for_review": "PROPOSED, NOT SENT", "staged": "PROPOSED, NOT SENT"}


def _conflict_lines(conflicts: Any) -> list:
    lines = []
    for c in _l(conflicts):
        if not isinstance(c, dict):
            continue
        parts = ["%s (%s)" % (v.get("value"), ", ".join(v.get("refs") or []) or "no ref") if isinstance(v, dict) else str(v)
                 for v in c.get("values") or []]
        lines.append("%s: %s" % (c.get("field"), " vs ".join(parts)))
    return lines


def reasoning_md(d: Dict[str, Any]) -> str:
    actions = [a for a in _l(d.get("actions")) if isinstance(a, dict)]
    escalation = next((a for a in actions if a.get("kind") == "escalation"), None)
    out = ["# Reasoning for case %s%s" % (d["case_id"], ": %s" % d["title"] if d.get("title") else ""), "",
           "- Decided by: %s" % ("the model, checked by code" if d["source"] == "model" else "automatic fallback"),
           "- Events seen: %s" % d["events_seen"]]
    if d.get("trace"):
        out += ["- Model: %s, %d turn(s), %d tokens" % (d.get("model") or "?", d.get("steps", 0), d.get("tokens", 0)),
                "- Evidence cited: %s" % (", ".join(d.get("evidence_refs") or []) or "none")]
    if d.get("waiting_on"):
        out.append("- Waiting on the %s for %s days" % (d["waiting_on"], d.get("waiting_days")))
    if d.get("confidence") is not None:
        out.append("- Model confidence: %.2f" % d["confidence"])
    if d.get("proposed_action"):
        out.append("- Model proposed %s; code changed it to %s" % (d["proposed_action"], d["action"]))
    if d.get("cause"):
        out.append("- Fallback cause: %s" % d["cause"])

    out += ["", "## 1. Decision and next action", "",
            "- **Final action:** %s (%s)" % (_TITLES.get(d["action"], d["action"]), d["action"]),
            "- **Priority:** %s" % (d.get("priority") or "not set"),
            "- **As of:** %s" % (d.get("as_of") or d.get("decided_at"))]
    if d.get("proposed_action"):
        out.append("- **Model's proposal:** %s, overridden by code for the reasons in section 4" % d["proposed_action"])
    if d.get("request"):
        out.append("- **Request received:** %s" % d["request"][:600].replace("\n", " "))
    if str(d.get("answer") or "").strip():
        out.append("- **Direct answer:** %s" % str(d["answer"]).strip())

    out += ["", "## 2. Why", "", d["reason"], ""]
    known = _l((escalation or {}).get("known"))
    if known:
        out += ["Facts the decision rests on:", "", _bullets(known), ""]
    if d.get("evidence_refs"):
        out += ["Evidence cited by the model: %s" % ", ".join(d["evidence_refs"]), ""]

    out += ["## 3. Missing information and conflicting facts", "", "Not known:", "",
            _bullets(_l(d.get("unknowns")) or _l((escalation or {}).get("unknowns"))), ""]
    conflicts = _conflict_lines((escalation or {}).get("conflicts"))
    if conflicts:
        out += ["Conflicting facts:", "", _bullets(conflicts), ""]
    out += [line.replace("## Inconsistencies and mismatches", "### Inconsistencies and mismatches") for line in _mismatch_section(d)]
    if d.get("consistency"):
        out += ["## Document consistency check", "", consistency.describe(d["consistency"]), ""]
    if d.get("red_flags"):
        out += ["## Red flags", "", redflags.describe(d["red_flags"]), ""]
    out += ["Input warnings:", "", _bullets(d.get("warnings")), ""]

    out += ["## 4. Actions taken, results and failures", "",
            "EXECUTED means the action was committed. PROPOSED, NOT SENT means it was staged and then held "
            "because the final decision changed or a person must approve it first.", ""]
    for a in actions:
        line = _action_line(a)
        label = _STATE_LABEL.get(a.get("state"))
        out.append(line.replace("**%s**" % a.get("state", "").upper(), "**%s**" % label, 1) if label else line)
    if not actions:
        out.append("- No action was staged.")
    out.append("")
    tried = _l((escalation or {}).get("tried"))
    if tried:
        out += ["What was tried before this decision:", "", _bullets(tried), ""]
    out += ["Checks applied by code:", "", _bullets(d.get("gate_notes")), ""]
    failed = ["Tool gate refused `%s`: %s" % (b.get("tool"), b.get("why")) for b in _l(d.get("blocked")) if isinstance(b, dict)]
    failed += [str(f) for f in _l((escalation or {}).get("failed"))]
    if d.get("cause"):
        failed.append("Run problem: %s" % d["cause"])
    out += ["Failures and refused actions:", "", _bullets(failed), ""]

    out += ["## 5. Handover to a person", ""]
    if escalation:
        out += ["- **Route:** %s, priority %s%s" % (escalation.get("route") or "?", escalation.get("priority") or "?",
                                                    ", respond by %s" % escalation["respond_by"] if escalation.get("respond_by") else ""),
                "- **Summary:** %s" % (escalation.get("summary") or ""), "", "Options for the person:", "",
                _bullets(escalation.get("options")), ""]
        if escalation.get("recommended"):
            out += ["%s" % escalation["recommended"], ""]
    elif d["action"] == "ESCALATE":
        out += ["Escalated without a handover ticket. Suggested next steps:", "", _bullets(d.get("options")), ""]
    else:
        out += ["No person is needed for this step; the system handles it autonomously within the code checks above.", ""]
    if d.get("unrelated_issues"):
        out += ["Separate issues to raise as new requests:", "", _bullets(d["unrelated_issues"]), ""]

    out += ["## Uncertainty", "",
            "- Model confidence: %s" % ("%.2f" % d["confidence"] if isinstance(d.get("confidence"), (int, float)) else "not given"),
            "- Open questions: %d" % len(_l(d.get("unknowns"))),
            "- Code overrides: %s" % ("; ".join(d.get("gate_notes") or []) or "none"),
            "- Safety hazard flagged: %s" % ("yes" if d.get("hazard") else "no"), ""]

    out += ["## Logs and traces", "",
            "- Full decision record: `decision.json` in this folder",
            "- Run-level log: `../trace.jsonl` and `../manifest.json`",
            "- Idempotency key: `%s`" % d["idempotency_key"], ""]
    if d.get("trace"):
        out += ["## Tool trace", "", "Every tool call the agent made, in order, with the code's response.", ""]
        for t in d["trace"]:
            if "thought" in t:
                out.append("%d. _Model note:_ %s" % (t["step"], t["thought"].replace("\n", " ")[:2000]))
            else:
                out.append("%d. `%s(%s)` -> `%s`" % (t["step"], t["tool"], json.dumps(t.get("args"), ensure_ascii=False)[:800],
                                                    json.dumps(t.get("result"), ensure_ascii=False)[:400]))
        out.append("")
    return "\n".join(out)


def write_case(out_dir: Path, d: Dict[str, Any]) -> None:
    folder = Path(out_dir) / d["case_id"]
    atomic_write(folder / "ANSWER.md", answer_md(d))
    atomic_write(folder / "REASONING.md", reasoning_md(d))
    # decision.json goes last: its presence marks the case as finished (used by resume)
    atomic_write(folder / "decision.json", json.dumps(d, indent=2, ensure_ascii=False) + "\n")
