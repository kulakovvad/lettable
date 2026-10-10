"""Routine work should go out instead of stalling in WAIT or escalating (staged actions, first approval)."""

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent.chat import ScriptedChat, Turn
from agent.config import Config
from agent.loop import run_loop
from agent.report import answer_md
from agent.timeline import load_case
from tests.helpers import make_case
from tests.loop_backends import call, submit

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
NEW_REPAIR = [
    ("2026-01-01 09:00:00", "Email", "Tenant", "Northbridge Lettings", "The garden door will not lock properly."),
    ("2026-01-01 09:05:00", "Note", "Agency / system", "Not specified", "Complete the landlord approval step first."),
]
VISIT_APPROVED = NEW_REPAIR + [
    ("2026-01-01 10:00:00", "Email", "Landlord", "Northbridge Lettings", "Yes, please go ahead and send someone."),
]
ASK_LANDLORD = dict(to="landlord", purpose="request_info", priority="P3", evidence_refs=["event-001"],
                    body="Hello, the tenant reports the garden door will not lock. May we send a contractor to look?")
FIRST_APPROVAL = dict(amount_gbp=None, scope="contractor visit to inspect and quote", evidence_refs=["event-001"],
                      body="Hello, the tenant reports the garden door will not lock. May we send a contractor to inspect and quote?")


class RoutineFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.n = 0

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, turns, events=NEW_REPAIR):
        self.n += 1
        folder = make_case(self.root, "c%d" % self.n, events)
        chat = ScriptedChat(turns)
        return run_loop(load_case(folder), chat, Config(loop_max_steps=5, as_of="now"), NOW, folder), chat

    @staticmethod
    def result(chat, turn, i=0):
        return json.loads(chat.seen[turn][-1]["results"][i]["content"])

    def test_wait_with_a_staged_request_is_refused_once_and_names_the_action(self):
        d, chat = self.run_script([Turn(calls=[call("send_message", 1, **ASK_LANDLORD)]),
                                   Turn(calls=[submit("WAIT", 2)]),
                                   Turn(calls=[submit("ASK_LANDLORD", 3)])])
        refused = self.result(chat, 2)
        self.assertEqual(refused["code"], "staged_not_submitted")
        self.assertIn("ASK_LANDLORD", refused["hint"])
        self.assertEqual(d.action, "ASK_LANDLORD")
        self.assertEqual([a["state"] for a in d.actions if a["kind"] == "message"], ["committed"])

    def test_a_second_wait_is_accepted_and_the_request_stays_held(self):
        d, chat = self.run_script([Turn(calls=[call("send_message", 1, **ASK_LANDLORD)]),
                                   Turn(calls=[submit("WAIT", 2)]),
                                   Turn(calls=[submit("WAIT", 2)])])
        self.assertEqual(d.trace[-1]["result"]["status"], "accepted")
        self.assertEqual(d.action, "WAIT")
        self.assertEqual([a["state"] for a in d.actions if a["kind"] == "message"], ["held_for_review"])

    def test_wait_with_only_a_followup_is_accepted(self):
        d, chat = self.run_script([Turn(calls=[call("schedule_followup", 1, after_hours=48, waiting_on="landlord", reason="Asked.")]),
                                   Turn(calls=[submit("WAIT", 2)])])
        self.assertEqual(d.trace[-1]["result"]["status"], "accepted")
        self.assertEqual(d.action, "WAIT")

    def test_first_approval_request_needs_no_amount(self):
        d, chat = self.run_script([Turn(calls=[call("route_for_approval", 1, **FIRST_APPROVAL)]),
                                   Turn(calls=[submit("ROUTE_FOR_APPROVAL", 2)])])
        self.assertEqual(self.result(chat, 1)["status"], "staged")
        self.assertEqual(d.action, "ROUTE_FOR_APPROVAL")
        approval = next(a for a in d.actions if a["kind"] == "approval_request")
        self.assertEqual((approval["state"], approval["amount_gbp"], approval["above_limit"]), ("committed", None, False))
        self.assertIn("to attend or quote, no cost", answer_md(d.to_dict()))

    def test_approval_without_amount_is_refused_when_a_visit_is_already_approved(self):
        _, chat = self.run_script([Turn(calls=[call("route_for_approval", 1, **FIRST_APPROVAL)]),
                                   Turn(calls=[submit("WAIT", 2)])], VISIT_APPROVED)
        self.assertEqual(self.result(chat, 1)["code"], "already_approved")

    def test_a_first_chase_points_to_the_first_message_actions(self):
        body = dict(ASK_LANDLORD, purpose="chase")
        _, chat = self.run_script([Turn(calls=[call("send_message", 1, **body)]), Turn(calls=[submit("WAIT", 2)])])
        blocked = self.result(chat, 1)
        self.assertEqual(blocked["code"], "nothing_to_chase")
        self.assertIn("ASK_LANDLORD", blocked["hint"])
        self.assertIn("route_for_approval", blocked["hint"])


if __name__ == "__main__":
    unittest.main()
