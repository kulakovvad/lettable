"""One case in, one decision out: model proposes, code decides."""

from __future__ import annotations

from datetime import datetime

from agent import gates
from agent.config import Config
from agent.llm import Backend
from agent.schema import Decision, Proposal
from agent.timeline import Case


def decide(case: Case, backend: Backend, cfg: Config, now: datetime) -> Decision:
    """Raises on a malformed proposal or a backend failure; the runner turns that into an escalation."""
    raw = backend.propose(case, now, cfg)
    proposal = Proposal.from_dict(raw)
    return gates.apply(case, proposal, cfg, now)
