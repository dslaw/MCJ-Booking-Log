"""EDA on number of daily arrivals."""

from datetime import date, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psycopg2

from config import pg_kwargs

with open("arrivals.sql", "r") as fh:
    query = fh.read()

# NB: can't differentiate between no arrivals on a given day and
# missing data - should be possible to cross reference with scraper
# logs to do this later.
with psycopg2.connect(**pg_kwargs) as conn:
    x = pd.read_sql(query, con=conn)
    x.rename(columns={"n": "counts"}, inplace=True)


# Get dates for California.
offset = timedelta(hours=8)
pst_dates = x.booking_date - offset
x.booking_date = pst_dates.dt.date

# Use data that has been collected regularly.
start_date = date(2016, 8, 1)
y = x.loc[x.booking_date >= start_date]


# Summarize.
bars = y.groupby("counts").count().reset_index()

fig, axes = plt.subplots(1, 2)
# Time series.
axes[0].plot(y.booking_date, y.counts)
axes[0].set_xlabel("Booking Date")
axes[0].set_ylabel("Arrivals")
# Distribution of daily arrivals.
axes[1].bar(bars.counts, bars.booking_date)
axes[1].set_xlabel("Arrivals")

median = np.nanmedian(y.counts)
spread = np.nanmean(np.abs(y.counts - median))

# Distribution over day of week.
y["dow"] = pd.to_datetime(y.booking_date).dt.dayofweek
total_by_day = y.groupby("dow").counts.sum()
total_by_day.plot.bar()

