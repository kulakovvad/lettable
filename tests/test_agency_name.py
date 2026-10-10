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
                  msg("Hello, this is Cedar Homes!")]
        self.assertEqual(name_for(events), "Northbridge Lettings")

    def test_a_staff_name_or_a_provider_introduction_is_not_the_agency(self):
        self.assertEqual(name_for([msg("Thanks.\n\nKind regards,\nMaya", channel="Email")]), "the agency")
        self.assertEqual(name_for([msg("Hello, this is Sam from Oakfield Services.", channel="Email")]), "the agency")
        self.assertEqual(name_for([msg("Kind regards,\nAva Fletcher", channel="Email")]), "the agency")

    def test_a_town_in_an_address_or_a_message_from_someone_else_is_not_the_agency(self):
        self.assertEqual(name_for([msg("Flat 1, Northbridge Lettings Road")]), "the agency")
        other = ("2026-01-02 10:00:00", "Email", "Contractor", "Agency / system", "Hello, this is Oakfield Homes!")
        self.assertEqual(name_for([other]), "the agency")

    def test_nothing_to_go_on_gives_the_placeholder(self):
        self.assertEqual(name_for([msg("Please confirm a date.")]), "the agency")


if __name__ == "__main__":
    unittest.main()
