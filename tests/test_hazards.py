"""Hazard phrases: ignore denials and boilerplate, and still escalate a real report."""

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent import gates
from agent.config import Config
from agent.schema import Proposal
from agent.timeline import load_case
from tests.helpers import WAITING_LANDLORD, make_case

CFG = Config()
NOW = datetime(2026, 1, 8, 12, 0, tzinfo=timezone.utc)


class HazardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.n = 0

    def tearDown(self):
        self.tmp.cleanup()

    def decide(self, sender, body, action="WAIT"):
        self.n += 1
        events = WAITING_LANDLORD + [("2026-01-02 10:00:00", "Email", sender, "Agency", body)]
        case = load_case(make_case(self.root, "h%d" % self.n, events))
        return gates.apply(case, Proposal.from_dict(dict(action=action, reason="r", confidence=0.9, message="Hello")), CFG, NOW)

    def test_negated_hazard_mentions_are_not_open(self):
        for body in ("There is no smell of gas.", "There is no sign of a gas leak.",
                     "The kitchen is not flooding.", "No carbon monoxide was found."):
            d = self.decide("Tenant", body)
            self.assertFalse(d.hazard, body)
            self.assertEqual(d.action, "WAIT", body)

    def test_a_negated_action_around_a_real_hazard_still_escalates(self):
        for body in ("I can't stop the flooding in the kitchen.", "They didn't fix the gas leak."):
            d = self.decide("Tenant", body)
            self.assertTrue(d.hazard, body)
            self.assertEqual(d.action, "ESCALATE", body)

    def test_bare_fire_threat_flood_and_unsafe_words_are_not_hazards(self):
        for body in ("Please fit a fire door and send the fire safety certificate.",
                     "The tenant threatened legal action over the delay.",
                     "This inbox is flooded with emails about the flood risk assessment.",
                     "Let us know if you feel unsafe leaving a review."):
            d = self.decide("Tenant", body)
            self.assertFalse(d.hazard, body)
            self.assertNotEqual(d.action, "ESCALATE", body)

    def test_reported_fire_threat_flood_and_unsafe_still_escalate(self):
        for body in ("The kitchen is on fire.", "He threatened to hurt me.",
                     "The flat is flooding.", "The boiler is unsafe.",
                     "I can smell gas in the kitchen."):
            d = self.decide("Tenant", body)
            self.assertTrue(d.hazard, body)
            self.assertEqual(d.action, "ESCALATE", body)

    def test_agency_advice_and_questions_are_not_hazard_reports(self):
        for body in ("If you smell gas, leave and call the emergency line.",
                     "Can you smell gas in the kitchen?"):
            d = self.decide("Northbridge Lettings", body)
            self.assertFalse(d.hazard, body)
            self.assertEqual(d.action, "WAIT", body)


if __name__ == "__main__":
    unittest.main()
