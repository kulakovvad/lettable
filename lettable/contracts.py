from dataclasses import dataclass
from typing import Literal
from pydantic import BaseModel, Field


class Triage(BaseModel):
    """Evidence-based case triage, independent of completion status."""
    priority: Literal["P0", "P1", "P2", "P3"]
    urgency: Literal["immediate", "urgent", "time_sensitive", "routine"]
    reason: str = Field(min_length=1)
    next_action: str = Field(min_length=1)


class Reply(BaseModel):
    """The agent's disposition; completion claims still need domain verification."""
    status: Literal["completed", "needs_input", "escalated"]
    message: str = Field(min_length=1)
    triage: Triage


@dataclass(frozen=True)
class Limits:
    max_turns: int = 8
    timeout_seconds: float = 45
    max_tokens: int = 16000
    max_tool_calls: int = 12
    max_identical_calls: int = 2
    max_input_chars: int = 12000
    approval_ttl_seconds: float = 900

    def __post_init__(self):
        if any(value <= 0 for value in self.__dict__.values()):
            raise ValueError("All limits must be positive")


class Outcome(BaseModel):
    request_id: str
    status: Literal["completed", "needs_input", "escalated", "awaiting_approval", "failed", "cancelled"]
    message: str
    triage: Triage | None = None
    code: str | None = None
    approvals: list[dict[str, str]] = Field(default_factory=list)
