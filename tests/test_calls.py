import copy
import dataclasses
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent import calls
from agent.chat import ScriptedChat, Turn
from agent.config import Config
from agent.loop import run_loop
from agent.report import answer_md
from agent.runner import run_all
from agent.timeline import load_case
from agent.voice import CallRequest, CallResult, Conversation
from tests.call_backends import CALL
from tests.helpers import make_case
from tests.loop_backends import call, submit

LATER = datetime(2026, 1, 9, 12, 0, tzinfo=timezone.utc)  # 8 days after our last message
SAME_DAY = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
CFG = Config(loop_max_steps=6, as_of="now")
PROVIDER = [
    ("2025-12-30 10:00:00", "Note", "Agency / system", "Not specified", "Request: dishwasher leaks."),
    ("2025-12-30 11:00:00", "Email", "Contractor", "Agency / system", "Hello, I am the assigned engineer. Call me on 07700 900123."),
    ("2026-01-01 09:10:00", "Email", "Agency / system", "Contractor", "Please confirm a visit date for the dishwasher repair."),
    ("2026-01-01 09:11:00", "Update", "Agency / system", "Not specified", "Waiting for Provider (3 days)"),
]
NO_NUMBER = [PROVIDER[0], ("2025-12-30 11:00:00", "Email", "Contractor", "Agency / system", "Hello, I am the assigned engineer.")] + PROVIDER[2:]
GAS = PROVIDER + [("2026-01-01 10:00:00", "SMS", "Tenant", "Agency / system", "I can smell gas! My number is 07700 900456")]


class CountingDialer:
    def __init__(self, fail=False):
        self.placed, self.fail = [], fail

    def place(self, req: CallRequest) -> CallResult:
        if self.fail:
            raise RuntimeError("carrier down")
        self.placed.append(req)
        return CallResult("started", "conv_%d" % len(self.placed), "ringing")

    def fetch(self, conversation_id: str) -> Conversation:
        return Conversation(conversation_id, "done", (("agent", "Hello, when can you visit?"), ("user", "Friday morning.")),
                            "Provider will visit on Friday morning.", "success", {"confirmed_date": "Friday"}, 42.0)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.n = 0

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, turns, events=PROVIDER, now=LATER, cfg=CFG):
        self.n += 1
        folder = make_case(self.root, "c%d" % self.n, events)
        chat = ScriptedChat(turns)
        return run_loop(load_case(folder), chat, cfg, now, folder), chat

    def blocked_code(self, chat, i=1):
        return json.loads(chat.seen[i][-1]["results"][0]["content"])["code"]


