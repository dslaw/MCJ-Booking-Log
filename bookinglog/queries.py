insert_entry = (
    "INSERT INTO booking "
    "(jail_id, orig_booking_date, latest_charge_date) "
    "VALUES (%(jail_id)s, %(orig_booking_date)s, %(latest_charge_date)s) "
    "ON CONFLICT (jail_id) DO UPDATE "
    "SET jail_id = EXCLUDED.jail_id, "
    "  orig_booking_date = EXCLUDED.orig_booking_date, "
    "  latest_charge_date = EXCLUDED.latest_charge_date "
    "RETURNING id"
)

insert_arrest = (
    "INSERT INTO arrests "
    "(booking_id, arrest_date, agency, location) "
    "VALUES (%(booking_id)s, %(arrest_date)s, %(arrest_agency)s, %(arrest_location)s) "
    "ON CONFLICT (booking_id) DO UPDATE "
    "SET arrest_date = EXCLUDED.arrest_date, "
    "  agency = EXCLUDED.agency, "
    "  location = EXCLUDED.location"
)

insert_inmate = (
    "INSERT INTO inmates "
    "(booking_id, name, dob, eye_color, hair_color, height, weight, race, sex, occupation) "
    "VALUES (%(booking_id)s, %(name)s, %(date_of_birth)s, %(eye_color)s, %(hair_color)s, %(height)s, %(weight)s, %(race)s, %(sex)s, %(occupation)s) "
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
    "VALUES (%(booking_id)s, %(recorded)s) "
    "ON CONFLICT (booking_id) DO UPDATE "
    "SET recorded = EXCLUDED.recorded"
)
