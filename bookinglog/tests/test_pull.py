from pkg_resources import resource_filename
import unittest

from bookinglog import pull


class TestParsing(unittest.TestCase):
    def test_parse(self):
        mock_html = resource_filename("bookinglog", "tests/data/mock.html")
        with open(mock_html, "r") as fh:
            html = fh.read()

        out = pull.parse(html)

        self.assertEqual(len(out), 2)

        self.assertEqual(len(out[0]), 2)
        self.assertEqual(len(out[1]), 2)

        self.assertEqual(out[0][0]["Name"], "DUNLOP, FUZZY")
        self.assertEqual(len(out[0][1]), 5)

        self.assertEqual(out[1][0]["Name"], "RODRIGUEZ, BENDER BENDING")
        self.assertEqual(len(out[1][1]), 2)
