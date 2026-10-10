"""End to end, offline: an audio file comes in, a call goes out, its result comes back."""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from agent import __main__ as cli
from agent.calls import with_call_events
from agent.config import Config
from agent.runner import run_all
from agent.timeline import load_case
from tests.helpers import make_case
from tests.test_calls import PROVIDER
from tests.test_voice_elevenlabs import ENV, OK, Resp

CHAT = "tests.call_backends:ReadVoicemailAndCallChat"
NOW = "2026-01-09T12:00:00+00:00"  # 8 days after our last message to the provider
DONE = {"status": "done", "transcript": [{"role": "agent", "message": "When can you visit?"}, {"role": "user", "message": "Friday morning."}],
        "analysis": {"call_successful": "success", "transcript_summary": "Provider will visit on Friday morning.",
                     "data_collection_results": {"outcome": {"value": "confirmed"}, "confirmed_date": {"value": "Friday"}}},
        "metadata": {"call_duration_secs": 42}}


class Network:
    """Stands in for ElevenLabs: records what was sent, answers like the real API."""

    def __init__(self):
        self.posts = []

    def __call__(self, req, timeout=None):
        if req.get_method() == "POST":
            self.posts.append(json.loads(req.data))
            return Resp(OK)
        return Resp(DONE)


class VoiceEndToEnd(unittest.TestCase):
    def test_audio_in_call_out_result_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp, out = root / "in", root / "out"
            inp.mkdir()
            folder = make_case(inp, "v1", PROVIDER)
            (folder / "voicemail.mp3").write_bytes(b"not really audio")
            cfg = Config(as_of="now", stt_backend="fake", stt_cache_dir=str(root / "stt"), call_backend="elevenlabs",
                         call_hours=(0, 24), loop_max_steps=6, case_timeout_s=60)
            env = dict(ENV, LETTABLE_CALL_LEDGER=str(root / "ledger.json"))
            net = Network()
            with mock.patch.dict(os.environ, env), mock.patch("urllib.request.urlopen", net):
                # 1. run: the voicemail is transcribed, the model reads it and phones the provider
                summary = run_all(inp, out, cfg, CHAT, NOW)
                d = json.loads((out / "v1" / "decision.json").read_text())
                self.assertTrue(summary["reconciled"])
                self.assertEqual(d["action"], "CHASE_PROVIDER")
                read = [t for t in d["trace"] if t.get("tool") == "read_attachment"][0]
                self.assertEqual(read["result"]["status"], "ok")  # the transcript was available
                call = [a for a in d["actions"] if a["kind"] == "call"][0]
                self.assertEqual((call["state"], call["call_status"], call["conversation_id"]), ("committed", "started", "conv-1"))
                self.assertEqual(len(net.posts), 1)
                self.assertEqual(net.posts[0]["to_number"], "+447700900123")  # taken from the case, never from the model

                # 2. collect: the finished call is fetched and stored
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(cli.main(["calls", "collect", str(out), "--backend", "elevenlabs"]), 0)
                record = json.loads((out / "v1" / "calls" / "conv-1.json").read_text())
                self.assertEqual(record["data"]["confirmed_date"], "Friday")
                self.assertIn("Friday", (out / "v1" / "ANSWER.md").read_text())

                # 3. the next decision sees what was said, and the same call is not dialled again
                case = with_call_events(load_case(folder), out / "v1")
                self.assertIn("Provider will visit on Friday morning.", case.events[-1].body)
                self.assertGreater(case.events[-1].ts, case.events[-2].ts)  # stamped when the call was placed
                run_all(inp, out, cfg, CHAT, NOW)
                self.assertEqual(len(net.posts), 1)
                again = json.loads((out / "v1" / "decision.json").read_text())
                self.assertEqual([a["kind"] for a in again["actions"] if a["kind"] == "call"], [])


if __name__ == "__main__":
    unittest.main()
