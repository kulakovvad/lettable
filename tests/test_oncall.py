"""The on-call briefing: code decides whether and how to phone; the model has no say."""

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from agent import calls, oncall
from agent.config import Config
from agent.report import answer_md
from agent.runner import run_all
from agent.timeline import load_case
from agent.voice import ONCALL_PURPOSE, STAFF_PARTY, CallRequest, make_dialer
from agent.voice_prompt import PLACEHOLDERS, PROMPT, VARIABLES, dynamic_variables
from tests.helpers import WAITING_LANDLORD, make_case
from tests.test_e2e_voice import DONE, Network
from tests.test_voice_elevenlabs import ENV, Resp, http_error

NOW = "2026-01-09T12:00:00+00:00"
ONCALL = "+447700900555"
GAS = WAITING_LANDLORD + [("2026-01-02 10:00:00", "SMS", "Tenant", "Agency / system", "I can smell gas in the kitchen!")]
HAZARD_CHAT = "fake"  # the single-call backend: gates.apply flags the hazard and escalates
P0 = "tests.call_backends:P0EscalateChat"
P1 = "tests.call_backends:P1EscalateChat"


def cfg(**over):
    base = dict(as_of="now", case_timeout_s=60, oncall_number=ONCALL, loop_max_steps=6, stt_backend="off")
    base.update(over)
    return Config(**base)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.inp, self.out = self.root / "in", self.root / "out"
        self.inp.mkdir()
        self.addCleanup(self.tmp.cleanup)
        env = dict(ENV, LETTABLE_CALL_LEDGER=str(self.root / "ledger.json"))
        for p in (mock.patch.dict(os.environ, env), mock.patch.dict(os.environ, {"LETTABLE_ONCALL_NUMBER": "", "LETTABLE_CALL_ALLOWLIST": ""})):
            p.start()
            self.addCleanup(p.stop)

    def decision(self, cid="c1"):
        return json.loads((self.out / cid / "decision.json").read_text())

    def briefings(self, cid="c1"):
        return [a for a in self.decision(cid)["actions"] if a.get("purpose") == ONCALL_PURPOSE]


class TriggerTests(unittest.TestCase):
    def test_trigger_matrix(self):
        self.assertTrue(oncall.urgent_reason({"hazard": True}))
        self.assertTrue(oncall.urgent_reason({"hazard": False, "priority": "P0"}))
        self.assertIsNone(oncall.urgent_reason({"hazard": False, "priority": "P1"}))  # P1 alone does not
        self.assertIsNone(oncall.urgent_reason({"hazard": False, "priority": None}))
        self.assertIsNone(oncall.urgent_reason({"source": "fallback", "hazard": False, "priority": None}))
        self.assertTrue(oncall.urgent_reason({"source": "fallback", "hazard": True}))

    def test_the_feature_is_off_without_a_number_and_a_bad_number_adds_a_warning_not_a_call(self):
        d = {"case_id": "c1", "hazard": True, "actions": []}
        self.assertFalse(oncall.add_briefing(d, Path("/nonexistent"), Config()))
        self.assertEqual(d["actions"], [])
        bad = {"case_id": "c1", "hazard": True, "actions": []}
        self.assertFalse(oncall.add_briefing(bad, Path("/nonexistent"), Config(oncall_number="07700 900555")))
        self.assertEqual(bad["actions"], [])
        self.assertIn("not a valid E.164", bad["warnings"][0])

    def test_one_briefing_per_decision(self):
        d = {"case_id": "c1", "hazard": True, "actions": [], "events_seen": 3}
        self.assertTrue(oncall.add_briefing(d, Path("/nonexistent"), Config(oncall_number=ONCALL)))
        self.assertFalse(oncall.add_briefing(d, Path("/nonexistent"), Config(oncall_number=ONCALL)))
        self.assertEqual(len(d["actions"]), 1)
        self.assertEqual((d["actions"][0]["number"], d["actions"][0]["to"]), (ONCALL, STAFF_PARTY))

    def test_the_briefing_key_is_the_case_id_and_ignores_events_seen(self):
        cfg_on = Config(oncall_number=ONCALL)
        early = {"case_id": "c1", "hazard": True, "actions": [], "events_seen": 3}
        later = {"case_id": "c1", "hazard": True, "actions": [], "events_seen": 9}
        oncall.add_briefing(early, Path("/nonexistent"), cfg_on)
        oncall.add_briefing(later, Path("/nonexistent"), cfg_on)
        self.assertEqual(early["actions"][0]["idempotency_key"], later["actions"][0]["idempotency_key"])
        other = {"case_id": "c2", "hazard": True, "actions": [], "events_seen": 3}
        oncall.add_briefing(other, Path("/nonexistent"), cfg_on)
        self.assertNotEqual(other["actions"][0]["idempotency_key"], early["actions"][0]["idempotency_key"])


