"""All tunable values in one place. Nothing here is hard-coded elsewhere."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class Config:
    # Time budgets (seconds)
    case_timeout_s: float = 120.0
    run_deadline_s: Optional[float] = None
    call_timeout_s: float = 60.0
    max_retries: int = 2
    concurrency: int = 4

    # Decision thresholds. Starting values; tune on the public cases.
    chase_after_days: float = 3.0
    approval_limit_gbp: float = 300.0  # placeholder until the real limit is known
    min_confidence: float = 0.5

    # Model
    model: str = "claude-sonnet-5-5"
    max_prompt_chars: int = 24000
    max_tokens: int = 1200

    # Input caps
    max_file_bytes: int = 2_000_000
    pdf_chars: int = 3000

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
        if "hazard_patterns" in clean:
            clean["hazard_patterns"] = tuple(clean["hazard_patterns"])
        return cls(**clean)

    @classmethod
    def load(cls, path: Optional[Path]) -> "Config":
        if path is None:
            return cls()
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
