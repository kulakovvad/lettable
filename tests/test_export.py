import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from agent import __main__ as cli
from agent.export import ExportError, export


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_run(root: Path, ids, with_logs=True):
    """A finished run folder like `agent run` writes it."""
    out = root / "out"
    for cid in ids:
        d = out / cid
        d.mkdir(parents=True)
        (d / "ANSWER.md").write_bytes(("# Case %s\n\nCafé — decision\r\n" % cid).encode("utf-8"))
        (d / "REASONING.md").write_bytes(("reasoning %s\n" % cid).encode("utf-8"))
        (d / "decision.json").write_bytes(json.dumps({"case_id": cid, "action": "WAIT"}).encode("utf-8"))
    if with_logs:
        (out / "summary.json").write_text('{"total": %d}\n' % len(ids))
        (out / "trace.jsonl").write_text('{"case_id": "x"}\n')
    return out


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.dest = self.root / "ANSWERS"

    def tearDown(self):
        self.tmp.cleanup()

    def test_files_are_copied_byte_for_byte(self):
        out = make_run(self.root, ["001", "002"])
        result = export(out, self.dest)
        self.assertEqual(result["exported"], 2)
        for cid, n in (("001", "1"), ("002", "2")):
            for name in ("ANSWER.md", "REASONING.md", "decision.json"):
                self.assertEqual(sha(out / cid / name), sha(self.dest / n / name), "%s/%s" % (n, name))
        # a CRLF and non-ASCII text survived untouched
        self.assertIn(b"\r\n", (self.dest / "1" / "ANSWER.md").read_bytes())

    def test_numeric_ids_keep_their_number_and_others_follow_in_order(self):
        out = make_run(self.root, ["007", "alpha", "012", "beta"])
        export(out, self.dest)
        index = json.loads((self.dest / "index.json").read_text())
        self.assertEqual(index, {"7": "007", "12": "012", "13": "alpha", "14": "beta"})

    def test_only_non_numeric_ids_are_numbered_from_one(self):
        out = make_run(self.root, ["b", "a"])
        export(out, self.dest)
        self.assertEqual(json.loads((self.dest / "index.json").read_text()), {"1": "a", "2": "b"})

    def test_run_logs_are_copied_with_a_marker(self):
        out = make_run(self.root, ["001"])
        export(out, self.dest)
        self.assertEqual(sha(out / "summary.json"), sha(self.dest / "_run" / "summary.json"))
        self.assertEqual(sha(out / "trace.jsonl"), sha(self.dest / "_run" / "trace.jsonl"))
        marker = json.loads((self.dest / "_run" / "export.json").read_text())
        self.assertEqual(marker["out_dir"], str(out.resolve()))

    def test_missing_logs_are_not_an_error(self):
        out = make_run(self.root, ["001"], with_logs=False)
        result = export(out, self.dest)
        self.assertEqual(result["run_files"], [])
        self.assertFalse((self.dest / "_run" / "summary.json").exists())

    def test_cases_without_a_decision_are_listed_and_skipped(self):
        out = make_run(self.root, ["001"])
        (out / "002").mkdir()
        (out / "002" / "ANSWER.md").write_text("half written")
        result = export(out, self.dest)
        self.assertEqual((result["exported"], result["skipped_without_decision"]), (1, ["002"]))
        self.assertFalse((self.dest / "2").exists())

    def test_two_cases_with_the_same_number_are_refused_and_nothing_is_written(self):
        out = make_run(self.root, ["001", "1"])
        with self.assertRaisesRegex(ExportError, "both be ANSWERS/1"):
            export(out, self.dest)
        self.assertFalse(self.dest.exists())

    def test_an_empty_run_is_refused(self):
        out = self.root / "out"
        out.mkdir()
        (out / "summary.json").write_text("{}")
        with self.assertRaisesRegex(ExportError, "no case with a decision.json"):
            export(out, self.dest)
        self.assertFalse(self.dest.exists())
        with self.assertRaises(ExportError):
            export(self.root / "missing", self.dest)

    def test_a_finished_case_missing_a_file_is_refused(self):
        out = make_run(self.root, ["001", "002"])
        (out / "002" / "REASONING.md").unlink()
        with self.assertRaisesRegex(ExportError, "002 lacks REASONING.md.*--skip-incomplete"):
            export(out, self.dest)
        self.assertFalse(self.dest.exists())

    def test_skip_incomplete_exports_the_rest_and_lists_the_bad_case(self):
        out = make_run(self.root, ["001", "002", "003"])
        (out / "002" / "REASONING.md").unlink()
        result = export(out, self.dest, skip_incomplete=True)
        self.assertEqual((result["exported"], result["skipped_incomplete"]), (2, ["002"]))
        self.assertFalse((self.dest / "2").exists())
        self.assertEqual(sorted(json.loads((self.dest / "index.json").read_text())), ["1", "3"])
        (out / "003" / "ANSWER.md").unlink()
        (out / "003" / "ANSWER.md").symlink_to(out / "001" / "ANSWER.md")
        self.assertEqual(export(out, self.dest, force=True, skip_incomplete=True)["skipped_incomplete"], ["002", "003"])

    def test_a_second_export_from_the_same_place_removes_folders_the_new_run_does_not_have(self):
        export(make_run(self.root, ["010", "011", "003"]), self.dest)
        other = self.root / "other"
        other.mkdir()
        result = export(make_run(other, ["003"]), self.dest, force=True)
        self.assertEqual(sorted(p.name for p in self.dest.iterdir() if p.name.isdecimal()), ["3"])
        self.assertEqual(result["stale_folders_not_from_this_export"], [])

    def test_folders_that_this_exporter_did_not_write_are_reported_not_deleted(self):
        (self.dest / "7").mkdir(parents=True)
        (self.dest / "7" / "ANSWER.md").write_text("hand-made")
        result = export(make_run(self.root, ["001"]), self.dest)
        self.assertTrue((self.dest / "7" / "ANSWER.md").is_file())
        self.assertEqual(result["stale_folders_not_from_this_export"], ["7"])

    def test_odd_inputs_are_refused_cleanly(self):
        out = make_run(self.root, ["001"])
        (self.root / "afile").write_text("x")
        with self.assertRaisesRegex(ExportError, "not a folder"):
            export(out, self.root / "afile")
        out2 = self.root / "out2"
        (out2 / "\u00b2").mkdir(parents=True)
        for name in ("ANSWER.md", "REASONING.md", "decision.json"):
            (out2 / "\u00b2" / name).write_text("x")
        self.assertEqual(export(out2, self.root / "ANS2")["index"], {"1": "\u00b2"})  # not a number, so numbered in order

    def test_existing_folders_from_another_run_need_force(self):
        first = make_run(self.root, ["001"])
        export(first, self.dest)
        other = self.root / "other"
        other.mkdir()
        second = make_run(other, ["001"])
        (second / "001" / "ANSWER.md").write_text("different")
        before = sha(self.dest / "1" / "ANSWER.md")
        with self.assertRaisesRegex(ExportError, "use --force"):
            export(second, self.dest)
        self.assertEqual(sha(self.dest / "1" / "ANSWER.md"), before)  # nothing changed
        export(second, self.dest, force=True)
        self.assertEqual((self.dest / "1" / "ANSWER.md").read_text(), "different")

    def test_exporting_the_same_run_again_is_allowed(self):
        out = make_run(self.root, ["001"])
        export(out, self.dest)
        export(out, self.dest)
        self.assertEqual(sha(out / "001" / "decision.json"), sha(self.dest / "1" / "decision.json"))

    def test_no_temp_files_and_no_other_files_are_left(self):
        out = make_run(self.root, ["001"])
        (out / ".env").write_text("SECRET=1")
        (out / "001" / "notes.txt").write_text("not exported")
        export(out, self.dest)
        names = sorted(str(p.relative_to(self.dest)) for p in self.dest.rglob("*") if p.is_file())
        self.assertEqual(names, ["1/ANSWER.md", "1/REASONING.md", "1/decision.json", "_run/export.json",
                                 "_run/summary.json", "_run/trace.jsonl", "index.json"])


