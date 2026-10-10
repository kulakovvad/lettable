"""Regression tests for the PR #5 review (items 1-5 and the should-fix list)."""

import dataclasses
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent import evidence, gates
from agent.chat import ScriptedChat, Turn
from agent.config import Config
from agent.loop import run_loop
from agent.runner import run_all
from agent.schema import Proposal
from agent.timeline import load_case
from tests.helpers import WAITING_LANDLORD, make_case
from tests.loop_backends import call, submit

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
QUOTE = [("2026-01-01 09:00:00", "Note", "Agency / system", "Not specified", "Request: dishwasher leaks."),
         ("2026-01-01 09:10:00", "Email", "Northbridge Lettings", "Contractor", "Please quote for the dishwasher."),
         ("2026-01-02 09:00:00", "Email", "Contractor", "Northbridge Lettings", "Quote is £450 plus VAT.")]
INSTRUCT = dict(to="provider", purpose="instruct_provider", priority="P3", evidence_refs=["event-003"],
                body="Please go ahead with the dishwasher repair as quoted. Thank you.")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.n = 0

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, turns, events, now=NOW, cfg=None):
        self.n += 1
        folder = make_case(self.root, "c%d" % self.n, events)
        chat = ScriptedChat(turns)
        cfg = cfg or Config(loop_max_steps=4, as_of="now")
        return run_loop(load_case(folder), chat, cfg, now, folder), chat

    @staticmethod
    def result(chat, turn=1, i=0):
        return json.loads(chat.seen[turn][-1]["results"][i]["content"])


class Item1PriorityIsNotAuthority(Base):
    def test_model_priority_does_not_skip_landlord_approval(self):
        for priority in ("P0", "P1", "P3"):
            d, chat = self.run_script([Turn(calls=[call("send_message", 1, **dict(INSTRUCT, priority=priority))]),
                                       Turn(calls=[submit("WAIT")])], QUOTE)
            self.assertEqual(self.result(chat)["code"], "no_landlord_approval", priority)

    def test_model_priority_does_not_allow_an_early_chase(self):
        chase = dict(to="landlord", purpose="chase", priority="P0", evidence_refs=["event-002"],
                     body="Hello, following up on our approval request for the dishwasher. Thank you.")
        d, chat = self.run_script([Turn(calls=[call("send_message", 1, **chase)]), Turn(calls=[submit("WAIT")])], WAITING_LANDLORD)
        self.assertEqual(self.result(chat)["code"], "too_early")

    def test_a_hazard_found_by_code_allows_an_early_chase(self):
        events = WAITING_LANDLORD + [("2026-01-01 10:00:00", "SMS", "Tenant", "Agency", "There is water pouring through the ceiling, it is flooding")]
        chase = dict(to="landlord", purpose="chase", priority="P3", evidence_refs=["event-002"],
                     body="Hello, urgent follow-up on the approval request: the flat is flooding. Thank you.")
        d, chat = self.run_script([Turn(calls=[call("send_message", 1, **chase)]), Turn(calls=[submit("ESCALATE")])], events)
        self.assertEqual(self.result(chat)["status"], "staged")


class Item2NegatedApproval(Base):
    def test_negated_or_questioning_landlord_replies_are_not_approval(self):
        for text in ("I do not approve this quote.", "I don't want you to go ahead yet", "Can you approve it for less?",
                     "Please hold off, I'm not happy to proceed."):
            d, chat = self.run_script([Turn(calls=[call("send_message", 1, **INSTRUCT)]), Turn(calls=[submit("WAIT")])],
                                      QUOTE + [("2026-01-02 12:00:00", "Email", "Landlord", "Northbridge Lettings", text)])
            self.assertEqual(self.result(chat)["code"], "no_landlord_approval", text)

    def test_plain_approval_after_the_quote_counts(self):
        d, chat = self.run_script([Turn(calls=[call("send_message", 1, **INSTRUCT)]), Turn(calls=[submit("INSTRUCT_PROVIDER")])],
                                  QUOTE + [("2026-01-02 12:00:00", "Email", "Landlord", "Northbridge Lettings", "Yes please go ahead.")])
        self.assertEqual(d.action, "INSTRUCT_PROVIDER")
        self.assertEqual(d.actions[0]["state"], "committed")


