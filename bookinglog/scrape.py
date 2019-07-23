"""Scrape Marin County Jail Booking Log.

Conduct a search of the public booking log and store the
results. Valid searches are:

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


logging.basicConfig(**config.logging_cfg)


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

def make_argparser():
    parser = argparse.ArgumentParser(prog="bookinglog", description=__doc__)
    parser.add_argument(
        "-s", "--search",
        help="Type of search to perform",
        type=str,
        required=False,
        choices=("latest", "current"),
        default="latest"
    )
    return parser

def main(search_type):
    logging.info("Running with search argument: %s", search_type)

    with psycopg2.connect(**config.pg_kwargs) as conn:
        try:
            logging.info("Starting ingest")
            html = pull.scrape(search_type)
            entries = pull.parse(html)
            converted_entries = starmap(coerce.convert, entries)
        except Exception as e:
            logging.critical("Failed scraping with %s", e)
            return 1
        else:
            logging.info("Scraped %s entries", len(entries))

        try:
            cursor = conn.cursor()
            ingest(converted_entries, cursor)
        except Exception as e:
            logging.critical("Failed ingest with %s", e)
            conn.rollback()
            return 1
        else:
            logging.info("Ingested to db")
            conn.commit()

    return 0


if __name__ == "__main__":
    parser = make_argparser()
    args = parser.parse_args()
    status = main(args.search)
    sys.exit(status)
