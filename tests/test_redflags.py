"""Red-flag detectors, gate enforcement, and what is shown to the model."""

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent import gates, redflags
from agent.chat import ScriptedChat, Turn
from agent.fallback import fallback_decision
from agent.config import Config
from agent.loop import run_loop
from agent.report import answer_md, reasoning_md
from agent.schema import Proposal
from agent.timeline import load_case
from tests.helpers import WAITING_LANDLORD, make_case
from tests.loop_backends import call, submit

NOW = datetime(2026, 1, 2, 12, 0, tzinfo=timezone.utc)
CFG = Config(loop_max_steps=4, as_of="now")
EVALS = Path(__file__).resolve().parent.parent / "evals" / "exceptions"


def prop(action="WAIT", **kw):
    base = dict(action=action, reason="because the timeline says so", confidence=0.9, message="")
    base.update(kw)
    return Proposal.from_dict(base)


def one_event(root, cid, body, sender="Tenant"):
    events = [("2026-01-02 10:00:00", "Email", sender, "Agency", body)]
    return load_case(make_case(root, cid, events))


class DetectorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.n = 0

    def tearDown(self):
        self.tmp.cleanup()

    def case(self, body, sender="Tenant"):
        self.n += 1
        return one_event(self.root, "c%d" % self.n, body, sender)

    def cats(self, body, sender="Tenant"):
        return [f["category"] for f in redflags.scan(self.case(body, sender))]

    def test_payment_redirection_and_direct_debit_force_accounts(self):
        for text in (
            "Please note we have changed banks. New account sort code 20-45-77. Update your records.",
            "Please complete the attached Direct Debit mandate so we can collect the fee.",
            "With immediate effect please pay all invoices to our new account.",
        ):
            flags = redflags.scan(self.case(text, "Contractor"))
            self.assertEqual(flags[0]["category"], "payment", text)
            self.assertTrue(flags[0]["force"])
            self.assertEqual(flags[0]["route"], "accounts")
            self.assertEqual(flags[0]["priority"], "P1")

    def test_payment_negation_and_false_positives(self):
        for text in (
            "Our bank details have not changed. Please ignore any email that says otherwise.",
            "We do not use direct debit for this contractor.",
            "The visit is delayed because of the bank holiday on Monday.",
            "Please pay the invoice to the account on file.",
            "Please deposit the keys at the office.",
            "The landlord will pay by bank transfer as usual.",
        ):
            self.assertNotIn("payment", self.cats(text), text)

    def test_legal_deposit_and_section_21(self):
        flags = redflags.scan(self.case(
            "I've taken advice from a solicitor and I'll be claiming compensation at the tribunal."))
        self.assertEqual(flags[0]["category"], "legal")
        self.assertEqual(flags[0]["route"], "property_manager")
        self.assertTrue(flags[0]["force"])
        flags = redflags.scan(self.case(
            "The cleaning will be deducted from my deposit. I am raising a dispute with the deposit protection scheme."))
        self.assertEqual(flags[0]["category"], "legal")
        flags = redflags.scan(self.case("We have served a Section 21 notice."))
        self.assertEqual(flags[0]["category"], "legal")

    def test_legal_negation_and_false_positives(self):
        for text in (
            "Please confirm this is not a Section 21 notice.",
            "There is no solicitor involved and we are not claiming compensation.",
            "Please deposit the keys with the concierge.",
            "The tenant left the flat clean. No deposit deduction is proposed.",
        ):
            self.assertNotIn("legal", self.cats(text), text)

    def test_vulnerability_needs_both_a_person_and_a_lost_service(self):
        flags = redflags.scan(self.case(
            "The boiler has stopped completely - no hot water and no heating. I'm 34 weeks pregnant and have a baby."))
        self.assertEqual(flags[0]["category"], "vulnerability")
        self.assertEqual(flags[0]["priority"], "P1")
        self.assertTrue(flags[0]["force"])
        self.assertEqual(self.cats("I am pregnant but the heating is working and the hot water is fine."), [])
        self.assertEqual(self.cats("There is no heating, please book a boiler service."), [])
        self.assertEqual(self.cats("The tenant is not vulnerable and there is no heating problem."), [])
        self.assertNotIn("vulnerability", self.cats("Just to be clear there's no smell of gas, the oven just doesn't get hot."))

    def test_abuse_and_its_negation(self):
        flags = redflags.scan(self.case(
            "If it's not sorted by tomorrow I'm coming down to your office and you'll regret it."))
        self.assertEqual(flags[0]["category"], "abuse")
        self.assertTrue(flags[0]["force"])
        self.assertNotIn("abuse", self.cats("I'm not coming down to your office. You will not regret helping us."))
        self.assertNotIn("abuse", self.cats("There is no threat to the staff."))

    def test_failed_action_is_not_forcing(self):
        bounced = self.case("Undeliverable: recipient address rejected: user unknown.", "Mail Delivery System")
        flags = redflags.scan(bounced)
        self.assertEqual(flags[0]["category"], "failed_action")
        self.assertFalse(flags[0]["force"])
        self.assertIn("another channel", flags[0]["guidance"])
        self.assertNotIn("failed_action", self.cats("Left one voicemail and they called back."))
        self.assertNotIn("failed_action", self.cats("The email did not bounce. Delivery has not failed."))

    def test_repeated_voicemail_is_one_advisory_flag(self):
        events = [
            ("2026-01-02 10:00:00", "Call", "Agency", "Contractor", "Call went to voicemail. Left a message."),
            ("2026-01-05 10:00:00", "Call", "Agency", "Contractor", "Second call went to voicemail again."),
        ]
        case = load_case(make_case(self.root, "vm", events))
        flags = redflags.scan(case)
        self.assertEqual([f["category"] for f in flags], ["failed_action"])
        self.assertFalse(flags[0]["force"])


class GateAndLoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.n = 0

    def tearDown(self):
        self.tmp.cleanup()

    def test_payment_flag_overrides_wait_and_routes_to_accounts(self):
        events = WAITING_LANDLORD + [(
            "2026-01-02 10:00:00", "Email", "Contractor", "Agency",
            "We have changed banks. Sort code 20-45-77. Please update your records and pay the new account.",
        )]
        folder = make_case(self.root, "pay", events)
        case = load_case(folder)
        d = gates.apply(case, prop("WAIT"), Config(), NOW)
        self.assertEqual(d.action, "ESCALATE")
        self.assertEqual(d.red_flags[0]["category"], "payment")
        chat = ScriptedChat([
            Turn(calls=[call("schedule_followup", 1, after_hours=48, waiting_on="landlord", reason="Asked today.")]),
            Turn(calls=[submit("WAIT")]),
        ])
        decided = run_loop(case, chat, CFG, NOW, folder)
        self.assertEqual(decided.action, "ESCALATE")
        self.assertEqual(decided.priority, "P1")
        ticket = [a for a in decided.actions if a["kind"] == "escalation"][0]
        self.assertEqual(ticket["route"], "accounts")
        self.assertEqual(ticket["state"], "committed")
        self.assertIn("CODE RED FLAGS", chat.seen[0][0]["text"])
        self.assertIn("changed banks", chat.seen[0][0]["text"])
        text = reasoning_md(decided.to_dict())
        self.assertIn("## Red flags", text)
        self.assertIn("payment", text)
        self.assertIn("respond_by", ticket)
        self.assertTrue(ticket["recommended"].lower().startswith("recommended:"))
        self.assertGreaterEqual(len(ticket["options"]), 2)

    def test_failed_bounce_does_not_override_a_real_next_step(self):
        events = [(
            "2026-04-17 14:55:20", "Email", "Mail Delivery System", "Agency",
            "Undeliverable: your message to the tenant could not be delivered: recipient address rejected.",
        )]
        case = load_case(make_case(self.root, "bounce", events))
        d = gates.apply(case, prop("ASK_TENANT", message="Please reply by text with a working email."), Config(), NOW)
        self.assertEqual(d.action, "ASK_TENANT")
        self.assertEqual(d.red_flags[0]["category"], "failed_action")
        self.assertFalse(d.red_flags[0]["force"])

    def test_hazard_route_stays_on_call_when_there_is_no_payment_flag(self):
        events = WAITING_LANDLORD + [("2026-01-01 10:00:00", "SMS", "Tenant", "Agency", "I can smell gas in the kitchen")]
        folder = make_case(self.root, "gas", events)
        chase = dict(to="landlord", purpose="chase", priority="P3", evidence_refs=["event-002"],
                     body="Hello, following up on the approval request for the dishwasher. Thank you.")
        chat = ScriptedChat([
            Turn(calls=[call("send_message", 1, **chase)]),
            Turn(calls=[submit("CHASE_LANDLORD")]),
        ])
        d = run_loop(load_case(folder), chat, CFG, datetime(2026, 1, 8, tzinfo=timezone.utc), folder)
        self.assertEqual(d.action, "ESCALATE")
        ticket = [a for a in d.actions if a["kind"] == "escalation"][0]
        self.assertEqual(ticket["route"], "on_call_emergency")
        self.assertEqual([a["state"] for a in d.actions if a["kind"] == "message"], ["held_for_review"])

    def test_model_written_tenant_update_stays_held_on_escalation(self):
        events = WAITING_LANDLORD + [(
            "2026-01-02 10:00:00", "Email", "Tenant", "Agency",
            "If this is not sorted I'm coming down to your office and you'll regret it.",
        )]
        safe = dict(to="tenant", purpose="update", priority="P2", evidence_refs=["event-004"],
                    body="Thank you for your message. A colleague will be in touch shortly. Northbridge Lettings.")
        unsafe = dict(to="tenant", purpose="update", priority="P2", evidence_refs=["event-004"],
                      body="Thank you. Please pay the new account and we have approved the compensation.")
        info = dict(to="tenant", purpose="request_info", priority="P3", evidence_refs=["event-001"],
                    body="Hello, could you send a photo of the dishwasher leak please? Thank you.")
        folder = make_case(self.root, "hold", events)
        chat = ScriptedChat([
            Turn(calls=[call("send_message", 1, **safe), call("escalate_to_human", 2, priority="P1",
                             route="property_manager", summary="Threat to staff.", known=["Threat in the latest email"],
                             unknowns=["Whether anyone is at the office"], tried=["Read the email"],
                             options=["Call the tenant on a known number", "Ask the property manager to respond"],
                             evidence_refs=["event-004"])]),
            Turn(calls=[submit("ESCALATE", priority="P1")]),
        ])
        d = run_loop(load_case(folder), chat, CFG, NOW, folder)
        self.assertEqual([a["state"] for a in d.actions if a["kind"] == "message"], ["held_for_review"])
        self.assertEqual([a["state"] for a in d.actions if a["kind"] == "escalation"], ["committed"])

        folder2 = make_case(self.root, "hold-bad", events)
        chat2 = ScriptedChat([
            Turn(calls=[call("send_message", 1, **unsafe)]),
            Turn(calls=[submit("ESCALATE", priority="P1")]),
        ])
        d2 = run_loop(load_case(folder2), chat2, CFG, NOW, folder2)
        self.assertEqual([a["state"] for a in d2.actions if a["kind"] == "message"], ["held_for_review"])

        folder3 = make_case(self.root, "hold-ask", events)
        chat3 = ScriptedChat([
            Turn(calls=[call("send_message", 1, **info)]),
            Turn(calls=[submit("ESCALATE", priority="P1")]),
        ])
        d3 = run_loop(load_case(folder3), chat3, CFG, NOW, folder3)
        self.assertEqual([a["state"] for a in d3.actions if a["kind"] == "message"], ["held_for_review"])


