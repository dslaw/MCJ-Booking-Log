#!/usr/bin/env python

"""
Scrape Marin County Jail Booking Log.

Conduct a search of the public booking log and store the
results. PhantomJS is used to scrape the search results.
Valid searches are:

    latest : entries in the last 48 hours.
    current : all inmates currently in custody.
"""
# Not supported:
#last-name : search for a specific inmate by last name.

import argparse
import logging
import psycopg2
import sys

from bookinglog import coerce
from bookinglog import config
from bookinglog import models
from bookinglog import pull


def ingest(entries, cursor):
    """ Add booking log entries to database.

    Parameters
    ----------
    entries : iterable of dicts
        Iterable of booking log entries to input.
    cursor : database cursor

    Returns
    -------
    None
    """

    for entry in entries:
        arrest_table = entry["arrest-table"]
        personal_table = entry["personal-table"]
        charges = entry["charge-table"]
        # These should have disjoint keys.
        merged = models.rename({**arrest_table, **personal_table})

        booking_entry = models.make_entry(**merged)
        cursor.execute(models.insert_entry, tuple(booking_entry))
        booking_id = cursor.fetchone()[0]

        arrest_entry = models.make_arrest(**merged, booking_id=booking_id)
        inmate_entry = models.make_inmate(**merged, booking_id=booking_id)
        charges_entry = models.make_charges(charges, booking_id=booking_id)

        cursor.execute(models.insert_arrest, tuple(arrest_entry))
        cursor.execute(models.insert_inmate, tuple(inmate_entry))
        cursor.execute(models.insert_charge, tuple(charges_entry))

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
    logging.debug("Running with arguments: {0}".format(args))


    try:
        logging.info("Starting ingest")
        html = pull.scrape(args.search)
        entries = pull.parse(html)
        converted_entries = map(coerce.convert, entries)
    except Exception as e:
        msg = "Failed scraping with {0}".format(e)
        logging.critical(msg)
        sys.exit(1)
    else:
        msg = "Scraped {0} entries".format(len(entries))
        logging.debug(msg)

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
            logging.debug("Ingested to db")
            conn.commit()

    sys.exit(0)

