import contextlib
import io
import json
import os
import re
import tempfile
import unittest
import urllib.error
from datetime import datetime
from pathlib import Path
from unittest import mock

from agent import __main__ as cli
from agent.config import Config
from agent.voice import CallRequest
from agent.voice_elevenlabs import ElevenLabsDialer
from agent.voice_prompt import PROMPT, VARIABLES, dynamic_variables
from agent.voice_setup import create_agent, import_twilio_number

ENV = {"ELEVENLABS_API_KEY": "key-123", "ELEVENLABS_AGENT_ID": "agent-1", "ELEVENLABS_PHONE_NUMBER_ID": "pn-1"}
REQ = CallRequest("c1", "provider", "+447000000001", "Ask for a visit date.", {"address": "Flat 1", "name": "Sam"}, "k1")


def DAY():
    return datetime(2026, 1, 5, 11, 0)


def NIGHT():
    return datetime(2026, 1, 5, 23, 0)


class Resp:
    def __init__(self, body):
        self.body = json.dumps(body).encode()

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def http_error(code):
    return urllib.error.HTTPError("https://x", code, "err", {}, io.BytesIO(b'{"detail":"boom"}'))


OK = {"success": True, "conversation_id": "conv-1", "callSid": "CA1"}


class DialerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = str(Path(self.tmp.name) / "calls.json")
        patches = [mock.patch.dict(os.environ, {**ENV, "LETTABLE_CALL_LEDGER": self.ledger}, clear=False),
                   mock.patch("agent.voice_elevenlabs.time.sleep")]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self.tmp.cleanup)

    def dialer(self, cfg=None, clock=DAY):
        return ElevenLabsDialer(cfg or Config(), clock)

    def test_place_sends_the_documented_request(self):
        with mock.patch("urllib.request.urlopen", return_value=Resp(OK)) as uo:
            result = self.dialer().place(REQ)
        self.assertEqual((result.status, result.conversation_id), ("started", "conv-1"))
        sent = uo.call_args[0][0]
        self.assertEqual((sent.get_method(), sent.full_url), ("POST", "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"))
        self.assertEqual(sent.get_header("Xi-api-key"), "key-123")
        body = json.loads(sent.data)
        self.assertEqual((body["agent_id"], body["agent_phone_number_id"], body["to_number"]), ("agent-1", "pn-1", "+447000000001"))
        self.assertTrue(body["call_recording_enabled"])
        dv = body["conversation_initiation_client_data"]["dynamic_variables"]
        self.assertEqual((dv["party"], dv["objective"], dv["address"]), ("provider", "Ask for a visit date.", "Flat 1"))

    def test_same_key_never_dials_twice_even_from_a_new_instance(self):
        with mock.patch("urllib.request.urlopen", return_value=Resp(OK)) as uo:
            first = self.dialer().place(REQ)
            second = self.dialer().place(REQ)
        self.assertEqual(uo.call_count, 1)
        self.assertEqual(second.conversation_id, first.conversation_id)
        self.assertIn("idempotent", second.detail)

    def test_failed_request_is_not_recorded_and_can_be_retried(self):
        with mock.patch("urllib.request.urlopen", side_effect=http_error(400)):
            self.assertEqual(self.dialer().place(REQ).status, "failed")
        with mock.patch("urllib.request.urlopen", return_value=Resp(OK)):
            self.assertEqual(self.dialer().place(REQ).status, "started")

    def test_refusals_do_not_call_the_api(self):
        night = self.dialer(clock=NIGHT)
        bad = CallRequest("c1", "provider", "07000000001", "x", {}, "k2")
        capped = self.dialer(Config(max_calls_per_run=1))
        with mock.patch("urllib.request.urlopen", return_value=Resp(OK)) as uo:
            self.assertIn("calling hours", night.place(REQ).detail)
            self.assertIn("E.164", self.dialer().place(bad).detail)
            capped.place(REQ)
            over = capped.place(CallRequest("c2", "tenant", "+447000000002", "x", {}, "k3"))
        self.assertEqual(uo.call_count, 1)
        self.assertEqual(over.status, "failed")
        self.assertIn("cap", over.detail)

    def test_post_is_not_retried_on_5xx_but_is_on_429(self):
        with mock.patch("urllib.request.urlopen", side_effect=http_error(503)) as uo:
            self.assertEqual(self.dialer().place(REQ).status, "failed")
        self.assertEqual(uo.call_count, 1)
        again = CallRequest("c1", "provider", "+447000000001", "Ask for a visit date.", {}, "k-429")
        with mock.patch("urllib.request.urlopen", side_effect=[http_error(429), Resp(OK)]) as uo:
            self.assertEqual(self.dialer().place(again).status, "started")
        self.assertEqual(uo.call_count, 2)

    def test_a_request_that_may_have_dialled_is_never_retried_automatically(self):
        for failure in (http_error(503), TimeoutError("timed out"), urllib.error.URLError("reset")):
            with self.subTest(failure=repr(failure)):
                req = CallRequest("c1", "provider", "+447000000001", "x", {}, "k-%r" % (failure,))
                with mock.patch("urllib.request.urlopen", side_effect=failure):
                    first = self.dialer().place(req)
                self.assertEqual(first.status, "failed")
                self.assertIn("may have been placed", first.detail)
                with mock.patch("urllib.request.urlopen") as uo:  # even from a new process: no second POST
                    second = self.dialer().place(req)
                self.assertEqual((second.status, uo.call_count), ("failed", 0))
                self.assertIn("check the ElevenLabs", second.detail)

    def test_a_clear_refusal_is_not_recorded_so_it_can_be_tried_again(self):
        with mock.patch("urllib.request.urlopen", side_effect=http_error(400)):
            self.assertEqual(self.dialer().place(REQ).status, "failed")
        with mock.patch("urllib.request.urlopen", return_value=Resp(OK)) as uo:
            self.assertEqual(self.dialer().place(REQ).status, "started")
        self.assertEqual(uo.call_count, 1)

    def test_fetch_maps_the_conversation(self):
        body = {"status": "done",
                "transcript": [{"role": "agent", "message": "Hello"}, {"role": "user", "message": "Friday at 10"},
                               {"role": "agent", "message": None, "tool_calls": []}],
                "analysis": {"call_successful": "success", "transcript_summary": "Visit confirmed.",
                             "data_collection_results": {"outcome": {"value": "confirmed", "rationale": "x"},
                                                         "confirmed_date": {"value": "Friday 10am"}}},
                "metadata": {"call_duration_secs": 42}}
        with mock.patch("urllib.request.urlopen", return_value=Resp(body)) as uo:
            conv = self.dialer().fetch("conv-1")
        self.assertEqual(uo.call_args[0][0].full_url, "https://api.elevenlabs.io/v1/convai/conversations/conv-1")
        self.assertEqual((conv.status, conv.success, conv.summary, conv.duration_s), ("done", "success", "Visit confirmed.", 42.0))
        self.assertEqual(conv.transcript, (("agent", "Hello"), ("user", "Friday at 10")))
        self.assertEqual(conv.data, {"outcome": "confirmed", "confirmed_date": "Friday 10am"})

    def test_fetch_tolerates_missing_fields(self):
        with mock.patch("urllib.request.urlopen", return_value=Resp({"analysis": None, "transcript": None})):
            conv = self.dialer().fetch("conv-2")
        self.assertEqual((conv.status, conv.transcript, conv.data, conv.success, conv.duration_s), ("unknown", (), {}, None, None))

    def test_fetch_retries_503_then_succeeds_but_not_400(self):
        with mock.patch("urllib.request.urlopen", side_effect=[http_error(503), Resp({"status": "done"})]) as uo:
            self.assertEqual(self.dialer().fetch("c").status, "done")
        self.assertEqual(uo.call_count, 2)
        with mock.patch("urllib.request.urlopen", side_effect=http_error(400)) as uo:
            with self.assertRaises(RuntimeError):
                self.dialer().fetch("c")
        self.assertEqual(uo.call_count, 1)

    def test_missing_environment_raises_a_clear_error(self):
        with mock.patch.dict(os.environ, {"ELEVENLABS_AGENT_ID": ""}):
            with self.assertRaisesRegex(RuntimeError, "ELEVENLABS_AGENT_ID"):
                self.dialer()


