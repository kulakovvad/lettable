"""Case decisions are proposals, never model-authored execution receipts."""
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


Action = Literal["wait", "chase_landlord", "chase_provider", "route_for_approval",
                 "ask_tenant", "send_reminder", "close", "escalate"]
TenantField = Literal["issue_details", "availability", "access_instructions", "tenant_photo"]


class Event(StrictModel):
    id: str
    at: datetime
    channel: str
    sender: str
    recipient: str
    text: str
    source: str


class Document(StrictModel):
    source: str
    available_from: str
    pages: list[str]


class CaseSnapshot(StrictModel):
    case_id: str
    initial_request: str
    property: str | None = None
    as_of: datetime
    events: list[Event]
    documents: list[Document] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    fingerprint: str

    def evidence_refs(self):
        return {event.id for event in self.events} | {
            f"{doc.source}:page:{page}" for doc in self.documents
            for page in range(1, len(doc.pages) + 1)
        }


class Proposal(StrictModel):
    action: Action
    reason: str = Field(min_length=1, max_length=1200)
    evidence_refs: list[str] = Field(min_length=1, max_length=30)
    unknowns: list[str] = Field(max_length=20)
    uncertain: bool
    priority: Literal["P0", "P1", "P2", "P3"]
    requested_fields: list[TenantField] = Field(max_length=4)


class CasePolicy(StrictModel):
    """Trusted application config; never loaded from a case or a model proposal."""
    allowed_actions: list[Action] = Field(default_factory=lambda: ["wait", "escalate"])
    landlord_wait_hours: float | None = Field(default=None, gt=0)
    provider_wait_hours: float | None = Field(default=None, gt=0)
    max_provider_chases: int | None = Field(default=None, ge=1)
    approval_limit: Decimal | None = Field(default=None, ge=0)
    currency: str | None = None
    escalation_route: str = "local-human-review"
    timeout_seconds: float = Field(default=45, gt=0)
    max_input_chars: int = Field(default=100000, gt=0)
    max_tokens: int = Field(default=24000, gt=0)
    max_pdf_pages: int = Field(default=40, gt=0)


class OperationalFacts(StrictModel):
    """Optional verified facts supplied by the application, not the model.

    The public histories do not consistently contain contacts or financial state.
    Missing facts fail closed. A future CRM adapter supplies this contract.
    """
    evidence_refs: list[str] = Field(default_factory=list)
    quote_amount: Decimal | None = Field(default=None, ge=0)
    approved_quote_amount: Decimal | None = Field(default=None, ge=0)
    currency: str | None = None
    appointment_at: datetime | None = None
    tenant_phone: str | None = None
    provider_or_tenant_confirmed_completion: bool = False
    invoice_settled: bool = False
    keys_settled: bool = False
    known_tenant_fields: list[TenantField] = Field(default_factory=list)

    @model_validator(mode="after")
    def dated_appointment(self):
        if self.appointment_at and self.appointment_at.tzinfo is None:
            raise ValueError("Appointment requires an explicit timezone")
        return self


class GateResult(StrictModel):
    allowed: bool
    code: str
    recipient: str | None = None
    review_at: datetime | None = None
    message: str | None = None
    idempotency_key: str | None = None


class Receipt(StrictModel):
    id: str
    kind: str
    state: Literal["recorded", "queued"]
    payload: dict


class CasePacket(StrictModel):
    case_id: str
    trace_id: str
    status: Literal["waiting", "queued", "decided", "escalated"]
    code: str
    summary: str
    as_of: datetime | None = None
    proposal: Proposal | None = None
    gate: GateResult | None = None
    known: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    tried: list[str] = Field(default_factory=list)
    options: list[str] = Field(default_factory=list)
    receipts: list[Receipt] = Field(default_factory=list)


class CaseFailure(Exception):
    """Stable, non-sensitive fallback code; do not copy raw exceptions to outputs."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)
