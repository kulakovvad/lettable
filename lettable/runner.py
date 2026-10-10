"""Run every case on its own so one failure never stops the batch.

Each case runs in a separate child process with a hard time limit. A crash, a
hang, a model error or a malformed proposal all end in the same fallback
escalation, so the number of outputs always equals the number of inputs.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from lettable.config import Config
from lettable.decide import decide
from lettable.fallback import fallback_decision
from lettable.llm import make_backend
from lettable.report import atomic_write, write_case
from lettable.schema import ACTIONS
from lettable.timeline import load_case


def parse_now(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _child(conn, path: str, cfg: Dict[str, Any], backend: str, now_iso: str) -> None:
    try:
        config = Config.from_dict(cfg)
        case = load_case(Path(path), config)
        result = decide(case, make_backend(backend, config), config, parse_now(now_iso))
        conn.send(("ok", result.to_dict()))
    except BaseException as exc:  # a child must always report, whatever went wrong
        try:
            conn.send(("error", "%s: %s" % (type(exc).__name__, exc)))
        except Exception:
            pass
    finally:
        conn.close()


def run_isolated(
    path: Path, cfg: Config, backend: str, now_iso: str, timeout: float
) -> Tuple[str, Any]:
    """Return ("ok", decision_dict) or (cause, detail)."""
    ctx = mp.get_context("spawn")
    parent, child = ctx.Pipe(duplex=False)
    proc = ctx.Process(target=_child, args=(child, str(path), cfg.to_dict(), backend, now_iso), daemon=True)
    proc.start()
    child.close()
    try:
        if parent.poll(timeout):
            try:
                kind, payload = parent.recv()
            except EOFError:
                proc.join(1)
                return "crash", "worker exited with code %s" % proc.exitcode
            if kind == "ok" and isinstance(payload, dict) and payload.get("action") in ACTIONS:
                return "ok", payload
            return "error", str(payload)[:300]
        return "timeout", "no result within %.0f seconds" % timeout
    finally:
        if proc.is_alive():
            proc.terminate()
            proc.join(2)
            if proc.is_alive():
                proc.kill()
                proc.join(2)
        parent.close()


def list_cases(input_dir: Path) -> List[Path]:
    return sorted(p for p in Path(input_dir).iterdir() if p.is_dir() and not p.name.startswith("."))


def _finished(out_dir: Path, case_id: str) -> bool:
    f = out_dir / case_id / "decision.json"
    try:
        return json.loads(f.read_text(encoding="utf-8")).get("source") == "model"
    except Exception:
        return False


def run_all(
    input_dir: Path,
    out_dir: Path,
    cfg: Config,
    backend: str = "fake",
    now_iso: Optional[str] = None,
    resume: bool = False,
) -> Dict[str, Any]:
    input_dir, out_dir = Path(input_dir), Path(out_dir)
    cases = list_cases(input_dir)
    now_iso = now_iso or datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    lock = threading.Lock()
    trace_path = out_dir / "trace.jsonl"
    out_dir.mkdir(parents=True, exist_ok=True)
    results: List[Dict[str, Any]] = []

    def trace(row: Dict[str, Any]) -> None:
        with lock:
            with open(trace_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    def one(path: Path) -> Dict[str, Any]:
        case_id = path.name
        t0 = time.monotonic()
        if resume and _finished(out_dir, case_id):
            return {"case_id": case_id, "skipped": True}
        remaining = None
        if cfg.run_deadline_s is not None:
            remaining = cfg.run_deadline_s - (t0 - started)
        if remaining is not None and remaining <= 0:
            kind, payload = "deadline", "run deadline reached before this case started"
        else:
            limit = cfg.case_timeout_s if remaining is None else min(cfg.case_timeout_s, remaining)
            try:
                kind, payload = run_isolated(path, cfg, backend, now_iso, limit)
            except Exception as exc:  # could not even start a worker
                kind, payload = "runner", "%s: %s" % (type(exc).__name__, exc)
        if kind == "ok":
            decision = payload
        else:
            try:
                case = load_case(path, cfg)
            except Exception:
                case = None
            decision = fallback_decision(case_id, kind, str(payload), parse_now(now_iso), case, cfg).to_dict()
        try:
            write_case(out_dir, decision)
        except Exception as exc:
            decision["write_error"] = str(exc)
        trace({
            "case_id": case_id,
            "seconds": round(time.monotonic() - t0, 2),
            "source": decision["source"],
            "action": decision["action"],
            "cause": decision.get("cause"),
            "gate_notes": decision.get("gate_notes"),
            "write_error": decision.get("write_error"),
        })
        return decision

    with ThreadPoolExecutor(max_workers=max(1, cfg.concurrency)) as pool:
        for r in pool.map(one, cases):
            results.append(r)

    done = [r for r in results if not r.get("skipped")]
    summary = {
        "total": len(cases),
        "written": len(done),
        "skipped": len(results) - len(done),
        "by_action": dict(Counter(r["action"] for r in done)),
        "fallbacks": dict(Counter(r["cause"] for r in done if r["source"] == "fallback")),
        "write_errors": [r["case_id"] for r in done if r.get("write_error")],
        "seconds": round(time.monotonic() - started, 2),
    }
    summary["reconciled"] = summary["written"] + summary["skipped"] == summary["total"] and not summary["write_errors"]
    atomic_write(out_dir / "summary.json", json.dumps(summary, indent=2) + "\n")
    return summary
