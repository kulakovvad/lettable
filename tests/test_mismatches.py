import tempfile
import unittest
from pathlib import Path

from agent import mismatches
from agent.timeline import Attachment, load_case
from dataclasses import replace
from tests.helpers import make_case

AG = "Northbridge Lettings"


def case_for(events, attachments=()):
    with tempfile.TemporaryDirectory() as tmp:
        case = load_case(make_case(Path(tmp), "c1", events))
    return replace(case, attachments=tuple(attachments)) if attachments else case


def ev(n, sender, to, body, channel="Email"):
    return ("2026-01-%02d 10:00:00" % n, channel, sender, to, body)


def kinds(items):
    return [i["kind"] for i in items]


class AddressTests(unittest.TestCase):
    def test_a_different_address_in_the_agency_messages_is_flagged_once_with_all_refs(self):
        events = [ev(1, AG, "Tenant", "Address: Flat 12, 182 Meadow Row, Kingshaven, ZZ5 7ZZ\n\nHello"),
                  ev(2, AG, "Landlord", "Address: **Flat 12, 182 Meadow Row, Kingshaven, ZZ5 7ZZ**\n\nHi")]
        items = mismatches.find(case_for(events))
        self.assertEqual(kinds(items), ["address"])
        self.assertEqual(items[0]["refs"], ["event-001", "event-002"])
        self.assertEqual(items[0]["severity"], "flag")
        self.assertIn("Flat 1, 2 Test Road", items[0]["summary"])

    def test_the_same_address_written_differently_is_not_a_mismatch(self):
        for line in ("Flat 1, 2 Test Road", "2 test road", "FLAT 1 2 TEST ROAD.", "Flat 1, 2 Test Road, Alderwick, ZZ3 2ZZ", "Flat 1"):
            self.assertEqual(mismatches.find(case_for([ev(1, AG, "Tenant", "Address: %s\n\nHello" % line)])), [], line)

    def test_a_different_postcode_or_street_is_flagged(self):
        for line in ("Flat 1, 2 Test Road, ZZ9 9ZZ", "Flat 1, 2 Other Lane", "Flat 3, 2 Test Road"):
            case = replace(case_for([ev(1, AG, "Tenant", "Address: %s" % line)]), property="Flat 1, 2 Test Road, ZZ3 2ZZ")
            self.assertEqual(kinds(mismatches.find(case)), ["address"], line)
        self.assertEqual(mismatches.find(case_for([ev(1, AG, "Tenant", "Address: Flat 1, 2 Test Road, ZZ9 9ZZ")])), [])  # no postcode on the property to compare

    def test_an_attachment_with_another_address_is_flagged_by_its_name(self):
        att = [Attachment("invoice.pdf", "Invoice\nProperty address: Flat 9, 77 Elm Close\nTotal 100")]
        items = mismatches.find(case_for([ev(1, AG, "Tenant", "Hello")], att))
        self.assertEqual((kinds(items), items[0]["refs"]), (["address"], ["invoice.pdf"]))

    def test_no_property_or_no_address_lines_give_nothing(self):
        self.assertEqual(mismatches.find(case_for([ev(1, AG, "Tenant", "Hello")])), [])
        c = case_for([ev(1, AG, "Tenant", "Address: Flat 9, 77 Elm Close")])
        self.assertEqual(mismatches.find(replace(c, property="")), [])


class AmountTests(unittest.TestCase):
    def quote(self, text="Quote for the repair: GBP 100 + VAT."):
        return ev(1, "Contractor", AG, text)

    def test_an_invoice_matching_no_quote_is_flagged(self):
        items = mismatches.find(case_for([self.quote(), ev(2, "Contractor", AG, "Invoice attached, total GBP 300.")]))
        self.assertEqual(kinds(items), ["amount"])
        self.assertIn("matches none of the quoted amounts", items[0]["summary"])
        self.assertEqual(items[0]["refs"], ["event-002", "event-001"])

    def test_vat_makes_a_matching_invoice_fine(self):
        for body in ("Invoice: GBP 120 including VAT.", "Invoice for GBP 100.", "Invoice GBP 100 net, GBP 120 gross."):
            self.assertEqual(mismatches.find(case_for([self.quote(), ev(2, "Contractor", AG, body)])), [], body)

    def test_an_invoice_above_the_landlord_approval_is_flagged(self):
        events = [self.quote("Quote GBP 100 plus VAT."), ev(2, "Landlord", AG, "Approved GBP 100, go ahead."),
                  ev(3, "Contractor", AG, "Quote revised to GBP 250."), ev(4, "Contractor", AG, "Invoice GBP 250.")]
        items = mismatches.find(case_for(events))
        self.assertTrue([i for i in items if "above the" in i["summary"] or "matches none" in i["summary"] or i["severity"] == "info"])

    def test_two_different_quotes_are_a_note_not_a_flag(self):
        items = mismatches.find(case_for([self.quote(), ev(2, "Contractor", AG, "Revised quote: GBP 400.")]))
        self.assertEqual([(i["kind"], i["severity"]) for i in items], [("amount", "info")])

    def test_no_quote_means_no_amount_check(self):
        self.assertEqual(mismatches.find(case_for([ev(1, "Contractor", AG, "Invoice GBP 300.")])), [])


