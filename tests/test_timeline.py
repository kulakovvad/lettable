import dataclasses
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent.timeline import load_case, parse_history, render_case
from tests.helpers import WAITING_LANDLORD, make_case


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_parses_events_in_order(self):
        case = load_case(make_case(self.root, "001", WAITING_LANDLORD))
        self.assertEqual([e.index for e in case.events], [1, 2, 3])
        self.assertEqual(case.events[1].recipient, "Landlord")
        self.assertEqual(case.title, "Dishwasher repair")
        self.assertEqual(case.request, "Dishwasher leaks.")

    def test_summary_and_outcome_never_loaded(self):
        case = load_case(make_case(self.root, "001", WAITING_LANDLORD))
        blob = repr(dataclasses.asdict(case)) + render_case(case, 10000)
        self.assertNotIn("OVERVIEW-SECRET", blob)
        self.assertNotIn("OUTCOME-SECRET", blob)

    def test_waiting_state_and_reply_clears_it(self):
        case = load_case(make_case(self.root, "001", WAITING_LANDLORD))
        wait = case.waiting()
        self.assertEqual(wait.party, "landlord")
        self.assertEqual(wait.since, datetime(2026, 1, 1, 9, 6, tzinfo=timezone.utc))
        replied = WAITING_LANDLORD + [("2026-01-02 10:00:00", "Email", "Landlord", "Agency", "Approved.")]
        case2 = load_case(make_case(self.root, "002", replied))
        self.assertIsNone(case2.waiting())

    def test_reply_from_a_differently_named_provider_clears_wait(self):
        events = [
            ("2026-01-01 09:00:00", "Update", "Agency / system", "Not specified", "Waiting for Provider (1 day)"),
            ("2026-01-02 09:00:00", "Email", "Maintenance provider", "Agency", "Booked for Friday."),
        ]
        self.assertIsNone(load_case(make_case(self.root, "p1", events)).waiting())

    def test_cut_hides_later_events(self):
        case = load_case(make_case(self.root, "001", WAITING_LANDLORD))
        self.assertEqual(len(case.cut(2).events), 2)
        self.assertIsNone(case.cut(2).waiting())

    def test_cut_drops_attachments_so_later_documents_cannot_leak(self):
        from dataclasses import replace
        from agent.timeline import Attachment
        case = load_case(make_case(self.root, "001", WAITING_LANDLORD))
        case = replace(case, attachments=(Attachment("invoice.pdf", "Total GBP 120, paid"),))
        self.assertEqual(case.cut(2).attachments, ())
        self.assertNotIn("invoice", render_case(case.cut(2), 5000))

    def test_missing_files_do_not_raise(self):
        (self.root / "empty").mkdir()
        case = load_case(self.root / "empty")
        self.assertEqual(case.events, ())
        self.assertTrue(case.warnings)

    def test_unstructured_history_kept_as_one_note(self):
        events, warnings = parse_history("Tenant rang about a smell of gas.")
        self.assertEqual(len(events), 1)
        self.assertTrue(warnings)

    def test_binary_garbage_does_not_raise(self):
        folder = self.root / "bin"
        folder.mkdir()
        (folder / "history.md").write_bytes(b"\xff\xfe\x00garbage" * 100)
        (folder / "index.md").write_bytes(b"\x80\x81")
        case = load_case(folder)
        self.assertEqual(case.case_id, "bin")

    def test_render_keeps_latest_events_when_too_long(self):
        events = [("2026-01-01 09:%02d:00" % i, "Email", "Tenant", "Agency", "message %d " % i + "x" * 200) for i in range(40)]
        case = load_case(make_case(self.root, "long", events))
        text = render_case(case, 3000)
        self.assertLessEqual(len(text), 3200)
        self.assertIn("message 39", text)
        self.assertIn("events omitted", text)


if __name__ == "__main__":
    unittest.main()
