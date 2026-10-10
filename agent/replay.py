"""Replay: test the loop on finished cases without an answer key.

For a chosen point in a case's history, the agent gets only the events up to
that point (the clock is set to the moment the next event happened). Its
proposed action is then compared with what the agency actually did next.

The "what happened next" label is a rough rule on the next event, so the result
is an agreement rate to read, not an accuracy score. A different action is not
automatically wrong; disagreements are listed for reading by hand.
"""

from __future__ import annotations

import json
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agent.config import Config
from agent.report import atomic_write
from agent.runner import list_cases, run_isolated
from agent.timeline import Event, load_case

_QUOTE = re.compile(r"\b(quote|quotation|estimate|invoice|approv\w*)\b", re.I)
_BOOKING = re.compile(r"\b(appointment|scheduled|reminder|booked|booking|visit)\b", re.I)
_CLOSE = re.compile(r"\b(closed|case closed|request closed|all done|completed)\b", re.I)
_WAIT = re.compile(r"waiting for|on hold|put on hold", re.I)
_CHASE = re.compile(r"\b(follow(?:ing)? up|chas\w*|remind\w*|still waiting|any update|(?:not|haven't) heard)\b", re.I)
_INTERNAL = ("agency", "northbridge", "system")


def _is_internal(sender: str) -> bool:
    low = sender.lower()
    return any(t in low for t in _INTERNAL)


def label_next(e: Event) -> str:
    """What the agency did at this event, in the agent's own action names."""
    if _is_internal(e.sender):
        to = e.recipient.lower()
        if e.channel in ("Email", "SMS", "Call"):
            asks = "?" in e.body and not _CHASE.search(e.body)
            if "landlord" in to:
                if _QUOTE.search(e.body):
                    return "ROUTE_FOR_APPROVAL"
                return "ASK_LANDLORD" if asks else "CHASE_LANDLORD"
            if any(t in to for t in ("contractor", "provider", "supplier")):
                return "ASK_PROVIDER" if asks else "CHASE_PROVIDER"
            if "tenant" in to:
                return "SEND_REMINDER" if _BOOKING.search(e.body) else "ASK_TENANT"
        if e.channel in ("Hold", "Update") and _WAIT.search(e.body):
            return "WAIT"
        if e.channel == "Update" and _CLOSE.search(e.body):
            return "CLOSE"
        return "OTHER"
    return "WAIT"  # the other side moved first; the agency had nothing to do before that


def decision_points(n_events: int, points: int) -> List[int]:
    """Cut sizes k (events visible) with a next event to compare to, evenly spaced, k >= 2."""
    candidates = list(range(2, n_events))
    if len(candidates) <= points:
        return candidates
    step = (len(candidates) - 1) / float(max(1, points - 1)) if points > 1 else 0
    return sorted({candidates[int(round(i * step))] for i in range(points)})


def _compare(proposed: str, real: str) -> str:
    if real == "OTHER":
        return "unscored"
    if proposed == real:
        return "agree"
    if proposed == "ESCALATE":
        return "escalated"
    return "differ"


def replay(
    input_dir: Path,
    out_dir: Path,
    cfg: Config,
    backend: str = "fake",
    points: int = 3,
    max_calls: Optional[int] = None,
) -> Dict[str, Any]:
    input_dir, out_dir = Path(input_dir), Path(out_dir)
    tasks: List[Tuple[Path, int, Event, Event]] = []
    for path in list_cases(input_dir):
        try:
            full = load_case(path, cfg)
        except Exception:
            continue
        for k in decision_points(len(full.events), points):
            nxt = full.events[k]
            now_ev = full.events[k - 1]
            if nxt.ts is None or now_ev.ts is None:
                continue
            tasks.append((path, k, nxt, now_ev))
    if max_calls is not None:
        tasks = tasks[:max_calls]

    started = time.monotonic()

    def one(task: Tuple[Path, int, Event, Event]) -> Dict[str, Any]:
        path, k, nxt, _ = task
        kind, payload = run_isolated(path, cfg, backend, nxt.ts.isoformat(), cfg.case_timeout_s, cut=k)
        real = label_next(nxt)
        if kind == "ok":
            proposed, notes, reason = payload["action"], payload.get("gate_notes", []), payload["reason"]
            model_action = payload.get("proposed_action") or payload["action"]
        else:
            proposed, notes, reason, model_action = "FALLBACK", [], "%s: %s" % (kind, payload), "FALLBACK"
        return {
            "case_id": path.name,
            "events_visible": k,
            "now": nxt.ts.isoformat(),
            "proposed": proposed,
            "model_proposed": model_action,
            "real_next": real,
            "real_next_text": nxt.body[:160].replace("\n", " "),
            "result": "fallback" if kind != "ok" else _compare(proposed, real),
            "gate_notes": notes,
            "reason": reason[:300],
        }

    with ThreadPoolExecutor(max_workers=max(1, cfg.concurrency)) as pool:
        rows = list(pool.map(one, tasks))

    out_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(out_dir / "rows.jsonl", "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    results = Counter(r["result"] for r in rows)
    scored = sum(v for k, v in results.items() if k != "unscored")
    summary = {
        "points": len(rows),
        "results": dict(results),
        "agreement_rate": round(results["agree"] / scored, 3) if scored else None,
        "agree_or_escalated_rate": round((results["agree"] + results["escalated"]) / scored, 3) if scored else None,
        "by_real_next": {k: dict(Counter(r["result"] for r in rows if r["real_next"] == k))
                         for k in sorted({r["real_next"] for r in rows})},
        "seconds": round(time.monotonic() - started, 2),
        "backend": backend,
    }
    atomic_write(out_dir / "summary.json", json.dumps(summary, indent=2) + "\n")
    atomic_write(out_dir / "report.md", _report(summary, rows))
    return summary


def _report(summary: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    out = ["# Replay report", "",
           "Backend: `%s`. Decision points: %d." % (summary["backend"], summary["points"]), "",
           "| Result | Count |", "|---|---|"]
    out += ["| %s | %d |" % (k, v) for k, v in sorted(summary["results"].items())]
    out += ["", "Agreement rate (agree / scored): %s" % summary["agreement_rate"],
            "Agree or escalated: %s" % summary["agree_or_escalated_rate"], "",
            "`escalated` means the agent handed the case to a person where the agency carried on. "
            "`unscored` means the next event had no clear action label. "
            "The label comes from a rule on the next event, so read the disagreements before changing anything.", "",
            "## Disagreements to read", ""]
    diffs = [r for r in rows if r["result"] in ("differ", "fallback")]
    if not diffs:
        out.append("None.")
    for r in diffs:
        out += ["- **%s** after %d events: proposed `%s`, agency did `%s` (\"%s\"). Gates: %s. Reason: %s"
                % (r["case_id"], r["events_visible"], r["proposed"], r["real_next"], r["real_next_text"],
                   "; ".join(r["gate_notes"]) or "none", r["reason"])]
    return "\n".join(out) + "\n"
