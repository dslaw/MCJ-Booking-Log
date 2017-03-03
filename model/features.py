"""Derive features."""

import pandas as pd
import re


def match(pattern, string):
    result = re.search(pattern, string, flags=re.IGNORECASE)
    return result is not None

def is_unemployed(occupation):
    """Determine employment status based on recorded occupation.
    Disability, retirement, being a student or stay at home parent
    are not considered as unemployment status.
    """

    if occupation is None or not occupation:
        return None

    occupation = occupation.lower()
    observed = ("none", "non", "never had a job", "nothing", "homeless")

    return (
        # Check substrings as "unemployed" is commonly misspelled.
        "nempl" in occupation or
        occupation.startswith("unem") or
        occupation in observed)

def is_male(s):
    return s.lower() == "m"

def is_violentcrime(charge, description):
    """Determine if a charge is for a violent crime, based on either
    the description or penal code.
    """

    # Reference:
    # http://www.cdcr.ca.gov/parole/non_revocable_parole/violent_offenses_defined.html
    names = (
        'murder',                   # 1
        'voluntary manslaughter',   # 1
        'mayhem',                   # 2
        'rape',                     # 3
        'sodomy',                   # 4
        'oral copulation',          # 5
        'lewd/lascivious|l/l act',  # 6
        'robbery',                  # 9
        'arson',                    # 10
        'penetration',              # 11
        'attempted murder',         # 12
        'kidnapping',               # 14
        'carjacking',               # 17
        'extortion'                 # 19
    )

    penal_codes = (
        '^261[^0-9]',               # 3*
        '^262[^0-9]',               # 3*
        '^288[^0-9]',               # 5*, 6*, 16
        '^12022.7[^0-9]',           # 8
        '^12022.8[^0-9]',           # 8
        '^12022.9[^0-9]',           # 8
        '^451[^0-9]',               # 10*
        '^289[^0-9]',               # 11*
        '^12308[^0-9]',             # 13
        '^12309[^0-9]',             # 13
        '^12310[^0-9]',             # 13
        '^220[^0-9]',               # 15
        '^215[^0-9]',               # 17*
        '^264.1[^0-9]',             # 18
        '^136.1[^0-9]',             # 20
        '^182.66[^0-9]',            # 20
        '^460[^0-9]',               # 21
        '^12022.53[^0-9]',          # 22
        '^11418\(B\)',              # 23
        '^11418\(C\)'               # 23
    )

    return (
        any(match(pattern, description) for pattern in names) or
        any(match(pattern, charge) for pattern in penal_codes)
    )

def is_drugcrime(charge, description):
    """Determine if a charge is for a drug crime, based on the
    description or penal code.
    """

    name_pattern = 'cntl|cntrd|contld|contrld|controlled|substance'
    penal_codes = ('113[0-9]{2}.+?',       # 11350 (A), 11377, etc
                   '381B.+?')              # Poss. nitrous oxide

    return (
        match(name_pattern, description) or
        any(match(pattern, charge) for pattern in penal_codes)
    )

def rollup_charges(x, by):
    """Collapse charges into a single record per inmate."""

    groups = x.groupby(by)
    level_defaults = {name: 0 for name in x.level[x.level.notnull()]}

    records = []
    for group_index, df in groups:
        record = {
            **level_defaults,
            **df.level.value_counts().to_dict(),
            "violent_crimes": df.violent.sum(),
            "drug_crimes":    df.drug.sum(),
            "n_charges":      df.shape[0],
            "total_bail":     df.bail.sum(),
            "booking_id":     group_index
        }
        records.append(record)

    return pd.DataFrame(records)

