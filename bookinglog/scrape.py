"""Scrape Marin County Jail Booking Log.

Conduct a search of the public booking log and store the
results. PhantomJS is used to scrape the search results.
Valid searches are:

    latest : entries in the last 48 hours.
    current : all inmates currently in custody.
"""
# Not supported:
# last-name : search for a specific inmate by last name.

import argparse
import json
import logging
import psycopg2
import sys

from . import coerce
from . import config
from . import queries
from . import pull
from itertools import starmap


def ingest(entries, cursor):
    """Add booking log entries to database.

    Parameters
    ----------
    entries : iterable of dicts
        Iterable of booking log entries to input.
    cursor : database cursor

    Returns
    -------
    None
    """

    for inmate_table, charges in entries:
        record = inmate_table.copy()
        cursor.execute(queries.insert_entry, record)
        booking_id = cursor.fetchone()[0]
        record["booking_id"] = booking_id

        charges_record = {
            "booking_id": booking_id,
            "recorded": json.dumps(charges),
        }

        cursor.execute(queries.insert_arrest, record)
        cursor.execute(queries.insert_inmate, record)
        cursor.execute(queries.insert_charge, charges_record)

    return

def main():

    parser = argparse.ArgumentParser(prog="bookinglog", description=__doc__)
    parser.add_argument(
        "-s", "--search",
        help="Type of search to perform",
        type=str,
        required=False,
        choices=("latest", "current"),
        default="latest")

    args = parser.parse_args()

    logging.basicConfig(**config.logging_cfg)
    logging.info("Running with arguments: {0}".format(args))

    try:
        logging.info("Starting ingest")
        html = pull.scrape(args.search)
        entries = pull.parse(html)
        converted_entries = starmap(coerce.convert, entries)
    except Exception as e:
        msg = "Failed scraping with {0}".format(e)
        logging.critical(msg)
        sys.exit(1)
    else:
        msg = "Scraped {0} entries".format(len(entries))
        logging.info(msg)

    with psycopg2.connect(**config.pg_kwargs) as conn:
        cursor = conn.cursor()

        try:
            ingest(converted_entries, cursor)
        except psycopg2.Error as e:
            msg = "Failed ingest with {0}".format(e)
            logging.critical(msg)
            conn.rollback()
            sys.exit(1)
        else:
            logging.info("Ingested to db")
            conn.commit()

    sys.exit(0)
