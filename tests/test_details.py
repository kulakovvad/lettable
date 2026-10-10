import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from agent import details
from agent.timeline import Attachment, load_case
from tests.helpers import make_case

AG = "Northbridge Lettings"
KEYS = {"schema", "case", "property", "tenant", "landlord", "agency", "provider", "money", "appointments", "timeline",
        "attachments", "decision", "calls", "warnings"}


def ev(n, sender, to, body, channel="Email"):
    return ("2026-01-%02d 10:00:00" % n, channel, sender, to, body)


def card_for(events, decision=None, attachments=()):
    with tempfile.TemporaryDirectory() as tmp:
        if events:
            case = load_case(make_case(Path(tmp), "c1", events))
        else:  # a folder with no files at all
            (Path(tmp) / "c1").mkdir()
            case = load_case(Path(tmp) / "c1")
    if attachments:
        case = replace(case, attachments=tuple(attachments))
    return case, details.build(case, decision or {"action": "WAIT", "source": "model"})


def refs_of(entries):
    return {r for e in entries for r in e["refs"]}


class SchemaTests(unittest.TestCase):
    def test_every_key_is_present_with_the_right_type_on_an_empty_case(self):
        _, card = card_for([])
        self.assertEqual(set(card), KEYS)
        self.assertEqual(card["schema"], "case-card/1")
        self.assertEqual((card["timeline"]["events"], card["timeline"]["first"], card["timeline"]["waiting_on"]), (0, None, None))
        for party in ("tenant", "landlord"):
            self.assertEqual(set(card[party]), {"name", "names", "phones", "emails"})
            self.assertEqual((card[party]["name"], card[party]["phones"]), (None, []))
        self.assertEqual(set(card["agency"]), {"name", "phones", "emails", "staff"})
        self.assertEqual(set(card["provider"]), {"name", "assigned_ref", "phones", "emails"})
        self.assertEqual(set(card["money"]), {"quotes", "invoices", "approval", "payments", "deposit"})
        self.assertEqual(card["money"]["approval"], {"amount_gbp": None, "ref": None, "covers": "unknown"})
        self.assertEqual((card["appointments"], card["calls"], card["attachments"]), ([], [], []))
        json.dumps(card)  # plain JSON types only

    def test_decision_fields_come_from_an_object_or_a_dict(self):
        _, card = card_for([ev(1, "Tenant", AG, "Hi")], {"action": "ESCALATE", "priority": "P1", "confidence": 0.7, "source": "fallback",
                                                          "cause": "timeout", "as_of": "2026-01-02T00:00:00+00:00", "evidence_refs": ["event-001"]})
        self.assertEqual(card["decision"], {"action": "ESCALATE", "priority": "P1", "confidence": 0.7, "decided_by": "fallback",
                                            "cause": "timeout", "as_of": "2026-01-02T00:00:00+00:00", "evidence_refs": ["event-001"]})


