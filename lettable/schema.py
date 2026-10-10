"""The proposal the model returns and the decision the system records."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional, Tuple

ACTIONS = (
    "WAIT",
    "CHASE_LANDLORD",
    "CHASE_PROVIDER",
    "ASK_TENANT",
    "ROUTE_FOR_APPROVAL",
    "SEND_REMINDER",
    "CLOSE",
    "ESCALATE",
)
NEEDS_MESSAGE = ("CHASE_LANDLORD", "CHASE_PROVIDER", "ASK_TENANT", "SEND_REMINDER")
MAX_TEXT = 1200


def _text(value: Any, limit: int = MAX_TEXT) -> str:
    return str(value if value is not None else "").strip()[:limit]


def _texts(value: Any, limit: int = 6) -> Tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(_text(v, 300) for v in value[:limit] if _text(v, 300))


@dataclass(frozen=True)
class Proposal:
    action: str
    reason: str
    confidence: float
    message: str = ""
    unknowns: Tuple[str, ...] = ()
    options: Tuple[str, ...] = ()
    amount_gbp: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Any) -> "Proposal":
        """Strict: anything malformed raises ValueError and the case is escalated."""
        if not isinstance(data, dict):
            raise ValueError("proposal is not an object")
        action = _text(data.get("action"), 40).upper()
        if action not in ACTIONS:
            raise ValueError("unknown action %r" % action)
        reason = _text(data.get("reason"))
        if not reason:
            raise ValueError("proposal has no reason")
        try:
            confidence = float(data.get("confidence"))
        except (TypeError, ValueError):
            raise ValueError("confidence is not a number")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence outside 0..1")
        amount = data.get("amount_gbp")
        if amount is not None:
            try:
                amount = float(amount)
            except (TypeError, ValueError):
                raise ValueError("amount_gbp is not a number")
            if amount < 0:
                raise ValueError("amount_gbp is negative")
        return cls(
            action=action,
            reason=reason,
            confidence=confidence,
            message=_text(data.get("message")),
            unknowns=_texts(data.get("unknowns")),
            options=_texts(data.get("options")),
            amount_gbp=amount,
        )


@dataclass
class Decision:
    case_id: str
    action: str
    reason: str
    source: str  # "model" or "fallback"
    message: str = ""
    unknowns: Tuple[str, ...] = ()
    options: Tuple[str, ...] = ()
    confidence: Optional[float] = None
    hazard: bool = False
    waiting_on: Optional[str] = None
    waiting_days: Optional[float] = None
    events_seen: int = 0
    gate_notes: Tuple[str, ...] = ()
    proposed_action: Optional[str] = None  # what the model asked for, if the gates changed it
    cause: Optional[str] = None  # why the fallback ran
    idempotency_key: str = ""
    decided_at: str = ""
    warnings: Tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        for k in ("unknowns", "options", "gate_notes", "warnings"):
            d[k] = list(d[k])
        return d


def idempotency_key(case_id: str, events_seen: int, action: str, message: str) -> str:
    raw = "%s|%d|%s|%s" % (case_id, events_seen, action, message)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
