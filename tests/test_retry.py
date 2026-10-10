import io
import unittest
import urllib.error
from email.message import Message
from unittest import mock

from agent import chat
from agent.chat import ChatError, retry_delay
from agent.config import Config


def http_error(code, retry_after=None):
    headers = Message()
    if retry_after is not None:
        headers["retry-after"] = retry_after
    return urllib.error.HTTPError("https://x", code, "err", headers, io.BytesIO(b'{"error": "busy"}'))


class Ok:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return b'{"ok": true}'


class RetryTests(unittest.TestCase):
    def post(self, outcomes, cfg=None):
        sleeps = []
        with mock.patch.object(chat.urllib.request, "urlopen", side_effect=outcomes), \
                mock.patch.object(chat.time, "sleep", side_effect=sleeps.append):
            result = chat._post("https://x", {}, {}, cfg or Config())
        return result, sleeps

    def test_overloaded_and_rate_limited_calls_are_retried_honouring_retry_after(self):
        result, sleeps = self.post([http_error(529), http_error(429, "7"), Ok()])
        self.assertEqual(result, {"ok": True})
        self.assertEqual(len(sleeps), 2)
        self.assertLessEqual(sleeps[0], 1.0)
        self.assertEqual(sleeps[1], 7.0)

    def test_retry_after_is_capped(self):
        _, sleeps = self.post([http_error(429, "600"), Ok()], Config(retry_after_cap_s=30))
        self.assertEqual(sleeps, [30.0])

    def test_gives_up_after_max_retries(self):
        with self.assertRaises(ChatError):
            self.post([http_error(529)] * 5, Config(max_retries=4))
        with self.assertRaises(ChatError):
            self.post([http_error(400)])

    def test_default_retries_and_delay_shapes(self):
        self.assertEqual(Config().max_retries, 4)
        self.assertEqual(retry_delay(0, "Wed, 21 Oct 2015 07:28:00 GMT", Config()), 0.0)  # a date in the past
        for attempt in range(6):
            self.assertLessEqual(retry_delay(attempt, None, Config()), 8)
        self.assertEqual(retry_delay(0, "junk", Config(retry_after_cap_s=5)) <= 1, True)


if __name__ == "__main__":
    unittest.main()
