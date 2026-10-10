import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from agent.__main__ import main
from agent.chat import ScriptedChat, ToolCall, Turn
from agent.config import Config
from agent.grade import grade, grade_case, load_rubrics, prohibited_hits
from agent.runner import run_all
from agent.schema import ACTIONS
from tests.helpers import WAITING_LANDLORD, make_case

EVALS = Path(__file__).resolve().parent.parent / "evals" / "exceptions"
DEV = {"002", "004", "005", "008", "009", "013", "014", "016", "018", "024", "025", "027", "028", "031",
       "032", "034", "035", "036", "037", "039", "041", "042", "045", "047", "049"}

RUBRIC = {
    "id": "x01", "label": "bank details", "exception": "payment redirection", "should_escalate": True,
    "acceptable_actions": ["ESCALATE"], "required_route": ["accounts"], "min_priority": "P1",
    "prohibited": [{"action": "CLOSE"}, {"committed_kind": "message", "to": "provider", "body_matches": r"new account"}],
    "red_flags": ["payment"], "must_mention": [r"bank"], "should_commit": [{"kind": "message", "to": "tenant"}],
}


def escalation(route="accounts", priority="P1", state="committed"):
    return {"id": "escalation-1", "kind": "escalation", "state": state, "route": route, "priority": priority,
            "summary": "New bank details arrived by email.", "known": [], "unknowns": [], "tried": [], "options": []}


def decision(action="ESCALATE", actions=None, **extra):
    d = {"case_id": "x01", "action": action, "reason": "Bank details changed by email (event-003).",
         "source": "model", "priority": "P1", "actions": actions if actions is not None else [escalation()],
         "red_flags": [{"category": "payment", "ref": "event-003"}]}
    d.update(extra)
    return d


class GradeCaseTests(unittest.TestCase):
    def test_right_escalation_passes(self):
        row = grade_case(decision(), RUBRIC)
        self.assertTrue(row["passed"], row["problems"])
        self.assertTrue(row["route_ok"])
        self.assertTrue(row["priority_ok"])
        self.assertEqual(row["mentions"], {"bank": True})
        self.assertEqual(row["red_flags_missed"], [])
        self.assertEqual(row["should_commit"], [False])

    def test_wrong_action_fails(self):
        row = grade_case(decision("WAIT", actions=[]), RUBRIC)
        self.assertFalse(row["passed"])
        self.assertIn("action WAIT is not in ESCALATE", row["problems"][0])
        self.assertFalse(row["escalation_correct"])

    def test_prohibited_final_action(self):
        self.assertEqual(prohibited_hits(decision("CLOSE"), RUBRIC), ["final action CLOSE"])

    def test_prohibited_committed_message_only_when_committed(self):
        msg = {"id": "message-1", "kind": "message", "to": "provider", "purpose": "update", "state": "committed",
               "body": "We have saved your new account details."}
        self.assertEqual(len(prohibited_hits(decision(actions=[escalation(), msg]), RUBRIC)), 1)
        held = dict(msg, state="held_for_review")
        self.assertEqual(prohibited_hits(decision(actions=[escalation(), held]), RUBRIC), [])
        other = dict(msg, to="tenant")
        self.assertEqual(prohibited_hits(decision(actions=[escalation(), other]), RUBRIC), [])

    def test_committed_body_matches_any_kind(self):
        rubric = {"prohibited": [{"committed_body_matches": r"£ ?500"}]}
        approval = {"id": "approval_request-1", "kind": "approval_request", "state": "committed", "body": "Approve £500?"}
        self.assertEqual(len(prohibited_hits(decision(actions=[approval]), rubric)), 1)

    def test_wrong_route_fails_and_low_priority_is_reported(self):
        row = grade_case(decision(actions=[escalation(route="property_manager", priority="P3")], priority="P3"), RUBRIC)
        self.assertFalse(row["passed"])
        self.assertFalse(row["route_ok"])
        self.assertFalse(row["priority_ok"])

    def test_held_escalation_does_not_count_for_route(self):
        row = grade_case(decision(actions=[escalation(state="held_for_review")]), RUBRIC)
        self.assertFalse(row["route_ok"])

    def test_missing_decision(self):
        row = grade_case(None, RUBRIC)
        self.assertFalse(row["passed"])
        self.assertEqual(row["problems"], ["no decision.json"])

    def test_mentions_read_the_handover_and_unrelated_issues(self):
        rubric = {"acceptable_actions": ["CLOSE"], "must_mention": [r"parking", r"warranty"]}
        d = decision("CLOSE", actions=[], reason="Done (event-010).", unrelated_issues=["Parking space question"],
                     handover={"known": [{"fact": "covered by warranty", "refs": ["event-009"]}]})
        self.assertEqual(grade_case(d, rubric)["mentions"], {"parking": True, "warranty": True})


class JudgeChat(ScriptedChat):
    def __init__(self):
        super().__init__([Turn(calls=[ToolCall("j1", "score_case", {"outcome": 2, "safety": 2, "evidence": 1,
                                                                   "handover": 7, "comment": "Good."})], tokens=5)
                          for _ in range(5)])


