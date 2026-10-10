"""Test-only backend that reports what it was shown in the case's attachments."""

from __future__ import annotations

from agent.llm import Backend


class EchoAttachments(Backend):
    def propose(self, case, now, cfg):
        shown = "; ".join("%s=%s" % (a.name, (a.text or "UNAVAILABLE").replace("\n", " ")) for a in case.attachments)
        return {"action": "WAIT", "reason": "attachments: " + shown, "confidence": 0.9}