class CompletionTests(unittest.TestCase):
    def test_done_then_the_tenant_reports_the_fault_again(self):
        events = [ev(1, "Contractor", AG, "Job completed, all fixed."), ev(2, "Tenant", AG, "The leak is back again.", "SMS")]
        items = mismatches.find(case_for(events))
        self.assertEqual((kinds(items), items[0]["refs"]), (["completion"], ["event-001", "event-002"]))

    def test_harmless_or_negated_follow_ups_are_not_flagged(self):
        for later in ("Thanks again, all working now.", "No more leaks, thanks.", "Thank you!", "Can you send the invoice?"):
            events = [ev(1, "Contractor", AG, "Job completed."), ev(2, "Tenant", AG, later, "SMS")]
            self.assertEqual(mismatches.find(case_for(events)), [], later)

    def test_a_problem_before_the_completion_is_not_a_mismatch(self):
        events = [ev(1, "Tenant", AG, "It is leaking again.", "SMS"), ev(2, "Contractor", AG, "Job completed.")]
        self.assertEqual(mismatches.find(case_for(events)), [])

    def test_agency_notes_do_not_count_as_a_completion(self):
        events = [ev(1, AG, "Landlord", "Job completed per system note."), ev(2, "Tenant", AG, "Still leaking.", "SMS")]
        self.assertEqual(mismatches.find(case_for(events)), [])


class ContactTests(unittest.TestCase):
    def test_two_numbers_from_the_same_party_are_a_note(self):
        events = [ev(1, "Tenant", AG, "Call me on 07700 900123."), ev(2, "Tenant", AG, "New number +44 7700 900456", "SMS")]
        items = mismatches.find(case_for(events))
        self.assertEqual([(i["kind"], i["severity"]) for i in items], [("contact", "info")])
        self.assertEqual(items[0]["refs"], ["event-001", "event-002"])

    def test_the_same_number_written_two_ways_is_one_number(self):
        events = [ev(1, "Tenant", AG, "07700 900123"), ev(2, "Tenant", AG, "+44 7700 900123", "SMS")]
        self.assertEqual(mismatches.find(case_for(events)), [])

    def test_numbers_of_different_parties_are_not_compared(self):
        events = [ev(1, "Tenant", AG, "07700 900123"), ev(2, "Contractor", AG, "07700 900456")]
        self.assertEqual(mismatches.find(case_for(events)), [])

    def test_two_emails_from_the_landlord(self):
        events = [ev(1, "Landlord", AG, "a@example.com"), ev(2, "Landlord", AG, "b@example.com")]
        self.assertEqual(kinds(mismatches.find(case_for(events))), ["contact"])


class ConsistencyAndLimitsTests(unittest.TestCase):
    def test_flag_and_escalate_checks_from_the_document_check_are_listed_and_passes_are_not(self):
        report = {"status": "ok", "checks": [
            {"field": "tenant_name", "values": ["Dawson", "Davidson"], "refs": [["event-001"], ["event-004"]], "score": 0.3, "tier": "escalate"},
            {"field": "tenant_phone", "values": ["1", "2"], "refs": [["event-001"], ["event-002"]], "score": 0.5, "tier": "flag"},
            {"field": "reference_number", "values": ["a", "b"], "refs": [["x"], ["y"]], "score": 0.9, "tier": "pass"}]}
        items = mismatches.find(case_for([ev(1, AG, "Tenant", "Hello")]), report)
        self.assertEqual([i["kind"] for i in items], ["document consistency"] * 2)
        self.assertIn("tenant name differs between documents", items[0]["summary"])
        self.assertEqual(items[0]["refs"], ["event-001", "event-004"])

    def test_an_unavailable_or_odd_report_gives_nothing(self):
        case = case_for([ev(1, AG, "Tenant", "Hello")])
        for report in ({"status": "unavailable"}, None, "x", {"status": "ok", "checks": ["nope", {"tier": "flag"}]}, {"status": "ok", "checks": 5}):
            mismatches.find(case, report)  # must not raise

    def test_at_most_twenty_items_flags_first(self):
        events = [ev(1, "Tenant", AG, "07700 900123")] + [ev(2 + i % 20, AG, "Tenant", "Address: Flat %d, %d Other Street" % (i + 20, i + 300)) for i in range(40)]
        items = mismatches.find(case_for(events))
        self.assertLessEqual(len(items), 20)
        self.assertEqual(items[0]["severity"], "flag")

    def test_a_detector_that_raises_does_not_stop_the_others(self):
        original = mismatches._address
        mismatches._address = lambda case: 1 / 0
        try:
            events = [ev(1, "Tenant", AG, "07700 900123"), ev(2, "Tenant", AG, "07700 900456")]
            self.assertEqual(kinds(mismatches.find(case_for(events))), ["contact"])
        finally:
            mismatches._address = original

    def test_empty_and_hostile_input_never_raises(self):
        self.assertEqual(mismatches.find(case_for([])), [])
        nasty = "Address: " + "x" * 50000 + "\n" + "£" * 5000 + "\x00‮" + "(" * 3000
        mismatches.find(case_for([ev(1, "Contractor", AG, nasty), ev(2, "Tenant", AG, nasty)]))


if __name__ == "__main__":
    unittest.main()