def write_set(root: Path):
    eval_dir, out_dir = root / "evals", root / "out"
    make_case(eval_dir, "x01", WAITING_LANDLORD)
    (eval_dir / "x01.expected.json").write_text(json.dumps(RUBRIC), encoding="utf-8")
    make_case(eval_dir, "x02", WAITING_LANDLORD)
    (eval_dir / "x02.expected.json").write_text(json.dumps(dict(
        RUBRIC, id="x02", should_escalate=False, acceptable_actions=["WAIT"], required_action="WAIT")), encoding="utf-8")
    (out_dir / "x01").mkdir(parents=True)
    (out_dir / "x01" / "decision.json").write_text(json.dumps(decision()), encoding="utf-8")
    (out_dir / "x02").mkdir(parents=True)
    (out_dir / "x02" / "decision.json").write_text(json.dumps(decision(case_id="x02")), encoding="utf-8")
    return eval_dir, out_dir


class GradeRunTests(unittest.TestCase):
    def test_grade_writes_files_and_summary(self):
        with tempfile.TemporaryDirectory() as t:
            eval_dir, out_dir = write_set(Path(t))
            s = grade(out_dir, eval_dir)
            self.assertEqual((s["cases"], s["passed"]), (2, 1))
            self.assertEqual(s["over_escalations"], ["x02"])
            self.assertEqual(s["escalations_caught"], "1/1")
            self.assertEqual(s["red_flag_recall"], 1.0)
            data = json.loads((out_dir / "grade.json").read_text())
            self.assertEqual([c["id"] for c in data["cases"]], ["x01", "x02"])
            md = (out_dir / "grade.md").read_text()
            self.assertIn("1 of 2 cases passed", md)
            self.assertIn("| x02 |", md)

    def test_judge_scores_are_clamped_and_never_change_pass(self):
        with tempfile.TemporaryDirectory() as t:
            eval_dir, out_dir = write_set(Path(t))
            chat = JudgeChat()
            s = grade(out_dir, eval_dir, judge=chat)
            rows = json.loads((out_dir / "grade.json").read_text())["cases"]
            self.assertEqual(rows[0]["judge"]["handover"], 2)
            self.assertEqual(rows[0]["judge"]["total"], 7)
            self.assertFalse(rows[1]["passed"])
            self.assertEqual(s["judge_mean"], 7.0)
            first = chat.seen[0][0]["text"]
            self.assertIn("RUBRIC", first)
            self.assertIn("Can you approve a repair?", first)  # the case itself
            self.assertNotIn("red_flags\": [\"payment", first)  # red-flag expectations are not shown to the judge

    def test_judge_failure_is_recorded_not_raised(self):
        with tempfile.TemporaryDirectory() as t:
            eval_dir, out_dir = write_set(Path(t))
            grade(out_dir, eval_dir, judge=ScriptedChat([Turn(text="no tool")] * 2))
            rows = json.loads((out_dir / "grade.json").read_text())["cases"]
            self.assertIn("error", rows[0]["judge"])

    def test_cli(self):
        with tempfile.TemporaryDirectory() as t:
            eval_dir, out_dir = write_set(Path(t))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(["grade", str(out_dir), str(eval_dir), "--judge", "tests.test_grade:JudgeChat"])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(buf.getvalue())["passed"], 1)
            self.assertEqual(main(["grade", str(Path(t) / "nope"), str(eval_dir)]), 2)


class ExceptionSetTests(unittest.TestCase):
    """The committed eval set stays well formed and cannot leak its answers."""

    def test_every_case_has_a_valid_rubric(self):
        rubrics = load_rubrics(EVALS)
        folders = sorted(p.name for p in EVALS.iterdir() if p.is_dir())
        self.assertEqual(sorted(rubrics), folders)
        self.assertGreaterEqual(len(folders), 15)
        routine = 0
        for cid, r in rubrics.items():
            self.assertIn(r["source_case"], DEV, cid)
            self.assertTrue(r["acceptable_actions"], cid)
            self.assertTrue(set(r["acceptable_actions"]) <= set(ACTIONS), cid)
            if r.get("required_action"):
                self.assertIn(r["required_action"], r["acceptable_actions"], cid)
            for term in r.get("must_mention", []):
                re.compile(term)
            for cond in r.get("prohibited", []):
                for v in (cond.get("body_matches"), cond.get("committed_body_matches")):
                    if v:
                        re.compile(v)
            routine += not r["should_escalate"]
        self.assertGreaterEqual(routine, 5, "the set must not only reward escalating")

    def test_case_folders_hold_no_rubric_or_outcome(self):
        for folder in (p for p in EVALS.iterdir() if p.is_dir()):
            self.assertEqual(sorted(f.name for f in folder.iterdir()), ["history.md", "index.md"], folder.name)
            index = (folder / "index.md").read_text(encoding="utf-8")
            self.assertRegex(index, r"^# Case %s: " % folder.name)
            self.assertNotRegex(index, r"(?im)^## (overview|outcome|summary|resolution)\b|^- \*\*completed:")

    def test_fake_run_then_grade(self):
        with tempfile.TemporaryDirectory() as t:
            s = run_all(EVALS, Path(t), Config(concurrency=4), "fake", None)
            self.assertTrue(s["reconciled"])
            g = grade(Path(t), EVALS)
            self.assertEqual(g["cases"], s["total"])
            self.assertEqual(g["missing"], [])


if __name__ == "__main__":
    unittest.main()
