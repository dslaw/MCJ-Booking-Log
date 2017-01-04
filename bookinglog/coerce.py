"""Cast text to native data types."""

from datetime import datetime
from functools import partial
from schema import And, Schema, Use

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

def len_eq(x, n):
    return len(x) == n

len_eq1 = partial(len_eq, n=1)
len_eq3 = partial(len_eq, n=3)

inmate_schema = Schema({
    "address": str,
    "arrest_agency": str,
    "arrest_date": Use(convert_dt),
    "arrest_location": str,
    "date_of_birth": Use(convert_dob),
    "eye_color": And(str, len_eq3),
    "hair_color": And(str, len_eq3),
    "height": Use(parse_height),
    "jail_id": str,
    "latest_charge_date": Use(convert_dt),
    "name": str,
    "occupation": str,
    "orig_booking_date": Use(convert_dt),
    "race": And(str, len_eq1),
    "sex": And(str, len_eq1),
    "weight": Use(int)
})

charge_schema = Schema([{
    "bail": Use(parse_bail),
    "charge": str,
    "charge_authority": str,
    "description": str,
    "level": And(str, len_eq1)
}])


def convert(inmate, charges):
    """ Convert data to native objects."""

    # Standardize keys and coervert/validate data.
    inmate = inmate_schema.validate(keywordize(inmate))
    charges = charge_schema.validate(list(map(keywordize, charges)))
    return inmate, charges