class PeopleTests(unittest.TestCase):
    def test_names_come_from_greetings_to_that_party_and_carry_the_event(self):
        events = [ev(1, AG, "Landlord", "Address: Flat 1\nJob Id: X-1\n\nHi Rowan,\n\nWe have a request."),
                  ev(2, AG, "Tenant", "Hello Dawson,\n\nYour visit is booked.")]
        _, card = card_for(events)
        self.assertEqual((card["landlord"]["name"], card["landlord"]["names"]), ("Rowan", [{"value": "Rowan", "refs": ["event-001"]}]))
        self.assertEqual(card["tenant"]["name"], "Dawson")

    def test_explicit_labels_are_read_and_a_greeting_to_someone_else_is_not_taken(self):
        events = [ev(1, "Tenant", AG, "Tenant: Harriet Rowan\nLandlord: Mr Oakley"),
                  ev(2, AG, "Contractor", "Hi Sam,\n\nPlease confirm.")]
        _, card = card_for(events)
        self.assertEqual((card["tenant"]["name"], card["landlord"]["name"]), ("Harriet Rowan", "Mr Oakley"))
        self.assertNotIn("Sam", json.dumps(card["tenant"]) + json.dumps(card["landlord"]))

    def test_two_different_names_are_listed_but_not_guessed(self):
        _, card = card_for([ev(1, AG, "Tenant", "Hi Harriet,\n\nx"), ev(2, AG, "Tenant", "Hi Nora Quinn,\n\ny")])
        self.assertEqual(card["tenant"]["name"], None)
        self.assertEqual([n["value"] for n in card["tenant"]["names"]], ["Harriet", "Nora Quinn"])

    def test_a_first_name_and_the_full_name_are_one_person(self):
        _, card = card_for([ev(1, AG, "Tenant", "Hi Freya,\n\nx"), ev(2, AG, "Tenant", "Hi Freya Bennett,\n\ny")])
        self.assertEqual(card["tenant"]["name"], "Freya Bennett")

    def test_words_that_are_not_names_are_ignored(self):
        _, card = card_for([ev(1, AG, "Tenant", "Hi there,\n\nx"), ev(2, AG, "Tenant", "Dear Sir,\n\ny"), ev(3, AG, "Tenant", "Hello team,\n\nz")])
        self.assertEqual((card["tenant"]["name"], card["tenant"]["names"]), (None, []))

    def test_phones_and_emails_belong_to_the_party_whose_own_messages_have_them(self):
        events = [ev(1, "Tenant", AG, "Ring 07700 900123 or t@example.com"), ev(2, "Tenant", AG, "+44 7700 900123", "SMS"),
                  ev(3, "Contractor", AG, "Me on 07700 900456"), ev(4, AG, "Tenant", "The landlord's number is 07700 900777")]
        _, card = card_for(events)
        self.assertEqual([p["value"] for p in card["tenant"]["phones"]], ["07700 900123"])
        self.assertEqual(card["tenant"]["phones"][0]["refs"], ["event-001", "event-002"])
        self.assertEqual(card["tenant"]["emails"], [{"value": "t@example.com", "refs": ["event-001"]}])
        self.assertEqual([p["value"] for p in card["provider"]["phones"]], ["07700 900456"])
        self.assertEqual([p["value"] for p in card["landlord"]["phones"]], ["07700 900777"])

    def test_agency_staff_and_contact_and_provider_assignment(self):
        events = [ev(1, AG, "Tenant", "Please call us on 07700 900422 to reschedule.\n\nKind regards,\nMaya"),
                  ev(2, AG, "Tenant", "Our maintenance provider **Juniper Surveying** will be attending your property."),
                  ev(3, AG, "Tenant", "Kind regards,\nNorthbridge Lettings")]
        _, card = card_for(events)
        self.assertEqual(card["agency"]["name"], AG)
        self.assertEqual([p["value"] for p in card["agency"]["phones"]], ["07700 900422"])
        self.assertEqual(card["agency"]["staff"], [{"value": "Maya", "refs": ["event-001"]}])
        self.assertEqual((card["provider"]["name"], card["provider"]["assigned_ref"]), ("Juniper Surveying", "event-002"))

    def test_an_unnamed_agency_and_unassigned_provider_stay_null(self):
        _, card = card_for([ev(1, "Agency / system", "Tenant", "Please confirm.")])
        self.assertEqual((card["agency"]["name"], card["provider"]["name"], card["provider"]["assigned_ref"]), (None, None, None))


