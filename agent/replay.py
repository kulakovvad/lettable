"""Replay public cases from a point in their history.

For each case, cut the history after event N, drop the summary/outcome from
index.md and keep only attachments already referenced, then let the agent decide.
What the agency actually did next is written to expected.json for comparison.
That reference is one acceptable answer, not the only one.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.timeline import parse_history
from agent.tools import role_of

_EVENT_SPLIT_RE = re.compile(r"(?=^<a id=\"event-\d+\"></a>\s*$)", re.M)
_SECTION_RE = re.compile(r"^## (Overview|Outcome|Summary|Resolution)\b.*?(?=^## |\Z)", re.M | re.S | re.I)
_STATUS_RE = re.compile(r"^- \*\*(Status|Updated|Completed):\*\*.*\n", re.M)


def next_agency_step(events, after: int) -> Optional[Dict[str, Any]]:
    for e in events:
        if e.index <= after:
            continue
        if role_of(e.sender) == "agency" and role_of(e.recipient) in ("tenant", "landlord", "provider"):
            return {"event": e.index, "to": role_of(e.recipient), "text": e.body[:400]}
        if e.channel.lower() == "hold" or "completed" in e.body.lower() or "closed" in e.body.lower():
            return {"event": e.index, "to": "internal", "text": e.body[:400]}
    return None


def decision_points(events, count: int) -> List[int]:
    """Cut right after an inbound message from a party: the agency must respond to something."""
    points = [e.index for e in events[:-1] if role_of(e.sender) in ("tenant", "landlord", "provider")]
    if not points:
        return []
    step = max(1, len(points) // count)
    return points[::step][:count]


def cut_case(src: Path, dst: Path, through: int) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    history = (src / "history.md").read_text(encoding="utf-8")
    parts = _EVENT_SPLIT_RE.split(history)
    kept = [parts[0]] + [p for p in parts[1:] if int(re.search(r"event-(\d+)", p).group(1)) <= through]
    text = "".join(kept)
    index = _STATUS_RE.sub("", _SECTION_RE.sub("", (src / "index.md").read_text(encoding="utf-8")))
    # Attachments that only appear later in the history would reveal the ending (e.g. an invoice).
    index = "\n".join(line for line in index.splitlines()
                      if not (line.startswith("- [") and "attachments/" in line and Path(line.split("](")[-1].rstrip(")")).name not in text))
    (dst / "index.md").write_text(index + "\n", encoding="utf-8")
    (dst / "history.md").write_text(re.sub(r"Total events: \d+", "Total events: %d" % through, text), encoding="utf-8")
    if (src / "attachments").is_dir():
        for f in (src / "attachments").iterdir():
            if f.name in text:
                (dst / "attachments").mkdir(exist_ok=True)
                shutil.copy2(f, dst / "attachments" / f.name)


def build(cases_dir: Path, out_dir: Path, points: int = 2, only: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    rows = []
    for src in sorted(p for p in Path(cases_dir).iterdir() if p.is_dir()):
        if only and src.name not in only:
            continue
        events, _ = parse_history((src / "history.md").read_text(encoding="utf-8"))
        for n in decision_points(events, points):
            cid = "%s-at-%03d" % (src.name, n)
            cut_case(src, Path(out_dir) / cid, n)
            row = {"case_id": cid, "source": src.name, "through_event": n, "next_step": next_agency_step(events, n)}
            (Path(out_dir) / cid / "expected.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
            rows.append(row)
    return rows


def compare(replay_dir: Path, out_dir: Path) -> List[Dict[str, Any]]:
    rows = []
    for exp in sorted(Path(replay_dir).glob("*/expected.json")):
        row = json.loads(exp.read_text(encoding="utf-8"))
        dec = Path(out_dir) / row["case_id"] / "decision.json"
        d = json.loads(dec.read_text(encoding="utf-8")) if dec.is_file() else {}
        nxt = row.get("next_step") or {}
        rows.append({"case": row["case_id"], "agent": d.get("action"), "priority": d.get("priority"),
                     "agency_next_to": nxt.get("to"), "agency_next": (nxt.get("text") or "").replace("\n", " ")[:140]})
    return rows
