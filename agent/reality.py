"""python3 -m agent reality CHALLENGE_DIR --out ANSWERS: find every case, decide it, export ANSWERS/<n>/.

The challenge layout is not known in advance, so cases are found at any depth: a folder holding index.md
or history.md, or a folder of text files with no case folders below it. When the drop has one folder per
track, only our track runs unless --track says otherwise. Each case is copied into a staging folder named
by its number and the normal runner does the work, so every case still gets its own process, time limit
and fallback. Fallbacks get further passes while the deadline allows.
"""

from __future__ import annotations

import dataclasses
import json
import os
import re
import shutil
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agent.config import Config
from agent.files import atomic_write
from agent.runner import run_all
from agent.stt import AUDIO_SUFFIXES

TRACKS = ("Banking & Financial Services", "Delivery & Logistics", "Insurance Claims Processing", "Property Management")
DEFAULT_TRACK = "Property Management"
CASE_FILES = ("index.md", "history.md")
TEXT_SUFFIXES = (".md", ".txt", ".eml")
# Folders inside a case that hold its documents, never cases of their own.
DOC_DIRS = {"attachments", "attachment", "files", "documents", "docs", "images", "media", "audio"}
SKIP_DIRS = {"ANSWERS", "node_modules", "__pycache__"}
_NUMBER_RE = re.compile(r"(?:case[\s_-]*)?0*(\d+)", re.I)


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower().replace("&", "and"))


def _track_of(name: str) -> Optional[str]:
    for t in TRACKS:
        if _norm(name) == _norm(t):
            return t
    return None


def _subdirs(folder: Path) -> List[Path]:
    try:
        return sorted(p for p in folder.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))
                      and p.name not in SKIP_DIRS)
    except OSError:
        return []


def _has_case_file(folder: Path) -> bool:
    try:
        return any(p.is_file() and p.name.lower() in CASE_FILES for p in folder.iterdir())
    except OSError:
        return False


def _has_text(folder: Path) -> bool:
    try:
        return any(p.is_file() and p.suffix.lower() in TEXT_SUFFIXES and p.name.lower() != "readme.md"
                   for p in folder.iterdir())
    except OSError:
        return False


def find_cases(folder: Path, skip: Optional[Path] = None) -> List[Path]:
    folder = Path(folder)
    if skip is not None and folder.resolve() == skip:
        return []
    if _has_case_file(folder):
        return [folder]
    found: List[Path] = []
    for sub in _subdirs(folder):
        if sub.name.lower() not in DOC_DIRS:
            found += find_cases(sub, skip)
    if not found and _has_text(folder):
        return [folder]
    return found


def discover(root: Path, track: Optional[str] = None, skip: Optional[Path] = None) -> Tuple[List[Path], Dict[str, Any]]:
    """Case folders under root, filtered to one track when the drop is split by track.

    track: None for the default track, "all", or a track name in any spelling. Returns (cases, info).
    """
    root = Path(root)
    cases = find_cases(root, skip.resolve() if skip else None)
    by_track: Dict[str, List[Path]] = {}
    for c in cases:
        rel = c.relative_to(root).parts
        t = next((_track_of(p) for p in rel[:-1] if _track_of(p)), None)
        by_track.setdefault(t or "", []).append(c)
    named = sorted(t for t in by_track if t)
    info: Dict[str, Any] = {"tracks_found": named, "track": None}
    if not named or (track or "").lower() == "all":
        info["track"] = "all" if named else None
        return cases, info
    wanted = _track_of(track) if track else DEFAULT_TRACK
    if track and wanted is None:
        wanted = next((t for t in named if _norm(track) in _norm(t)), None)
    if wanted not in by_track:
        raise ValueError("track %r not found; tracks in the folder: %s" % (track or DEFAULT_TRACK, ", ".join(named)))
    info["track"] = wanted
    return by_track[wanted], info


def number_cases(cases: List[Path], root: Path) -> List[Tuple[str, Path]]:
    """Numeric folder names keep their number, unpadded (001 -> 1); the rest, and clashes, get the next free one."""
    used, out, pending = set(), [], []
    for c in sorted(cases, key=lambda p: str(p.relative_to(root))):
        m = _NUMBER_RE.fullmatch(c.name.strip())
        n = str(int(m.group(1))) if m else None
        if n is not None and n not in used:
            used.add(n)
            out.append((n, c))
        else:
            pending.append(c)
    k = 1
    for c in pending:
        while str(k) in used:
            k += 1
        used.add(str(k))
        out.append((str(k), c))
    return sorted(out, key=lambda x: int(x[0]))


def has_audio(cases: List[Path]) -> bool:
    return any(p.suffix.lower() in AUDIO_SUFFIXES for c in cases for p in c.rglob("*") if p.is_file())


def choose_stt(cfg: Config, cases: List[Path], explicit: Optional[str]) -> Tuple[str, str]:
    """(stt_backend, note). Transcription is paid, so it only turns itself on when there is audio and a key."""
    if explicit:
        return explicit, "set on the command line"
    configured = cfg.stt_backend if cfg.stt_backend != "off" else (os.environ.get("LETTABLE_STT") or "off")
    if configured != "off":
        return configured, "set by config or LETTABLE_STT"
    if not has_audio(cases):
        return "off", "no audio files in the cases"
    if os.environ.get("ELEVENLABS_API_KEY"):
        return "elevenlabs", "audio files found and ELEVENLABS_API_KEY is set"
    return "off", "audio files found but ELEVENLABS_API_KEY is not set, so audio is listed as unavailable"


def _stage(numbered: List[Tuple[str, Path]], staging: Path) -> None:
    for n, src in numbered:
        shutil.copytree(src, staging / n, symlinks=True)


