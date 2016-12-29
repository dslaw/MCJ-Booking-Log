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

def parse(html):
    soup = BeautifulSoup(html, "html.parser")

    # Find data sections. Each inmate has three tables:
    # Arrest | Personal
    # -----------------
    #      Charges
    top_sections = soup.find_all("div", {"id": "sec1"})
    paired_tables = (section.find_all("table") for section in top_sections)
    charge_tables = soup.find_all("div", {"id": "sec2"})

    # Parse data into maps.
    # Merge arrest and personal tables together.
    paired_tables = (map(parse_table, tables) for tables in paired_tables)
    inmate_tables = ({**arrest, **personal} for arrest, personal in paired_tables)
    charge_tables = map(parse_charges, charge_tables)

    entries = zip(inmate_tables, charge_tables)
    return list(entries)

def search_terms(term):
    """ Mapping to POST search terms."""

    terms = {
        "latest": "DisplayLatestBookings",  # Last 48 Hours
        "current": "DisplayAllBookings",    # Currently In Custody
    }
    return terms[term]

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

    button_name = search_terms(query_type)
    search_button = browser.find_element_by_name(button_name)

    # Assume that data is loaded when the page is loaded.
    search_button.click()
    html = browser.page_source
    browser.close()

    assert len(html) > template_len
    return html

