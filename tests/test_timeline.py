import dataclasses
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent.timeline import case_images, load_case, parse_history, parse_index, redact_index, render_case
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

    def test_question_sections_reach_the_prompt_and_endings_do_not(self):
        folder = make_case(self.root, "001", WAITING_LANDLORD)
        idx = folder / "index.md"
        text = idx.read_text(encoding="utf-8")
        text = text.replace(
            "- **Status:** Completed\n",
            "- **Status:** Completed\n- **Updated:** 2026-02-01\n- **Completed:** 2026-02-02\n- **Created:** 2026-01-01\n",
        )
        text = text.replace(
            "## Attachments",
            "## Question\n\nWhich contractor should attend?\n\n"
            "## Task\n\nBook the visit.\n\n"
            "## Decision point\n\nApprove the quote or wait.\n\n"
            "## Instructions\n\nReply to the tenant today.\n\n"
            "## Summary\n\nSUMMARY-SECRET finished yesterday.\n\n"
            "## Resolution\n\nRESOLUTION-SECRET closed.\n\n"
            "## History\n\n[Read the complete event history](history.md).\n\n"
            "## Context\n\nThe hedge was last cut in March.\n\n"
            "## Attachments",
        )
        idx.write_text(text, encoding="utf-8")
        case = load_case(folder)
        shown = render_case(case, 20000)
        for secret in ("OVERVIEW-SECRET", "OUTCOME-SECRET", "SUMMARY-SECRET", "RESOLUTION-SECRET"):
            self.assertNotIn(secret, shown)
        self.assertNotIn("history.md", shown)
        self.assertNotIn("**Status:**", shown)
        self.assertNotIn("**Updated:**", shown)
        self.assertNotIn("**Completed:**", shown)
        for needed in ("Which contractor should attend?", "Book the visit.", "Approve the quote or wait.",
                       "Reply to the tenant today.", "The hedge was last cut in March.", "**Created:**"):
            self.assertIn(needed, shown)
        self.assertTrue(case.explicit_question)
        self.assertIn("Which contractor", case.index_notes)

    def test_a_question_mark_in_the_request_is_an_explicit_question(self):
        _title, _role, _prop, _request, _names, _notes, explicit = parse_index(
            "# Case 9: Transfer\n\n## Initial request\n\nWas the payment sent?\n")
        self.assertTrue(explicit)

    def test_generic_history_headings(self):
        text = """# Thread

## 2026-03-01 09:00 Email from Tenant

- **From:** Tenant
- **To:** Agency

The boiler is off.

## 2026-03-01 10:15 Call from Provider

Booked Friday.
"""
        events, warnings = parse_history(text)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].channel, "Email")
        self.assertEqual(events[0].sender, "Tenant")
        self.assertEqual(events[0].ts.year, 2026)
        self.assertIn("boiler", events[0].body)
        self.assertEqual(events[1].channel, "Call")
        self.assertTrue(any("generic" in w for w in warnings))

    def test_standard_events_ignore_the_generic_parser(self):
        case = load_case(make_case(self.root, "001", WAITING_LANDLORD))
        self.assertEqual([e.index for e in case.events], [1, 2, 3])
        self.assertFalse(any("generic" in w for w in case.warnings))

    def test_text_attachments_are_preloaded_and_images_are_labelled(self):
        folder = make_case(self.root, "001", WAITING_LANDLORD)
        att = folder / "attachments"
        att.mkdir()
        (att / "note.txt").write_text("plumber attended", encoding="utf-8")
        (att / "rows.csv").write_text("a,b\n1,2\n", encoding="utf-8")
        (att / "photo.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 20)
        case = load_case(folder)
        by_name = {a.name: a.text for a in case.attachments}
        self.assertIn("plumber attended", by_name["note.txt"])
        self.assertIn("a,b", by_name["rows.csv"])
        self.assertIsNone(by_name["photo.png"])
        shown = render_case(case, 20000)
        self.assertIn("note.txt (text): plumber attended", shown)
        self.assertIn("photo.png (image)", shown)
        images = case_images(folder)
        self.assertEqual(images[0]["media_type"], "image/png")
        self.assertTrue(images[0]["data"])
        (att / "huge.jpg").write_bytes(b"\xff" * 200)
        self.assertEqual([i["name"] for i in case_images(folder, max_bytes=100)], ["photo.png"])

    def test_redact_index_strips_status_lines(self):
        raw = "## Case details\n\n- **Status:** Completed\n- **Updated:** yesterday\n- **Completed:** today\n- **Created:** Monday\n\n## Outcome\n\nOUTCOME-SECRET\n"
        shown = redact_index(raw)
        self.assertNotIn("Status", shown)
        self.assertNotIn("Updated", shown)
        self.assertNotIn("OUTCOME-SECRET", shown)
        self.assertIn("Created", shown)

    def test_render_keeps_latest_events_when_too_long(self):
        events = [("2026-01-01 09:%02d:00" % i, "Email", "Tenant", "Agency", "message %d " % i + "x" * 200) for i in range(40)]
        case = load_case(make_case(self.root, "long", events))
        text = render_case(case, 3000)
        self.assertLessEqual(len(text), 3200)
        self.assertIn("message 39", text)
        self.assertIn("events omitted", text)


if __name__ == "__main__":
    unittest.main()
