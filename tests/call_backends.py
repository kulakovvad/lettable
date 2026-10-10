"""Scripted chat backends for the phone-call tests (loaded as module:Class)."""

from __future__ import annotations

from agent.chat import ScriptedChat, Turn
from tests.loop_backends import call, submit

CALL = dict(party="provider", purpose="chase", objective="Ask when the engineer can visit to repair the dishwasher.",
            facts={"job": "Dishwasher repair"}, evidence_refs=["event-003"], priority="P3")


class ProviderCallChat(ScriptedChat):
    def __init__(self):
        super().__init__([Turn(calls=[call("place_call", 1, **CALL)]), Turn(calls=[submit("CHASE_PROVIDER")])])
