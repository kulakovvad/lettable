import dataclasses
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from agent import consistency
from agent.chat import ChatError, ScriptedChat, Turn
from agent.config import Config
from agent.loop import run_loop
from agent.report import reasoning_md
from agent.timeline import load_case
from tests.helpers import make_case
from tests.loop_backends import call, submit

CFG = Config(loop_max_steps=6, consistency_check=True, as_of="now")
NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

EVENTS = [
    ("2026-01-01 09:00:00", "Email", "Tenant", "Agency / system",
     "Hi, Sarah Okafor here at Flat 1, 2 Test Road. The dishwasher leaks."),
    ("2026-01-01 09:05:00", "Email", "Agency / system", "Landlord", "Can you approve a repair for Sarah Okafor?"),
    ("2026-01-01 09:06:00", "Update", "Agency / system", "Not specified", "Waiting for Landlord (0 days)"),
]

WAIT_TURNS = [
    Turn(calls=[call("schedule_followup", 2, after_hours=48, waiting_on="landlord", reason="Asked today.")]),
    Turn(calls=[submit("WAIT")]),
]


def facts(*mentions):
    return Turn(calls=[call("report_facts", 1, mentions=[dict(field=f, value=v, ref=r) for f, v, r in mentions])], tokens=100)


def jev_answer(score, confidence=0.9, levels=4):
    return {"type": "score", "score": score * (levels - 1), "confidence": confidence}


class ConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.env = mock.patch.dict("os.environ", {"TYPESAFE_API_KEY": "test-key"})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def run_case(self, turns, events=EVENTS, cfg=CFG, jev=None):
        self.n = getattr(self, "n", 0) + 1
        folder = make_case(self.root, "c%d" % self.n, events)
        chat = ScriptedChat(turns)
        with mock.patch.object(consistency, "_post", side_effect=jev or AssertionError("Jev should not be called")) as post:
            d = run_loop(load_case(folder), chat, cfg, NOW, folder)
        return d, chat, post

    def test_disabled_by_default_makes_no_extraction_call(self):
        d, chat, _ = self.run_case(list(WAIT_TURNS), cfg=dataclasses.replace(CFG, consistency_check=False))
        self.assertEqual(d.action, "WAIT")
        self.assertIsNone(d.consistency)
        self.assertNotIn("CONSISTENCY", chat.seen[0][0]["text"])

    def test_values_equal_after_normalising_pass_without_calling_jev(self):
        turn = facts(("tenant_name", "Sarah Okafor", "event-001"), ("tenant_name", "sarah  okafor", "event-002"))
        d, _, post = self.run_case([turn] + WAIT_TURNS)
        self.assertEqual(d.action, "WAIT")
        self.assertEqual(d.consistency["status"], "ok")
        self.assertEqual(d.consistency["checks"], [])
        post.assert_not_called()

    def test_clear_address_mismatch_forces_escalation(self):
        events = list(EVENTS)
        events[0] = events[0][:4] + ("The dishwasher leaks at Flat 1, 2 Test Road.",)
        events[1] = events[1][:4] + ("Please attend Flat 9, 44 Other Street instead.",)
        turn = facts(("property_address", "Flat 1, 2 Test Road", "event-001"),
                     ("property_address", "Flat 9, 44 Other Street", "event-002"))
        jev = lambda url, headers, body, cfg: {"answers": {"property_address": jev_answer(0.1)}}
        d, _, post = self.run_case([turn] + WAIT_TURNS, events=events, jev=jev)
        self.assertEqual(d.action, "ESCALATE")
        self.assertEqual(d.proposed_action, "WAIT")
        self.assertTrue(any("property_address" in n for n in d.gate_notes))
        self.assertEqual(d.consistency["checks"][0]["tier"], "escalate")
        reasoning = reasoning_md(d.to_dict())
        self.assertIn("## Document consistency check", reasoning)
        self.assertIn("44 Other Street", reasoning)
        body = post.call_args[0][2]
        self.assertEqual(body["model"], "jev-1.13.0")
        self.assertEqual(set(body["questions"]), {"property_address"})

    def test_name_phone_and_email_mismatches_are_flagged_not_escalated(self):
        events = list(EVENTS)
        events[0] = events[0][:4] + ("Sarah Okafor, 07700 900123, sarah@example.com. The dishwasher leaks.",)
        events[1] = events[1][:4] + ("Contact Michael Brennan on 07700 900999 or michael@example.com.",)
        turn = facts(
            ("tenant_name", "Sarah Okafor", "event-001"), ("tenant_name", "Michael Brennan", "event-002"),
            ("tenant_phone", "07700 900123", "event-001"), ("tenant_phone", "07700 900999", "event-002"),
            ("tenant_email", "sarah@example.com", "event-001"), ("tenant_email", "michael@example.com", "event-002"),
        )
        jev = lambda url, headers, body, cfg: {"answers": {f: jev_answer(0.05) for f in body["questions"]}}
        d, chat, _ = self.run_case([turn] + WAIT_TURNS, events=events, jev=jev)
        self.assertEqual(d.action, "WAIT")
        tiers = {c["field"]: c["tier"] for c in d.consistency["checks"]}
        self.assertEqual(tiers, {"tenant_name": "flag", "tenant_phone": "flag", "tenant_email": "flag"})
        self.assertIn("Michael Brennan", chat.seen[1][0]["text"])

    def test_payee_or_bank_change_forces_escalation(self):
        events = list(EVENTS)
        events[0] = events[0][:4] + ("Pay Riverside Maintenance, sort code 20-00-00 account 11111111.",)
        events[1] = events[1][:4] + ("Pay BrightServe Ltd, sort code 30-00-00 account 22222222.",)
        turn = facts(("payee", "Riverside Maintenance", "event-001"), ("payee", "BrightServe Ltd", "event-002"),
                     ("bank_details", "sort code 20-00-00 account 11111111", "event-001"),
                     ("bank_details", "sort code 30-00-00 account 22222222", "event-002"))
        jev = lambda url, headers, body, cfg: {"answers": {f: jev_answer(0.1) for f in body["questions"]}}
        d, _, _ = self.run_case([turn] + WAIT_TURNS, events=events, jev=jev)
        self.assertEqual(d.action, "ESCALATE")
        tiers = {c["field"]: c["tier"] for c in d.consistency["checks"]}
        self.assertEqual(tiers, {"payee": "escalate", "bank_details": "escalate"})

    def test_minor_variation_is_flagged_to_the_model_and_does_not_override(self):
        events = list(EVENTS)
        events[1] = events[1][:4] + ("Can you approve a repair for Sara Okafor?",)
        turn = facts(("tenant_name", "Sarah Okafor", "event-001"), ("tenant_name", "Sara Okafor", "event-002"))
        jev = lambda url, headers, body, cfg: {"answers": {"tenant_name": jev_answer(0.66)}}
        d, chat, _ = self.run_case([turn] + WAIT_TURNS, events=events, jev=jev)
        self.assertEqual(d.action, "WAIT")
        self.assertEqual(d.consistency["checks"][0]["tier"], "flag")
        loop_prompt = chat.seen[1][0]["text"]
        self.assertIn("CONSISTENCY", loop_prompt)
        self.assertIn("Sara Okafor", loop_prompt)

    def test_low_confidence_mismatch_is_only_flagged(self):
        events = list(EVENTS)
        events[1] = events[1][:4] + ("Can you approve a repair for Michael Brennan?",)
        turn = facts(("tenant_name", "Sarah Okafor", "event-001"), ("tenant_name", "Michael Brennan", "event-002"))
        jev = lambda url, headers, body, cfg: {"answers": {"tenant_name": jev_answer(0.1, confidence=0.3)}}
        d, _, _ = self.run_case([turn] + WAIT_TURNS, events=events, jev=jev)
        self.assertEqual(d.action, "WAIT")
        self.assertEqual(d.consistency["checks"][0]["tier"], "flag")

    def test_value_not_in_the_cited_event_is_dropped(self):
        turn = facts(("tenant_name", "Sarah Okafor", "event-001"), ("tenant_name", "Michael Brennan", "event-002"))
        d, _, post = self.run_case([turn] + WAIT_TURNS)
        self.assertEqual(d.action, "WAIT")
        self.assertEqual(d.consistency["dropped"], 1)
        post.assert_not_called()

    def test_jev_failure_is_recorded_and_the_case_continues(self):
        events = list(EVENTS)
        events[1] = events[1][:4] + ("Can you approve a repair for Michael Brennan?",)
        turn = facts(("tenant_name", "Sarah Okafor", "event-001"), ("tenant_name", "Michael Brennan", "event-002"))

        def down(url, headers, body, cfg):
            raise ChatError("HTTP 503")

        d, _, _ = self.run_case([turn] + WAIT_TURNS, events=events, jev=down)
        self.assertEqual(d.action, "WAIT")
        self.assertEqual(d.consistency["status"], "unavailable")

    def test_extraction_without_a_tool_call_is_unavailable(self):
        d, _, _ = self.run_case([Turn(text="I cannot help with that.")] + WAIT_TURNS)
        self.assertEqual(d.action, "WAIT")
        self.assertEqual(d.consistency["status"], "unavailable")

    def test_missing_key_skips_jev(self):
        events = list(EVENTS)
        events[1] = events[1][:4] + ("Can you approve a repair for Michael Brennan?",)
        turn = facts(("tenant_name", "Sarah Okafor", "event-001"), ("tenant_name", "Michael Brennan", "event-002"))
        with mock.patch.dict("os.environ", {"TYPESAFE_API_KEY": ""}):
            d, _, post = self.run_case([turn] + WAIT_TURNS, events=events)
        self.assertEqual(d.action, "WAIT")
        self.assertEqual(d.consistency["status"], "unavailable")
        post.assert_not_called()

    def test_phone_formats_normalise_to_the_same_number(self):
        events = list(EVENTS)
        events[0] = events[0][:4] + ("Sarah Okafor, call me on 07700 900123. The dishwasher leaks.",)
        events[1] = events[1][:4] + ("Tenant number is +44 7700 900123.",)
        turn = facts(("tenant_phone", "07700 900123", "event-001"), ("tenant_phone", "+44 7700 900123", "event-002"))
        d, _, post = self.run_case([turn] + WAIT_TURNS, events=events)
        self.assertEqual(d.consistency["checks"], [])
        post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
