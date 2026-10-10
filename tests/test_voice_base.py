import unittest

from agent.config import Config
from agent.voice import CallRequest, DryRunDialer, make_dialer


class VoiceBaseTests(unittest.TestCase):
    def test_dry_run_dials_nothing_and_is_repeatable(self):
        req = CallRequest("c1", "provider", "+447000000000", "Ask for a visit date.", {"address": "Flat 1"}, "abc123")
        d = DryRunDialer()
        a, b = d.place(req), d.place(req)
        self.assertEqual((a.status, a.conversation_id), ("dry_run", "dryrun-abc123"))
        self.assertEqual(a, b)
        self.assertEqual(d.fetch(a.conversation_id).status, "done")

    def test_default_backend_is_dry_run_and_unknown_is_rejected(self):
        self.assertIsInstance(make_dialer(Config().call_backend, Config()), DryRunDialer)
        with self.assertRaises(ValueError):
            make_dialer("carrier-pigeon", Config())

    def test_config_round_trips_tuples(self):
        self.assertEqual(Config.from_dict(Config().to_dict()).call_hours, (8, 21))
        self.assertEqual(Config.from_dict({"call_hours": [9, 18]}).call_hours, (9, 18))


if __name__ == "__main__":
    unittest.main()
