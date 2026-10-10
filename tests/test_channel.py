"""Who decides to phone: the code (agent/channel.py). The model may ask for a call; the policy decides."""

import dataclasses
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent.channel import phone_allowed, unanswered
from agent.chat import ScriptedChat, Turn
from agent.config import Config
from agent.loop import run_loop
from agent.timeline import load_case
from tests.call_backends import CALL
from tests.helpers import make_case
from tests.loop_backends import call, submit
from tests.test_calls import PROVIDER

AG = "Northbridge Lettings"
NOW = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
CFG = Config()


def sent(day, to="Contractor", channel="Email", hour=9):
    return ("2026-01-%02d %02d:00:00" % (day, hour), channel, AG, to, "Please confirm a visit date for the repair.")


def got(day, sender="Contractor", channel="Email", body="Will do, thanks."):
    return ("2026-01-%02d 10:00:00" % day, channel, sender, AG, body)


BASE = [("2026-01-01 08:00:00", "Note", "Agency / system", "Not specified", "Request: dishwasher leaks.")]


class Matrix(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.n = 0
        self.addCleanup(self.tmp.cleanup)

    def check(self, events, party="provider", purpose="chase", now=NOW, cfg=CFG, urgent=False):
        self.n += 1
        case = load_case(make_case(self.root, "c%d" % self.n, BASE + events))
        return phone_allowed(case, party, purpose, now, cfg, urgent)

    # ---- written contact must have failed
    def test_no_written_message_yet_is_blocked_and_the_hint_says_what_to_do(self):
        ok, why, hint = self.check([])
        self.assertFalse(ok)
        self.assertIn("only 0 unanswered written message(s) to the provider", why)
        self.assertIn("send a message first", hint.lower())

    def test_one_unanswered_message_is_not_enough(self):
        ok, why, hint = self.check([sent(2)])
        self.assertFalse(ok)
        self.assertIn("only 1 unanswered", why)
        self.assertIn("2 go unanswered", why)
        self.assertIn("send_message", hint)

    def test_two_unanswered_messages_old_enough_allow_the_call(self):
        ok, why, _ = self.check([sent(2), sent(4)])
        self.assertTrue(ok)
        self.assertIn("2 written messages to the provider went unanswered", why)

    def test_two_unanswered_but_the_latest_is_too_recent_is_blocked(self):
        ok, why, hint = self.check([sent(2), sent(10, hour=7)])  # 5 hours before NOW
        self.assertFalse(ok)
        self.assertIn("is only 5 hours old", why)
        self.assertIn("WAIT", hint)

    def test_a_reply_in_between_resets_the_count(self):
        self.assertFalse(self.check([sent(2), got(3), sent(4)])[0])  # 1 unanswered since the reply
        self.assertFalse(self.check([sent(2), sent(3), got(4), sent(5)])[0])
        self.assertTrue(self.check([sent(2), got(3), sent(4), sent(5)])[0])  # 2 since the reply

    def test_calls_notes_and_updates_are_not_written_contact(self):
        extra = [("2026-01-02 09:00:00", "Call", AG, "Contractor", "Left a voicemail."),
                 ("2026-01-03 09:00:00", "Update", "Agency / system", "Not specified", "Waiting for Provider (3 days)"),
                 sent(4)]
        ok, why, _ = self.check(extra)
        self.assertFalse(ok)
        self.assertIn("only 1 unanswered", why)

    def test_messages_to_other_parties_do_not_count(self):
        self.assertFalse(self.check([sent(2, to="Landlord"), sent(3, to="Tenant"), sent(4)])[0])

    def test_landlord_follows_the_same_rule(self):
        self.assertFalse(self.check([sent(2, to="Landlord")], party="landlord")[0])
        self.assertTrue(self.check([sent(2, to="Landlord"), sent(4, to="Landlord")], party="landlord")[0])

    # ---- urgent and bounced
    def test_urgent_allows_a_call_with_no_written_contact(self):
        ok, why, _ = self.check([], urgent=True)
        self.assertTrue(ok)
        self.assertIn("urgent", why)

    def test_a_bounce_of_the_latest_message_allows_a_call(self):
        bounce = ("2026-01-03 09:00:00", "Update", "Agency / system", "Contractor", "Delivery failed: mailbox full")
        ok, why, _ = self.check([sent(2), bounce])
        self.assertTrue(ok)
        self.assertIn("did not arrive", why)

    def test_a_bounce_of_an_older_message_does_not(self):
        bounce = ("2026-01-02 12:00:00", "Update", "Agency / system", "Contractor", "Message bounced")
        three = dataclasses.replace(CFG, call_after_unanswered=3)  # isolate the bounce rule from the unanswered rule
        self.assertFalse(self.check([sent(2), bounce, sent(5)], cfg=three)[0])  # a later message went out after the bounce
        self.assertTrue(self.check([sent(2), sent(5), ("2026-01-05 12:00:00", "Update", "Agency / system", "Contractor", "Message bounced")],
                                   cfg=three)[0])  # a bounce of the latest one counts

    def test_bounce_wording_from_the_party_itself_is_not_a_bounce(self):
        self.assertFalse(self.check([sent(2), got(3, body="your last email bounced for me, please resend")])[0])

    def test_a_later_note_that_something_was_not_delivered_is_not_a_bounce(self):
        # a tenant talking about a part, or a system note using the same words, is not a mailer bounce
        tenant = ("2026-01-03 09:00:00", "Email", "Tenant", AG, "The new part was not delivered.")
        self.assertFalse(self.check([sent(2), tenant])[0])
        system = ("2026-01-03 09:00:00", "Update", "Agency / system", "Contractor", "The new part was not delivered.")
        self.assertFalse(self.check([sent(2), system])[0])

    def test_a_bounce_that_does_not_name_this_recipient_does_not_allow_a_call(self):
        unnamed = ("2026-01-03 09:00:00", "Update", "Agency / system", "Not specified", "Message bounced")
        self.assertFalse(self.check([sent(2), unnamed])[0])
        other = ("2026-01-03 09:00:00", "Update", "Agency / system", "Landlord", "Message bounced")
        self.assertFalse(self.check([sent(2), other])[0])
        named = ("2026-01-03 09:00:00", "Email", "Mailer-Daemon", AG, "Undeliverable: returned to sender for the contractor.")
        ok, why, _ = self.check([sent(2), named])
        self.assertTrue(ok)
        self.assertIn("did not arrive", why)

    # ---- tenant
    def test_tenant_who_phoned_in_can_be_phoned_back_for_a_question_only(self):
        phoned = ("2026-01-02 09:00:00", "Call", "Tenant", AG, "The tenant called about the leak.")
        self.assertTrue(self.check([phoned], party="tenant", purpose="request_info")[0])
        self.assertFalse(self.check([phoned], party="tenant", purpose="update")[0])
        self.assertFalse(self.check([phoned], party="tenant", purpose="chase")[0])
        self.assertFalse(self.check([phoned], party="provider", purpose="request_info")[0])  # only the tenant who called

    def test_tenant_otherwise_follows_the_unanswered_rule(self):
        self.assertFalse(self.check([sent(2, to="Tenant")], party="tenant", purpose="request_info")[0])
        self.assertTrue(self.check([sent(2, to="Tenant"), sent(4, to="Tenant")], party="tenant", purpose="request_info")[0])

    def test_safety_advice_needs_the_hazard_which_the_caller_checks(self):
        # the tool applies the hazard rule to safety_advice and skips this policy; the function itself says
        # urgent allows it and not-urgent is the plain unanswered rule
        self.assertTrue(self.check([], party="tenant", purpose="safety_advice", urgent=True)[0])
        self.assertFalse(self.check([], party="tenant", purpose="safety_advice", urgent=False)[0])

    # ---- config and odd input
    def test_the_thresholds_come_from_the_config(self):
        one = dataclasses.replace(CFG, call_after_unanswered=1)
        self.assertTrue(self.check([sent(2)], cfg=one)[0])
        recent = [sent(2), sent(10, hour=7)]
        self.assertFalse(self.check(recent)[0])
        self.assertTrue(self.check(recent, cfg=dataclasses.replace(CFG, call_after_hours=0))[0])
        self.assertFalse(self.check([sent(2), sent(4)], cfg=dataclasses.replace(CFG, call_after_unanswered=3))[0])

    def test_an_unknown_time_is_not_enough(self):
        self.n += 1
        folder = make_case(self.root, "c%d" % self.n, BASE + [sent(2), sent(4)])
        (folder / "history.md").write_text((folder / "history.md").read_text().replace("2026-01-04 09:00:00", "2026-13-99 99:99:99"))
        case = load_case(folder)
        ok, why, _ = phone_allowed(case, "provider", "chase", NOW, CFG, False)
        self.assertFalse(ok)

    def test_an_empty_case_and_a_missing_clock_do_not_raise(self):
        self.n += 1
        (self.root / "empty").mkdir()
        case = load_case(self.root / "empty")
        self.assertFalse(phone_allowed(case, "provider", "chase", NOW, CFG, False)[0])
        self.n += 1
        case2 = load_case(make_case(self.root, "c%d" % self.n, BASE + [sent(2), sent(4)]))
        self.assertFalse(phone_allowed(case2, "provider", "chase", None, CFG, False)[0])
        self.assertEqual(len(unanswered(case2, "provider")), 2)


class ScriptedLoopTests(unittest.TestCase):
    """The model asks for a call too early: the code says no and why, and the model sends a message instead."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.n = 0

    def run_script(self, turns, events):
        self.n += 1
        folder = make_case(self.root, "c%d" % self.n, events)
        chat = ScriptedChat(turns)
        cfg = Config(loop_max_steps=6, as_of="now")
        return run_loop(load_case(folder), chat, cfg, datetime(2026, 1, 9, 12, 0, tzinfo=timezone.utc), folder), chat

    CHASE = dict(to="provider", purpose="chase", priority="P3", evidence_refs=["event-003"],
                 body="Hello, a quick follow-up: could you confirm a visit date for the dishwasher repair? Thank you.")

    def test_a_call_asked_for_too_early_is_refused_and_the_model_recovers_with_a_message(self):
        one_message = [e for e in PROVIDER if "A reminder" not in e[4]]  # PROVIDER has two unanswered; drop the reminder
        d, chat = self.run_script([Turn(calls=[call("place_call", 1, **CALL)]),
                                   Turn(calls=[call("send_message", 2, **self.CHASE)]),
                                   Turn(calls=[submit("CHASE_PROVIDER")])], one_message)
        first = json.loads(chat.seen[1][-1]["results"][0]["content"])
        self.assertEqual(first["code"], "channel_policy")
        self.assertIn("only 1 unanswered", first["why"])
        self.assertIn("send_message", first["hint"])
        self.assertEqual([b["code"] for b in d.blocked], ["channel_policy"])
        self.assertEqual(d.action, "CHASE_PROVIDER")
        kinds = [(a["kind"], a["state"]) for a in d.actions]
        self.assertEqual(kinds, [("message", "committed")])  # the message went out, no call was staged

    def test_with_two_unanswered_messages_the_same_request_is_staged(self):
        d, _ = self.run_script([Turn(calls=[call("place_call", 1, **CALL)]), Turn(calls=[submit("CHASE_PROVIDER")])], PROVIDER)
        self.assertEqual([(a["kind"], a["state"]) for a in d.actions], [("call", "committed")])
        self.assertEqual(d.blocked, [])


if __name__ == "__main__":
    unittest.main()
