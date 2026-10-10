import json
import tempfile
import time
import unittest
from pathlib import Path

from agent.config import Config
from agent.runner import run_all
from tests.helpers import WAITING_LANDLORD, make_case

CHAOS = "tests.chaos_backend:ChaosBackend"
NOW = "2026-01-10T09:00:00+00:00"


def build(root: Path, ids):
    for cid in ids:
        make_case(root, cid, WAITING_LANDLORD)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.inp = Path(self.tmp.name) / "in"
        self.out = Path(self.tmp.name) / "out"
        self.inp.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def decision(self, cid):
        return json.loads((self.out / cid / "decision.json").read_text())

    def test_one_failure_never_stops_the_batch(self):
        ids = ["ok1", "ok2", "ok3", "crash1", "hang1", "raise1", "junk1", "ok4"]
        build(self.inp, ids)
        (self.inp / "empty1").mkdir()  # no files at all
        cfg = Config(case_timeout_s=4, concurrency=4)
        t0 = time.monotonic()
        summary = run_all(self.inp, self.out, cfg, CHAOS, NOW)
        self.assertLess(time.monotonic() - t0, 30)

        self.assertEqual(summary["total"], 9)
        self.assertEqual(summary["written"], 9)
        self.assertTrue(summary["reconciled"])
        for cid in ids + ["empty1"]:
            for name in ("decision.json", "ANSWER.md", "REASONING.md"):
                self.assertTrue((self.out / cid / name).is_file(), "%s/%s" % (cid, name))

        for cid in ("ok1", "ok2", "ok3", "ok4"):
            d = self.decision(cid)
            self.assertEqual(d["source"], "model")
            self.assertEqual(d["action"], "CHASE_LANDLORD")
        causes = {cid: self.decision(cid)["cause"] for cid in ("crash1", "hang1", "raise1", "junk1")}
        self.assertEqual(causes, {"crash1": "crash", "hang1": "timeout", "raise1": "error", "junk1": "error"})
        for cid in ("crash1", "hang1", "raise1", "junk1"):
            d = self.decision(cid)
            self.assertEqual(d["action"], "ESCALATE")
            self.assertEqual(d["source"], "fallback")
        self.assertEqual(summary["fallbacks"], {"crash": 1, "timeout": 1, "error": 2})
        empty = self.decision("empty1")  # an empty folder is bad input, not a failure
        self.assertEqual(empty["action"], "ESCALATE")
        self.assertTrue(empty["warnings"])

    def test_fallback_keeps_hazard_flag(self):
        events = WAITING_LANDLORD + [("2026-01-02 10:00:00", "SMS", "Tenant", "Agency", "carbon monoxide alarm is going off")]
        make_case(self.inp, "crash-gas", events)
        run_all(self.inp, self.out, Config(case_timeout_s=4), CHAOS, NOW)
        d = self.decision("crash-gas")
        self.assertEqual(d["source"], "fallback")
        self.assertTrue(d["hazard"])
        self.assertIn("urgent", d["reason"])

    def test_run_deadline_gives_remaining_cases_a_fallback(self):
        build(self.inp, ["hang1", "late1", "late2"])
        cfg = Config(case_timeout_s=30, run_deadline_s=2, concurrency=1)
        summary = run_all(self.inp, self.out, cfg, CHAOS, NOW)
        self.assertEqual(summary["written"], 3)
        self.assertTrue(summary["reconciled"])
        self.assertEqual(self.decision("late1")["cause"], "deadline")

    def test_resume_skips_model_decisions_and_redoes_fallbacks(self):
        build(self.inp, ["ok1", "raise1"])
        cfg = Config(case_timeout_s=10)
        run_all(self.inp, self.out, cfg, CHAOS, NOW)
        marker = self.out / "ok1" / "decision.json"
        before = marker.stat().st_mtime_ns
        summary = run_all(self.inp, self.out, cfg, CHAOS, NOW, resume=True)
        self.assertEqual(summary["skipped"], 1)
        self.assertEqual(summary["written"], 1)
        self.assertEqual(marker.stat().st_mtime_ns, before)
        self.assertTrue(summary["reconciled"])

    def test_no_temp_files_left_behind(self):
        build(self.inp, ["ok1", "ok2"])
        run_all(self.inp, self.out, Config(case_timeout_s=10), "fake", NOW)
        leftovers = [p for p in self.out.rglob(".tmp-*")]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
