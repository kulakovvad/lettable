"""The files the submission rules require exist and say what they should."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HEADINGS = [
    "## 1. What we built",
    "## 2. The operational problem it solves",
    "## 3. Architecture",
    "## 4. How to run it",
    "## 5. Models, APIs and external services",
    "## 6. Important assumptions",
    "## 7. Known limitations",
    "## 8. What we would build next",
]
FORM_FIELDS = [
    "Public repository URL", "Team name", "Track", "Names of all team members", "Commit hash at the 17:00 freeze",
    "Reality Test results", "Path to the demo video", "LinkedIn post URL", "X post URL",
]


class SubmissionFileTests(unittest.TestCase):
    def test_licence_is_apache_2(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertTrue(text.lstrip().startswith("Apache License"))
        self.assertIn("Version 2.0", text[:200])
        self.assertIn("TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION", text)

    def test_submission_lists_the_nine_form_fields(self):
        text = (ROOT / "SUBMISSION.md").read_text(encoding="utf-8")
        for field in FORM_FIELDS:
            self.assertIn(field, text)
        self.assertEqual(len(re.findall(r"^\| \d \|", text, re.M)), 9)
        self.assertIn("Property Management", text)
        self.assertIn("ANSWERS/", text)

    def test_readme_has_the_eight_required_sections_in_order(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        positions = [text.find("\n" + h) for h in HEADINGS]
        self.assertNotIn(-1, positions, [h for h, p in zip(HEADINGS, positions) if p == -1])
        self.assertEqual(positions, sorted(positions))

    def test_every_relative_link_in_the_readme_points_at_a_file(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        links = [m for m in re.findall(r"\]\(([^)\s]+)\)", text) if not m.startswith(("http://", "https://", "#", "mailto:"))]
        self.assertTrue(links)
        for link in links:
            self.assertTrue((ROOT / link.split("#")[0]).exists(), link)

    def test_readme_documents_every_variable_in_env_example(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        names = re.findall(r"^([A-Z][A-Z0-9_]+)=", (ROOT / ".env.example").read_text(encoding="utf-8"), re.M)
        self.assertTrue(names)
        missing = [n for n in names if n not in readme]
        self.assertEqual(missing, [])

    def test_env_example_holds_no_values(self):
        for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
            if re.match(r"^[A-Z][A-Z0-9_]+=", line):
                value = line.split("=", 1)[1]
                self.assertIn(value, ("", "fake", "off", "dry_run"), line)


if __name__ == "__main__":
    unittest.main()
