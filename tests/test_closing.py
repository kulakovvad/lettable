"""Finished jobs should close: completion wording, side issues, keys and invoice hints."""

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent import evidence, gates
from agent.config import Config
from agent.schema import Proposal
from agent.timeline import Event, load_case
from agent.tools import Toolbox
from tests.helpers import make_case

NOW = datetime(2026, 1, 8, 12, 0, tzinfo=timezone.utc)
CFG = Config()
DONE = [
    ("2026-01-01 09:00:00", "Email", "Tenant", "Agency", "The bath drain is blocked."),
    ("2026-01-02 09:00:00", "Email", "Northbridge Lettings", "Contractor", "Please attend the blocked bath drain."),
    ("2026-01-05 10:00:00", "Email", "Contractor", "Agency", "Job completed. Invoice sent to the landlord."),
]


def said(sender, body):
    return Event(index=1, ts=None, channel="Email", sender=sender, recipient="Agency", body=body)


def close_args(**extra):
    args = dict(completion_refs=["event-003"], invoice_status="sent_to_landlord", invoice_refs=["event-003"],
                keys_status="not_applicable", key_refs=[], reason="Provider confirmed completion.")
    args.update(extra)
    return args


class CompletionWordingTests(unittest.TestCase):
    def test_plain_completion_phrases_count(self):
        for body in ("Thank you, a plunger could do it. Its now clear, thanks for the help.",
                     "The plunger worked, thanks.", "This one is done now.", "The shower is working again.",
                     "All sorted, thanks.", "The leak has been sorted."):
            self.assertTrue(evidence.reports_completion(said("Tenant", body)), body)

    def test_asked_hedged_or_unrelated_mentions_do_not_count(self):
        for body in ("The landlord inquires about the status and whether it has been resolved.",
                     "It is clear that the boiler is broken.", "It should be fixed by Friday.",
                     "Please let us know if it is now clear.", "It is not working again yet."):
            self.assertFalse(evidence.reports_completion(said("Tenant", body)), body)


class CloseCaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.n = 0

    def tearDown(self):
        self.tmp.cleanup()

    def case(self, extra=(), base=DONE):
        self.n += 1
        return load_case(make_case(self.root, "c%d" % self.n, list(base) + list(extra),
                                   title="Blocked Bath Drain Request", request="The bath drain is blocked."))

    def close(self, case, **extra):
        return Toolbox(case, CFG, NOW).call("close_case", close_args(**extra))

    def test_unanswered_side_issue_blocks_close_without_escalating(self):
        case = self.case([("2026-01-06 10:00:00", "Email", "Tenant", "Agency",
                           "Thanks. Do I need to register for a parking space in the garage?")])
        self.assertIsNone(gates.confirmed_completion(case))
        result = self.close(case)
        self.assertEqual(result["code"], "side_unanswered")
        self.assertIn("unrelated_issues", result["hint"])
        self.assertIn("not a reason to escalate", result["hint"])
        d = gates.apply(case, Proposal.from_dict(dict(action="CLOSE", reason="r", confidence=0.9)), CFG, NOW)
        self.assertEqual(d.action, "WAIT")
        self.assertEqual(d.proposed_action, "CLOSE")

    def test_tenant_message_about_the_job_still_reopens(self):
        for text in ("Thanks, but the bath is draining slowly again.", "When will the drain be looked at?",
                     "Can someone call me"):
            case = self.case([("2026-01-06 10:00:00", "Email", "Tenant", "Agency", text)])
            self.assertIsNone(gates.confirmed_completion(case), text)
            self.assertEqual(self.close(case)["code"], "possibly_reopened", text)

    def test_conjunctions_and_updates_are_not_problems(self):
        case = self.case([("2026-01-06 10:00:00", "Email", "Tenant", "Agency",
                           "Thanks, all fixed. I will update you when I am back home.")])
        self.assertIsNotNone(gates.confirmed_completion(case))

    def test_keys_not_applicable_when_held_keys_came_back(self):
        case = self.case([("2026-01-04 10:00:00", "Email", "Contractor", "Agency", "We collected the keys from the office."),
                          ("2026-01-05 12:00:00", "Email", "Contractor", "Agency", "Keys have been returned to the office.")])
        self.assertEqual(self.close(case, keys_status="not_applicable")["status"], "staged")

    def test_keys_still_out_block_with_a_routine_ask(self):
        case = self.case([("2026-01-04 10:00:00", "Email", "Contractor", "Agency", "We collected the keys from the office."),
                          DONE[2]], base=DONE[:2])
        result = self.close(case, completion_refs=["event-004"], invoice_refs=["event-004"], keys_status="unknown")
        self.assertEqual(result["code"], "keys_unknown")
        self.assertIn("ASK_PROVIDER", result["hint"])

    def test_unknown_keys_with_no_key_ever_held_closes(self):
        box = Toolbox(self.case(), CFG, NOW)
        self.assertEqual(box.call("close_case", close_args(keys_status="unknown"))["status"], "staged")
        self.assertEqual(box.staged[-1]["keys_status"], "not_applicable")

    def test_unknown_invoice_points_to_asking_the_provider(self):
        result = self.close(self.case(), invoice_status="unknown")
        self.assertEqual(result["code"], "invoice_unknown")
        self.assertIn("ASK_PROVIDER", result["hint"])
        self.assertIn("not a reason to escalate", result["hint"])


if __name__ == "__main__":
    unittest.main()
