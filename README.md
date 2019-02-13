# MCJ-Booking-Log

Scrape [Marin County Jail Booking Log](http://apps.marincounty.org/BookingLog)
for inmate data.

The scraper retrieves data from the public booking log and writes it to a
Postgres (9.5+) database. It can be run as a python script or by using the
provided Docker container. The following database connection parameters must be
set as environment variables or passed to the container, respectively.

* `POSTGRES_HOST`
* `POSTGRES_PORT`
* `POSTGRES_DB`
* `POSTGRES_USER`
* `POSTGRES_PASSWORD`

To run the scraper via python, first install the runtime dependencies

```bash
pip install -r requirements.txt
```

and run the script after ensuring the necessary environment variables are set

```bash
python -m bookinglog.scrape
```

Or use the Docker container to run the scraper

```bash
docker build . --tag=mcj-scraper
docker run \
    --rm \
    -e POSTGRES_DB=${POSTGRES_DB} \
    -e POSTGRES_HOST=${POSTGRES_HOST} \
    -e POSTGRES_PORT=${POSTGRES_PORT} \
    -e POSTGRES_USER=${POSTGRES_USER} \
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    --name=mcj-booking-log \
    mcj-scraper
```


## Development

First, create a new Python 3.5 environment. Activate it and install dependencies
into it

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Choose values for and set the environment variables `POSTGRES_PORT`,
`POSTGRES_DB`, `POSTGRES_USER` and `POSTGRES_PASSWORD` for the development
database and set `POSTGRES_HOST=localhost`. Then setup the dev database

```bash
# Start database container.
docker run \
    -d \
    -p ${POSTGRES_PORT}:5432 \
    -e POSTGRES_USER=${POSTGRES_USER} \
    -e POSTGRES_DB=${POSTGRES_DB} \
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    --name=mcj-db-dev \
    postgres:9.6-alpine

# Create tables, etc.
psql \
    --host=${POSTGRES_HOST} \
    --port=${POSTGRES_PORT} \
    --user=${POSTGRES_USER} \
    --db=${POSTGRES_DB} \
    --file=db/schema.sql
```

The linter and test suite can be run from within the python environment

```bash
flake8 --config=.flake8 bookinglog/ tests/
pytest tests/
```

If you don't have a dev database set up, tests against it can be disabled by
passing `-m "not integration"` when running `pytest`. Tests that interact with
the website to be scraped can also be optionally disabled via `-m "not
external"`.
