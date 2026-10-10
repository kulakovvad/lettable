"""All tunable values in one place. Nothing here is hard-coded elsewhere."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class Config:
    # Time budgets (seconds)
    case_timeout_s: float = 240.0  # the tool loop makes up to loop_max_steps model calls
    run_deadline_s: Optional[float] = None
    call_timeout_s: float = 60.0
    max_retries: int = 2
    concurrency: int = 4

    # Decision thresholds. Starting values; tune on the public cases.
    chase_after_days: float = 3.0
    approval_limit_gbp: float = 300.0  # placeholder until the real limit is known
    min_confidence: float = 0.5

    # Model. Claude is the main driver; OpenAI is a fallback (env ANTHROPIC_MODEL / OPENAI_MODEL override).
    model: str = "claude-sonnet-5-5"
    openai_model: str = "gpt-5.4-mini"
    max_prompt_chars: int = 24000
    max_tokens: int = 1200

    # Tool loop budgets
    loop_max_steps: int = 12  # model turns before the loop is forced to finish
    loop_max_tokens_per_turn: int = 2500
    loop_token_budget: int = 150_000  # whole case, across all turns
    run_token_budget: Optional[int] = 3_000_000  # whole run; later cases fall back to escalation once spent
    # When waits are judged. last_event: the case's latest event (synthetic dates do not relate to the clock);
    # now: the wall clock or --now; later: whichever of the two is later. An explicit --now implies "now".
    as_of: str = "last_event"

    # Speech-to-text for audio files in a case ("off" | "fake" | "elevenlabs"). Paid, so off by default.
    stt_backend: str = "off"
    stt_model: str = "scribe_v2"
    stt_cache_dir: str = ".cache/stt"
    stt_timeout_s: float = 120.0
    stt_max_audio_bytes: int = 50_000_000

    # Phone calls ("dry_run" records the call and dials nothing | "elevenlabs" places it)
    call_backend: str = "dry_run"
    call_hours: Tuple[int, int] = (8, 21)  # UK local hours in which a live call may be placed
    call_ring_timeout_s: int = 30  # stop ringing after this long (the provider default is 60)
    collect_calls: bool = True  # at the start of a live run, fetch the results of calls placed earlier
    max_calls_per_case: int = 1
    max_calls_per_run: int = 10

    # Document consistency check (agent/consistency.py): one extraction call, then Jev scores fields whose
    # values differ. Scores are normalised to 0..1. Below jev_min_confidence a mismatch is only flagged.
    consistency_check: bool = False
    jev_model: str = "jev-1.13.0"
    jev_pass: float = 0.85
    jev_escalate: float = 0.4
    jev_min_confidence: float = 0.6

    # Input caps
    max_file_bytes: int = 2_000_000
    pdf_chars: int = 3000

    # Reality Test command (agent/reality.py): extra passes over fallbacks while the deadline allows,
    # and the least time left that is still worth starting one.
    reality_resume_passes: int = 1
    reality_min_resume_s: float = 60.0

    # Phrases that force an escalation. Checked on the most recent events.
    hazard_patterns: Tuple[str, ...] = (
        r"smell(?:s|ing)? (?:of )?gas",
        r"gas leak",
        r"carbon monoxide",
        r"\bco alarm\b",
        r"\bflood(?:ing|ed)?\b",
        r"burst pipe",
        r"exposed wir",
        r"\bsparking\b",
        r"\bon fire\b",
        r"\bfire\b",
        r"ceiling (?:has )?collaps",
        r"no heating.{0,40}(?:baby|elderly|vulnerable)",
        r"\bunsafe\b",
        r"\bthreat",
    )
    hazard_window: int = 5  # how many latest events to scan

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        known = {f.name for f in fields(cls)}
        clean = {k: v for k, v in data.items() if k in known}
        for name in ("hazard_patterns", "call_hours"):
            if name in clean:
                clean[name] = tuple(clean[name])
        return cls(**clean)

    @classmethod
    def load(cls, path: Optional[Path]) -> "Config":
        if path is None:
            return cls()
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
