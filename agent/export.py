"""Copy a run's results into the layout the submission needs.

    ANSWERS/<n>/ANSWER.md, REASONING.md, decision.json     one folder per case
    ANSWERS/index.json                                      n -> case id
    ANSWERS/_run/summary.json, trace.jsonl, export.json     the run's logs and where it came from

Files are copied byte for byte: the results must come from the system and are
never edited or regenerated here. Every check runs before the first write, so a
refused export leaves nothing behind.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agent.files import atomic_write_bytes

CASE_FILES = ("ANSWER.md", "REASONING.md", "decision.json")
RUN_FILES = ("summary.json", "trace.jsonl")


class ExportError(Exception):
    """The export was refused; nothing was written."""


def case_number(case_id: str) -> Optional[int]:
    return int(case_id) if case_id.isascii() and case_id.isdecimal() else None


def _number_cases(case_ids: List[str]) -> Dict[int, str]:
    """Numeric folder names keep their number (001 -> 1); the others follow in sorted order."""
    numbered: Dict[int, str] = {}
    for cid in case_ids:
        n = case_number(cid)
        if n is None:
            continue
        if n in numbered:
            raise ExportError("cases %r and %r would both be ANSWERS/%d" % (numbered[n], cid, n))
        numbered[n] = cid
    nxt = max(numbered) + 1 if numbered else 1
    for cid in case_ids:
        if case_number(cid) is None:
            numbered[nxt] = cid
            nxt += 1
    return numbered


def _from_this_run(dest: Path, out_dir: Path) -> bool:
    marker = dest / "_run" / "export.json"
    try:
        return json.loads(marker.read_text(encoding="utf-8")).get("out_dir") == str(out_dir.resolve())
    except (OSError, ValueError):
        return False


def _plain_file(path: Path) -> bool:
    return path.is_file() and not path.is_symlink()


def _old_index(dest: Path) -> Dict[str, str]:
    try:
        data = json.loads((dest / "index.json").read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def export(out_dir: Path, dest: Path, force: bool = False, skip_incomplete: bool = False) -> Dict[str, Any]:
    out_dir, dest = Path(out_dir), Path(dest)
    if not out_dir.is_dir():
        raise ExportError("output directory not found: %s" % out_dir)
    if dest.exists() and not dest.is_dir():
        raise ExportError("%s exists and is not a folder" % dest)

    folders = sorted(p for p in out_dir.iterdir() if p.is_dir() and not p.name.startswith("."))
    started = [p for p in folders if _plain_file(p / "decision.json")]
    skipped = [p.name for p in folders if p not in started]
    if not started:
        raise ExportError("no case with a decision.json in %s; nothing to export" % out_dir)

    incomplete = {p.name: [f for f in CASE_FILES if not _plain_file(p / f)] for p in started}
    incomplete = {k: v for k, v in incomplete.items() if v}
    if incomplete and not skip_incomplete:
        raise ExportError("finished cases are missing files: %s. Fix them, or export the rest with --skip-incomplete"
                          % "; ".join("%s lacks %s" % (k, ", ".join(v)) for k, v in sorted(incomplete.items())))
    finished = [p for p in started if p.name not in incomplete]
    if not finished:
        raise ExportError("every finished case is incomplete; nothing to export")

    numbered = _number_cases([p.name for p in finished])
    clashes = sorted(n for n in numbered if (dest / str(n)).exists())
    if clashes and not force and not _from_this_run(dest, out_dir):
        raise ExportError("%s already has folder(s) %s from somewhere else; use --force to overwrite them"
                          % (dest, ", ".join(str(n) for n in clashes)))

    # All checks passed: write. First drop folders this exporter wrote earlier that this run no longer has,
    # so ANSWERS/ never mixes two runs.
    for old in _old_index(dest):
        if old.isascii() and old.isdecimal() and int(old) not in numbered and (dest / old).is_dir():
            shutil.rmtree(dest / old)
    for n, cid in sorted(numbered.items()):
        for name in CASE_FILES:
            atomic_write_bytes(dest / str(n) / name, (out_dir / cid / name).read_bytes())
    run_files = [name for name in RUN_FILES if (out_dir / name).is_file()]
    for name in run_files:
        atomic_write_bytes(dest / "_run" / name, (out_dir / name).read_bytes())
    index = {str(n): cid for n, cid in sorted(numbered.items())}
    atomic_write_bytes(dest / "index.json", (json.dumps(index, indent=2) + "\n").encode("utf-8"))
    atomic_write_bytes(dest / "_run" / "export.json", (json.dumps(
        {"out_dir": str(out_dir.resolve()), "cases": len(numbered), "run_files": run_files}, indent=2) + "\n").encode("utf-8"))

    stale = sorted(p.name for p in dest.iterdir() if p.is_dir() and p.name.isdecimal() and int(p.name) not in numbered)
    return {"to": str(dest), "case_folders": len(folders), "exported": len(numbered),
            "skipped_without_decision": skipped, "skipped_incomplete": sorted(incomplete),
            "stale_folders_not_from_this_export": stale, "run_files": run_files, "index": index}