def _read_decision(out_dir: Path, n: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads((out_dir / n / "decision.json").read_text(encoding="utf-8"))
    except Exception:
        return None


def _cell(text: Any, limit: int = 80) -> str:
    s = " ".join(str(text or "").split()).replace("|", "/")
    return s if len(s) <= limit else s[:limit - 3] + "..."


def index_md(rows: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
    out = ["# Reality Test answers", "",
           "Generated by `python3 -m agent reality`. Do not edit by hand; re-run instead.", "",
           "- Cases: %d (%d decided by the model, %d automatic fallbacks)" % (
               summary["total"], summary["total"] - sum(summary["fallbacks"].values()), sum(summary["fallbacks"].values())),
           "- Track: %s" % (summary.get("track") or "(not split by track)"),
           "- Backend: %s, finished %s" % (summary.get("backend"), summary.get("finished_at")),
           "- Actions: %s" % (", ".join("%s %d" % kv for kv in sorted(summary["by_action"].items())) or "none"), "",
           "| Case | Source folder | Title | Final action | Priority | Escalated | Fallback / cause | Answer |",
           "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        d = r["decision"] or {}
        action = d.get("action") or "(missing)"
        cause = d.get("cause") or ""
        fallback = ("fallback: %s" % cause) if d.get("source") == "fallback" else cause
        out.append("| %s | %s | %s | %s | %s | %s | %s | [ANSWER.md](%s/ANSWER.md) |" % (
            r["n"], _cell(r["source"], 60), _cell(d.get("title") or r.get("title")), action, d.get("priority") or "",
            "yes" if action == "ESCALATE" else "no", _cell(fallback, 40), r["n"]))
    return "\n".join(out) + "\n"


def _title_of(folder: Path) -> str:
    try:
        text = (folder / "index.md").read_text(encoding="utf-8", errors="replace")[:4000]
    except OSError:
        return ""
    m = re.search(r"^# (?:Case [^:\n]*:\s*)?(.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def run_reality(
    challenge_dir: Path,
    out_dir: Path,
    cfg: Config,
    backend: str = "claude",
    track: Optional[str] = None,
    resume: bool = False,
    stt: Optional[str] = None,
    now_iso: Optional[str] = None,
    log=print,
) -> Dict[str, Any]:
    challenge_dir, out_dir = Path(challenge_dir), Path(out_dir)
    started = time.monotonic()
    cases, info = discover(challenge_dir, track, skip=out_dir)
    if not cases:
        raise ValueError("no case folders found under %s" % challenge_dir)
    numbered = number_cases(cases, challenge_dir)
    stt_backend, stt_note = choose_stt(cfg, cases, stt)
    cfg = dataclasses.replace(cfg, stt_backend=stt_backend)
    consistency_note = "on" if cfg.consistency_check else "off in config"
    if cfg.consistency_check and not os.environ.get("TYPESAFE_API_KEY"):
        # Without Jev the check can only report "unavailable", after paying for its extraction call.
        cfg = dataclasses.replace(cfg, consistency_check=False)
        consistency_note = "off: TYPESAFE_API_KEY is not set"
    log("reality: %d case(s) in %s (track: %s); speech-to-text %s (%s); consistency check %s" % (
        len(numbered), challenge_dir, info["track"] or "not split", stt_backend, stt_note, consistency_note))

    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "challenge_dir": str(challenge_dir.resolve()),
        "track": info["track"], "tracks_found": info["tracks_found"],
        "backend": backend, "stt": stt_backend, "stt_note": stt_note, "consistency_check": consistency_note,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "cases": [{"n": n, "source": str(src.relative_to(challenge_dir)) or "."} for n, src in numbered],
    }
    atomic_write(out_dir / "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    passes: List[Dict[str, Any]] = []
    staging = Path(tempfile.mkdtemp(prefix="reality-"))
    try:
        _stage(numbered, staging)
        for attempt in range(1 + max(0, cfg.reality_resume_passes)):
            remaining = None if cfg.run_deadline_s is None else cfg.run_deadline_s - (time.monotonic() - started)
            if attempt and remaining is not None and remaining < cfg.reality_min_resume_s:
                log("reality: %.0f s left, too little for another pass over fallbacks" % remaining)
                break
            pcfg = dataclasses.replace(cfg, run_deadline_s=remaining)
            s = run_all(staging, out_dir, pcfg, backend, now_iso, resume=resume or attempt > 0)
            passes.append({k: s[k] for k in ("written", "skipped", "by_action", "fallbacks", "seconds")})
            log("reality: pass %d wrote %d, skipped %d, fallbacks %s" % (attempt + 1, s["written"], s["skipped"], s["fallbacks"] or "none"))
            if not s["fallbacks"]:
                break
    finally:
        shutil.rmtree(staging, ignore_errors=True)

    rows = [{"n": n, "source": str(src.relative_to(challenge_dir)) or ".", "title": _title_of(src),
             "decision": _read_decision(out_dir, n)} for n, src in numbered]
    decided = [r["decision"] for r in rows if r["decision"]]
    summary = {
        "total": len(rows),
        "written": len(decided),
        "missing": [r["n"] for r in rows if not r["decision"]],
        "by_action": dict(Counter(d.get("action") for d in decided)),
        "fallbacks": dict(Counter(d.get("cause") for d in decided if d.get("source") == "fallback")),
        "escalated": sum(1 for d in decided if d.get("action") == "ESCALATE"),
        "passes": passes,
        "seconds": round(time.monotonic() - started, 2),
        "track": info["track"], "backend": backend, "stt": stt_backend,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }
    summary["reconciled"] = not summary["missing"]
    atomic_write(out_dir / "summary.json", json.dumps(summary, indent=2) + "\n")
    atomic_write(out_dir / "README.md", index_md(rows, summary))
    return summary
