import re
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent.config import Config
from agent.loop import SYSTEM_PROMPT
from agent.policy import policy_topics
from agent.timeline import load_case
from agent.tools import TOOL_SPECS, Toolbox
from tests.helpers import WAITING_LANDLORD, make_case

NOW = datetime(2026, 1, 2, tzinfo=timezone.utc)


class PolicyTests(unittest.TestCase):
    def test_every_topic_is_listed_in_the_tool_description(self):
        spec = next(s for s in TOOL_SPECS if s["name"] == "check_policy")
        for topic in policy_topics(Config()):
            self.assertIn(topic, spec["description"])

    def test_numbers_come_from_config(self):
        text = " ".join(policy_topics(Config(approval_limit_gbp=299.99, chase_after_days=2.5)).values())
        self.assertIn("GBP 299.99", text)
        self.assertIn("2.5 days", text)

    def test_topics_are_not_empty(self):
        for topic, text in policy_topics(Config()).items():
            self.assertGreater(len(text), 100, topic)


class CheckPolicyToolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        case = load_case(make_case(Path(self.tmp.name), "001", WAITING_LANDLORD))
        self.box = Toolbox(case, Config(), NOW)

    def tearDown(self):
        self.tmp.cleanup()

    def test_known_topic(self):
        result = self.box.call("check_policy", {"topic": "Verify_Claims"})
        self.assertEqual(result["topic"], "verify_claims")
        self.assertIn("claim, not a fact", result["policy"])

    def test_unknown_topic_returns_all_with_a_note(self):
        result = self.box.call("check_policy", {"topic": "invoices"})
        self.assertIn("unknown topic", result["note"])
        self.assertEqual(set(result["policy"]), set(policy_topics(Config())))

    def test_several_topics(self):
        result = self.box.call("check_policy", {"topic": "verify_claims, amounts"})
        self.assertEqual(set(result["policy"]), {"verify_claims", "amounts"})
        self.assertNotIn("note", result)

    def test_system_prompt_names_only_real_topics(self):
        topics = set(policy_topics(Config()))
        named = {t.strip() for group in re.findall(r"\[([a-z_, ]+)\]", SYSTEM_PROMPT) for t in group.split(",")}
        named |= set(re.search(r'topic "([a-z_,]+)"', SYSTEM_PROMPT).group(1).split(","))
        self.assertTrue(named)
        self.assertLessEqual(named, topics)

    def test_all(self):
        result = self.box.call("check_policy", {"topic": "all"})
        self.assertNotIn("note", result)
        self.assertIn("amounts", result["policy"])


if __name__ == "__main__":
    unittest.main()
