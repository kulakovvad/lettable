import json
import tempfile
import unittest
from pathlib import Path

from agent.config import Config
from agent.replay import decision_points, label_next, replay
from agent.timeline import Event
from tests.helpers import make_case

ECHO = "tests.echo_backend:EchoBackend"
EVENTS = [
    ("2026-01-01 09:00:00", "Note", "Agency / system", "Not specified", "Request: dishwasher leaks."),
    ("2026-01-01 09:05:00", "Email", "Agency / system", "Landlord", "Can you approve a repair?"),
    ("2026-01-01 09:06:00", "Update", "Agency / system", "Not specified", "Waiting for Landlord (0 days)"),
    ("2026-01-05 10:00:00", "Email", "Agency / system", "Landlord", "Following up on the repair approval."),
    ("2026-01-06 10:00:00", "Email", "Landlord", "Agency", "Approved."),
]


def ev(channel, sender, to, body):
    return Event(1, None, channel, sender, to, body)


class LabelTests(unittest.TestCase):
    def test_labels(self):
        self.assertEqual(label_next(ev("Email", "Agency / system", "Landlord", "Following up")), "CHASE_LANDLORD")
        self.assertEqual(label_next(ev("Email", "Agency / system", "Landlord", "Attached is the quote for approval")), "ROUTE_FOR_APPROVAL")
        self.assertEqual(label_next(ev("Email", "Northbridge Lettings", "Contractor", "Any update?")), "CHASE_PROVIDER")
        self.assertEqual(label_next(ev("SMS", "Agency / system", "Tenant", "Your appointment is scheduled for Friday")), "SEND_REMINDER")
        self.assertEqual(label_next(ev("Email", "Agency / system", "Tenant", "Can you send a photo?")), "ASK_TENANT")
        self.assertEqual(label_next(ev("Hold", "Agency / system", "Not specified", "Put on hold. Reason: Waiting for Landlord")), "WAIT")
        self.assertEqual(label_next(ev("Email", "Landlord", "Agency", "Approved")), "WAIT")
        self.assertEqual(label_next(ev("Note", "Agency / system", "Not specified", "Random note")), "OTHER")

    def test_decision_points_are_spread_and_leave_a_next_event(self):
        self.assertEqual(decision_points(5, 10), [2, 3, 4])
        pts = decision_points(40, 3)
        self.assertEqual(len(pts), 3)
        self.assertTrue(all(2 <= k <= 39 for k in pts))
        self.assertEqual(decision_points(2, 3), [])


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.inp = Path(self.tmp.name) / "in"
        self.out = Path(self.tmp.name) / "out"
        self.inp.mkdir()
        make_case(self.inp, "c1", EVENTS)

    def tearDown(self):
        self.tmp.cleanup()

    def rows(self):
        return [json.loads(x) for x in (self.out / "rows.jsonl").read_text().splitlines()]

    def test_agent_only_sees_events_up_to_the_cut(self):
        replay(self.inp, self.out, Config(case_timeout_s=20), ECHO, points=10)
        rows = self.rows()
        self.assertEqual([r["events_visible"] for r in rows], [2, 3, 4])
        for r in rows:
            self.assertIn("saw %d events" % r["events_visible"], r["reason"])
        # the clock is the time of the next event
        self.assertEqual(rows[0]["now"], "2026-01-01T09:06:00+00:00")

    def test_summary_and_report_written(self):
        s = replay(self.inp, self.out, Config(case_timeout_s=20), "fake", points=10)
        self.assertEqual(s["points"], 3)
        self.assertTrue((self.out / "report.md").is_file())
        self.assertIn("Disagreements", (self.out / "report.md").read_text())
        self.assertEqual(sum(s["results"].values()), 3)

    def test_max_calls_caps_the_run(self):
        s = replay(self.inp, self.out, Config(case_timeout_s=20), "fake", points=10, max_calls=1)
        self.assertEqual(s["points"], 1)


if __name__ == "__main__":
    unittest.main()
