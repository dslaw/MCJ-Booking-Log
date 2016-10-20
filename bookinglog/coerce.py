""" Cast text to native data types."""

from datetime import datetime
from functools import reduce

import logging
import pytz


logger = logging.getLogger(__name__)


def catch(*exceptions):
    """ Log exceptions and return None to indicate failure."""

    if not exceptions:
        exceptions = (Exception,)

    def decorator(fn):
        def inner(*args, **kwargs):
            try:
                out = fn(*args, **kwargs)
            except exceptions as e:
                logger.debug(e)
                out = None
            return out
        return inner
    return decorator

def keywordize(x):
    keyword = lambda x: x.lower().replace(" ", "_")
    return {keyword(k): v for k, v in x.items()}

def update(d, k, fn):
    """ Update the value at `d[k]` by applying `fn` to it."""
    value = d[k]
    updated = {k: fn(value)}
    return {**d, **updated}

def parse_bail(x):
    # $1,000.00 -> 1000
    dollars = x.lstrip("$").split(".")[0]
    amount = dollars.replace(",", "")
    # Check for empty string (no-data).
    return int(amount) if amount else None

@catch(ValueError)
def parse_height(x):
    # 5' 10'' -> inches
    feet, inches = x.split("'", 1)
    inches = inches.replace("'", "").replace('"', "")
    return (int(feet) * 12) + int(inches)

@catch(ValueError)
def convert_dob(x):
    dob = datetime.strptime(x, "%m/%d/%Y")
    return dob

@catch(ValueError)
def convert_dt(x):
    # Assume that the time displayed by the website is fixed (California).
    pacific = pytz.timezone("US/Pacific")

    # NB: %p depends on locale being en_US.
    dt = datetime.strptime(x, "%m/%d/%Y %I:%M %p")
    # TODO: determine daylight savings
    localized = pacific.localize(dt)
    return localized

def convert(entry):
    """ Convert text to native objects and update keys."""

    # Standardize keys to match database columns/model fields.
    charges_kw = map(keywordize, entry["charge-table"])
    arrest_kw = keywordize(entry["arrest-table"])
    inmate_kw = keywordize(entry["personal-table"])

    # Convert text to native objects.
    charges = [update(charge, "bail", parse_bail) for charge in charges_kw]
    arrest = reduce(
        lambda d, k: update(d, k, convert_dt),
        ("arrest_date", "latest_charge_date", "orig_booking_date"),
        arrest_kw)
    inmate = update(
        update(inmate_kw, "date_of_birth", convert_dob),
        "height",
        parse_height)

    out = {
        "charge-table": charges,
        "arrest-table": arrest,
        "personal-table": inmate}
    return out

