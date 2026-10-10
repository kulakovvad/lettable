"""Scripted chat backends for runner-level tests (loaded as module:Class)."""

from __future__ import annotations

from agent.chat import ScriptedChat, ToolCall, Turn


def call(tool, n=1, **args):
    return ToolCall(id="c%d-%s" % (n, tool), name=tool, arguments=args)


def submit(action, n=9, **extra):
    args = dict(action=action, priority="P3", reason="Scripted decision citing event-003.", confidence=0.9,
                evidence_refs=["event-003"], unknowns=[], options=[], unrelated_issues=[], amount_gbp=None)
    args.update(extra)
    return call("submit_decision", n, **args)


class WaitChat(ScriptedChat):
    def __init__(self):
        super().__init__([
            Turn(calls=[call("case_facts")]),
            Turn(calls=[call("schedule_followup", 2, after_hours=48, waiting_on="landlord", reason="Asked today.")]),
            Turn(calls=[submit("WAIT")]),
        ])


class SilentChat(ScriptedChat):
    """Never calls submit_decision."""
    def __init__(self):
        super().__init__([Turn(calls=[call("case_facts", i)]) for i in range(1, 40)])


class LeakProbeChat(ScriptedChat):
    """Tries to read the raw history file, then waits."""
    def __init__(self):
        super().__init__([
            Turn(calls=[call("read_case_file", 1, path="history.md")]),
            Turn(calls=[call("schedule_followup", 2, after_hours=24, waiting_on="landlord", reason="probe")]),
            Turn(calls=[submit("WAIT")]),
        ])
