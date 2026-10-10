"""Test-only backend that reports how many events it was shown."""

from __future__ import annotations

from agent.llm import Backend


class EchoBackend(Backend):
    def propose(self, case, now, cfg):
        return {"action": "WAIT", "reason": "saw %d events at %s" % (len(case.events), now.isoformat()), "confidence": 0.9}
