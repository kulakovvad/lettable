import dataclasses
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent.chat import ScriptedChat, Turn
from agent.config import Config
from agent.loop import run_loop
from agent.report import answer_md, reasoning_md
from agent.runner import run_all
from agent.timeline import load_case
from tests.helpers import WAITING_LANDLORD, make_case
from tests.loop_backends import call, submit

CFG = Config(loop_max_steps=6)
NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
LATER = datetime(2026, 1, 9, 12, 0, tzinfo=timezone.utc)
CHASE = dict(to="landlord", purpose="chase", body="Hello, a quick follow-up on the dishwasher repair approval. Northbridge Lettings",
             evidence_refs=["event-002"], priority="P3")


class LoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def case(self, events, cid="c1"):
        folder = make_case(self.root, cid, events)
        return load_case(folder), folder

    def run_script(self, turns, events=WAITING_LANDLORD, now=NOW, cfg=CFG):
        self.n = getattr(self, "n", 0) + 1
        case, folder = self.case(events, "c%d" % self.n)
        chat = ScriptedChat(turns)
        return run_loop(case, chat, dataclasses.replace(cfg, as_of="now"), now, folder), chat

    def test_early_chase_is_blocked_and_the_model_recovers_with_wait(self):
        d, chat = self.run_script([
            Turn(calls=[call("send_message", 1, **CHASE)]),
            Turn(calls=[call("schedule_followup", 2, after_hours=48, waiting_on="landlord", reason="Asked today.")]),
            Turn(calls=[submit("WAIT")]),
        ])
        first_result = json.loads(chat.seen[1][-1]["results"][0]["content"])
        self.assertEqual(first_result["code"], "too_early")
        self.assertEqual(d.action, "WAIT")
        self.assertEqual([a["kind"] for a in d.actions], ["followup"])
        self.assertEqual(d.actions[0]["state"], "committed")
        self.assertEqual(d.blocked[0]["code"], "too_early")

    def test_overdue_chase_is_staged_and_committed(self):
        d, _ = self.run_script([Turn(calls=[call("send_message", 1, **CHASE)]), Turn(calls=[submit("CHASE_LANDLORD")])], now=LATER)
        self.assertEqual(d.action, "CHASE_LANDLORD")
        self.assertEqual(d.actions[0]["state"], "committed")
        self.assertIn("follow-up", d.message)

    def test_invented_phone_number_is_blocked(self):
        body = dict(CHASE, body="Please call the landlord on 07700 123456 to approve. Northbridge Lettings")
        d, chat = self.run_script([Turn(calls=[call("send_message", 1, **body)]), Turn(calls=[submit("WAIT")])], now=LATER)
        result = json.loads(chat.seen[1][-1]["results"][0]["content"])
        self.assertEqual(result["code"], "unverified_detail")

    def test_primary_action_must_be_staged_first(self):
        d, chat = self.run_script([Turn(calls=[submit("CHASE_LANDLORD")]), Turn(calls=[submit("WAIT", 2)])], now=LATER)
        result = json.loads(chat.seen[1][-1]["results"][0]["content"])
        self.assertEqual(result["code"], "action_not_staged")
        self.assertEqual(d.action, "WAIT")

    def test_final_gate_override_holds_staged_message_and_escalates(self):
        events = WAITING_LANDLORD + [("2026-01-01 10:00:00", "SMS", "Tenant", "Agency", "I can smell gas in the kitchen")]
        d, _ = self.run_script([Turn(calls=[call("send_message", 1, **CHASE)]), Turn(calls=[submit("CHASE_LANDLORD")])],
                               events=events, now=LATER)
        self.assertEqual(d.action, "ESCALATE")
        self.assertEqual(d.proposed_action, "CHASE_LANDLORD")
        message = [a for a in d.actions if a["kind"] == "message"][0]
        self.assertEqual(message["state"], "held_for_review")
        escalation = [a for a in d.actions if a["kind"] == "escalation"][0]
        self.assertEqual(escalation["state"], "committed")
        self.assertEqual(escalation["route"], "on_call_emergency")

    def test_no_decision_within_budget_escalates_with_trace(self):
        d, _ = self.run_script([Turn(calls=[call("case_facts", i)]) for i in range(1, 20)])
        self.assertEqual(d.action, "ESCALATE")
        self.assertEqual(d.cause, "loop_no")
        self.assertTrue(d.trace)

    def test_bad_tool_calls_do_not_crash_the_case(self):
        d, chat = self.run_script([
            Turn(calls=[call("delete_everything", 1), call("read_events", 2, first="x", last=3)]),
            Turn(calls=[call("read_attachment", 3, name="nope.pdf")]),
            Turn(calls=[submit("WAIT")]),
        ])
        statuses = [json.loads(r["content"])["status"] for r in chat.seen[1][-1]["results"]]
        self.assertEqual(statuses, ["error", "error"])
        self.assertEqual(d.action, "WAIT")

    def test_close_requires_confirmation_from_a_party(self):
        events = WAITING_LANDLORD + [("2026-01-02 10:00:00", "Note", "Agency / system", "Not specified", "Job completed")]
        d, chat = self.run_script([
            Turn(calls=[call("close_case", 1, completion_refs=["event-004"], invoice_status="no_charge", keys_status="not_applicable", reason="done")]),
            Turn(calls=[submit("WAIT")]),
        ], events=events)
        self.assertEqual(json.loads(chat.seen[1][-1]["results"][0]["content"])["code"], "no_confirmation")

    def test_instructing_a_provider_needs_approval_after_the_quote(self):
        instruct = dict(to="provider", purpose="instruct_provider", priority="P3", evidence_refs=["event-005"],
                        body="Please go ahead with the dishwasher repair as quoted. Northbridge Lettings")
        before = [("2026-01-01 09:00:00", "Note", "Agency / system", "Not specified", "Request: dishwasher leaks."),
                  ("2026-01-01 09:10:00", "Email", "Landlord", "Agency", "Yes please send someone."),
                  ("2026-01-02 09:00:00", "Email", "Agency / system", "Contractor", "Please quote."),
                  ("2026-01-03 09:00:00", "Email", "Contractor", "Agency", "Quote is £180 plus VAT.")]
        d, chat = self.run_script([Turn(calls=[call("send_message", 1, **instruct)]), Turn(calls=[submit("WAIT")])], events=before)
        self.assertEqual(json.loads(chat.seen[1][-1]["results"][0]["content"])["code"], "no_landlord_approval")
        after = before + [("2026-01-03 12:00:00", "Email", "Landlord", "Agency", "Happy to proceed at that price.")]
        d, _ = self.run_script([Turn(calls=[call("send_message", 1, **instruct)]), Turn(calls=[submit("INSTRUCT_PROVIDER")])], events=after)
        self.assertEqual(d.action, "INSTRUCT_PROVIDER")
        self.assertEqual(d.actions[0]["state"], "committed")

    def test_index_summary_is_hidden_from_read_case_file(self):
        d, chat = self.run_script([Turn(calls=[call("read_case_file", 1, path="index.md")]), Turn(calls=[submit("WAIT")])])
        text = json.loads(chat.seen[1][-1]["results"][0]["content"])["text"]
        self.assertNotIn("OUTCOME-SECRET", text)
        self.assertNotIn("OVERVIEW-SECRET", text)
        self.assertNotIn("**Status:**", text)
        self.assertIn("Initial request", text)

    def test_explicit_question_is_answered_and_images_go_only_to_claude(self):
        folder = make_case(self.root, "q1", WAITING_LANDLORD)
        idx = (folder / "index.md").read_text(encoding="utf-8")
        (folder / "index.md").write_text(idx.replace(
            "## Attachments", "## Question\n\nWhich contractor should attend?\n\n## Attachments"), encoding="utf-8")
        (folder / "attachments").mkdir()
        (folder / "attachments" / "photo.png").write_bytes(b"\x89PNG\r\n")
        (folder / "attachments" / "quote.pdf").write_bytes(b"%PDF-1.1\n")
        case = load_case(folder)
        chat = ScriptedChat([Turn(calls=[submit("WAIT", answer="Send the usual gardener.")])])
        chat.name = "anthropic"
        d = run_loop(case, chat, dataclasses.replace(CFG, as_of="now"), NOW, folder)
        opening = chat.seen[0][0]
        self.assertIn("Which contractor should attend?", opening["text"])
        self.assertIn("answer field", opening["text"])
        self.assertEqual(opening["images"][0]["name"], "photo.png")
        self.assertEqual(opening["documents"][0]["name"], "quote.pdf")
        self.assertIn("quote.pdf", opening["text"])
        self.assertIn("untrusted case data", opening["text"])
        self.assertEqual(d.answer, "Send the usual gardener.")
        self.assertEqual(d.details["property"]["address"], "Flat 1, 2 Test Road")
        rendered = answer_md(d.to_dict())
        self.assertLess(rendered.find("## Answer"), rendered.find("**Decision:**"))
        self.assertIn("Send the usual gardener.", rendered)
        plain = ScriptedChat([Turn(calls=[submit("WAIT")])])
        run_loop(case, plain, dataclasses.replace(CFG, as_of="now"), NOW, folder)
        self.assertNotIn("images", plain.seen[0][0])
        self.assertNotIn("documents", plain.seen[0][0])

    def test_report_renders_actions_and_trace(self):
        d, _ = self.run_script([Turn(calls=[call("send_message", 1, **CHASE)]), Turn(calls=[submit("CHASE_LANDLORD")])], now=LATER)
        answer, reasoning = answer_md(d.to_dict()), reasoning_md(d.to_dict())
        self.assertIn("Actions taken", answer)
        self.assertIn("COMMITTED", answer)
        self.assertIn("Tool trace", reasoning)

    def test_as_of_last_event_judges_waits_at_the_snapshot(self):
        case, folder = self.case(WAITING_LANDLORD)
        chat = ScriptedChat([Turn(calls=[call("send_message", 1, **CHASE)]), Turn(calls=[submit("WAIT", 2)])])
        d = run_loop(case, chat, CFG, LATER, folder)
        self.assertEqual(d.blocked[0]["code"], "too_early")


