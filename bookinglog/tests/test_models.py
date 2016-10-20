from collections import namedtuple
import unittest

from bookinglog import models


class TestModels(unittest.TestCase):
    """ Smoke tests."""

    def test_rename(self):
        d = {
            "arrest_agency": "FBI",
            "date_of_birth": "1/1/1970",
            "arrest_location": "850 Bryant St.",
            "extra": "key"
        }
        expected = {
            "agency": "FBI",
            "dob": "1/1/1970",
            "location": "850 Bryant St.",
            "extra": "key"
        }

        out = models.rename(d)
        self.assertEqual(out, expected)

        # Original dict is not modified.
        self.assertEqual(d["arrest_agency"], "FBI")
        self.assertEqual(d["date_of_birth"], "1/1/1970")
        self.assertEqual(d["arrest_location"], "850 Bryant St.")
        self.assertEqual(d["extra"], "key")

    def test_create_model(self):
        Mock = namedtuple("Mock", ["x", "y"])
        expected = Mock(10, 20)
        out = models.create_model(Mock, x=10, y=20, z=30)
        self.assertEqual(out, expected)

    def test_make_charges(self):
        b_id = 1
        charges = [
            {"first": "charge"},
            {"second": "time"}
        ]

        expected_json = '[{"first": "charge"}, {"second": "time"}]'
        expected = models.Charges(b_id, expected_json)
        out = models.make_charges(charges, b_id)
        self.assertEqual(out, expected)

