import dataclasses
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agent import stt
from agent.config import Config
from agent.runner import run_all
from agent.stt import (ElevenLabsTranscriber, FakeTranscriber, OpenAITranscriber, Transcriber, case_keyterms,
                       format_words, make_transcriber, transcript_for)
from agent.timeline import load_case, render_case
from tests.helpers import WAITING_LANDLORD, make_case

ECHO = "tests.stt_backends:EchoAttachments"


class Counting(Transcriber):
    def __init__(self, text="Speaker 1: hello"):
        self.calls, self.text = 0, text

    def transcribe(self, path, keyterms):
        self.calls += 1
        return self.text


class Boom(Transcriber):
    def transcribe(self, path, keyterms):
        raise RuntimeError("network down")


class SttTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cfg = Config(stt_cache_dir=str(self.root / "cache"))

    def tearDown(self):
        self.tmp.cleanup()

    def case_with_audio(self, cid="c1", where="attachments", name="voicemail.mp3", data=b"audio-bytes-1"):
        cases = self.root / "cases"
        cases.mkdir(exist_ok=True)
        folder = make_case(cases, cid, WAITING_LANDLORD)
        target = folder if where == "." else folder / where
        target.mkdir(exist_ok=True)
        (target / name).write_bytes(data)
        return folder


class LoadCaseTests(SttTestCase):
    def test_audio_is_transcribed_and_flows_into_the_prompt(self):
        folder = self.case_with_audio()
        case = load_case(folder, self.cfg, FakeTranscriber())
        att = {a.name: a.text for a in case.attachments}
        self.assertTrue(att["voicemail.mp3"].startswith(stt.TRANSCRIPT_NOTE))
        self.assertIn("fake transcript of voicemail.mp3", att["voicemail.mp3"])
        self.assertIn("fake transcript", render_case(case, 5000))

    def test_audio_is_listed_even_when_the_index_does_not_mention_it(self):
        folder = self.case_with_audio()
        self.assertNotIn("voicemail", (folder / "index.md").read_text())
        self.assertEqual([a.name for a in load_case(folder, self.cfg).attachments], ["voicemail.mp3"])

    def test_top_level_audio_is_found_but_other_top_level_files_are_not_attachments(self):
        folder = self.case_with_audio(where=".", name="call.wav")
        (folder / "notes.txt").write_text("x")
        (folder / "other.pdf").write_bytes(b"%PDF")
        self.assertEqual([a.name for a in load_case(folder, self.cfg, FakeTranscriber()).attachments], ["call.wav"])

    def test_without_a_transcriber_content_is_unavailable(self):
        case = load_case(self.case_with_audio(), self.cfg)
        self.assertEqual([(a.name, a.text) for a in case.attachments], [("voicemail.mp3", None)])

    def test_transcriber_failure_gives_unavailable_content_not_an_error(self):
        case = load_case(self.case_with_audio(), self.cfg, Boom())
        self.assertIsNone(case.attachments[0].text)

    def test_a_cut_case_drops_attachments(self):
        case = load_case(self.case_with_audio(), self.cfg, FakeTranscriber())
        self.assertEqual(case.cut(2).attachments, ())


class TranscriptForTests(SttTestCase):
    def audio(self, data=b"abc"):
        p = self.root / "a.mp3"
        p.write_bytes(data)
        return p

    def test_second_call_is_served_from_the_cache(self):
        t, p = Counting(), self.audio()
        first = transcript_for(p, t, self.cfg, [])
        second = transcript_for(p, t, self.cfg, [])
        self.assertEqual((t.calls, first), (1, second))

    def test_cache_is_keyed_by_content_and_model(self):
        t = Counting()
        transcript_for(self.audio(b"one"), t, self.cfg, [])
        transcript_for(self.audio(b"two"), t, self.cfg, [])
        transcript_for(self.audio(b"two"), t, dataclasses.replace(self.cfg, stt_model="other"), [])
        self.assertEqual(t.calls, 3)

    def test_failures_and_empty_results_are_not_cached(self):
        p = self.audio()
        self.assertIsNone(transcript_for(p, Boom(), self.cfg, []))
        self.assertIsNone(transcript_for(p, Counting(text=""), self.cfg, []))
        t = Counting()
        self.assertIsNotNone(transcript_for(p, t, self.cfg, []))
        self.assertEqual(t.calls, 1)

    def test_oversize_file_is_skipped_without_calling_the_transcriber(self):
        t = Counting()
        cfg = dataclasses.replace(self.cfg, stt_max_audio_bytes=5)
        self.assertIsNone(transcript_for(self.audio(b"0123456789"), t, cfg, []))
        self.assertEqual(t.calls, 0)

    def test_unwritable_cache_still_returns_the_text(self):
        blocker = self.root / "cache"
        blocker.write_text("a file, so the cache directory cannot be created")
        self.assertIn("hello", transcript_for(self.audio(), Counting(), self.cfg, []))


