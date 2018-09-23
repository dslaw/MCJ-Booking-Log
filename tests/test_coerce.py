from datetime import datetime
import json

from bookinglog import coerce


class TestKeywordize(object):
    def test_lowercases(self):
        value = "FooBar"
        expected = "foobar"

        out = coerce.keywordize(value)
        assert out == expected

    def test_replaces_spaces(self):
        value = "foo bar"
        expected = "foo_bar"

        out = coerce.keywordize(value)
        assert out == expected

    def test_converts(self):
        value = "Foo Bar"
        expected = "foo_bar"

        out = coerce.keywordize(value)
        assert out == expected

class TestStandardizeKeys(object):
    def test_standardizes_keys(self):
        values = {
            "foo bar": None,
            "FooBar": None,
            "okay": None,
        }
        expected = {
            "foo_bar": None,
            "foobar": None,
            "okay": None,
        }

        out = coerce.standardize_keys(values)
        assert out == expected

class TestUpdate(object):
    def test_updates(self):
        data = {"a": 1, "b": 2}
        expected = {"a": 1, "b": 12}

        out = coerce.update(data, "b", lambda x: x + 10)
        assert out == expected

        # Original is not modified.
        assert data["a"] == 1
        assert data["b"] == 2

class TestParseBail(object):
    def test_empty_string(self):
        bail = ""
        out = coerce.parse_bail(bail)
        assert out is None

    def test_no_commas(self):
        bail = "220.00"
        expected = 220

        out = coerce.parse_bail(bail)
        assert out == expected

    def test_commas(self):
        bail = "1,222,222.00"
        expected = 1222222

        out = coerce.parse_bail(bail)
        assert out == expected

    def test_removes_cents(self):
        bail = "13,333,333.13"
        expected = 13333333

        out = coerce.parse_bail(bail)
        assert out == expected

class TestParseHeight(object):
    def test_two_single_quotes(self):
        height = "5' 11''"
        expected = (5 * 12) + 11

        out = coerce.parse_height(height)
        assert out == expected

    def test_returns_none_for_text(self):
        height = "five feet eleven inches"

        out = coerce.parse_height(height)
        assert out is None

    def test_double_quotes(self):
        # This is an unexpected format, oddly enough.
        height = "5' 10\""
        expected = (5 * 12) + 10

        out = coerce.parse_height(height)
        assert out == expected

class TestConvertDOB(object):
    def test_expected_format(self):
        dob = "9/15/1987"
        expected = datetime(1987, 9, 15)

        out = coerce.convert_dob(dob)
        assert out == expected

    def test_returns_none_for_invalid(self):
        dob = "9/150/1987"

        out = coerce.convert_dob(dob)
        assert out is None

class TestConvertDT(object):
    def test_morning(self):
        dt = "9/15/2016 4:15 AM"

        out = coerce.convert_dt(dt)
        assert isinstance(out, datetime)
        assert out.year == 2016
        assert out.month == 9
        assert out.day == 15
        assert out.hour == 4
        assert out.minute == 15

    def test_afternoon(self):
        dt = "9/15/2016 4:15 PM"

        out = coerce.convert_dt(dt)
        assert isinstance(out, datetime)
        assert out.year == 2016
        assert out.month == 9
        assert out.day == 15
        assert out.hour == 16
        assert out.minute == 15

    def test_returns_none_for_invalid(self):
        dt = "Sept. 15, 2016 4:15 PM"

        out = coerce.convert_dt(dt)
        assert out is None

class TestConvert(object):
    def test_mock_data(self):
        with open("tests/data/mock.json") as fh:
            data = json.load(fh)

        inmate, charges = coerce.convert(*data)

        assert inmate["jail_id"] == "PJAILID12"
        assert inmate["weight"] == 200

        assert len(charges) == 2
        assert charges[0]["bail"] == 0
        assert charges[1]["bail"] is None
