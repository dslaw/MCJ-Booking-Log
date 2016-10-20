from pkg_resources import resource_filename
import sys
import unittest

from bookinglog import pull


class TestParsing(unittest.TestCase):
    def test_parse(self):
        mock_html = resource_filename("bookinglog", "tests/data/mock.html")
        with open(mock_html, "r") as fh:
            html = fh.read()

        out = pull.parse(html)

        self.assertEqual(len(out), 2)

        self.assertIn("arrest-table", out[0])
        self.assertIn("charge-table", out[0])
        self.assertIn("personal-table", out[0])

        self.assertEqual(
            out[0]["arrest-table"]["Name"],
            "DUNLOP, FUZZY"
        )

        self.assertEqual(
            out[1]["arrest-table"]["Name"],
            "RODRIGUEZ, BENDER BENDING"
        )

