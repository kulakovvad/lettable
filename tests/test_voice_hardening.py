"""Limits and safe defaults for the phone agent: call length, ringing, voicemail, callbacks, auto-collect."""

import dataclasses
import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agent.config import Config
from agent.runner import run_all
from agent.voice import CallRequest
from agent.voice_elevenlabs import ElevenLabsDialer
from agent.voice_prompt import (DATA_COLLECTION, FIRST_MESSAGE, MAX_CALL_SECONDS, PLACEHOLDERS, PROMPT, VARIABLES,
                                VOICEMAIL_MESSAGE, dynamic_variables)
from agent.voice_setup import agent_config
from tests.helpers import make_case
from tests.test_calls import PROVIDER
from tests.test_e2e_voice import CHAT, NOW, Network
from tests.test_voice_elevenlabs import ENV, OK, REQ, Resp


def holders(text):
    return set(re.findall(r"\{\{(\w+)\}\}", text))


class AgentConfigTests(unittest.TestCase):
    def test_the_call_has_a_hard_length_limit_and_says_goodbye_when_it_hits_it(self):
        cc = agent_config()["conversation_config"]
        self.assertEqual(cc["conversation"]["max_duration_seconds"], MAX_CALL_SECONDS)
        self.assertLessEqual(MAX_CALL_SECONDS, 300)
        self.assertIn("colleague will follow up", cc["agent"]["max_conversation_duration_message"])

    def test_a_callback_hears_sensible_words_because_every_variable_has_a_default(self):
        placeholders = agent_config()["conversation_config"]["agent"]["dynamic_variables"]["dynamic_variable_placeholders"]
        self.assertEqual(set(placeholders), set(VARIABLES))
        self.assertEqual(set(PLACEHOLDERS), set(VARIABLES))
        said = FIRST_MESSAGE
        for k, v in placeholders.items():
            said = said.replace("{{%s}}" % k, v)
        self.assertNotIn("{{", said)
        self.assertEqual(said, "Hello, this is an automated assistant calling for the letting agency about a maintenance job. "
                               "This call is recorded.")
        self.assertIn("phones you", PROMPT)  # the prompt covers an inbound call

    def test_voicemail_detection_is_on_and_a_machine_hears_no_objective_or_personal_detail(self):
        tool = agent_config()["conversation_config"]["agent"]["prompt"]["built_in_tools"]["voicemail_detection"]
        self.assertEqual(tool["params"]["system_tool_type"], "voicemail_detection")
        self.assertEqual(tool["params"]["voicemail_message"], VOICEMAIL_MESSAGE)
        self.assertEqual(holders(VOICEMAIL_MESSAGE), {"agency_name", "job"})  # nothing else can leak
        self.assertNotRegex(VOICEMAIL_MESSAGE, r"\d")
        self.assertIn("voicemail tool", PROMPT)
        self.assertNotIn("leave a short message with the agency name", PROMPT)

    def test_an_exact_calendar_date_is_extracted_but_a_relative_one_is_never_worked_out(self):
        field = DATA_COLLECTION["confirmed_date_iso"]["description"]
        self.assertIn("YYYY-MM-DD", field)
        self.assertIn("never work a date out", field)
        self.assertIn("confirmed_date", DATA_COLLECTION)  # the spoken form is still kept

    def test_create_and_update_still_send_the_same_configuration(self):
        self.assertEqual(agent_config()["platform_settings"]["data_collection"], DATA_COLLECTION)


class RingingTests(unittest.TestCase):
    def test_the_call_stops_ringing_after_the_configured_time(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {**ENV, "LETTABLE_CALL_LEDGER": str(Path(tmp) / "l.json")}):
            for cfg, secs in ((Config(), 30), (Config(call_ring_timeout_s=20), 20)):
                req = dataclasses.replace(REQ, idempotency_key="k%d" % secs)
                with mock.patch("urllib.request.urlopen", return_value=Resp(OK)) as uo:
                    ElevenLabsDialer(cfg, lambda: __import__("datetime").datetime(2026, 1, 5, 11, 0)).place(req)
                sent = json.loads(uo.call_args[0][0].data)
                self.assertEqual(sent["telephony_call_config"], {"ringing_timeout_secs": secs})


class AutoCollectTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.inp, self.out = self.root / "in", self.root / "out"
        self.inp.mkdir()
        make_case(self.inp, "v1", PROVIDER)
        env = dict(ENV, LETTABLE_CALL_LEDGER=str(self.root / "ledger.json"))
        self.net = Network()
        for p in (mock.patch.dict(os.environ, env), mock.patch("urllib.request.urlopen", self.net)):
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self.tmp.cleanup)
        self.cfg = Config(as_of="now", call_backend="elevenlabs", call_hours=(0, 24), loop_max_steps=6, case_timeout_s=60,
                          stt_backend="off")

    def record(self):
        return self.out / "v1" / "calls" / "conv-1.json"

    def test_the_next_run_fetches_finished_calls_before_deciding(self):
        first = run_all(self.inp, self.out, self.cfg, "tests.call_backends:ProviderCallChat", NOW)
        self.assertEqual(first["calls"], {"collected": 0, "pending": 0, "errors": 0})
        self.assertFalse(self.record().exists())
        second = run_all(self.inp, self.out, self.cfg, "tests.call_backends:ProviderCallChat", NOW)
        self.assertEqual(second["calls"]["collected"], 1)
        self.assertTrue(self.record().is_file())
        self.assertEqual(len(self.net.posts), 1)  # fetched, not dialled again

    def test_it_can_be_turned_off_and_a_dry_run_never_touches_the_network(self):
        run_all(self.inp, self.out, self.cfg, "tests.call_backends:ProviderCallChat", NOW)
        off = run_all(self.inp, self.out, dataclasses.replace(self.cfg, collect_calls=False), "tests.call_backends:ProviderCallChat", NOW)
        self.assertEqual(off["calls"], {"collected": 0, "pending": 0, "errors": 0})
        self.assertFalse(self.record().exists())
        dry = run_all(self.inp, self.out, dataclasses.replace(self.cfg, call_backend="dry_run"), "fake", NOW)
        self.assertNotIn("calls", dry)

    def test_a_dialer_that_cannot_be_built_does_not_stop_the_cases(self):
        run_all(self.inp, self.out, self.cfg, "tests.call_backends:ProviderCallChat", NOW)
        with mock.patch.dict(os.environ, {"ELEVENLABS_API_KEY": ""}):
            summary = run_all(self.inp, self.out, self.cfg, "fake", NOW)
        self.assertTrue(summary["reconciled"])
        self.assertEqual(summary["calls"]["errors"], 1)


if __name__ == "__main__":
    unittest.main()
