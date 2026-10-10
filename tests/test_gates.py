import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from lettable import gates
from lettable.config import Config
from lettable.schema import Proposal
from lettable.timeline import load_case
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
