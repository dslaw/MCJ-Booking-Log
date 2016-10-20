from datetime import datetime
import pytz
import unittest

from bookinglog import coerce


class TestCoerce(unittest.TestCase):
    """ Smoke tests."""

    def test_keywordize(self):
        d = {
            "Napulitan": 10,
            "combatReggae": 20,
            "Curre Curre Uaglio": 30
        }

        expected = {
            "napulitan": 10,
            "combatreggae": 20,
            "curre_curre_uaglio": 30
        }

        out = coerce.keywordize(d)
        self.assertEqual(out, expected)

        # Fail on non-string keys.
        bad_input = {
            1: "ten",
            -1: "twenty",
            (2, 3): "thirty"
        }

        with self.assertRaises(AttributeError):
            coerce.keywordize(bad_input)

    def test_update(self):
        d = {
            "a": 1,
            "b": 2,
        }

        expected = {
            "a": 1,
            "b": 12
        }

        out = coerce.update(d, "b", lambda x: x + 10)
        self.assertEqual(out, expected)

        # Original is not modified.
        self.assertEqual(d["a"], 1)
        self.assertEqual(d["b"], 2)

    def test_parse_bail(self):
        bail = "2,222.00"
        expected = 2222
        out = coerce.parse_bail(bail)
        self.assertEqual(out, expected)

        no_data = ""
        expected_no_data = None
        out_no_data = coerce.parse_bail(no_data)
        self.assertEqual(out_no_data, expected_no_data)

        big_money = "13,333,333.13"
        expected_big_money = 13333333 # Ignore cents
        out_big_money = coerce.parse_bail(big_money)
        self.assertEqual(out_big_money, expected_big_money)

    def test_parse_height(self):
        height = "5' 11''"
        expected = (5 * 12) + 11
        out = coerce.parse_height(height)
        self.assertEqual(out, expected)

        not_numeric = "five feet eleven inches"
        expected_not_numeric = None
        out_not_numeric = coerce.parse_height(not_numeric)
        self.assertEqual(out_not_numeric, expected_not_numeric)

        unexpected = "5' 10\"" # Double quote instead of two single quotes
        expected_unexpected = (5 * 12) + 10
        out_unexpected = coerce.parse_height(unexpected)
        self.assertEqual(out_unexpected, expected_unexpected)

    def test_convert_dob(self):
        date_of_birth = "9/15/1987"
        expected = datetime(1987, 9, 15)
        out = coerce.convert_dob(date_of_birth)
        self.assertEqual(out, expected)

        invalid_dob = "9/150/1987"
        out_invalid = coerce.convert_dob(invalid_dob)
        self.assertEqual(out_invalid, None)

    def test_convert_dt(self):
        morning = "9/15/2016 4:15 AM"
        out_morning = coerce.convert_dt(morning)

        self.assertIsInstance(out_morning, datetime)
        self.assertEqual(out_morning.year, 2016)
        self.assertEqual(out_morning.month, 9)
        self.assertEqual(out_morning.day, 15)
        self.assertEqual(out_morning.hour, 4)
        self.assertEqual(out_morning.minute, 15)

        afternoon = "9/15/2016 4:15 PM"
        out_afternoon = coerce.convert_dt(afternoon)

        self.assertIsInstance(out_afternoon, datetime)
        self.assertEqual(out_afternoon.year, 2016)
        self.assertEqual(out_afternoon.month, 9)
        self.assertEqual(out_afternoon.day, 15)
        self.assertEqual(out_afternoon.hour, 16)
        self.assertEqual(out_afternoon.minute, 15)

        invalid_date = "Sept. 15, 2016 4:15 PM"
        out_invalid_date = coerce.convert_dt(invalid_date)
        self.assertEqual(out_invalid_date, None)

