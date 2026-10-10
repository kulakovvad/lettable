"""python3 -m agent doctor: preflight checks before a paid run. Never prints a secret value.

Without --live nothing leaves the machine. With --live one tiny model call checks that the key and the
model name work, which is the failure that would otherwise turn every case into a fallback.
"""

from __future__ import annotations

import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Mapping, Optional

from agent.config import Config

KEYS = {"claude": ("ANTHROPIC_API_KEY",), "anthropic": ("ANTHROPIC_API_KEY",), "anthropic-single": ("ANTHROPIC_API_KEY",),
        "openai": ("OPENAI_API_KEY",), "auto": ("ANTHROPIC_API_KEY", "OPENAI_API_KEY")}


@dataclass(frozen=True)
class Check:
    status: str  # ok | warn | fail
    name: str
    detail: str


def _model_name(backend: str, cfg: Config, env: Mapping[str, str]) -> str:
    if backend == "openai" or (backend == "auto" and not env.get("ANTHROPIC_API_KEY")):
        return env.get("OPENAI_MODEL") or cfg.openai_model
    return env.get("ANTHROPIC_MODEL") or cfg.model


def check_keys(backend: str, cfg: Config, env: Mapping[str, str]) -> List[Check]:
    out: List[Check] = []
    needed = KEYS.get(backend)
    if needed is None:
        out.append(Check("ok", "model key", "backend %r needs no API key" % backend))
    elif any(env.get(k) for k in needed):
        present = [k for k in needed if env.get(k)]
        out.append(Check("ok", "model key", "%s is set; model %s" % (" and ".join(present), _model_name(backend, cfg, env))))
    else:
        out.append(Check("fail", "model key", "%s is not set (backend %s)" % (" or ".join(needed), backend)))
    if cfg.consistency_check:
        out.append(Check("ok", "consistency check", "TYPESAFE_API_KEY is set") if env.get("TYPESAFE_API_KEY") else
                   Check("warn", "consistency check", "on in config but TYPESAFE_API_KEY is not set; each case records it as unavailable"))
    if env.get("ELEVENLABS_API_KEY"):
        out.append(Check("ok", "speech-to-text", "ELEVENLABS_API_KEY is set; audio files can be transcribed"))
    else:
        out.append(Check("warn", "speech-to-text", "ELEVENLABS_API_KEY is not set; audio files will be listed as unavailable"))
    return out


def check_pypdf() -> Check:
    try:
        import pypdf
    except Exception as exc:
        return Check("fail", "pypdf", "not importable (%s); PDF attachments would be unreadable. pip install pypdf" % type(exc).__name__)
    return Check("ok", "pypdf", "version %s" % getattr(pypdf, "__version__", "?"))


def check_writable(out_dir: Path) -> Check:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=str(out_dir), prefix=".doctor-", delete=True) as fh:
            fh.write(b"ok")
    except Exception as exc:
        return Check("fail", "output dir", "%s is not writable: %s" % (out_dir, exc))
    return Check("ok", "output dir", "%s is writable" % out_dir)


def check_python() -> Check:
    v = sys.version_info
    status = "ok" if v >= (3, 9) else "fail"
    return Check(status, "python", "%d.%d.%d" % (v.major, v.minor, v.micro))


def check_cases(challenge_dir: Path, track: Optional[str]) -> Check:
    from agent.reality import discover, has_audio

    try:
        cases, info = discover(challenge_dir, track)
    except Exception as exc:
        return Check("fail", "challenge folder", str(exc))
    if not cases:
        return Check("fail", "challenge folder", "no case folders found under %s" % challenge_dir)
    images = sum(1 for c in cases for p in c.rglob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp"))
    return Check("ok", "challenge folder", "%d case(s), track %s, audio: %s, images: %d" % (
        len(cases), info["track"] or "not split", "yes" if has_audio(cases) else "no", images))


def live_call(backend: str, cfg: Config) -> Check:
    """One minimal request with max_tokens 1: proves the key, the model name and the network."""
    from agent import chat

    try:
        client = chat.make_chat("anthropic" if backend == "anthropic-single" else backend, cfg)
        if isinstance(client, chat.AnthropicChat):
            chat._post(client.url, {"x-api-key": client.key, "anthropic-version": "2023-06-01"},
                       {"model": client.model, "max_tokens": 1, "messages": [{"role": "user", "content": "Say OK."}]}, cfg)
        else:
            chat._post(client.url, {"authorization": "Bearer %s" % client.key},
                       {"model": client.model, "max_completion_tokens": 16, "messages": [{"role": "user", "content": "Say OK."}]}, cfg)
    except Exception as exc:
        return Check("fail", "live model call", "%s: %s" % (type(exc).__name__, str(exc)[:300]))
    return Check("ok", "live model call", "model %s answered" % client.model)


def run_checks(backend: str, cfg: Config, out_dir: Path, env: Optional[Mapping[str, str]] = None, live: bool = False,
               challenge_dir: Optional[Path] = None, track: Optional[str] = None,
               live_fn: Callable[[str, Config], Check] = live_call) -> List[Check]:
    env = os.environ if env is None else env
    checks = [check_python()] + check_keys(backend, cfg, env) + [check_pypdf(), check_writable(Path(out_dir))]
    if challenge_dir is not None:
        checks.append(check_cases(Path(challenge_dir), track))
    if live:
        if backend == "fake":
            checks.append(Check("ok", "live model call", "skipped for the fake backend"))
        elif any(c.status == "fail" and c.name == "model key" for c in checks):
            checks.append(Check("fail", "live model call", "skipped: no API key"))
        else:
            checks.append(live_fn(backend, cfg))
    else:
        checks.append(Check("warn", "live model call", "not run; add --live to check the model name with one tiny call"))
    return checks


def report(checks: List[Check]) -> str:
    return "\n".join("%-4s %-18s %s" % (c.status.upper(), c.name, c.detail) for c in checks)
