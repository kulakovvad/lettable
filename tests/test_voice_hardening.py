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
        self.assertEqual(holders(VOICEMAIL_MESSAGE), {"agency_name"})  # no job, objective or fact: nothing else can leak
        self.assertNotRegex(VOICEMAIL_MESSAGE, r"\d")
        self.assertIn("voicemail tool", PROMPT)
        self.assertNotIn("leave a short message with the agency name", PROMPT)

    def test_hostile_case_text_cannot_reach_a_voicemail_or_the_spoken_greeting_as_numbers_or_links(self):
        hostile = CallRequest("c1", "provider", "+447000000001", "Ask about the visit.", {
            "job": "Boiler repair \u00a3450, Mrs Smith 07700 900123 me@example.com https://evil.example/x " + "word " * 40,
            "agency_name": "Northbridge Lettings 07700 900123 \u00a3500 pay at www.evil.example"}, "k")
        v = dynamic_variables(hostile)
        for key in ("job", "agency_name"):
            self.assertNotRegex(v[key], r"\d|\u00a3|@|http|www|evil")
        self.assertEqual(v["agency_name"], "the letting agency")  # a name that needed cleaning is not trusted
        self.assertLessEqual(len(v["job"]), 80)
        heard = VOICEMAIL_MESSAGE.replace("{{agency_name}}", v["agency_name"])
        self.assertNotRegex(heard, r"\d|\u00a3|@|Smith|Boiler|evil")
        long_name = CallRequest("c1", "provider", "+447000000001", "x", {"agency_name": "Very " * 40 + "Lettings"}, "k")
        self.assertEqual(dynamic_variables(long_name)["agency_name"], "the letting agency")
        plain = CallRequest("c1", "provider", "+447000000001", "x", {"agency_name": "Northbridge Lettings"}, "k")
        self.assertEqual(dynamic_variables(plain)["agency_name"], "Northbridge Lettings")
        only_junk = CallRequest("c1", "provider", "+447000000001", "x", {"job": "\u00a3450 07700 900123", "agency_name": "07700 900123"}, "k")
        self.assertEqual((dynamic_variables(only_junk)["job"], dynamic_variables(only_junk)["agency_name"]),
                         ("a maintenance job", "the letting agency"))

    def test_an_inbound_caller_reporting_a_danger_is_sent_to_the_emergency_services(self):
        self.assertIn("999", PROMPT)
        self.assertNotIn("Find out where the job stands", PLACEHOLDERS["objective"])  # no outbound goal on an inbound call
        self.assertIn("contact the agency", PLACEHOLDERS["objective"])

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

    def test_a_live_run_does_not_ask_the_real_service_about_rehearsal_calls(self):
        run_all(self.inp, self.out, dataclasses.replace(self.cfg, call_backend="dry_run"), "tests.call_backends:ProviderCallChat", NOW)
        d = json.loads((self.out / "v1" / "decision.json").read_text())
        self.assertTrue([a for a in d["actions"] if a["kind"] == "call" and str(a["conversation_id"]).startswith("dryrun-")])
        gets = []
        real = self.net.__call__

        def spy(req, timeout=None):
            gets.append(req.get_method())
            return real(req, timeout)
        with mock.patch("urllib.request.urlopen", spy):
            summary = run_all(self.inp, self.out, self.cfg, "fake", NOW)
        self.assertEqual(summary["calls"], {"collected": 0, "pending": 0, "errors": 0})
        self.assertNotIn("GET", gets)

    def test_collect_failures_are_written_to_the_trace(self):
        run_all(self.inp, self.out, self.cfg, "tests.call_backends:ProviderCallChat", NOW)
        with mock.patch.dict(os.environ, {"ELEVENLABS_API_KEY": ""}):
            run_all(self.inp, self.out, self.cfg, "fake", NOW)
        rows = [json.loads(l) for l in (self.out / "trace.jsonl").read_text().splitlines()]
        self.assertTrue([r for r in rows if r.get("event") == "collect_calls" and r["errors"]])

    def test_a_dialer_that_cannot_be_built_does_not_stop_the_cases(self):
        run_all(self.inp, self.out, self.cfg, "tests.call_backends:ProviderCallChat", NOW)
        with mock.patch.dict(os.environ, {"ELEVENLABS_API_KEY": ""}):
            summary = run_all(self.inp, self.out, self.cfg, "fake", NOW)
        self.assertTrue(summary["reconciled"])
        self.assertEqual(summary["calls"]["errors"], 1)


if __name__ == "__main__":
    unittest.main()
