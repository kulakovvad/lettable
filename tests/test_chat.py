import os
import unittest
from unittest import mock

from agent import chat
from agent.chat import AnthropicChat, OpenAIChat, ToolCall
from agent.config import Config
from agent.loop import SYSTEM_PROMPT

REPLY = {"content": [{"type": "tool_use", "id": "t1", "name": "case_facts", "input": {}}],
         "usage": {"input_tokens": 10, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 1000,
                   "output_tokens": 5}}


class AnthropicCacheTests(unittest.TestCase):
    def setUp(self):
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test"}):
            self.client = AnthropicChat(Config())
        self.sent = []
        patcher = mock.patch.object(chat, "_post", side_effect=lambda url, headers, body, cfg: self.sent.append(body) or REPLY)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_system_and_last_message_are_cached(self):
        transcript = [
            {"role": "user", "text": "case"},
            {"role": "assistant", "text": "", "calls": [ToolCall(id="t0", name="case_facts", arguments={})]},
            {"role": "tool", "results": [{"id": "t0", "name": "case_facts", "content": "{}"}]},
        ]
        turn = self.client.chat("SYSTEM", transcript, [])
        body = self.sent[0]
        self.assertEqual(body["system"][0]["cache_control"], {"type": "ephemeral"})
        self.assertEqual(body["messages"][-1]["content"][-1]["cache_control"], {"type": "ephemeral"})
        self.assertNotIn("cache_control", str(body["messages"][:-1]))
        self.assertEqual(turn.tokens, 1115)

    def test_plain_text_user_message_becomes_a_block(self):
        self.client.chat("SYSTEM", [{"role": "user", "text": "case"}], [])
        content = self.sent[0]["messages"][0]["content"]
        self.assertEqual(content[0]["text"], "case")
        self.assertIn("cache_control", content[0])

    def test_system_prompt_has_no_per_case_placeholders(self):
        self.assertNotIn("{agency}", SYSTEM_PROMPT)

    def test_claude_inlines_images_and_openai_keeps_text(self):
        image = {"media_type": "image/png", "data": "QQ=="}
        msgs = AnthropicChat._messages([{"role": "user", "text": "see this", "images": [image]}])
        self.assertEqual(msgs[0]["content"][0]["text"], "see this")
        self.assertEqual(msgs[0]["content"][1]["source"]["data"], "QQ==")
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "x"}):
            client = OpenAIChat(Config())
        openai = client._messages("sys", [{"role": "user", "text": "see this", "images": [image]}])
        self.assertEqual(openai[-1]["content"], "see this")


if __name__ == "__main__":
    unittest.main()
