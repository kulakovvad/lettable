import tempfile
import unittest
from pathlib import Path

from agent import evidence
from agent.timeline import load_case
from tests.helpers import make_case


def name_for(events):
    with tempfile.TemporaryDirectory() as tmp:
        return evidence.agency_name(load_case(make_case(Path(tmp), "c1", events)))


def msg(body, sender="Agency / system", to="Tenant", channel="SMS"):
    return ("2026-01-02 10:00:00", channel, sender, to, body)


class AgencyNameTests(unittest.TestCase):
    def test_a_named_sender_wins(self):
        self.assertEqual(name_for([msg("Hello", sender="Northbridge Lettings", channel="Email")]), "Northbridge Lettings")

    def test_an_unnamed_sender_is_named_by_how_the_agency_introduces_itself(self):
        self.assertEqual(name_for([msg("Hello, this is Northbridge Lettings! Your visit is booked.")]), "Northbridge Lettings")

    def test_or_by_how_it_signs_off(self):
        body = "Hi Sam, please confirm a date.\n\nKind regards,\nNorthbridge Lettings"
        self.assertEqual(name_for([msg(body, to="Contractor", channel="Email")]), "Northbridge Lettings")

    def test_the_most_used_name_wins(self):
        events = [msg("Hello, this is Northbridge Lettings!"), msg("Hello, this is Northbridge Lettings!"),
                  msg("Hello, this is Cedar Homes!")]  # two against one
        self.assertEqual(name_for(events), "Northbridge Lettings")

    def test_a_staff_name_or_a_provider_introduction_is_not_the_agency(self):
        self.assertEqual(name_for([msg("Thanks.\n\nKind regards,\nMaya", channel="Email")]), "the agency")
        self.assertEqual(name_for([msg("Hello, this is Sam from Oakfield Services.", channel="Email")]), "the agency")
        self.assertEqual(name_for([msg("Kind regards,\nAva Fletcher", channel="Email")]), "the agency")

    def test_a_town_in_an_address_or_a_message_from_someone_else_is_not_the_agency(self):
        self.assertEqual(name_for([msg("Flat 1, Northbridge Lettings Road")]), "the agency")
        other = ("2026-01-02 10:00:00", "Email", "Contractor", "Agency / system", "Hello, this is Oakfield Homes!")
        self.assertEqual(name_for([other]), "the agency")

    def test_intro_forms_that_are_normal_still_match(self):
        for body in ("Hello, This is Northbridge Lettings!", "Hello, this is Northbridge Lettings\nYour visit is booked.",
                     "Hello, this is Northbridge Lettings", "Hi Sam, this is Northbridge Lettings.", "This is Northbridge Lettings, hello",
                     "Hello, this is Northbridge Lettings Ltd!"):
            self.assertTrue(name_for([msg(body)]).startswith("Northbridge Lettings"), body)

    def test_a_pasted_or_quoted_introduction_in_the_middle_of_a_message_is_not_the_agency(self):
        body = "Update from the contractor: Hello, this is Oakfield Homes! We can come Tuesday."
        self.assertEqual(name_for([msg(body, channel="Email")]), "the agency")
        self.assertEqual(name_for([msg("Please see below.\n\nHello, this is Oakfield Homes! Booked.", channel="Email")]), "the agency")

    def test_ordinary_prose_with_an_agency_word_is_not_the_agency(self):
        for body in ("Please note this is Property Management Policy.", "Note this is Estates Gazette.",
                     "Hello, this is Property Management Policy for tenants."):
            self.assertEqual(name_for([msg(body)]), "the agency", body)

    def test_a_sign_off_needs_the_sign_off_word_alone_on_its_line(self):
        self.assertEqual(name_for([msg("Thanks, it is best,\nCedar Homes", channel="Email")]), "the agency")
        self.assertEqual(name_for([msg("Hello.\nBest wishes\nNorthbridge Lettings", channel="Email")]), "Northbridge Lettings")

    def test_a_person_then_the_firm_is_read_from_the_firm_line(self):
        body = "Hi Sam, please confirm.\n\nKind regards,\nMaya Chen\nNorthbridge Lettings"
        self.assertEqual(name_for([msg(body, channel="Email")]), "Northbridge Lettings")
        self.assertEqual(name_for([msg("Kind regards,\nAva Fletcher\nProperty Management", channel="Email")]), "the agency")

    def test_an_accented_name_is_kept(self):
        self.assertEqual(name_for([msg("Hello, this is Zo\u00eb Lettings!")]), "Zo\u00eb Lettings")

    def test_two_different_names_used_equally_often_are_not_trusted(self):
        self.assertEqual(name_for([msg("Hello, this is A Homes!"), msg("Hello, this is B Homes!")]), "the agency")

    def test_nothing_to_go_on_gives_the_placeholder(self):
        self.assertEqual(name_for([msg("Please confirm a date.")]), "the agency")


if __name__ == "__main__":
    unittest.main()
