"""One case in, one decision out: model proposes, code decides."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from agent import gates
from agent.chat import ChatBackend
from agent.config import Config
from agent.llm import Backend
from agent.schema import Decision, Proposal
from agent.timeline import Case


def decide(case: Case, backend: Union[Backend, ChatBackend], cfg: Config, now: datetime,
           folder: Optional[Path] = None) -> Decision:
    """Raises on a malformed proposal or a backend failure; the runner turns that into an escalation."""
    if isinstance(backend, ChatBackend):
        from agent.loop import run_loop

        return run_loop(case, backend, cfg, now, folder)
    raw = backend.propose(case, now, cfg)
    proposal = Proposal.from_dict(raw)
    return gates.apply(case, proposal, cfg, now)