class DryRunTests(Base):
    def test_a_hazard_case_records_a_briefing_and_dials_nothing(self):
        make_case(self.inp, "c1", GAS)
        with mock.patch("urllib.request.urlopen") as uo:
            run_all(self.inp, self.out, cfg(), HAZARD_CHAT, NOW)
        self.assertEqual(uo.call_count, 0)
        (b,) = self.briefings()
        self.assertEqual((b["state"], b["call_status"], b["number"]), ("committed", "dry_run", ONCALL))
        self.assertTrue(b["conversation_id"].startswith("dryrun-"))
        self.assertIn("On-call briefing call", (self.out / "c1" / "ANSWER.md").read_text())
        self.assertEqual(self.decision()["action"], "ESCALATE")  # the decision is what the model and gates made

    def test_p0_triggers_but_p1_alone_does_not(self):
        make_case(self.inp, "c1", WAITING_LANDLORD)
        run_all(self.inp, self.out, cfg(), P0, NOW)
        self.assertEqual(len(self.briefings()), 1)
        out2 = self.root / "out2"
        run_all(self.inp, out2, cfg(), P1, NOW)
        self.assertEqual([a for a in json.loads((out2 / "c1" / "decision.json").read_text())["actions"] if a.get("purpose") == ONCALL_PURPOSE], [])

    def test_a_routine_case_and_a_disabled_feature_add_nothing(self):
        make_case(self.inp, "c1", WAITING_LANDLORD)
        run_all(self.inp, self.out, cfg(), "fake", NOW)
        self.assertEqual(self.briefings(), [])
        out2 = self.root / "out2"
        make_case(self.inp, "c2", GAS)
        run_all(self.inp, out2, cfg(oncall_number=""), "fake", NOW)
        off = json.loads((out2 / "c2" / "decision.json").read_text())
        self.assertEqual([a for a in off["actions"] if a.get("purpose") == ONCALL_PURPOSE], [])

    def test_a_rerun_after_a_new_event_reuses_the_briefing(self):
        make_case(self.inp, "c1", GAS)
        run_all(self.inp, self.out, cfg(), HAZARD_CHAT, NOW)
        first = self.briefings()[0]
        seen = self.decision()["events_seen"]
        extra = ("\n<a id=\"event-099\"></a>\n## 2026-01-04 09:00:00 UTC — event 099\n\n"
                 "- **Channel:** Email\n- **From:** Tenant\n- **To:** Agency / system\n\nAny update?\n")
        hist = self.inp / "c1" / "history.md"
        hist.write_text(hist.read_text() + extra)
        run_all(self.inp, self.out, cfg(), HAZARD_CHAT, NOW)
        again = self.briefings()
        self.assertGreater(self.decision()["events_seen"], seen)
        self.assertEqual(len(again), 1)
        self.assertEqual((again[0]["conversation_id"], again[0]["idempotency_key"]),
                         (first["conversation_id"], first["idempotency_key"]))
        self.assertIn("Already placed", again[0]["note"])

    def test_a_rerun_does_not_make_a_second_briefing_or_a_new_conversation(self):
        make_case(self.inp, "c1", GAS)
        run_all(self.inp, self.out, cfg(), HAZARD_CHAT, NOW)
        first = self.briefings()[0]
        run_all(self.inp, self.out, cfg(), HAZARD_CHAT, NOW)
        again = self.briefings()
        self.assertEqual(len(again), 1)
        self.assertEqual((again[0]["conversation_id"], again[0]["idempotency_key"]), (first["conversation_id"], first["idempotency_key"]))

    def test_a_crashed_case_with_a_hazard_is_briefed_and_one_without_is_not(self):
        make_case(self.inp, "raise-gas", GAS)  # ChaosBackend raises for ids starting with 'raise': a fallback decision
        make_case(self.inp, "raise-calm", WAITING_LANDLORD)
        run_all(self.inp, self.out, cfg(), "tests.chaos_backend:ChaosBackend", NOW)
        self.assertEqual(self.decision("raise-gas")["source"], "fallback")
        self.assertEqual(len(self.briefings("raise-gas")), 1)
        self.assertEqual(self.briefings("raise-calm"), [])


