"""Phone calls: the interface the rest of the agent uses, and a dialer that dials nothing.

The loop only ever stages a call. After the final decision passes the gates, a
Dialer places it. A call takes minutes, so placing returns at once with a
conversation id; the result is fetched later (`calls collect`).
The live ElevenLabs dialer is in agent/voice_elevenlabs.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, Tuple

from agent.config import Config


@dataclass(frozen=True)
class CallRequest:
    case_id: str
    party: str  # landlord | provider | tenant
    to_number: str  # a number that appears in the case
    objective: str  # what the call must achieve, in one or two sentences
    facts: Dict[str, str]  # what the caller may rely on and say (names, address, dates from the case)
    idempotency_key: str  # the same key must never dial twice


@dataclass(frozen=True)
class CallResult:
    status: str  # "dry_run" | "started" | "failed"
    conversation_id: Optional[str] = None
    detail: str = ""


@dataclass(frozen=True)
class Conversation:
    conversation_id: str
    status: str  # initiated | in-progress | processing | done | failed | unknown
    transcript: Tuple[Tuple[str, str], ...] = ()  # (role, message), role is "agent" or "user"
    summary: str = ""
    success: Optional[str] = None  # success | failure | unknown
    data: Dict[str, Any] = field(default_factory=dict)  # extracted fields, e.g. confirmed_date
    duration_s: Optional[float] = None


class Dialer(Protocol):
    def place(self, req: CallRequest) -> CallResult: ...

    def fetch(self, conversation_id: str) -> Conversation: ...


class DryRunDialer:
    """Records that a call would be placed. Nothing is dialled."""

    def place(self, req: CallRequest) -> CallResult:
        return CallResult("dry_run", "dryrun-" + req.idempotency_key, "not dialled (dry run)")

    def fetch(self, conversation_id: str) -> Conversation:
        return Conversation(conversation_id, "done", (("agent", "[dry run: no call was made]"),),
                            "Dry run: no call was made.", "unknown")


def make_dialer(name: str, cfg: Config) -> Dialer:
    name = (name or "dry_run").strip()
    if name == "dry_run":
        return DryRunDialer()
    if name == "elevenlabs":
        from agent.voice_elevenlabs import ElevenLabsDialer  # built on its own branch

        return ElevenLabsDialer(cfg)
    raise ValueError("unknown call backend %r" % name)
