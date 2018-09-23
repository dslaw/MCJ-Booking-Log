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
    def test_length(self, html):
        out = pull.parse(html)
        assert len(out) == 2

    def test_charges(self, html):
        expected_first = [{
            "Charge": "11377 HS",
            "Description": "Possess controlled substance",
            "Level": "F",
            "Bail": "$837.00",
            "Charge Authority": "Open charges",
        }, {
            "Charge": "243(B) PC",
            "Description": "Battery on PO/Emergency Personnel",
            "Level": "M",
            "Bail": "",
            "Charge Authority": "*Bench warrant",
        }, {
            "Charge": "242 PC",
            "Description": "Battery",
            "Level": "M",
            "Bail": "",
            "Charge Authority": "Court order",
        }]
        expected_second = [{
            "Charge": "23152(A) VC",
            "Description": "DUI alcohol/drugs",
            "Level": "M",
            "Bail": "$0.00",
            "Charge Authority": "Court order",
        }, {
            "Charge": "23152(B) VC",
            "Description": "DUI alcohol .08 percent",
            "Level": "M",
            "Bail": "",
            "Charge Authority": "Court order",
        }]

        out = pull.parse(html)
        assert out[0][1] == expected_first
        assert out[1][1] == expected_second

    def test_arrest_personal(self, html):
        expected_first = {
            # Arrest.
            "Name": "DUNLOP, FUZZY",
            "Address": "SAN RAFAEL, CA",
            "Orig Booking Date": "7/13/2016 3:40 PM",
            "Latest Charge Date": "7/14/2016 12:59 PM",
            "Arrest Date": "7/13/2016 3:30 PM",
            "Arrest Agency": "San Rafael PD",
            "Arrest Location": "75 ALBERTS PARK",
            "Jail Id": "PJAILID11",
            # Personal.
            "Date of Birth": "10/8/1981",
            "Occupation": "CONSTRUCTION",
            "Sex": "M",
            "Height": "5' 10''",
            "Weight": "170",
            "Race": "W",
            "Hair Color": "BRO",
            "Eye Color": "BLU",
        }
        expected_second = {
            # Arrest.
            "Name": "RODRIGUEZ, BENDER BENDING",
            "Address": "SAN RAFAEL, CA",
            "Orig Booking Date": "7/15/2016 9:01 AM",
            "Latest Charge Date": "7/15/2016 9:08 AM",
            "Arrest Date": "7/15/2016 9:00 AM",
            "Arrest Agency": "Marin County Sheriff Department",
            "Arrest Location": "MARIN COUNTY JAIL LOBBY",
            "Jail Id": "PJAILID12",
            # Personal.
            "Date of Birth": "6/26/1959",
            "Occupation": "BENDER",
            "Sex": "M",
            "Height": "6' 04''",
            "Weight": "200",
            "Race": "W",
            "Hair Color": "BLN",
            "Eye Color": "BLU",
        }

        out = pull.parse(html)
        assert out[0][0] == expected_first
        assert out[1][0] == expected_second