class PlaceCallToolTests(Base):
    def test_call_is_staged_with_the_number_from_the_case_and_stands_in_for_a_chase(self):
        d, _ = self.run_script([Turn(calls=[call("place_call", 1, **CALL)]), Turn(calls=[submit("CHASE_PROVIDER")])])
        self.assertEqual(d.action, "CHASE_PROVIDER")
        a = d.actions[0]
        self.assertEqual((a["kind"], a["to"], a["state"], a["call_status"]), ("call", "provider", "committed", "pending"))
        self.assertEqual(a["number"], "+447700900123")
        self.assertIn("Phone call:", d.message)

    def test_no_number_in_the_case_is_blocked(self):
        d, chat = self.run_script([Turn(calls=[call("place_call", 1, **CALL)]), Turn(calls=[submit("WAIT")])], events=NO_NUMBER)
        self.assertEqual(self.blocked_code(chat), "no_number")

    def test_the_model_cannot_supply_a_number_or_invent_one_in_the_facts(self):
        bad = dict(CALL, facts={"callback": "07700 900999"})
        _, chat = self.run_script([Turn(calls=[call("place_call", 1, **bad)]), Turn(calls=[submit("WAIT")])])
        self.assertEqual(self.blocked_code(chat), "unverified_detail")

    def test_a_chase_by_call_follows_the_same_timing_rule_as_a_message(self):
        _, chat = self.run_script([Turn(calls=[call("place_call", 1, **CALL)]), Turn(calls=[submit("WAIT")])], now=SAME_DAY)
        self.assertEqual(self.blocked_code(chat), "too_early")

    def test_only_one_call_per_case(self):
        second = dict(CALL, objective="Ask again whether the engineer can visit on Friday.")
        _, chat = self.run_script([Turn(calls=[call("place_call", 1, **CALL)]), Turn(calls=[call("place_call", 2, **second)]),
                                   Turn(calls=[submit("CHASE_PROVIDER")])])
        self.assertEqual(self.blocked_code(chat, 2), "call_limit")

    def test_on_a_hazard_only_safety_advice_to_the_tenant_goes_out(self):
        other = dict(CALL, purpose="request_info")
        advice = dict(party="tenant", purpose="safety_advice", priority="P0", evidence_refs=["event-005"],
                      objective="Tell the tenant to leave the property, avoid switches and call the gas emergency line.", facts={})
        d, chat = self.run_script([Turn(calls=[call("place_call", 1, **other)]), Turn(calls=[call("place_call", 2, **advice)]),
                                   Turn(calls=[submit("ESCALATE", priority="P0", options=["a", "b"])])], events=GAS)
        self.assertEqual(self.blocked_code(chat, 1), "hazard_escalate")
        a = [x for x in d.actions if x["kind"] == "call"][0]
        self.assertEqual((a["to"], a["purpose"], a["state"], a["number"]), ("tenant", "safety_advice", "committed", "+447700900456"))

    def test_a_safety_advice_call_without_a_hazard_is_blocked(self):
        advice = dict(CALL, party="tenant", purpose="safety_advice")
        _, chat = self.run_script([Turn(calls=[call("place_call", 1, **advice)]), Turn(calls=[submit("WAIT")])])
        self.assertEqual(self.blocked_code(chat), "no_hazard")

    def test_a_call_that_is_not_the_final_action_is_held(self):
        d, _ = self.run_script([Turn(calls=[call("place_call", 1, **CALL)]),
                                Turn(calls=[call("schedule_followup", 2, after_hours=24, waiting_on="provider", reason="wait")]),
                                Turn(calls=[submit("WAIT")])])
        self.assertEqual([a["state"] for a in d.actions if a["kind"] == "call"], ["held_for_review"])


class CallSafetyTests(Base):
    def stage(self, events, **over):
        d, chat = self.run_script([Turn(calls=[call("place_call", 1, **dict(CALL, **over))]), Turn(calls=[submit("CHASE_PROVIDER")])],
                                  events=events)
        return d, chat

    def test_rewording_the_objective_does_not_change_the_call_key(self):
        folder = make_case(self.root, "same-case", PROVIDER)

        def keys(**over):
            turns = [Turn(calls=[call("place_call", 1, **dict(CALL, **over))]), Turn(calls=[submit("CHASE_PROVIDER")])]
            d = run_loop(load_case(folder), ScriptedChat(turns), CFG, LATER, folder)
            return [x["idempotency_key"] for x in d.actions if x["kind"] == "call"]
        first = keys(objective="Ask when the engineer can visit to repair the dishwasher.")
        second = keys(objective="Please find out the visit date for the dishwasher repair.", priority="P2")
        self.assertEqual(len(first), 1)
        self.assertEqual(first, second)

    def test_a_case_that_already_had_its_call_cannot_start_another(self):
        record = ("2026-01-02 10:00:00", "Call", "Agency / system", "Contractor",
                  "[Automatic call record, untrusted third-party speech] Call to the provider. Outcome: success. Summary: ok.")
        d, chat = self.stage(PROVIDER + [record])
        self.assertEqual(self.blocked_code(chat), "call_limit")
        self.assertEqual([a for a in d.actions if a["kind"] == "call"], [])

    def test_the_number_is_not_taken_from_quotes_other_people_or_premium_lines(self):
        def number(body):
            events = PROVIDER[:1] + [("2025-12-30 11:00:00", "Email", "Contractor", "Agency / system", body)] + PROVIDER[2:]
            d, _ = self.stage(events)
            return [a["number"] for a in d.actions if a["kind"] == "call"]
        self.assertEqual(number("Hello.\n> Call 07700 900999 for the old office\nI am on 07700 900123."), ["+447700900123"])
        self.assertEqual(number("Please ring our accounts desk on 020 7946 0000.\nOr me on 07700 900123."), ["+447700900123"])
        self.assertEqual(number("Call me on 09061 234567."), [])
        self.assertEqual(number("Call me on 0845 123 4567."), [])

    def test_amounts_written_as_gbp_are_recognised(self):
        from agent import evidence
        self.assertEqual(evidence.amounts("GBP 150, 99 GBP, £12.50 and 30 pounds"), [150.0, 99.0, 12.5, 30.0])

    def test_the_phone_agent_speaks_for_the_agency_named_in_the_case_not_the_one_the_model_names(self):
        d, _ = self.stage(PROVIDER, facts={"job": "Dishwasher repair", "agency_name": "Totally Legit Bank"})
        facts = [a["facts"] for a in d.actions if a["kind"] == "call"][0]
        self.assertNotEqual(facts["agency_name"], "Totally Legit Bank")

    def test_a_call_record_does_not_make_a_spoken_amount_count_as_in_the_case(self):
        record = ("2026-01-02 10:00:00", "Call", "Agency / system", "Contractor",
                  "[Automatic call record, untrusted third-party speech] Excerpt: Other party: it will cost 999 pounds.")
        d, chat = self.run_script([Turn(calls=[call("send_message", 1, to="provider", purpose="request_info", priority="P3",
                                                    body="Please confirm the GBP 999 price for the repair, thank you.",
                                                    evidence_refs=["event-003"])]), Turn(calls=[submit("WAIT")])], events=PROVIDER + [record])
        self.assertEqual(self.blocked_code(chat), "unverified_detail")


