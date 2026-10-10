import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agent.config import Config
from agent.reality import choose_stt, discover, number_cases, run_reality
from tests.helpers import WAITING_LANDLORD, make_case

PM = "Property Management"


def quiet(_msg):
    pass


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "HackatonChallendges"

    def tearDown(self):
        self.tmp.cleanup()

    def names(self, cases):
        return sorted(str(c.relative_to(self.root)) for c in cases)

    def test_track_folders_default_to_property_management(self):
        for track in (PM, "Insurance Claims Processing"):
            make_case(self.root / track, "001", WAITING_LANDLORD)
            make_case(self.root / track, "002", WAITING_LANDLORD)
        (self.root / "README.md").write_text("# drop\n")
        cases, info = discover(self.root)
        self.assertEqual(self.names(cases), ["Property Management/001", "Property Management/002"])
        self.assertEqual(info["track"], PM)
        self.assertEqual(info["tracks_found"], ["Insurance Claims Processing", PM])

    def test_track_override_in_any_spelling_and_all(self):
        make_case(self.root / PM, "001", WAITING_LANDLORD)
        make_case(self.root / "Insurance Claims Processing", "007", WAITING_LANDLORD)
        cases, info = discover(self.root, "insurance-claims")
        self.assertEqual(self.names(cases), ["Insurance Claims Processing/007"])
        cases, info = discover(self.root, "all")
        self.assertEqual(len(cases), 2)
        self.assertEqual(info["track"], "all")
        with self.assertRaises(ValueError):
            discover(self.root, "Space Travel")

    def test_flat_drop_and_deep_nesting(self):
        make_case(self.root / "batch" / "a" / "deep", "case-x", WAITING_LANDLORD)
        make_case(self.root, "12", WAITING_LANDLORD)
        cases, info = discover(self.root, PM)  # no track folders: the track argument does not filter
        self.assertEqual(self.names(cases), ["12", "batch/a/deep/case-x"])
        self.assertIsNone(info["track"])

    def test_folder_of_text_files_is_a_case_but_its_documents_are_not(self):
        odd = self.root / "odd-case"
        (odd / "attachments").mkdir(parents=True)
        (odd / "thread.md").write_text("# Leak\n\nTenant: the sink leaks.\n")
        (odd / "attachments" / "note.txt").write_text("plumber note")
        cases, _ = discover(self.root)
        self.assertEqual(self.names(cases), ["odd-case"])

    def test_case_folder_passed_directly(self):
        folder = make_case(self.root, "005", WAITING_LANDLORD)
        cases, _ = discover(folder)
        self.assertEqual(cases, [folder])

    def test_output_folder_inside_the_drop_is_skipped(self):
        make_case(self.root, "001", WAITING_LANDLORD)
        make_case(self.root / "out", "001", WAITING_LANDLORD)
        cases, _ = discover(self.root, skip=self.root / "out")
        self.assertEqual(self.names(cases), ["001"])


class NumberingTests(unittest.TestCase):
    def test_numbers_unpadded_names_sequential_and_clashes_moved(self):
        root = Path("/drop")
        cases = [root / "PM" / "001", root / "PM" / "010", root / "x" / "Case 3", root / "alpha", root / "beta",
                 root / "other" / "001"]
        got = {str(p.relative_to(root)): n for n, p in number_cases(cases, root)}
        self.assertEqual(got["PM/001"], "1")
        self.assertEqual(got["PM/010"], "10")
        self.assertEqual(got["x/Case 3"], "3")
        self.assertEqual(len(set(got.values())), len(got))
        self.assertEqual(sorted({got["alpha"], got["beta"], got["other/001"]}), ["2", "4", "5"])


