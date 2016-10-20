""" Scrape and parse Booking Log results page."""

from bs4 import BeautifulSoup
from collections import ChainMap
from selenium import webdriver

# Each inmate entry has 3 tables:
#
# 1. Booking Information (arrest-table)
# 2. Personal Information (personal-table)
# 3. Charges (no class... assholes)
#
# Booking and personal are placed into the top section,
# while charges is on the bottom.

# Parse charge tables (columns)
def parse_columns(table):
    """ Extract column names and return as an ordered list."""

    cols = table.find_all("th", {"scope": "col"})
    colnames = [col.text.strip() for col in cols]
    return colnames

def parse_charges(table):
    """ Extract charge entries and return as a list of maps."""

    columns = parse_columns(table)

    rows = table.find_all("tr")
    row_entries = [
       [entry.text.strip() for entry in row.find_all("td")]
       for row in rows
    ]
    processed = [
        {col: entry for col, entry in zip(columns, entries)}
        for entries in row_entries
        # The first row gives the column names and does not have
        # td children -- skip it.
        if entries
    ]

    return processed

# Parse arrest and personal tables (key-values pairs displayed columnwise)
def parse_row(row):
    """ Extract key-value pair from a row."""

    key = row.find("th").text.strip().strip(":")
    value = row.find("td").text.strip()
    return {key: value}

def parse_table(table):
    """ Extract key-values from table."""

    rows = table.find_all("tr")
    parsed = map(parse_row, rows)
    pairs = dict(ChainMap(*parsed))
    return pairs

def format_tables(arrest, personal, charge):
    """ Create a convenient representation of the parsed tables."""

    mapping = {
        "arrest-table": arrest,
        "personal-table": personal,
        "charge-table": charge,
    }

    return mapping

def parse(html):
    soup = BeautifulSoup(html, "html.parser")

    # Find the data sections. Each inmate has three tables:
    # Arrest, Personal, Charges.
    top_sections = soup.find_all("div", {"id": "sec1"})
    charge_tables = soup.find_all("div", {"id": "sec2"})

    subtables = (section.find_all("table") for section in top_sections)
    arrest_tables, personal_tables = zip(*subtables)

    # Parse data into json.
    arrest_tables = map(parse_table, arrest_tables)
    personal_tables = map(parse_table, personal_tables)
    charge_tables = map(parse_charges, charge_tables)

    groups = zip(arrest_tables, personal_tables, charge_tables)
    entries = [format_tables(*group) for group in groups]
    return entries

def search_terms(term, key_only=True):
    """ Mapping to POST search terms."""

    terms = {
        "latest": {
            "name": "DisplayLatestBookings",
            "value": "Last 48 Hours"
        },
        "current": {
            "name": "DisplayAllBookings",
            "value": "Currently In Custody"
        },
        "last-name": {
            "name": "LastName",
            "value": ""
        }
    }

    kv = terms[term]
    return kv["name"] if key_only else kv

def scrape(query_type):
    """ Download Booking Log page source."""

    # Number of characters in the html template w/o data.
    # This can be obtained via:
    # import requests
    # response = requests.post(uri, json={"DisplayAllBookings", ""})
    # len(response.content)
    template_len = 40705

    # Selenium workaround.
    uri = "http://apps.marincounty.org/BookingLog"
    browser = webdriver.PhantomJS()
    browser.get(uri)

    # Won't work for Last Name search!
    button_name = search_terms(query_type)
    search_button = browser.find_element_by_name(button_name)

    # Assume that data is loaded when the page is loaded.
    search_button.click()
    html = browser.page_source
    browser.close()

    assert len(html) > template_len
    return html