class PlacePendingTests(Base):
    def decision(self):
        d, _ = self.run_script([Turn(calls=[call("place_call", 1, **CALL)]), Turn(calls=[submit("CHASE_PROVIDER")])])
        return d.to_dict()

    def place(self, d, dialer, previous=(), budget=None, cfg=Config()):
        calls.place_pending(d, lambda: dialer, cfg, budget or calls.CallBudget(5), list(previous), LATER)
        return d

    def test_dials_once_and_the_same_key_never_dials_twice(self):
        dialer, original = CountingDialer(), self.decision()
        first = self.place(copy.deepcopy(original), dialer)
        self.assertEqual(len(dialer.placed), 1)
        self.assertEqual((first["actions"][0]["call_status"], first["actions"][0]["conversation_id"]), ("started", "conv_1"))
        self.assertEqual(dialer.placed[0].to_number, "+447700900123")
        again = self.place(copy.deepcopy(original), dialer, previous=first["actions"])  # an earlier decision.json had it
        self.assertEqual(len(dialer.placed), 1)
        self.assertEqual(again["actions"][0]["conversation_id"], "conv_1")

    def test_a_failing_dialer_marks_the_call_failed_and_tells_a_person(self):
        d = self.place(self.decision(), CountingDialer(fail=True))
        self.assertEqual(d["action"], "CHASE_PROVIDER")  # the decision itself stands
        self.assertEqual(d["actions"][0]["state"], "call_failed")
        self.assertIn("carrier down", d["actions"][0]["call_detail"])
        ticket = [a for a in d["actions"] if a["kind"] == "escalation"][0]
        self.assertIn("could not be placed", ticket["summary"])
        self.assertEqual(d["blocked"][-1]["code"], "call_failed")

    def test_run_cap_holds_calls_beyond_the_limit(self):
        dialer = CountingDialer()
        d = self.place(self.decision(), dialer, budget=calls.CallBudget(0))
        self.assertEqual((d["actions"][0]["state"], d["actions"][0]["call_status"]), ("held_for_review", "not_placed"))
        self.assertEqual(dialer.placed, [])

    def test_live_calls_outside_uk_hours_are_held_but_dry_runs_are_recorded(self):
        night = datetime(2026, 1, 9, 3, 0, tzinfo=timezone.utc)
        live = dataclasses.replace(Config(), call_backend="elevenlabs")
        dialer, d = CountingDialer(), self.decision()
        calls.place_pending(d, lambda: dialer, live, calls.CallBudget(5), [], night)
        self.assertEqual((d["actions"][0]["state"], dialer.placed), ("held_for_review", []))
        self.assertEqual(d["blocked"][-1]["code"], "call_held")  # a held call still ends with a person told
        self.assertTrue([a for a in d["actions"] if a["kind"] == "escalation"])
        d2 = self.decision()
        calls.place_pending(d2, lambda: dialer, Config(), calls.CallBudget(5), [], night)
        self.assertEqual(len(dialer.placed), 1)

    def test_a_dry_run_record_does_not_stop_the_later_live_call(self):
        dialer, original = CountingDialer(), self.decision()
        dry = self.place(copy.deepcopy(original), calls_dialer := __import__("agent.voice", fromlist=["DryRunDialer"]).DryRunDialer())
        self.assertTrue(dry["actions"][0]["conversation_id"].startswith("dryrun-"))
        live = dataclasses.replace(Config(), call_backend="elevenlabs", call_hours=(0, 24))
        self.place(copy.deepcopy(original), dialer, previous=dry["actions"], cfg=live)
        self.assertEqual(len(dialer.placed), 1)

    def test_answer_md_lists_the_call_and_its_result(self):
        d = self.place(self.decision(), CountingDialer())
        self.assertIn("Phone call to provider", answer_md(d))
        d["actions"][0]["call_result"] = {"summary": "Visit on Friday."}
        self.assertIn("Result: Visit on Friday.", answer_md(d))


