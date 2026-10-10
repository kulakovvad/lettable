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
    max_retries: int = 4  # 429 / 529 / 5xx and network errors, waiting retry-after when the server sends it
    retry_after_cap_s: float = 30.0
    concurrency: int = 4

    # Decision thresholds. Starting values; tune on the public cases.
    chase_after_days: float = 3.0
    # Who decides to phone is code (agent/channel.py): a call needs this many unanswered emails/texts to the party,
    # the latest at least this many hours old (or a bounce, or a hazard found by code).
    call_after_unanswered: int = 2
    call_after_hours: float = 24.0
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
    # Code-driven briefing call to the agency's own on-call person when a case ends urgently (see agent/oncall.py).
    # Empty = off. The number is never taken from a case or from the model. Env: LETTABLE_ONCALL_NUMBER.
    oncall_number: str = ""
    # E.164 numbers a live call may dial. Empty keeps the old behaviour for ordinary calls; the on-call briefing always
    # needs its number on this list to be dialled live. Env: LETTABLE_CALL_ALLOWLIST (comma separated).
    call_allowlist: Tuple[str, ...] = ()

    # Document consistency check (agent/consistency.py): one extraction call, then Jev scores fields whose
    # values differ. Scores are normalised to 0..1. Below jev_min_confidence a mismatch is only flagged.
    # Name, phone and email mismatches never escalate. A Reality Test config should set this when
    # TYPESAFE_API_KEY is present.
    consistency_check: bool = False
    jev_model: str = "jev-1.13.0"
    jev_pass: float = 0.85
    jev_escalate: float = 0.4
    jev_min_confidence: float = 0.6

    # Input caps
    max_file_bytes: int = 2_000_000
    pdf_chars: int = 3000
    attachment_chars: int = 4000  # preloaded .txt/.csv/.json/.eml/.md text
    image_max_bytes: int = 1_500_000  # PNG/JPG/GIF/WEBP inlined for Claude, each
    max_images: int = 4

    # Reality Test command (agent/reality.py): extra passes over fallbacks while the deadline allows,
    # and the least time left that is still worth starting one.
    reality_resume_passes: int = 1
    reality_min_resume_s: float = 60.0

    # Phrases that force an escalation. Checked on the most recent events; denied mentions ("no smell of
    # gas") and advice or questions in agency messages do not count (agent.evidence.hazard_hits).
    hazard_patterns: Tuple[str, ...] = (
        r"smell(?:s|ing)? (?:of )?gas",
        r"gas (?:leak|escape)",
        r"carbon monoxide",
        r"\bco alarm\b",
        r"\bflood(?:ing|ed)\b(?! with)|\bflood (?:in|through|from|everywhere)\b|water (?:is )?(?:pouring|gushing|streaming)",
        r"burst pipe",
        r"exposed (?:live )?wir",
        r"\belectric(?:al)? shock\b",
        r"\bsmoke (?:is )?(?:pouring|billowing) (?:out of|from) (?:the |a )?(?:socket|plug)\b",
        r"\bgas fumes?\b",
        r"\bwater\b.{0,50}\bceiling\b.{0,40}\belectrics?\b",
        r"\b(?:cannot|can't|can not|unable to) lock the front door\b",
        r"\b(?:mould|mold)\b.{0,80}\b(?:baby|infant)\b.{0,40}\bcough\b"
        r"|\b(?:baby|infant)\b.{0,40}\bcough\b.{0,80}\b(?:mould|mold)\b",
        r"\bsparking\b|\bsparks (?:from|coming)",
        r"\bon fire\b|\bcaught fire\b|\b(?:a|the) fire (?:in|at|broke|started|has)\b|\bfire (?:brigade|service)\b|"
        r"\bburning smell\b|\bsmell of burning\b|\b(?:fire|smoke) alarm (?:is |keeps )?(?:going off|sounding)",
        r"ceiling (?:has )?collaps",
        r"no heating.{0,40}(?:baby|elderly|vulnerable)",
        r"\b(?:unsafe|dangerous) to (?:use|live|enter|stay)\b|\b(?:is|are|was|were) (?:unsafe|dangerous)\b|"
        r"\b(?:deemed|declared|classed|marked|condemned as) (?:unsafe|dangerous)\b|\bimmediately dangerous\b|"
        r"\bunsafe (?:gas|electrics?|electrical|wiring|appliance|boiler|structure)\b",
        r"\bthreat(?:en(?:ed|ing|s)?)? (?:to )?(?:hurt|harm|kill|attack|assault)\b|\bthreats? of violence\b|"
        r"\bthreatening (?:behaviou?r|me|us)\b",
    )
    hazard_window: int = 5  # how many latest events to scan

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        known = {f.name for f in fields(cls)}
        clean = {k: v for k, v in data.items() if k in known}
        for name in ("hazard_patterns", "call_hours", "call_allowlist"):
            if name in clean:
                clean[name] = tuple(clean[name])
        return cls(**clean)

    @classmethod
    def load(cls, path: Optional[Path]) -> "Config":
        if path is None:
            return cls()
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
