"""Copy a run's results into the layout the submission needs.

    ANSWERS/<n>/ANSWER.md, REASONING.md, decision.json     one folder per case
    ANSWERS/index.json                                      n -> case id
    ANSWERS/_run/summary.json, trace.jsonl, export.json     the run's logs and where it came from

Files are copied byte for byte: the results must come from the system and are
never edited or regenerated here. Every check runs before the first write, so a
refused export leaves nothing behind.
"""

from __future__ import annotations

import hashlib
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


def _run_id(out_dir: Path) -> str:
    """Identifies a run folder without writing its path (which would put the local checkout path in the submission)."""
    return hashlib.sha256(str(out_dir.resolve()).encode("utf-8")).hexdigest()[:16]


def _owner(dest: Path) -> Optional[str]:
    """The run id that wrote this ANSWERS folder, or None if it has no marker."""
    try:
        return json.loads((dest / "_run" / "export.json").read_text(encoding="utf-8")).get("run_id")
    except (OSError, ValueError, AttributeError):
        return None


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
    run_id = _run_id(out_dir)
    owner = _owner(dest)
    previous = _old_index(dest)
    # Another run's results are never touched without --force, whether or not the folder numbers overlap.
    if not force:
        if owner is not None and owner != run_id:
            raise ExportError("%s holds results from a different run; use --force to replace them" % dest)
        clashes = sorted(n for n in numbered if (dest / str(n)).exists() and owner != run_id)
        if clashes:
            raise ExportError("%s already has folder(s) %s that this export did not write; use --force to overwrite them"
                              % (dest, ", ".join(str(n) for n in clashes)))

    # All checks passed: write the new files first and clean up last, so a failure never leaves ANSWERS/ emptier.
    for n, cid in sorted(numbered.items()):
        for name in CASE_FILES:
            atomic_write_bytes(dest / str(n) / name, (out_dir / cid / name).read_bytes())
    run_files = [name for name in RUN_FILES if (out_dir / name).is_file()]
    for name in run_files:
        atomic_write_bytes(dest / "_run" / name, (out_dir / name).read_bytes())
    index = {str(n): cid for n, cid in sorted(numbered.items())}
    atomic_write_bytes(dest / "index.json", (json.dumps(index, indent=2) + "\n").encode("utf-8"))
    atomic_write_bytes(dest / "_run" / "export.json", (json.dumps(
        {"run_id": run_id, "run_folder": out_dir.name, "cases": len(numbered), "run_files": run_files}, indent=2) + "\n").encode("utf-8"))

    # Clean up what an earlier export of this folder left that this one does not have.
    for name in RUN_FILES:
        if name not in run_files and (dest / "_run" / name).is_file():
            (dest / "_run" / name).unlink()
    if owner == run_id or force:
        for old in previous:
            if old.isascii() and old.isdecimal() and int(old) not in numbered and (dest / old).is_dir():
                shutil.rmtree(dest / old)

    stale = sorted(p.name for p in dest.iterdir() if p.is_dir() and p.name.isdecimal() and int(p.name) not in numbered)
    return {"to": str(dest), "case_folders": len(folders), "exported": len(numbered),
            "skipped_without_decision": skipped, "skipped_incomplete": sorted(incomplete),
            "stale_folders_not_from_this_export": stale, "run_files": run_files, "index": index}