class CollectRobustnessTests(unittest.TestCase):
    def folder(self, root, actions):
        out = Path(root) / "out"
        (out / "c1").mkdir(parents=True)
        decision = {"case_id": "c1", "action": "CHASE_PROVIDER", "reason": "x", "source": "model", "events_seen": 1,
                    "idempotency_key": "k", "warnings": [], "actions": actions}
        (out / "c1" / "decision.json").write_text(json.dumps(decision))
        return out

    def test_one_failed_fetch_does_not_drop_the_other_calls_of_the_case(self):
        class Flaky(CountingDialer):
            def fetch(self, conversation_id):
                if conversation_id == "conv_bad":
                    raise RuntimeError("404")
                return super().fetch(conversation_id)
        call = lambda cid, key: {"id": key, "kind": "call", "to": "provider", "state": "committed", "call_status": "started",
                                 "conversation_id": cid, "idempotency_key": key, "number": "+447000000001", "objective": "x"}
        with tempfile.TemporaryDirectory() as tmp:
            out = self.folder(tmp, [call("conv_bad", "a"), call("conv_ok", "b")])
            result = calls.collect(out, lambda: Flaky())
            self.assertEqual([c["conversation_id"] for c in result["collected"]], ["conv_ok"])
            self.assertEqual(result["errors"][0]["conversation_id"], "conv_bad")
            self.assertTrue((out / "c1" / "calls" / "conv_ok.json").is_file())

    def test_rehearsal_calls_are_skipped_when_the_dialer_is_a_live_one(self):
        dry = {"id": "x", "kind": "call", "to": "provider", "state": "committed", "call_status": "dry_run",
               "conversation_id": "dryrun-abc", "idempotency_key": "k", "number": "+447000000001", "objective": "x"}
        with tempfile.TemporaryDirectory() as tmp:
            out = self.folder(tmp, [dry])
            seen = []

            class Spy(CountingDialer):
                def fetch(self, conversation_id):
                    seen.append(conversation_id)
                    return super().fetch(conversation_id)
            calls.collect(out, lambda: Spy(), skip_dry_run=True)
            self.assertEqual(seen, [])
            calls.collect(out, lambda: Spy())  # the default (a dry-run dialer) still collects them
            self.assertEqual(seen, ["dryrun-abc"])