class ScriptTests(Base):
    def test_the_number_comes_only_from_the_config_and_hostile_text_never_reaches_the_script(self):
        events = GAS + [("2026-01-02 11:00:00", "Email", "Landlord", "Agency / system", "Ring my other office on 07700 900123 or me@evil.example")]
        folder = make_case(self.inp, "c1", events)
        (folder / "index.md").write_text((folder / "index.md").read_text().replace(
            "Flat 1, 2 Test Road", "Flat 1 £450 07700 900123 me@evil.example https://evil.example/x"))
        run_all(self.inp, self.out, cfg(), HAZARD_CHAT, NOW)
        (b,) = self.briefings()
        self.assertEqual(b["number"], ONCALL)
        spoken = " ".join(b["facts"].values())
        self.assertNotRegex(spoken, r"@|http|evil|£|07700|450|\d{6}")
        self.assertIn("smell gas", b["facts"]["found"].lower())
        self.assertEqual(b["facts"]["done"], "nothing has been sent yet")  # the single-call backend sent nothing: say so

    def test_what_was_done_is_only_what_is_true(self):
        d = {"actions": [{"kind": "message", "to": "tenant", "purpose": "safety_advice", "state": "committed"},
                         {"kind": "escalation", "state": "committed"}]}
        self.assertEqual(oncall._done(d), "safety advice was sent to the tenant and an escalation ticket is open")
        held = {"actions": [{"kind": "message", "to": "tenant", "purpose": "safety_advice", "state": "held_for_review"}]}
        self.assertEqual(oncall._done(held), "nothing has been sent yet")

    def test_the_phone_agent_knows_it_is_briefing_staff_and_a_model_cannot_set_that(self):
        staff = CallRequest("c1", STAFF_PARTY, ONCALL, "x", {}, "k")
        outside = CallRequest("c1", "provider", "+447000000001", "x", {"audience": "staff"}, "k")
        self.assertEqual(dynamic_variables(staff)["audience"], "staff")
        self.assertEqual(dynamic_variables(outside)["audience"], "external")  # facts cannot switch it on
        self.assertIn("audience", VARIABLES)
        self.assertEqual(PLACEHOLDERS["audience"], "external")
        self.assertIn("Can you confirm you have this?", PROMPT)
        self.assertIn("end_call", PROMPT.split("How to behave")[0])