class ElevenLabsTests(SttTestCase):
    def audio(self):
        p = self.root / "My Voice.mp3"
        p.write_bytes(b"RIFFdata")
        return p

    def test_request_is_built_as_documented(self):
        seen = {}

        def fake_post(url, headers, body, content_type, cfg):
            seen.update(url=url, headers=headers, body=body, content_type=content_type)
            return {"text": "ignored", "words": [
                {"text": "Hello", "type": "word", "speaker_id": "speaker_0"}, {"text": " ", "type": "spacing", "speaker_id": "speaker_0"},
                {"text": "there", "type": "word", "speaker_id": "speaker_0"},
                {"text": "Hi", "type": "word", "speaker_id": "speaker_1"}, {"text": "(laughs)", "type": "audio_event", "speaker_id": "speaker_1"}]}

        with mock.patch.dict(os.environ, {"ELEVENLABS_API_KEY": "k-test"}), mock.patch("agent.stt._post", fake_post):
            text = ElevenLabsTranscriber(self.cfg).transcribe(self.audio(), ["Flat 4", "Rowan"])
        self.assertEqual(text, "Speaker 1: Hello there\nSpeaker 2: Hi")
        self.assertEqual(seen["url"], "https://api.elevenlabs.io/v1/speech-to-text")
        self.assertEqual(seen["headers"], {"xi-api-key": "k-test"})
        body = seen["body"].decode("utf-8", errors="replace")
        boundary = seen["content_type"].split("boundary=")[1]
        self.assertTrue(seen["content_type"].startswith("multipart/form-data"))
        for needle in ('name="model_id"\r\n\r\nscribe_v2', 'name="diarize"\r\n\r\ntrue',
                       'name="keyterms"\r\n\r\nFlat 4', 'name="keyterms"\r\n\r\nRowan',
                       'name="file"; filename="My Voice.mp3"', "RIFFdata"):
            self.assertIn(needle, body)
        self.assertTrue(body.rstrip().endswith("--%s--" % boundary))

    def test_falls_back_to_plain_text_when_there_are_no_words(self):
        with mock.patch.dict(os.environ, {"ELEVENLABS_API_KEY": "k"}), \
                mock.patch("agent.stt._post", lambda *a, **k: {"text": " plain text "}):
            self.assertEqual(ElevenLabsTranscriber(self.cfg).transcribe(self.audio(), []), "plain text")

    def test_no_key_means_no_call_and_no_text(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("agent.stt._post") as post:
            self.assertIsNone(ElevenLabsTranscriber(self.cfg).transcribe(self.audio(), []))
        post.assert_not_called()

    def test_failed_request_surfaces_as_none_through_transcript_for(self):
        def boom(*a, **k):
            raise stt.SttError("HTTP 500")

        with mock.patch.dict(os.environ, {"ELEVENLABS_API_KEY": "k"}), mock.patch("agent.stt._post", boom):
            self.assertIsNone(transcript_for(self.audio(), ElevenLabsTranscriber(self.cfg), self.cfg, []))

    def test_format_words_ignores_empty_input(self):
        self.assertEqual(format_words([]), "")


class FactoryTests(SttTestCase):
    def test_off_by_default_and_explicit_choices(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(make_transcriber(Config()))
            self.assertIsInstance(make_transcriber(Config(stt_backend="fake")), FakeTranscriber)
            self.assertIsInstance(make_transcriber(Config(stt_backend="elevenlabs")), ElevenLabsTranscriber)
            self.assertIsInstance(make_transcriber(Config(stt_backend="openai")), OpenAITranscriber)
            with self.assertRaises(ValueError):
                make_transcriber(Config(stt_backend="whisper-ish"))

    def test_environment_overrides_only_an_off_config(self):
        with mock.patch.dict(os.environ, {"LETTABLE_STT": "fake"}):
            self.assertIsInstance(make_transcriber(Config()), FakeTranscriber)
            self.assertIsInstance(make_transcriber(Config(stt_backend="elevenlabs")), ElevenLabsTranscriber)

    def test_keyterms_are_short_unique_and_capped(self):
        many = ["Hi %s," % "".join(chr(97 + (i // 26 ** k) % 26) for k in range(3)).capitalize() for i in range(100)]
        terms = case_keyterms("Flat 4, 12 Mill Lane, ZZ1 2ZZ", "Boiler repair " * 20, ["Hi Rowan, hello Dear Sam"] + many)
        self.assertIn("Flat 4", terms)
        self.assertIn("Rowan", terms)
        self.assertNotIn("Boiler repair " * 20, terms)
        self.assertEqual(len(terms), len(set(terms)))
        self.assertLessEqual(len(terms), 50)
        self.assertTrue(all(len(t) < 50 and len(t.split()) <= 5 for t in terms))


class RunnerTests(SttTestCase):
    def run_case(self, cfg):
        inp, out = self.root / "in", self.root / "out"
        inp.mkdir()
        folder = make_case(inp, "v1", WAITING_LANDLORD)
        (folder / "attachments").mkdir()
        (folder / "attachments" / "message.mp3").write_bytes(b"voice")
        run_all(inp, out, dataclasses.replace(cfg, case_timeout_s=30), ECHO, "2026-01-10T09:00:00+00:00")
        return json.loads((out / "v1" / "decision.json").read_text())["reason"]

    def test_transcription_happens_in_the_isolated_run(self):
        reason = self.run_case(dataclasses.replace(self.cfg, stt_backend="fake"))
        self.assertIn("Automatic transcript", reason)
        self.assertIn("fake transcript of message.mp3", reason)

    def test_audio_stays_unavailable_when_stt_is_off(self):
        with mock.patch.dict(os.environ, {"LETTABLE_STT": "off"}):
            self.assertIn("message.mp3=UNAVAILABLE", self.run_case(self.cfg))

    def test_the_fallback_path_never_transcribes(self):
        inp = self.root / "in"
        inp.mkdir()
        make_case(inp, "v1", WAITING_LANDLORD)
        calls = []
        real = load_case

        def spy(folder, cfg=None, transcriber=None):
            calls.append(transcriber)
            return real(folder, cfg, transcriber)

        cfg = dataclasses.replace(self.cfg, stt_backend="fake")
        with mock.patch("agent.runner.run_isolated", lambda *a, **k: ("timeout", "slow")), \
                mock.patch("agent.runner.load_case", spy):
            run_all(inp, self.root / "out", cfg, "fake", "2026-01-10T09:00:00+00:00")
        self.assertEqual(calls, [None])


if __name__ == "__main__":
    unittest.main()