class LoopRunnerTests(unittest.TestCase):
    def test_runner_runs_chat_backends_in_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_case(root / "in", "001", WAITING_LANDLORD)
            make_case(root / "in", "002", WAITING_LANDLORD)
            summary = run_all(root / "in", root / "out", Config(case_timeout_s=30), backend="tests.loop_backends:WaitChat")
            self.assertTrue(summary["reconciled"])
            self.assertEqual(summary["by_action"], {"WAIT": 2})
            data = json.loads((root / "out" / "001" / "decision.json").read_text())
            self.assertEqual(data["actions"][0]["kind"], "followup")

            summary = run_all(root / "in", root / "out2", Config(case_timeout_s=30, loop_max_steps=3),
                              backend="tests.loop_backends:SilentChat")
            self.assertEqual(summary["by_action"], {"ESCALATE": 2})


    def test_replay_cut_hides_files_and_uses_the_replay_clock(self):
        from agent.runner import run_isolated
        with tempfile.TemporaryDirectory() as tmp:
            folder = make_case(Path(tmp), "001", WAITING_LANDLORD + [
                ("2026-01-05 09:00:00", "Email", "Landlord", "Agency", "FUTURE-SECRET yes go ahead")])
            kind, d = run_isolated(folder, Config(case_timeout_s=30), "tests.loop_backends:LeakProbeChat",
                                   "2026-01-03T09:00:00+00:00", 30, cut=3)
            self.assertEqual(kind, "ok")
            self.assertEqual(d["trace"][0]["result"]["status"], "error")
            self.assertNotIn("FUTURE-SECRET", json.dumps(d))
            self.assertTrue(d["as_of"].startswith("2026-01-03T09:00"))


class WaitParsingTests(unittest.TestCase):
    def test_hold_wording_variants(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i, (text, party) in enumerate([("Awaiting TT response", "tenant"), ("await T reply", "tenant"),
                                               ("Reason: Waiting for contractor response", "provider"),
                                               ("Awaiting landlord response", "landlord")]):
                events = WAITING_LANDLORD[:2] + [("2026-01-01 09:06:00", "Hold", "Agency / system", "Not specified", text)]
                case = load_case(make_case(Path(tmp), "w%d" % i, events))
                self.assertEqual(case.waiting().party, party, text)


if __name__ == "__main__":
    unittest.main()