class EvalCaseTests(unittest.TestCase):
    def test_injected_exceptions_match_the_rubric_categories(self):
        expect = {
            "e02": {"payment"}, "e03": {"payment"}, "e04": {"failed_action"}, "e05": {"failed_action"},
            "e09": {"vulnerability"}, "e11": {"legal"}, "e12": {"legal"}, "e19": {"abuse"},
        }
        quiet = ["e01", "e06", "e07", "e08", "e10", "e13", "e14", "e15", "e16", "e17", "e18"]
        for cid, cats in expect.items():
            flags = redflags.scan(load_case(EVALS / cid))
            self.assertEqual({f["category"] for f in flags}, cats, cid)
            if cats == {"failed_action"}:
                self.assertFalse(any(f["force"] for f in flags), cid)
            else:
                self.assertTrue(all(f["force"] for f in flags), cid)
        for cid in quiet:
            forced = [f for f in redflags.scan(load_case(EVALS / cid)) if f["force"]]
            self.assertEqual(forced, [], "%s %s" % (cid, forced))


class FallbackHandoverTests(unittest.TestCase):
    def test_fallback_answer_has_title_request_digest_and_ticket(self):
        with tempfile.TemporaryDirectory() as tmp:
            events = WAITING_LANDLORD + [(
                "2026-01-02 10:00:00", "Email", "Tenant", "Agency", "The dishwasher is still leaking.")]
            case = load_case(make_case(Path(tmp), "001", events, title="Dishwasher repair", request="Dishwasher leaks."))
            d = fallback_decision("001", "error", "RuntimeError: model exploded", NOW, case, Config())
        self.assertEqual(d.title, "Dishwasher repair")
        self.assertIn("Dishwasher leaks", d.request)
        self.assertEqual(d.action, "ESCALATE")
        self.assertEqual(len(d.actions), 1)
        ticket = d.actions[0]
        self.assertEqual(ticket["kind"], "escalation")
        self.assertEqual(ticket["state"], "committed")
        self.assertTrue(ticket["respond_by"])
        self.assertGreaterEqual(len(ticket["options"]), 2)
        self.assertTrue(ticket["recommended"].lower().startswith("recommended:"))
        blob = " ".join(ticket["known"])
        self.assertIn("event-", blob)
        self.assertIn("Dishwasher", blob)
        text = answer_md(d.to_dict())
        self.assertIn("Dishwasher repair", text)
        self.assertIn("Initial request:", text)
        self.assertIn("Handover", text)
        self.assertIn("Respond by", text)
        self.assertIn("Automatic escalation", d.reason)
