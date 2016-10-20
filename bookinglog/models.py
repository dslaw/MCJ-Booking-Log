""" Model data to reflect database schema."""

from collections import namedtuple
from functools import partial
import json


Entry = namedtuple("BookingLogEntry", [
    "jail_id",
    "orig_booking_date",
    "latest_charge_date"
])

Arrest = namedtuple("Arrest", [
    "booking_id",
    "arrest_date",
    "agency",
    "location"
])

Inmate = namedtuple("Inmate", [
    "booking_id",
    "name",
    "dob",
    "eye_color",
    "hair_color",
    "height",
    "weight",
    "race",
    "sex",
    "occupation"
])

Charges = namedtuple("Charges", [
    "booking_id",
    "recorded"
])

# TODO: serial pks are being incremented too quickly like this...
insert_entry = (
    "INSERT INTO booking "
    "(jail_id, orig_booking_date, latest_charge_date) "
    "VALUES (%s, %s, %s) "
    "ON CONFLICT (jail_id) DO UPDATE "
    "SET jail_id = EXCLUDED.jail_id, "
    "  orig_booking_date = EXCLUDED.orig_booking_date, "
    "  latest_charge_date = EXCLUDED.latest_charge_date "
    "RETURNING id"
)

insert_arrest = (
    "INSERT INTO arrests "
    "(booking_id, arrest_date, agency, location) "
    "VALUES (%s, %s, %s, %s) "
    "ON CONFLICT (booking_id) DO UPDATE "
    "SET arrest_date = EXCLUDED.arrest_date, "
    "  agency = EXCLUDED.agency, "
    "  location = EXCLUDED.location"
)

insert_inmate = (
    "INSERT INTO inmates "
    "(booking_id, name, dob, eye_color, hair_color, height, weight, race, sex, occupation) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
    "ON CONFLICT (booking_id) DO UPDATE "
    "SET name = EXCLUDED.name, "
    "  dob = EXCLUDED.dob, "
    "  eye_color = EXCLUDED.eye_color, "
    "  hair_color = EXCLUDED.hair_color, "
    "  height = EXCLUDED.height, "
    "  weight = EXCLUDED.weight, "
    "  race = EXCLUDED.race, "
    "  sex = EXCLUDED.sex, "
    "  occupation = EXCLUDED.occupation"
)

insert_charge = (
    "INSERT INTO charges "
    "(booking_id, recorded) "
    "VALUES (%s, %s) "
    "ON CONFLICT (booking_id) DO UPDATE "
    "SET recorded = EXCLUDED.recorded"
)


def rename(d):
    # I know this shouldn't be inside...
    name_mapping = {
        "date_of_birth": "dob",
        "arrest_agency": "agency",
        "arrest_location": "location"
    }

    out = d.copy()
    for current, replacement in name_mapping.items():
        out[replacement] = out.pop(current, None)

    return out

def create_model(model, **kwargs):
    """ Initialize a named tuple from arbitrary key-value pairs."""
    # Eats extra kwargs for flexibility.

    items = {k: v for k, v in kwargs.items() if k in model._fields}
    return model(**items)

def make_charges(charges, booking_id):
    """ Initialize a Charges named tuple."""
    js = json.dumps(charges)
    return Charges(booking_id=booking_id, recorded=js)

make_arrest = partial(create_model, model=Arrest)
make_entry = partial(create_model, model=Entry)
make_inmate = partial(create_model, model=Inmate)

