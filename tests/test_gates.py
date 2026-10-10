import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent import gates
from agent.config import Config
from agent.schema import Proposal
from agent.timeline import load_case
from tests.helpers import WAITING_LANDLORD, make_case

CFG = Config()
SINCE = datetime(2026, 1, 1, 9, 6, tzinfo=timezone.utc)


def prop(action, **kw):
    base = dict(action=action, reason="because", confidence=0.9, message="Hello")
    base.update(kw)
    return Proposal.from_dict(base)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.case = load_case(make_case(self.root, "001", WAITING_LANDLORD))

    def tearDown(self):
        self.tmp.cleanup()

    def test_chase_after_limit_passes(self):
        d = gates.apply(self.case, prop("CHASE_LANDLORD"), CFG, SINCE + timedelta(days=4))
        self.assertEqual(d.action, "CHASE_LANDLORD")
        self.assertEqual(d.gate_notes, ())
        self.assertEqual(d.waiting_on, "landlord")

    def test_chase_too_early_becomes_wait(self):
        d = gates.apply(self.case, prop("CHASE_LANDLORD"), CFG, SINCE + timedelta(days=1))
        self.assertEqual(d.action, "WAIT")
        self.assertEqual(d.proposed_action, "CHASE_LANDLORD")
        self.assertEqual(d.message, "")

    def test_chasing_the_wrong_party_escalates(self):
        d = gates.apply(self.case, prop("CHASE_PROVIDER"), CFG, SINCE + timedelta(days=9))
        self.assertEqual(d.action, "ESCALATE")

    def test_message_required(self):
        d = gates.apply(self.case, prop("CHASE_LANDLORD", message=""), CFG, SINCE + timedelta(days=9))
        self.assertEqual(d.action, "ESCALATE")

    def test_low_confidence_escalates_but_wait_is_allowed(self):
        d = gates.apply(self.case, prop("CHASE_LANDLORD", confidence=0.2), CFG, SINCE + timedelta(days=9))
        self.assertEqual(d.action, "ESCALATE")
        d = gates.apply(self.case, prop("WAIT", confidence=0.2, message=""), CFG, SINCE)
        self.assertEqual(d.action, "WAIT")

    def test_close_needs_a_recorded_completion(self):
        d = gates.apply(self.case, prop("CLOSE", message=""), CFG, SINCE)
        self.assertEqual(d.action, "ESCALATE")
        done = WAITING_LANDLORD + [("2026-01-05 10:00:00", "Email", "Contractor", "Agency", "Job completed, invoice attached.")]
        case = load_case(make_case(self.root, "002", done))
        d = gates.apply(case, prop("CLOSE", message=""), CFG, SINCE)
        self.assertEqual(d.action, "CLOSE")

    def test_negated_completion_does_not_allow_close(self):
        for text in ("The repair is not completed; please send someone.", "It hasn't been completed yet", "Still not all done"):
            events = WAITING_LANDLORD + [("2026-01-05 10:00:00", "SMS", "Tenant", "Agency", text)]
            case = load_case(make_case(self.root, "neg%d" % abs(hash(text) % 1000), events))
            d = gates.apply(case, prop("CLOSE", message=""), CFG, SINCE)
            self.assertEqual(d.action, "ESCALATE", text)

    def test_reopened_job_does_not_allow_close(self):
        events = WAITING_LANDLORD + [
            ("2026-01-05 10:00:00", "Email", "Contractor", "Agency", "Job completed, invoice attached."),
            ("2026-01-06 10:00:00", "SMS", "Tenant", "Agency", "The leak is back, please send someone."),
        ]
        case = load_case(make_case(self.root, "reopen", events))
        d = gates.apply(case, prop("CLOSE", message=""), CFG, SINCE)
        self.assertEqual(d.action, "ESCALATE")

    def _done_then_tenant(self, cid, text):
        events = WAITING_LANDLORD + [
            ("2026-01-05 10:00:00", "Email", "Contractor", "Agency", "Job completed, invoice attached."),
            ("2026-01-06 10:00:00", "SMS", "Tenant", "Agency", text),
        ]
        return load_case(make_case(self.root, cid, events))

    def test_harmless_tenant_thanks_after_completion_still_closes(self):
        for i, text in enumerate(("Thanks, all fine now", "Perfect, thank you!", "All fixed, working now")):
            case = self._done_then_tenant("ok%d" % i, text)
            d = gates.apply(case, prop("CLOSE", message=""), CFG, SINCE)
            self.assertEqual(d.action, "CLOSE", text)

    def test_problem_or_unrecognised_tenant_replies_after_completion_escalate(self):
        for i, text in enumerate((
            "Thanks but it's leaking again",
            "Thank you, it still doesn't flush",
            "Thanks. When will the invoice be sorted?",
            "Can someone call me",
            "Received your email",
            "Thanks " + "x" * 300,
        )):
            case = self._done_then_tenant("bad%d" % i, text)
            d = gates.apply(case, prop("CLOSE", message=""), CFG, SINCE)
            self.assertEqual(d.action, "ESCALATE", text)

    def test_attachment_only_hazard_is_found(self):
        from dataclasses import replace
        from agent.timeline import Attachment
        events = WAITING_LANDLORD + [("2026-01-02 10:00:00", "Email", "Tenant", "Agency", "Please review attached report")]
        case = load_case(make_case(self.root, "att", events))
        case = replace(case, attachments=(Attachment("report.pdf", "There is a gas leak in the flat."),))
        d = gates.apply(case, prop("WAIT", message=""), CFG, SINCE)
        self.assertEqual(d.action, "ESCALATE")
        self.assertTrue(d.hazard)

    def test_old_unresolved_hazard_outside_the_window_still_counts(self):
        filler = [("2026-01-0%d 10:00:00" % (i + 3), "Update", "Agency / system", "Not specified", "note %d" % i) for i in range(6)]
        events = WAITING_LANDLORD + [("2026-01-02 10:00:00", "SMS", "Tenant", "Agency", "I can smell gas")] + filler
        case = load_case(make_case(self.root, "old", events))
        self.assertTrue(gates.apply(case, prop("WAIT", message=""), CFG, SINCE).hazard)

    def test_old_hazard_is_dropped_once_the_job_is_confirmed_done(self):
        filler = [("2026-01-0%d 10:00:00" % (i + 4), "Update", "Agency / system", "Not specified", "note %d" % i) for i in range(6)]
        events = (WAITING_LANDLORD
                  + [("2026-01-02 10:00:00", "SMS", "Tenant", "Agency", "I can smell gas"),
                     ("2026-01-03 10:00:00", "Email", "Contractor", "Agency", "Gas fixed, job completed.")]
                  + filler)
        case = load_case(make_case(self.root, "fixed", events))
        self.assertFalse(gates.apply(case, prop("WAIT", message=""), CFG, SINCE).hazard)

    def test_low_confidence_wait_without_a_pending_party_escalates(self):
        case = load_case(make_case(self.root, "nowait", WAITING_LANDLORD[:2]))
        d = gates.apply(case, prop("WAIT", confidence=0.01, message=""), CFG, SINCE)
        self.assertEqual(d.action, "ESCALATE")

    def test_spend_above_limit_escalates_unless_routed_for_approval(self):
        d = gates.apply(self.case, prop("CLOSE", amount_gbp=900, message=""), CFG, SINCE)
        self.assertEqual(d.action, "ESCALATE")
        d = gates.apply(self.case, prop("ROUTE_FOR_APPROVAL", amount_gbp=900, message=""), CFG, SINCE)
        self.assertEqual(d.action, "ROUTE_FOR_APPROVAL")

    def test_hazard_forces_escalation(self):
        events = WAITING_LANDLORD + [("2026-01-02 10:00:00", "SMS", "Tenant", "Agency", "I can smell gas in the kitchen")]
        case = load_case(make_case(self.root, "003", events))
        d = gates.apply(case, prop("WAIT", message=""), CFG, SINCE)
        self.assertEqual(d.action, "ESCALATE")
        self.assertTrue(d.hazard)

    def test_gates_never_soften_an_escalation(self):
        d = gates.apply(self.case, prop("ESCALATE", message=""), CFG, SINCE)
        self.assertEqual(d.action, "ESCALATE")
        self.assertTrue(d.options)

    def test_malformed_proposals_raise(self):
        bad = [None, {}, {"action": "NUKE", "reason": "x", "confidence": 1},
               {"action": "WAIT", "reason": "", "confidence": 1},
               {"action": "WAIT", "reason": "x", "confidence": 3},
               {"action": "WAIT", "reason": "x", "confidence": "high"},
               {"action": "WAIT", "reason": "x", "confidence": 1, "amount_gbp": -5}]
        for item in bad:
            with self.assertRaises(ValueError, msg=repr(item)):
                Proposal.from_dict(item)


if __name__ == "__main__":
    unittest.main()