class Item3OnlyTheFinalActionCommits(Base):
    MSG = dict(to="tenant", purpose="request_info", priority="P3", evidence_refs=["event-001"],
               body="Hello, could you send a photo of the dishwasher leak please? Thank you.")

    def test_budget_stop_holds_staged_messages(self):
        d, _ = self.run_script([Turn(calls=[call("send_message", 1, **self.MSG)])] +
                               [Turn(calls=[call("case_facts", i)]) for i in range(2, 10)], WAITING_LANDLORD)
        self.assertEqual(d.cause, "loop_no")
        message = [a for a in d.actions if a["kind"] == "message"][0]
        self.assertEqual(message["state"], "held_for_review")
        self.assertEqual([a["state"] for a in d.actions if a["kind"] == "escalation"], ["committed"])

    def test_message_then_escalate_holds_the_message(self):
        d, _ = self.run_script([Turn(calls=[call("send_message", 1, **self.MSG)]), Turn(calls=[submit("ESCALATE")])], WAITING_LANDLORD)
        self.assertEqual(d.action, "ESCALATE")
        self.assertEqual([a["state"] for a in d.actions if a["kind"] == "message"], ["held_for_review"])

    def test_safety_advice_commits_only_on_a_hazard_found_by_code(self):
        advice = dict(to="tenant", purpose="safety_advice", priority="P0", evidence_refs=["event-001"],
                      body="Please leave the property, do not use switches and call the gas emergency line on 0800 111 999.")
        gas = WAITING_LANDLORD + [("2026-01-01 10:00:00", "SMS", "Tenant", "Agency", "I can smell gas in the kitchen")]
        d, _ = self.run_script([Turn(calls=[call("send_message", 1, **advice)]), Turn(calls=[submit("ESCALATE")])], gas)
        self.assertEqual([a["state"] for a in d.actions if a["kind"] == "message"], ["committed"])
        d, _ = self.run_script([Turn(calls=[call("send_message", 1, **advice)]), Turn(calls=[submit("ESCALATE")])], WAITING_LANDLORD)
        self.assertEqual([a["state"] for a in d.actions if a["kind"] == "message"], ["held_for_review"])


class Item4CloseNeedsRealCompletion(Base):
    def test_citing_a_quote_as_completion_is_blocked(self):
        d, chat = self.run_script([Turn(calls=[call("close_case", 1, completion_refs=["event-003"], invoice_status="no_charge",
                                                     invoice_refs=["event-003"], keys_status="not_applicable", key_refs=[], reason="x")]),
                                   Turn(calls=[submit("WAIT")])], QUOTE)
        self.assertEqual(self.result(chat)["code"], "no_confirmation")

    def test_agency_note_saying_completed_does_not_satisfy_the_final_gate(self):
        case = load_case(make_case(self.root, "note", WAITING_LANDLORD + [
            ("2026-01-02 10:00:00", "Note", "Agency / system", "Not specified", "Job completed")]))
        d = gates.apply(case, Proposal.from_dict({"action": "CLOSE", "reason": "x", "confidence": 0.9}), Config(), NOW)
        self.assertEqual(d.action, "ESCALATE")

    def test_questions_about_completion_do_not_count(self):
        case = load_case(make_case(self.root, "q", WAITING_LANDLORD + [
            ("2026-01-02 10:00:00", "Email", "Contractor", "Agency", "Has the job been completed by the other team?")]))
        self.assertIsNone(gates.confirmed_completion(case))

    def test_invoice_position_must_be_cited(self):
        done = WAITING_LANDLORD + [("2026-01-02 10:00:00", "Email", "Contractor", "Agency", "Job completed today.")]
        d, chat = self.run_script([Turn(calls=[call("close_case", 1, completion_refs=["event-004"], invoice_status="sent_to_landlord",
                                                     invoice_refs=["event-004"], keys_status="not_applicable", key_refs=[], reason="x")]),
                                   Turn(calls=[submit("WAIT")])], done)
        self.assertEqual(self.result(chat)["code"], "invoice_unverified")
        done = done + [("2026-01-02 11:00:00", "Email", "Northbridge Lettings", "Landlord", "Please find the invoice attached.")]
        d, chat = self.run_script([Turn(calls=[call("close_case", 1, completion_refs=["event-004"], invoice_status="sent_to_landlord",
                                                     invoice_refs=["event-005"], keys_status="not_applicable", key_refs=[], reason="x")]),
                                   Turn(calls=[submit("CLOSE")])], done)
        self.assertEqual(d.action, "CLOSE")


