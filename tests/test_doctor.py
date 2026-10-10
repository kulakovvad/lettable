import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from agent.__main__ import main
from agent.config import Config
from agent.doctor import Check, check_keys, check_writable, report, run_checks
from tests.helpers import WAITING_LANDLORD, make_case

SECRET = "sk-ant-very-secret-value"


class DoctorTests(unittest.TestCase):
    def test_missing_key_fails_and_present_key_is_never_printed(self):
        self.assertEqual(check_keys("claude", Config(), {})[0].status, "fail")
        checks = check_keys("claude", Config(), {"ANTHROPIC_API_KEY": SECRET})
        self.assertEqual(checks[0].status, "ok")
        self.assertNotIn(SECRET, report(checks))
        self.assertIn("ANTHROPIC_API_KEY", report(checks))
        self.assertEqual(check_keys("fake", Config(), {})[0].status, "ok")
        self.assertEqual(check_keys("auto", Config(), {"OPENAI_API_KEY": "x"})[0].status, "ok")

    def test_consistency_check_without_jev_key_is_a_warning(self):
        checks = check_keys("claude", Config(consistency_check=True), {"ANTHROPIC_API_KEY": "x"})
        self.assertIn(("warn", "consistency check"), [(c.status, c.name) for c in checks])

    def test_unwritable_output_dir_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            blocker = Path(tmp) / "file"
            blocker.write_text("x")
            self.assertEqual(check_writable(blocker / "ANSWERS").status, "fail")
            self.assertEqual(check_writable(Path(tmp) / "ANSWERS").status, "ok")
            self.assertEqual(list((Path(tmp) / "ANSWERS").iterdir()), [])

    def test_live_call_only_when_asked_and_only_with_a_key(self):
        calls = []

        def fake_live(backend, cfg):
            calls.append(backend)
            return Check("ok", "live model call", "fine")

        with tempfile.TemporaryDirectory() as tmp:
            run_checks("claude", Config(), Path(tmp), env={"ANTHROPIC_API_KEY": "x"}, live=False, live_fn=fake_live)
            self.assertEqual(calls, [])
            checks = run_checks("claude", Config(), Path(tmp), env={}, live=True, live_fn=fake_live)
            self.assertEqual(calls, [])
            self.assertEqual(checks[-1].status, "fail")
            run_checks("claude", Config(), Path(tmp), env={"ANTHROPIC_API_KEY": "x"}, live=True, live_fn=fake_live)
            self.assertEqual(calls, ["claude"])

    def test_cli_exit_code_and_case_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_case(Path(tmp) / "drop" / "Property Management", "001", WAITING_LANDLORD)
            out = io.StringIO()
            with mock.patch("agent.doctor.check_pypdf", return_value=Check("ok", "pypdf", "test")), redirect_stdout(out):
                code = main(["doctor", str(Path(tmp) / "drop"), "--backend", "fake", "--out", str(Path(tmp) / "A")])
            self.assertEqual(code, 0, out.getvalue())
            self.assertIn("1 case(s), track Property Management", out.getvalue())
            out = io.StringIO()
            with mock.patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}), redirect_stdout(out):
                code = main(["doctor", "--backend", "claude", "--out", str(Path(tmp) / "A")])
            self.assertEqual(code, 1)
            self.assertIn("FAIL model key", out.getvalue())


if __name__ == "__main__":
    unittest.main()
