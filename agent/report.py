"""Write one case's results. Every file is written atomically (temp file, then rename)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from agent import consistency, redflags
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


def answer_md(d: Dict[str, Any]) -> str:
    out = ["# Case %s%s" % (d["case_id"], ": %s" % d["title"] if d.get("title") else ""), ""]
    if str(d.get("answer") or "").strip():
        out += ["## Answer", "", str(d["answer"]).strip(), ""]
    out.append("**Decision:** %s" % _TITLES.get(d["action"], d["action"]))
    if d.get("priority"):
        out.append("**Priority:** %s" % d["priority"])
    out += [""]
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
    if d.get("unrelated_issues"):
        out += ["## Separate issues to raise as new requests", "", _bullets(d["unrelated_issues"]), ""]
    if d.get("hazard"):
        out += ["**Possible safety hazard mentioned. Treat as urgent.**", ""]
    return "\n".join(out)


def reasoning_md(d: Dict[str, Any]) -> str:
    out = ["# Reasoning for case %s" % d["case_id"], "",
           "- Decided by: %s" % ("the model, checked by code" if d["source"] == "model" else "automatic fallback"),
           "- Events seen: %s" % d["events_seen"]]
    if d.get("waiting_on"):
        out.append("- Waiting on the %s for %s days" % (d["waiting_on"], d.get("waiting_days")))
    if d.get("confidence") is not None:
        out.append("- Model confidence: %.2f" % d["confidence"])
    if d.get("proposed_action"):
        out.append("- Model proposed %s; code changed it to %s" % (d["proposed_action"], d["action"]))
    if d.get("cause"):
        out.append("- Fallback cause: %s" % d["cause"])
    out += ["", "## Why", "", d["reason"], "", "## Checks applied by code", "", _bullets(d.get("gate_notes")), "",
            "## Not known", "", _bullets(d.get("unknowns")), "", "## Input warnings", "", _bullets(d.get("warnings")), "",
            "Idempotency key: `%s`" % d["idempotency_key"], ""]
    if d.get("consistency"):
        out[-2:-2] = ["## Document consistency check", "", consistency.describe(d["consistency"]), ""]
    if d.get("red_flags"):
        out[-2:-2] = ["## Red flags", "", redflags.describe(d["red_flags"]), ""]
    if d.get("trace"):
        out[3:3] = ["- Model: %s, %d turn(s), %d tokens" % (d.get("model") or "?", d.get("steps", 0), d.get("tokens", 0)),
                    "- Evidence cited: %s" % (", ".join(d.get("evidence_refs") or []) or "none")]
        out += ["## Tool trace", "", "Every tool call the agent made, in order, with the code's response.", ""]
        for t in d["trace"]:
            if "thought" in t:
                out.append("%d. _Model note:_ %s" % (t["step"], t["thought"].replace("\n", " ")[:600]))
            else:
                out.append("%d. `%s(%s)` -> `%s`" % (t["step"], t["tool"], json.dumps(t.get("args"), ensure_ascii=False)[:500],
                                                    json.dumps(t.get("result"), ensure_ascii=False)[:400]))
        out.append("")
    return "\n".join(out)


def write_case(out_dir: Path, d: Dict[str, Any]) -> None:
    folder = Path(out_dir) / d["case_id"]
    atomic_write(folder / "ANSWER.md", answer_md(d))
    atomic_write(folder / "REASONING.md", reasoning_md(d))
    # decision.json goes last: its presence marks the case as finished (used by resume)
    atomic_write(folder / "decision.json", json.dumps(d, indent=2, ensure_ascii=False) + "\n")
