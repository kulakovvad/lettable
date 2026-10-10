"""What the phone agent says and how it is set up. HTTP is mocked; nothing is dialled or created."""

import contextlib
import io
import json
import os
import re
import unittest
from unittest import mock

from agent import __main__ as cli
from agent.voice import CallRequest
from agent.voice_prompt import DATA_COLLECTION, FIRST_MESSAGE, OUTCOMES, PROMPT, TTS, dynamic_variables
from agent.voice_setup import agent_body, agent_config, create_agent, update_agent
from tests.test_voice_elevenlabs import ENV, Resp

REQ = CallRequest("c1", "provider", "+447000000001", "Ask when the engineer can visit. Record what is said.",
                  {"job": "the dishwasher repair", "agency_name": "Northbridge Lettings"}, "k1")


class WhatTheAgentSaysTests(unittest.TestCase):
    def test_first_message_is_one_short_statement_with_no_question(self):
        spoken = re.sub(r"\{\{\w+\}\}", "word", FIRST_MESSAGE)
        self.assertLessEqual(len(spoken.split()), 20)
        self.assertNotIn("?", FIRST_MESSAGE)
        self.assertIn("recorded", FIRST_MESSAGE)
        for name in ("agency_name", "job"):
            self.assertIn("{{%s}}" % name, FIRST_MESSAGE)

    def test_first_message_reads_well_with_real_values(self):
        said = FIRST_MESSAGE
        for k, v in dynamic_variables(REQ).items():
            said = said.replace("{{%s}}" % k, v)
        self.assertEqual(said, "Hello, this is an automated assistant calling for Northbridge Lettings about the dishwasher repair. "
                               "This call is recorded.")

    def test_job_falls_back_to_the_start_of_the_objective_and_agency_to_a_neutral_name(self):
        bare = CallRequest("c1", "tenant", "+447000000001", "Confirm the Monday visit works for you. Then say thanks.", {}, "k")
        v = dynamic_variables(bare)
        self.assertEqual(v["job"], "Confirm the Monday visit works for you")
        self.assertEqual(v["agency_name"], "the agency")
        long = CallRequest("c1", "tenant", "+447000000001", "x" * 300, {}, "k")
        self.assertLessEqual(len(dynamic_variables(long)["job"]), 80)

    def test_prompt_keeps_every_safety_rule_and_the_new_manners(self):
        text = PROMPT.lower()
        for must in ("no authority to approve spend", "never share one party", "colleague will", "recorded",
                     "never claim anything that is not in what you know", "voicemail", "safety"):
            self.assertIn(must, text)
        self.assertIn("never write bracketed tags", text)
        self.assertIn("one or two short sentences", text)
        self.assertIn("let the person finish", text)
        self.assertIn("cannot talk now", text)

    def test_outcomes_include_unclear_and_are_all_defined_in_the_field_description(self):
        self.assertIn("unclear", OUTCOMES)
        description = DATA_COLLECTION["outcome"]["description"]
        for name, meaning in OUTCOMES.items():
            self.assertIn("%s = %s" % (name, meaning), description)
        self.assertIn("never use this when a person answered", OUTCOMES["no_answer"])

    def test_voice_is_not_expressive(self):
        self.assertIs(TTS["expressive_mode"], False)
        self.assertEqual(TTS["model_id"], "eleven_flash_v2")


class SetupTests(unittest.TestCase):
    def test_create_and_update_send_the_same_configuration(self):
        with mock.patch("urllib.request.urlopen", return_value=Resp({"agent_id": "a-1"})) as uo:
            create_agent("key-123")
        created = json.loads(uo.call_args[0][0].data)
        with mock.patch("urllib.request.urlopen", return_value=Resp({})) as uo:
            update_agent("key-123", "a-1")
        sent = uo.call_args[0][0]
        updated = json.loads(sent.data)
        self.assertEqual((sent.get_method(), sent.full_url), ("PATCH", "https://api.elevenlabs.io/v1/convai/agents/a-1"))
        created.pop("name")
        self.assertEqual(created, updated)
        self.assertEqual(updated, agent_config())
        self.assertEqual(agent_body("n")["name"], "n")
        self.assertEqual(updated["conversation_config"]["tts"], {"model_id": "eleven_flash_v2", "expressive_mode": False})
        self.assertEqual(updated["conversation_config"]["agent"]["first_message"], FIRST_MESSAGE)
        self.assertNotIn("llm", updated["conversation_config"]["agent"]["prompt"])

    def run_cli(self, args, env):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, env, clear=False), mock.patch("urllib.request.urlopen", return_value=Resp({})) as uo, \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(["voice-setup"] + args)
        return code, out.getvalue(), err.getvalue(), uo

    def test_update_without_the_agent_id_is_refused(self):
        env = {k: v for k, v in ENV.items() if k != "ELEVENLABS_AGENT_ID"}
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ELEVENLABS_AGENT_ID", None)
            code, out, err, uo = self.run_cli(["--update-agent", "--yes"], env)
        self.assertEqual(code, 2)
        self.assertIn("ELEVENLABS_AGENT_ID", err)
        uo.assert_not_called()

    def test_update_without_yes_only_describes(self):
        code, out, err, uo = self.run_cli(["--update-agent"], ENV)
        self.assertEqual(code, 0)
        self.assertIn("Dry run", out)
        self.assertIn("agent-1", out)
        uo.assert_not_called()
        self.assertNotIn("key-123", out + err)

    def test_update_with_yes_patches_the_right_agent_and_prints_no_key(self):
        code, out, err, uo = self.run_cli(["--update-agent", "--yes"], ENV)
        self.assertEqual(code, 0)
        sent = uo.call_args[0][0]
        self.assertEqual((sent.get_method(), sent.full_url), ("PATCH", "https://api.elevenlabs.io/v1/convai/agents/agent-1"))
        self.assertEqual(json.loads(sent.data), agent_config())
        self.assertNotIn("key-123", out + err)

    def test_nothing_to_do_is_still_reported(self):
        self.assertEqual(self.run_cli([], ENV)[0], 2)


if __name__ == "__main__":
    unittest.main()