class MoneyAndFactsTests(unittest.TestCase):
    def test_quotes_with_vat_wording_invoices_and_approval(self):
        events = [ev(1, "Contractor", AG, "Quote: GBP 100 + VAT for the repair."),
                  ev(2, "Contractor", AG, "Alternative quote GBP 95 including parts, labour and VAT."),
                  ev(3, "Contractor", AG, "Quote GBP 50 for a call-out."),
                  ev(4, "Landlord", AG, "Approved GBP 100, go ahead."),
                  ev(5, "Contractor", AG, "Invoice attached: GBP 120.")]
        _, card = card_for(events)
        q = {x["ref"]: x for x in card["money"]["quotes"]}
        self.assertEqual((q["event-001"]["amount_gbp"], q["event-001"]["vat"], q["event-001"]["from"]), (100.0, "excl", "provider"))
        self.assertEqual((q["event-002"]["amount_gbp"], q["event-002"]["vat"]), (95.0, "incl"))
        self.assertEqual(q["event-003"]["vat"], "unknown")
        self.assertEqual(card["money"]["invoices"], [{"amount_gbp": 120.0, "from": "provider", "ref": "event-005"}])
        self.assertEqual(card["money"]["approval"], {"amount_gbp": 100.0, "ref": "event-004", "covers": "amount"})

    def test_an_approval_of_the_visit_has_no_amount(self):
        _, card = card_for([ev(1, "Landlord", AG, "Yes please go ahead and send someone.")])
        self.assertEqual(card["money"]["approval"], {"amount_gbp": None, "ref": "event-001", "covers": "visit"})

    def test_payment_and_deposit_sentences(self):
        events = [ev(1, "Contractor", AG, "Done. Task has been completed without payment. The landlord pays the contractor directly."),
                  ev(2, "Tenant", AG, "I have set up a Direct Debit with Meadow Maintenance."),
                  ev(3, "Contractor", AG, "Please send your bank details and sort code."),
                  ev(4, "Tenant", AG, "Can the cleaning (GBP 80) come out of my deposit?")]
        _, card = card_for(events)
        kinds = {(p["kind"], p["ref"]) for p in card["money"]["payments"]}
        self.assertTrue({("no_charge", "event-001"), ("paid_directly", "event-001"), ("direct_debit", "event-002"), ("bank_details", "event-003")} <= kinds)
        self.assertEqual(card["money"]["deposit"], [{"text": "Can the cleaning (GBP 80) come out of my deposit?", "amount_gbp": 80.0, "ref": "event-004"}])
        self.assertTrue(all(len(p["text"]) <= 200 for p in card["money"]["payments"]))

    def test_appointments_need_an_appointment_word_and_a_date_or_time(self):
        events = [ev(1, AG, "Tenant", "Your appointment is scheduled for Sunday (15/08/2026) after 10am.", "SMS"),
                  ev(2, AG, "Tenant", "The engineer will visit."), ev(3, AG, "Tenant", "See you on Friday for lunch.")]
        _, card = card_for(events)
        self.assertEqual([a["ref"] for a in card["appointments"]], ["event-001"])
        self.assertIn("15/08/2026", card["appointments"][0]["when_text"])

    def test_references_address_forms_and_attachments(self):
        events = [ev(1, AG, "Tenant", "Job Id: NBL-045-9445\nAddress: Flat 12, 182 Meadow Row\n\nHello")]
        att = [Attachment("quote.pdf", "Quote total GBP 200 + VAT"), Attachment("voicemail.mp3", None), Attachment("photo.JPG", None)]
        case, card = card_for(events, attachments=att)
        self.assertEqual(card["property"]["references"], [{"kind": "job id", "value": "NBL-045-9445", "refs": ["event-001"]}])
        self.assertEqual([v["value"] for v in card["property"]["address_variants"]], ["Flat 1, 2 Test Road", "Flat 12, 182 Meadow Row"])
        self.assertEqual([(a["name"], a["available"], a["kind"]) for a in card["attachments"]],
                         [("quote.pdf", True, "pdf"), ("voicemail.mp3", False, "audio"), ("photo.JPG", False, "image")])
        self.assertEqual(card["money"]["quotes"], [{"amount_gbp": 200.0, "vat": "excl", "from": "attachment", "ref": "quote.pdf"}])

    def test_every_ref_points_at_something_real_and_lists_are_capped(self):
        events = [ev(1 + i % 28, AG, "Tenant", "Hello Name%s,\n\nYour appointment is booked for Monday %d." % (chr(65 + i % 26), i)) for i in range(40)]
        case, card = card_for(events)
        real = {"event-%03d" % e.index for e in case.events} | {"index"} | {a.name for a in case.attachments}
        refs = set(refs_of(card["tenant"]["names"])) | {a["ref"] for a in card["appointments"]}
        self.assertTrue(refs <= real)
        self.assertLessEqual(len(card["appointments"]), details.CAP)
        self.assertLessEqual(len(card["tenant"]["names"]), details.CAP)

    def test_hostile_input_never_raises(self):
        nasty = "Address: " + "x" * 50000 + "\n" + "(" * 3000 + "£" * 5000 + "\x00‮ Direct Debit " * 500
        _, card = card_for([ev(1, "Contractor", AG, nasty), ev(2, "Tenant", AG, nasty)])
        self.assertEqual(set(card), KEYS)

    def test_one_extractor_failing_leaves_the_rest_of_the_card(self):
        original = details._money_block
        details._money_block = lambda case: 1 / 0
        try:
            _, card = card_for([ev(1, AG, "Tenant", "Hello Dawson,\n\nx")])
        finally:
            details._money_block = original
        self.assertEqual(card["money"]["quotes"], [])
        self.assertEqual(card["tenant"]["name"], "Dawson")


if __name__ == "__main__":
    unittest.main()
