"""Scripted chat backends for the phone-call tests (loaded as module:Class)."""

from __future__ import annotations

from agent.chat import ScriptedChat, Turn
from tests.loop_backends import call, submit

CALL = dict(party="provider", purpose="chase", objective="Ask when the engineer can visit to repair the dishwasher.",
            facts={"job": "Dishwasher repair"}, evidence_refs=["event-003"], priority="P3")


class ProviderCallChat(ScriptedChat):
    def __init__(self):
        super().__init__([Turn(calls=[call("place_call", 1, **CALL)]), Turn(calls=[submit("CHASE_PROVIDER")])])


class ReadVoicemailAndCallChat(ScriptedChat):
    """Reads the transcribed voicemail, then chases the provider by phone."""

    def __init__(self):
        super().__init__([
            Turn(calls=[call("read_attachment", 1, name="voicemail.mp3")]),
            Turn(calls=[call("place_call", 2, **CALL)]),
            Turn(calls=[submit("CHASE_PROVIDER")]),
        ])


class P0EscalateChat(ScriptedChat):
    """Escalates a case as P0 without any hazard words, to test the priority trigger."""

    def __init__(self):
        super().__init__([
            Turn(calls=[call("escalate_to_human", 1, priority="P0", route="on_call_emergency", summary="Urgent: a person must decide now.",
                             known=["event-001"], unknowns=["what happened"], tried=[], options=["call the tenant", "send an engineer"],
                             evidence_refs=["event-001"])]),
            Turn(calls=[submit("ESCALATE", priority="P0", options=["call the tenant", "send an engineer"], unknowns=["what happened"])]),
        ])


class P1EscalateChat(ScriptedChat):
    def __init__(self):
        super().__init__([
            Turn(calls=[call("escalate_to_human", 1, priority="P1", route="property_manager", summary="A person must decide.",
                             known=["event-001"], unknowns=["x"], tried=[], options=["a", "b"], evidence_refs=["event-001"])]),
            Turn(calls=[submit("ESCALATE", priority="P1", options=["a", "b"], unknowns=["x"])]),
        ])