class RunnerTests(unittest.TestCase):
    CALLS = "tests.call_backends:ProviderCallChat"
    NOW = "2026-01-09T12:00:00+00:00"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.inp, self.out = Path(self.tmp.name) / "in", Path(self.tmp.name) / "out"
        self.inp.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def decision(self, cid):
        return json.loads((self.out / cid / "decision.json").read_text())

    def test_dry_run_records_the_call_and_the_run_cap_applies_across_cases(self):
        for cid in ("a", "b"):
            make_case(self.inp, cid, PROVIDER)
        cfg = Config(as_of="now", max_calls_per_run=1, concurrency=1)
        run_all(self.inp, self.out, cfg, self.CALLS, self.NOW)
        states = sorted(self.decision(c)["actions"][0]["state"] for c in ("a", "b"))
        self.assertEqual(states, ["committed", "held_for_review"])
        placed = [c for c in ("a", "b") if self.decision(c)["actions"][0]["call_status"] == "dry_run"]
        self.assertEqual(len(placed), 1)
        self.assertTrue(self.decision(placed[0])["actions"][0]["conversation_id"].startswith("dryrun-"))

    def test_a_rerun_of_the_same_case_does_not_place_the_call_again(self):
        make_case(self.inp, "a", PROVIDER)
        cfg = Config(as_of="now")
        run_all(self.inp, self.out, cfg, self.CALLS, self.NOW)
        first = self.decision("a")["actions"][0]
        run_all(self.inp, self.out, cfg, self.CALLS, self.NOW)
        second = self.decision("a")["actions"][0]
        self.assertEqual(first["conversation_id"], second["conversation_id"])
        self.assertEqual(second["note"], "Already placed by an earlier run.")

    def test_collect_writes_the_result_once_and_a_rerun_sees_the_call(self):
        make_case(self.inp, "a", PROVIDER)
        cfg = Config(as_of="now")
        run_all(self.inp, self.out, cfg, self.CALLS, self.NOW)
        path = self.out / "a" / "decision.json"
        d = json.loads(path.read_text())
        d["actions"][0].update(conversation_id="conv_1", call_status="started")  # as if ElevenLabs had placed it
        path.write_text(json.dumps(d))
        dialer = CountingDialer()
        got = calls.collect(self.out, lambda: dialer)
        self.assertEqual(got["collected"], [{"case_id": "a", "conversation_id": "conv_1"}])
        record = json.loads((self.out / "a" / "calls" / "conv_1.json").read_text())
        self.assertEqual((record["success"], record["data"], record["party"]), ("success", {"confirmed_date": "Friday"}, "provider"))
        self.assertEqual(self.decision("a")["actions"][0]["call_result"]["summary"], "Provider will visit on Friday morning.")
        self.assertIn("Result: Provider will visit", (self.out / "a" / "ANSWER.md").read_text())
        self.assertEqual(calls.collect(self.out, lambda: dialer)["collected"], [])  # idempotent

        before = self.decision("a")["events_seen"]
        run_all(self.inp, self.out, cfg, self.CALLS, self.NOW)
        self.assertEqual(self.decision("a")["events_seen"], before + 1)  # the call record is now an event

    def test_collect_skips_calls_still_in_progress_and_survives_a_bad_case(self):
        make_case(self.inp, "a", PROVIDER)
        run_all(self.inp, self.out, Config(as_of="now"), self.CALLS, self.NOW)
        (self.out / "broken").mkdir()
        (self.out / "broken" / "decision.json").write_text("{not json")

        class Busy(CountingDialer):
            def fetch(self, conversation_id):
                return Conversation(conversation_id, "in-progress")

        got = calls.collect(self.out, lambda: Busy())
        self.assertEqual(len(got["pending"]), 1)
        self.assertEqual([e["case_id"] for e in got["errors"]], ["broken"])

    def test_the_call_record_is_not_a_reply_and_dry_runs_are_not_events(self):
        folder = make_case(self.inp, "a", PROVIDER)
        case_out = self.out / "a"
        (case_out / "calls").mkdir(parents=True)
        (case_out / "calls" / "x.json").write_text(json.dumps({"party": "provider", "status": "done", "success": "failure",
                                                               "summary": "Voicemail.", "transcript": []}))
        (case_out / "calls" / "y.json").write_text(json.dumps({"party": "provider", "status": "done", "dry_run": True,
                                                               "summary": "Dry run.", "transcript": []}))
        case = calls.with_call_events(load_case(folder), case_out)
        self.assertEqual(len(case.events), len(PROVIDER) + 1)
        e = case.events[-1]
        self.assertEqual((e.channel, e.sender, e.recipient, e.index), ("Call", "Agency / system", "Contractor", len(PROVIDER) + 1))


if __name__ == "__main__":
    unittest.main()
