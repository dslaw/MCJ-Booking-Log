import pytest

from bookinglog import pull


@pytest.fixture(scope="module")
def html():
    with open("tests/data/mock.html") as fh:
        mock_html = fh.read()
    return mock_html


class TestParse(object):
    def test_mock_data(self, html):
        out = pull.parse(html)

        assert len(out) == 2

        assert len(out[0]) == 2
        assert len(out[1]) == 2

        assert out[0][0]["Name"] == "DUNLOP, FUZZY"
        assert len(out[0][1]) == 5

        assert out[1][0]["Name"] == "RODRIGUEZ, BENDER BENDING"
        assert len(out[1][1]) == 2