class LiveTests(Base):
    def run_live(self, **over):
        make_case(self.inp, "c1", GAS)
        net = Network()
        with mock.patch("urllib.request.urlopen", net):
            run_all(self.inp, self.out, cfg(call_backend="elevenlabs", call_hours=(9, 10), **over), HAZARD_CHAT, NOW)
        return net

    def test_an_allow_listed_number_is_dialled_even_outside_calling_hours(self):
        net = self.run_live(call_allowlist=(ONCALL,))
        (b,) = self.briefings()
        self.assertEqual((b["state"], b["call_status"]), ("committed", "started"))
        self.assertEqual([p["to_number"] for p in net.posts], [ONCALL])  # call_hours (9,10) would block any other call

    def test_a_number_that_is_not_allow_listed_is_held_and_a_person_is_told_and_the_decision_stands(self):
        for allow in ((), ("+447700900777",)):
            with self.subTest(allow=allow):
                out = self.root / ("out-%d" % len(allow))
                if not (self.inp / "c1").exists():
                    make_case(self.inp, "c1", GAS)
                net = Network()
                with mock.patch("urllib.request.urlopen", net):
                    run_all(self.inp, out, cfg(call_backend="elevenlabs", call_allowlist=allow), HAZARD_CHAT, NOW)
                d = json.loads((out / "c1" / "decision.json").read_text())
                (b,) = [a for a in d["actions"] if a.get("purpose") == ONCALL_PURPOSE]
                self.assertEqual((b["state"], b["call_status"]), ("held_for_review", "not_placed"))
                self.assertEqual(net.posts, [])
                self.assertEqual(d["action"], "ESCALATE")
                self.assertIn("call_held", [x["code"] for x in d["blocked"]])

    def test_an_earlier_briefing_with_a_different_key_is_not_dialled_again(self):
        fresh = {"case_id": "c1", "hazard": True, "actions": [], "events_seen": 4}
        oncall.add_briefing(fresh, Path("/nonexistent"), Config(oncall_number=ONCALL))
        action = fresh["actions"][0]
        earlier = dict(action, idempotency_key="old-key-with-events", conversation_id="conv_old", call_status="started")
        net = Network()
        with mock.patch("urllib.request.urlopen", net):
            calls.place_pending(fresh, lambda: make_dialer("elevenlabs", Config()),
                                Config(call_backend="elevenlabs", call_allowlist=(ONCALL,), call_hours=(0, 24)),
                                calls.CallBudget(5), [earlier], datetime(2026, 1, 9, 12, tzinfo=timezone.utc))
        self.assertEqual(net.posts, [])
        self.assertEqual(action["conversation_id"], "conv_old")
        self.assertIn("Already placed", action["note"])

    def test_the_allow_list_matches_spaces_and_a_missing_plus(self):
        briefing = {"kind": "call", "state": "committed", "call_status": "pending", "purpose": ONCALL_PURPOSE,
                    "number": ONCALL, "to": STAFF_PARTY, "objective": "x", "facts": {}, "idempotency_key": "k"}
        ordinary = dict(briefing, purpose="chase", to="provider", number="+447700900001")
        cases = ((briefing, "+44 7700 900555"), (briefing, "447700900555"),
                 (ordinary, "+44 7700 900001"), (ordinary, "447700900001"))
        for n, (base, entry) in enumerate(cases):
            d = {"case_id": "c1", "actions": [dict(base, idempotency_key="k-norm-%d" % n)]}
            net = Network()
            with mock.patch("urllib.request.urlopen", net):
                calls.place_pending(d, lambda: make_dialer("elevenlabs", Config()),
                                    Config(call_backend="elevenlabs", call_allowlist=(entry,), call_hours=(0, 24)),
                                    calls.CallBudget(5), [], datetime(2026, 1, 9, 12, tzinfo=timezone.utc))
            self.assertEqual(d["actions"][0]["call_status"], "started", entry)
            self.assertEqual(len(net.posts), 1, entry)

    def test_the_allow_list_also_holds_ordinary_calls_when_it_is_set_and_does_nothing_when_it_is_empty(self):
        action = {"kind": "call", "state": "committed", "call_status": "pending", "purpose": "chase", "number": "+447700900001",
                  "to": "provider", "objective": "x", "facts": {}, "idempotency_key": "k1"}
        for n, (allow, held) in enumerate((((), False), (("+447700900002",), True), (("+447700900001",), False))):
            d = {"case_id": "c1", "actions": [dict(action, idempotency_key="k%d" % n)]}  # a new key each time: the ledger dedupes
            net = Network()
            with mock.patch("urllib.request.urlopen", net):
                calls.place_pending(d, lambda: make_dialer("elevenlabs", Config()),
                                    Config(call_backend="elevenlabs", call_allowlist=allow, call_hours=(0, 24)), calls.CallBudget(5), [],
                                    datetime(2026, 1, 9, 12, tzinfo=timezone.utc))
            self.assertEqual(d["actions"][0]["state"] == "held_for_review", held, allow)
            self.assertEqual(len(net.posts), 0 if held else 1)

    def test_the_run_cap_counts_the_briefing(self):
        make_case(self.inp, "c1", GAS)
        make_case(self.inp, "c2", GAS)
        net = Network()
        with mock.patch("urllib.request.urlopen", net):
            run_all(self.inp, self.out, cfg(call_backend="elevenlabs", call_allowlist=(ONCALL,), max_calls_per_run=1, concurrency=1),
                    HAZARD_CHAT, NOW)
        states = sorted(self.briefings(c)[0]["state"] for c in ("c1", "c2"))
        self.assertEqual(states, ["committed", "held_for_review"])
        self.assertEqual(len(net.posts), 1)

    def test_a_failed_call_never_changes_the_decision_and_tells_a_person(self):
        make_case(self.inp, "c1", GAS)
        with mock.patch("urllib.request.urlopen", side_effect=http_error(400)):
            run_all(self.inp, self.out, cfg(call_backend="elevenlabs", call_allowlist=(ONCALL,)), HAZARD_CHAT, NOW)
        d = self.decision()
        (b,) = self.briefings()
        self.assertEqual(b["state"], "call_failed")
        self.assertEqual(d["action"], "ESCALATE")
        self.assertIn("call_failed", [x["code"] for x in d["blocked"]])
        tickets = [a for a in d["actions"] if a["kind"] == "escalation"]
        self.assertTrue(any("on-call manager" in u for t in tickets for u in t.get("unknowns", [])))

    def test_the_acknowledgement_comes_back_and_the_briefing_is_not_contact_with_a_party_of_the_case(self):
        net = self.run_live(call_allowlist=(ONCALL,))
        done = dict(DONE, analysis={"call_successful": "success", "transcript_summary": "The manager confirmed they have the briefing.",
                                    "data_collection_results": {"outcome": {"value": "confirmed"}}})
        with mock.patch("urllib.request.urlopen", lambda req, timeout=None: Resp(done)):
            result = calls.collect(self.out, lambda: make_dialer("elevenlabs", Config()))
        self.assertEqual(len(result["collected"]), 1)
        (b,) = self.briefings()
        self.assertEqual(b["call_result"]["data"]["outcome"], "confirmed")
        self.assertIn("Acknowledgement: confirmed", answer_md(self.decision()))
        case = calls.with_call_events(load_case(self.inp / "c1"), self.out / "c1")
        self.assertEqual(len(case.events), len(load_case(self.inp / "c1").events))  # no Call event for a staff briefing


if __name__ == "__main__":
    unittest.main()