class PromptAndSetupTests(unittest.TestCase):
    def test_every_placeholder_in_the_prompt_is_supplied(self):
        names = set(re.findall(r"\{\{(\w+)\}\}", PROMPT))
        self.assertTrue(names <= set(dynamic_variables(CallRequest("c", "tenant", "+441", "o", {}, "k"))))
        self.assertTrue(set(VARIABLES) >= names)

    def test_create_agent_and_import_number_bodies(self):
        with mock.patch("urllib.request.urlopen", return_value=Resp({"agent_id": "a-9"})) as uo:
            self.assertEqual(create_agent("key-123"), "a-9")
        sent = uo.call_args[0][0]
        body = json.loads(sent.data)
        self.assertEqual(sent.full_url, "https://api.elevenlabs.io/v1/convai/agents/create")
        self.assertEqual(body["conversation_config"]["agent"]["language"], "en")
        self.assertIn("outcome", body["platform_settings"]["data_collection"])
        with mock.patch("urllib.request.urlopen", return_value=Resp({"phone_number_id": "pn-9"})) as uo:
            self.assertEqual(import_twilio_number("key-123", "+441", "ACx", "tok"), "pn-9")
        self.assertEqual(json.loads(uo.call_args[0][0].data),
                         {"phone_number": "+441", "label": "Lettings calls", "sid": "ACx", "token": "tok", "provider": "twilio"})

    def test_cli_describes_by_default_and_never_prints_keys(self):
        out = io.StringIO()
        with mock.patch.dict(os.environ, ENV), mock.patch("urllib.request.urlopen") as uo, contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["voice-setup", "--create-agent"]), 0)
        uo.assert_not_called()
        self.assertIn("Dry run", out.getvalue())
        self.assertNotIn("key-123", out.getvalue())

    def test_cli_with_yes_creates_the_agent(self):
        out = io.StringIO()
        with mock.patch.dict(os.environ, ENV), mock.patch("urllib.request.urlopen", return_value=Resp({"agent_id": "a-9"})), \
                contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["voice-setup", "--create-agent", "--yes"]), 0)
        self.assertIn("ELEVENLABS_AGENT_ID=a-9", out.getvalue())
        self.assertNotIn("key-123", out.getvalue())


if __name__ == "__main__":
    unittest.main()
