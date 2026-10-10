import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent import gates
from agent.chat import ScriptedChat, Turn
from agent.config import Config
from agent.loop import run_loop
from agent.replay import label_next
from agent.schema import Proposal
from agent.timeline import Event, load_case
from tests.helpers import WAITING_LANDLORD, make_case
from tests.loop_backends import call, submit

NOW = datetime(2026, 1, 3, 12, 0, tzinfo=timezone.utc)
PROVIDER_REPLIED = [
    ("2026-01-01 09:00:00", "Note", "Agency / system", "Not specified", "Request: dishwasher leaks."),
    ("2026-01-01 09:10:00", "Email", "Northbridge Lettings", "Contractor", "Please attend the dishwasher leak."),
    ("2026-01-02 09:00:00", "Email", "Contractor", "Northbridge Lettings", "Attended. Invoice to follow."),
]
ASK_PROVIDER = dict(to="provider", purpose="request_info", priority="P3", evidence_refs=["event-003"],
                    body="Hello, could you send an itemised invoice for the dishwasher visit please? Thank you.")
ASK_LANDLORD = dict(to="landlord", purpose="request_info", priority="P3", evidence_refs=["event-002"],
                    body="Hello, do you use your own contractor for dishwasher repairs? Thank you.")


class AskActionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.n = 0

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, turns, events, now=NOW):
        self.n += 1
        folder = make_case(self.root, "c%d" % self.n, events)
        chat = ScriptedChat(turns)
        return run_loop(load_case(folder), chat, Config(loop_max_steps=4, as_of="now"), now, folder), chat

    def test_question_to_a_provider_who_replied_is_sent(self):
        d, _ = self.run_script([Turn(calls=[call("send_message", 1, **ASK_PROVIDER)]),
                                Turn(calls=[submit("ASK_PROVIDER")])], PROVIDER_REPLIED)
        self.assertEqual(d.action, "ASK_PROVIDER")
        self.assertEqual([a["state"] for a in d.actions if a["kind"] == "message"], ["committed"])
        self.assertIn("itemised invoice", d.message)

    def test_question_to_a_party_we_are_waiting_on_is_an_early_chase(self):
        d, chat = self.run_script([Turn(calls=[call("send_message", 1, **ASK_LANDLORD)]),
                                   Turn(calls=[submit("WAIT")])], WAITING_LANDLORD,
                                  now=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc))
        self.assertEqual(json.loads(chat.seen[1][-1]["results"][0]["content"])["code"], "too_early")

    def test_ask_needs_a_staged_request_info(self):
        d, chat = self.run_script([Turn(calls=[submit("ASK_PROVIDER", 1)]), Turn(calls=[submit("WAIT")])],
                                  PROVIDER_REPLIED)
        self.assertEqual(json.loads(chat.seen[1][-1]["results"][0]["content"])["code"], "action_not_staged")

    def test_gate_turns_an_early_question_into_wait(self):
        case = load_case(make_case(self.root, "gate", WAITING_LANDLORD))
        proposal = Proposal.from_dict(dict(action="ASK_LANDLORD", reason="r", confidence=0.9, message="Hello there"))
        decision = gates.apply(case, proposal, Config(), datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc))
        self.assertEqual(decision.action, "WAIT")


class ReplayLabelTests(unittest.TestCase):
    @staticmethod
    def ev(to, body):
        return Event(index=1, ts=None, channel="Email", sender="Agency / system", recipient=to, body=body)

    def test_questions_and_chases_are_told_apart(self):
        self.assertEqual(label_next(self.ev("Contractor", "Could you send a photo of the part?")), "ASK_PROVIDER")
        self.assertEqual(label_next(self.ev("Contractor", "Following up: any update on the visit?")), "CHASE_PROVIDER")
        self.assertEqual(label_next(self.ev("Landlord", "Do you use your own plumber?")), "ASK_LANDLORD")
        self.assertEqual(label_next(self.ev("Landlord", "Following up on our message")), "CHASE_LANDLORD")


if __name__ == "__main__":
    unittest.main()
