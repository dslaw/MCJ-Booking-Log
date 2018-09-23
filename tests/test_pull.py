from bs4 import BeautifulSoup
import pytest

from bookinglog import pull


@pytest.fixture(scope="module")
def html():
    with open("tests/data/mock.html") as fh:
        mock_html = fh.read()
    return mock_html

@pytest.fixture
def table():
    html = (
        '<tbody>\n'
        '  <tr>\n'
        '    <th scope="col"> First </th>\n'
        '    <th scope="col"> Second </th>\n'
        '  </tr>\n'
        '  <tr>\n'
        '    <td>11</td>\n'
        '    <td>12</td>\n'
        '  </tr>\n'
        '  <tr>\n'
        '    <td>21</td>\n'
        '    <td>22</td>\n'
        '  </tr>\n'
        '</tbody>'
    )
    return BeautifulSoup(html, "html.parser")

@pytest.fixture
def keyvalue_table():
    html = (
        '<tbody>\n'
        '  <tr>\n'
        '    <th scope="row">First:</th>\n'
        '    <td>Hello</td>\n'
        '  </tr>\n'
        '  <tr>\n'
        '    <th scope="row">Second:</th>\n'
        '    <td>World</td>\n'
        '  </tr>\n'
        '</tbody>'
    )
    return BeautifulSoup(html, "html.parser")


class TestTable(object):
    def test_parse_columns(self, table):
        expected = ["First", "Second"]

        out = pull.parse_columns(table)
        assert out == expected

    def test_parse_charges(self, table):
        expected = [{
            "First": "11",
            "Second": "12",
        }, {
            "First": "21",
            "Second": "22",
        }]

        out = pull.parse_charges(table)
        assert out == expected

class TestKeyValueTable(object):
    def test_parse_row(self):
        html = (
            '<tr>\n'
            '  <th scope="row">Key:</th>\n'
            '  <td>Value</td>\n'
            '</tr>'
        )
        row = BeautifulSoup(html, "html.parser")
        expected = {"Key": "Value"}

        out = pull.parse_row(row)
        assert out == expected

    def test_parse_table(self, keyvalue_table):
        expected = {"First": "Hello", "Second": "World"}

        out = pull.parse_table(keyvalue_table)
        assert out == expected

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