class Item5DecisionTime(Base):
    CHASE = dict(to="landlord", purpose="chase", priority="P3", evidence_refs=["event-002"],
                 body="Hello, following up on our approval request for the dishwasher. Thank you.")

    def test_explicit_clock_is_honoured(self):
        later = datetime(2026, 6, 1, tzinfo=timezone.utc)
        d, chat = self.run_script([Turn(calls=[call("send_message", 1, **self.CHASE)]), Turn(calls=[submit("CHASE_LANDLORD")])],
                                  WAITING_LANDLORD, now=later, cfg=Config(as_of="now"))
        self.assertEqual(self.result(chat)["status"], "staged")
        self.assertEqual(d.action, "CHASE_LANDLORD")

    def test_later_mode_uses_the_clock_only_when_it_is_later(self):
        d, _ = self.run_script([Turn(calls=[submit("WAIT")])], WAITING_LANDLORD, now=datetime(2026, 6, 1, tzinfo=timezone.utc),
                               cfg=Config(as_of="later"))
        self.assertTrue(d.as_of.startswith("2026-06-01"))
        d, _ = self.run_script([Turn(calls=[submit("WAIT")])], WAITING_LANDLORD, now=datetime(2025, 1, 1, tzinfo=timezone.utc),
                               cfg=Config(as_of="later"))
        self.assertTrue(d.as_of.startswith("2026-01-01T09:06"))


class ShouldFix(Base):
    def test_spend_gate_passes_an_approved_amount(self):
        case = load_case(make_case(self.root, "spend", QUOTE + [
            ("2026-01-02 12:00:00", "Email", "Landlord", "Northbridge Lettings", "Happy to proceed at £450 plus VAT.")]))
        p = Proposal.from_dict({"action": "INSTRUCT_PROVIDER", "reason": "x", "confidence": 0.9, "message": "Go ahead.", "amount_gbp": 450})
        self.assertEqual(gates.apply(case, p, Config(), NOW).action, "INSTRUCT_PROVIDER")
        p = Proposal.from_dict({"action": "INSTRUCT_PROVIDER", "reason": "x", "confidence": 0.9, "message": "Go ahead.", "amount_gbp": 900})
        self.assertEqual(gates.apply(case, p, Config(), NOW).action, "ESCALATE")

    def test_later_invoice_or_same_figure_keeps_the_approval(self):
        approved = QUOTE + [("2026-01-02 12:00:00", "Email", "Landlord", "Agency", "Yes please go ahead.")]
        for text in ("Invoice for £450 plus VAT attached.", "Confirming the £450 plus VAT, booked for Monday."):
            case = load_case(make_case(self.root, "keep%d" % len(text), approved + [("2026-01-03 09:00:00", "Email", "Contractor", "Agency", text)]))
            self.assertIsNotNone(evidence.covering_approval(case)[0], text)
        case = load_case(make_case(self.root, "bigger", approved + [("2026-01-03 09:00:00", "Email", "Contractor", "Agency", "Revised quote £1,200.")]))
        self.assertIsNone(evidence.covering_approval(case)[0])

    def test_search_treats_the_query_as_plain_text(self):
        d, chat = self.run_script([Turn(calls=[call("search_case", 1, query="(a+)+$")]), Turn(calls=[submit("WAIT")])], WAITING_LANDLORD)
        self.assertEqual(self.result(chat)["status"], "ok")

    def test_agency_name_comes_from_the_case(self):
        case = load_case(make_case(self.root, "name", QUOTE))
        self.assertEqual(evidence.agency_name(case), "Northbridge Lettings")
        self.assertEqual(evidence.agency_name(load_case(make_case(self.root, "anon", WAITING_LANDLORD))), "the agency")
        d, chat = self.run_script([Turn(calls=[submit("WAIT")])], QUOTE)

    def test_tool_hazard_facts_match_the_gate(self):
        events = WAITING_LANDLORD + [("2026-01-02 10:00:00", "SMS", "Tenant", "Agency", "I can smell gas")] + [
            ("2026-01-0%d 10:00:00" % (i + 3), "Update", "Agency / system", "Not specified", "note %d" % i) for i in range(6)]
        d, chat = self.run_script([Turn(calls=[call("case_facts", 1)]), Turn(calls=[submit("ESCALATE")])], events)
        facts = self.result(chat)
        self.assertTrue(facts["urgent_by_code"])
        self.assertEqual(facts["open_hazard_hits"][0]["match"], gates.find_hazard(load_case(make_case(self.root, "h", events)), Config()))

    def test_run_wide_token_cap_stops_model_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            for cid in ("001", "002", "003"):
                make_case(Path(tmp) / "in", cid, WAITING_LANDLORD)
            cfg = Config(case_timeout_s=30, concurrency=1, run_token_budget=1)
            summary = run_all(Path(tmp) / "in", Path(tmp) / "out", cfg, backend="tests.loop_backends:TokenWaitChat")
            self.assertEqual(summary["fallbacks"], {"spend_cap": 2})


if __name__ == "__main__":
    unittest.main()
