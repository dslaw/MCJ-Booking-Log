"""Scrape and parse Booking Log results page."""

from bs4 import BeautifulSoup
from collections import ChainMap

import requests


# Each inmate entry has 3 tables:
#
# 1. Booking Information (class: arrest-table)
# 2. Personal Information (class: personal-table)
# 3. Charges (no class)
#
# Booking and personal are placed into the top section,
# while charges is on the bottom.

# Parse charge tables (columns)
def parse_columns(table):
    """Extract column names and return as an ordered list."""

    cols = table.find_all("th", {"scope": "col"})
    colnames = [col.text.strip() for col in cols]
    return colnames

def parse_charges(table):
    """Extract charge entries and return as a list of maps."""

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
    """Extract key-value pair from a row."""

    key = row.find("th").text.strip().strip(":")
    value = row.find("td").text.strip()
    return {key: value}

def parse_table(table):
    """Extract key-values from table."""

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
    arrest_tables, personal_tables = zip(*paired_tables)
    charge_tables = soup.find_all("div", {"id": "sec2"})

    # Parse data into maps.
    arrests = map(parse_table, arrest_tables)
    personals = map(parse_table, personal_tables)
    charges = map(parse_charges, charge_tables)
    inmates = (
        {**arrest, **personal}
        for arrest, personal in zip(arrests, personals)
    )

    entries = zip(inmates, charges)
    return list(entries)

def scrape(search_type):
    """Download Booking Log page source."""

    url = "https://apps.marincounty.org/BookingLog/Booking/Action"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = {
        "latest": "DisplayLatestBookings=Last+48+Hours",
        "current": "DisplayAllBookings=Currently+In+Custody",
    }[search_type]
    response = requests.post(url, headers=headers, data=body)

    if not response.ok:
        response.raise_for_status()
    return response.content
