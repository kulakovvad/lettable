import json
import re
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent import details, mismatches
from agent.fallback import fallback_decision
from agent.report import answer_md, write_case
from agent.timeline import load_case
from tests.helpers import make_case

NOW = datetime(2026, 1, 9, tzinfo=timezone.utc)
AG = "Northbridge Lettings"
EVENTS = [("2026-01-02 10:00:00", "Email", AG, "Tenant", "Address: Flat 12, 182 Meadow Row\n\nHello Dawson,\n\nYour appointment is booked for Monday 10am."),
          ("2026-01-03 10:00:00", "Email", "Contractor", AG, "Quote GBP 100 + VAT.")]


def decision_dict(events=EVENTS, consistency=None):
    with tempfile.TemporaryDirectory() as tmp:
        case = load_case(make_case(Path(tmp), "c1", events))
    d = fallback_decision("c1", "timeout", "x", NOW, case).to_dict()
    d["consistency"] = consistency
    return d


def card_block(md):
    return json.loads(re.search(r"### Case card \(machine-readable\)\n\n```json\n(.*?)\n```", md, re.S).group(1))


class RenderingTests(unittest.TestCase):
    def test_details_come_after_the_heading_and_the_json_block_is_exactly_the_stored_card(self):
        d = decision_dict()
        md = answer_md(d)
        self.assertLess(md.index("## Details"), md.index("## Decision"))
        self.assertEqual(card_block(md), d["details"])
        self.assertEqual(d["details"]["schema"], "case-card/1")
        for heading in ("### Case", "### Property", "### Tenant", "### Agency", "### Money", "### Appointments", "### Timeline", "### Decision"):
            self.assertIn(heading, md)

    def test_groups_with_nothing_in_them_are_left_out(self):
        md = answer_md(decision_dict())
        for heading in ("### Landlord", "### Provider", "### Attachments", "### Calls", "### Input warnings"):
            self.assertNotIn(heading, md)
        self.assertNotIn("None", md.split("### Case card")[0])

    def test_mismatches_are_listed_with_refs_and_the_checked_line(self):
        md = answer_md(decision_dict())
        section = md.split("## Inconsistencies and mismatches")[1]
        self.assertIn("**address** (flag)", section)
        self.assertIn("[event-001]", section)
        self.assertIn("Checked: addresses, invoice amounts", section)
        self.assertIn("document consistency check off", section)
        self.assertLess(md.index("What was blocked or failed"), md.index("## Inconsistencies and mismatches"))

    def test_none_found_says_what_was_checked(self):
        d = decision_dict([("2026-01-02 10:00:00", "Email", AG, "Tenant", "Hello")])
        self.assertEqual(d["mismatches"], [])
        section = answer_md(d).split("## Inconsistencies and mismatches")[1]
        self.assertTrue(section.lstrip().startswith("None found."))
        self.assertIn("Checked:", section)

    def test_the_consistency_check_state_is_shown(self):
        on = answer_md(decision_dict(consistency={"status": "ok", "checks": []}))
        broken = answer_md(decision_dict(consistency={"status": "unavailable"}))
        self.assertIn("document consistency check on", on)
        self.assertIn("document consistency check unavailable", broken)

    def test_an_old_decision_without_the_new_fields_still_renders(self):
        d = decision_dict()
        for key in ("details", "mismatches"):
            d.pop(key)
        md = answer_md(d)
        self.assertNotIn("## Details", md)
        self.assertNotIn("## Inconsistencies", md)
        self.assertIn("## Decision", md)

    def test_odd_shapes_do_not_crash_the_render(self):
        d = decision_dict()
        for details_value in ("text", {"schema": "case-card/1"}, {"schema": "other"}, {"schema": "case-card/1", "money": "x", "calls": [1, None]}, None):
            d["details"] = details_value
            answer_md(d)
        for value in ("x", [1, None, {"summary": "no kind"}], None):
            d["mismatches"] = value
            answer_md(d)

    def test_markdown_structure_stays_valid(self):
        md = answer_md(decision_dict())
        self.assertEqual(md.count("```"), 2)  # one fenced block, opened and closed
        for line in md.splitlines():
            self.assertFalse(line.startswith("##") and not re.match(r"#{1,3} \S", line), line)

    def test_write_case_stores_the_card_in_decision_json_and_answer_md(self):
        d = decision_dict()
        with tempfile.TemporaryDirectory() as tmp:
            write_case(Path(tmp), d)
            stored = json.loads((Path(tmp) / "c1" / "decision.json").read_text())
            md = (Path(tmp) / "c1" / "ANSWER.md").read_text()
        self.assertEqual(stored["details"], card_block(md))
        self.assertEqual(stored["mismatches"][0]["kind"], "address")


class LoopTests(unittest.TestCase):
    def run_loop_on(self, events=EVENTS):
        from agent.chat import ScriptedChat, Turn
        from agent.config import Config
        from agent.loop import run_loop
        from tests.loop_backends import call, submit
        with tempfile.TemporaryDirectory() as tmp:
            folder = make_case(Path(tmp), "c1", events)
            chat = ScriptedChat([Turn(calls=[call("schedule_followup", 1, after_hours=24, waiting_on="provider", reason="wait")]),
                                 Turn(calls=[submit("WAIT")])])
            return run_loop(load_case(folder), chat, Config(loop_max_steps=4, as_of="now"), NOW, folder)

    def test_a_real_loop_decision_carries_the_card_and_the_mismatches(self):
        d = self.run_loop_on()
        self.assertEqual(d.details["schema"], "case-card/1")
        self.assertEqual(d.details["decision"]["action"], "WAIT")
        self.assertEqual([m["kind"] for m in d.mismatches], ["address"])
        md = answer_md(d.to_dict())
        self.assertEqual(card_block(md), d.to_dict()["details"])

    def test_the_loop_decision_survives_a_failure_in_the_extras(self):
        originals = (details.build, mismatches.find)
        details.build = lambda case, decision: 1 / 0
        try:
            d = self.run_loop_on()
        finally:
            details.build, mismatches.find = originals
        self.assertEqual(d.action, "WAIT")
        self.assertEqual((d.details, d.mismatches), ({}, []))
        self.assertTrue([w for w in d.warnings if "not recorded" in w])


class FailureTests(unittest.TestCase):
    def test_a_decision_is_still_written_when_the_findings_code_raises(self):
        from agent import fallback
        originals = (details.build, mismatches.find)
        details.build = lambda case, decision: 1 / 0
        mismatches.find = lambda case, report=None: 1 / 0
        try:
            with tempfile.TemporaryDirectory() as tmp:
                case = load_case(make_case(Path(tmp), "c1", EVENTS))
                d = fallback.fallback_decision("c1", "timeout", "x", NOW, case).to_dict()
        finally:
            details.build, mismatches.find = originals
        self.assertEqual((d["action"], d["details"], d["mismatches"]), ("ESCALATE", {}, []))
        self.assertIn("## Decision", answer_md(d))
        self.assertNotIn("## Details", answer_md(d))


if __name__ == "__main__":
    unittest.main()
