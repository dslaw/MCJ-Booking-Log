import logging

# TODO: read a config file in resources/
pg_kwargs = {
    "host": "localhost",
    "port": 5433,
    "dbname": "bookinglog",
    "user": "mcj",
    "password": "breakfasttrays"
}

logging_cfg = {
    "filename": "/home/dave/bookinglog-ingest.log",
    "filemode": "a",
    "level": logging.INFO,
    "format": "%(asctime)s:%(levelname)s: %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S"
}