class SttChoiceTests(unittest.TestCase):
    def test_audio_needs_a_key_before_paying_for_transcripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = Path(tmp) / "001"
            case.mkdir()
            (case / "voicemail.mp3").write_bytes(b"\x00")
            cfg = Config()
            with mock.patch.dict(os.environ, {"ELEVENLABS_API_KEY": "", "LETTABLE_STT": ""}):
                self.assertEqual(choose_stt(cfg, [case], None)[0], "off")
            with mock.patch.dict(os.environ, {"ELEVENLABS_API_KEY": "k", "LETTABLE_STT": ""}):
                self.assertEqual(choose_stt(cfg, [case], None)[0], "elevenlabs")
                self.assertEqual(choose_stt(cfg, [case], "off")[0], "off")
            (case / "voicemail.mp3").unlink()
            with mock.patch.dict(os.environ, {"ELEVENLABS_API_KEY": "k", "LETTABLE_STT": ""}):
                self.assertEqual(choose_stt(cfg, [case], None)[0], "off")


class RunRealityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "HackatonChallendges"
        self.out = Path(self.tmp.name) / "ANSWERS"

    def tearDown(self):
        self.tmp.cleanup()

    def test_exports_numbered_answers_manifest_and_index(self):
        make_case(self.root / PM, "001", WAITING_LANDLORD)
        make_case(self.root / PM, "017", WAITING_LANDLORD)
        make_case(self.root / "Delivery & Logistics", "002", WAITING_LANDLORD)
        summary = run_reality(self.root, self.out, Config(case_timeout_s=20), "fake",
                              now_iso="2026-01-10T09:00:00+00:00", log=quiet)
        self.assertTrue(summary["reconciled"])
        self.assertEqual(summary["total"], 2)
        for n in ("1", "17"):
            for name in ("ANSWER.md", "REASONING.md", "decision.json"):
                self.assertTrue((self.out / n / name).is_file(), "%s/%s" % (n, name))
        self.assertFalse((self.out / "2").exists())
        manifest = json.loads((self.out / "manifest.json").read_text())
        self.assertEqual([(c["n"], c["source"]) for c in manifest["cases"]],
                         [("1", "Property Management/001"), ("17", "Property Management/017")])
        index = (self.out / "README.md").read_text()
        self.assertIn("[ANSWER.md](17/ANSWER.md)", index)
        self.assertIn("Dishwasher repair", index)
        for name in ("summary.json", "trace.jsonl"):
            self.assertTrue((self.out / name).is_file())
        self.assertEqual(json.loads((self.out / "1" / "decision.json").read_text())["case_id"], "1")

    def test_fallbacks_get_another_pass(self):
        make_case(self.root, "001", WAITING_LANDLORD)
        make_case(self.root, "002", WAITING_LANDLORD, title="FLAKY boiler")
        with tempfile.TemporaryDirectory() as flaky, mock.patch.dict(os.environ, {"LETTABLE_FLAKY_DIR": flaky}):
            summary = run_reality(self.root, self.out, Config(case_timeout_s=20), "tests.chaos_backend:FlakyBackend",
                                  now_iso="2026-01-10T09:00:00+00:00", log=quiet)
        self.assertEqual(len(summary["passes"]), 2)
        self.assertEqual(summary["passes"][0]["fallbacks"], {"error": 1})
        self.assertEqual(summary["passes"][1]["skipped"], 1)
        self.assertEqual(summary["fallbacks"], {})
        self.assertEqual(json.loads((self.out / "2" / "decision.json").read_text())["source"], "model")

    def test_no_resume_pass_when_the_deadline_is_too_close(self):
        make_case(self.root, "001", WAITING_LANDLORD, title="FLAKY boiler")
        cfg = Config(case_timeout_s=20, run_deadline_s=30, reality_min_resume_s=60)
        with tempfile.TemporaryDirectory() as flaky, mock.patch.dict(os.environ, {"LETTABLE_FLAKY_DIR": flaky}):
            summary = run_reality(self.root, self.out, cfg, "tests.chaos_backend:FlakyBackend",
                                  now_iso="2026-01-10T09:00:00+00:00", log=quiet)
        self.assertEqual(len(summary["passes"]), 1)
        self.assertEqual(summary["fallbacks"], {"error": 1})
        self.assertTrue(summary["reconciled"])
        self.assertIn("fallback: error", (self.out / "README.md").read_text())

    def test_empty_drop_is_an_error(self):
        self.root.mkdir(parents=True)
        with self.assertRaises(ValueError):
            run_reality(self.root, self.out, Config(), "fake", log=quiet)


if __name__ == "__main__":
    unittest.main()