class ExportRealRunTests(unittest.TestCase):
    def test_a_real_offline_run_exports_cleanly(self):
        from agent.config import Config
        from agent.runner import run_all
        from tests.helpers import WAITING_LANDLORD, make_case

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "in").mkdir()
            for cid in ("003", "010"):
                make_case(root / "in", cid, WAITING_LANDLORD)
            out = root / "out"
            self.assertTrue(run_all(root / "in", out, Config(case_timeout_s=30), "fake", "2026-01-10T09:00:00+00:00")["reconciled"])
            result = export(out, root / "ANSWERS")
            self.assertEqual(result["index"], {"3": "003", "10": "010"})
            for n, cid in (("3", "003"), ("10", "010")):
                self.assertEqual(sha(out / cid / "ANSWER.md"), sha(root / "ANSWERS" / n / "ANSWER.md"))
            self.assertTrue((root / "ANSWERS" / "_run" / "trace.jsonl").is_file())


class ExportCliTests(unittest.TestCase):
    def test_cli_exports_and_refuses_with_exit_code_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = make_run(root, ["001"])
            dest = root / "A"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(cli.main(["export", str(out), "--to", str(dest)]), 0)
            self.assertEqual(json.loads(buf.getvalue())["exported"], 1)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(cli.main(["export", str(root / "nope"), "--to", str(root / "B")]), 2)
            self.assertIn("export refused", err.getvalue())
            self.assertFalse((root / "B").exists())


if __name__ == "__main__":
    unittest.main()
