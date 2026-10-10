"""Write one case's results. Every file is written atomically (temp file, then rename)."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict

_TITLES = {
    "WAIT": "Wait, nothing to do yet",
    "CHASE_LANDLORD": "Chase the landlord",
    "CHASE_PROVIDER": "Chase the provider",
    "ASK_TENANT": "Ask the tenant for more information",
    "ROUTE_FOR_APPROVAL": "Send for landlord approval",
    "SEND_REMINDER": "Send an appointment reminder",
    "CLOSE": "Close the case",
    "ESCALATE": "Escalate to a person",
}


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=path.suffix)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _bullets(items: Any) -> str:
    return "\n".join("- %s" % i for i in items) if items else "- none"


def answer_md(d: Dict[str, Any]) -> str:
    out = ["# Case %s" % d["case_id"], "", "**Decision:** %s" % _TITLES.get(d["action"], d["action"]), ""]
    out += [d["reason"], ""]
    if d.get("message"):
        out += ["## Message to send", "", d["message"], ""]
    if d["action"] == "ESCALATE":
        out += ["## For the person taking over", "", "Not known:", _bullets(d.get("unknowns")), "",
                "Suggested next steps:", _bullets(d.get("options")), ""]
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
    return "\n".join(out)


def write_case(out_dir: Path, d: Dict[str, Any]) -> None:
    folder = Path(out_dir) / d["case_id"]
    atomic_write(folder / "ANSWER.md", answer_md(d))
    atomic_write(folder / "REASONING.md", reasoning_md(d))
    # decision.json goes last: its presence marks the case as finished (used by resume)
    atomic_write(folder / "decision.json", json.dumps(d, indent=2, ensure_ascii=False) + "\n")
