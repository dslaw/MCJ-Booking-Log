import logging
import os


pg_kwargs = {
    "host": os.environ.get("POSTGRES_HOST"),
    "port": os.environ.get("POSTGRES_PORT"),
    "dbname": os.environ.get("POSTGRES_DB"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
}

logging_cfg = {
    "filename": "/home/dave/bookinglog-ingest.log",
    "filemode": "a",
    "level": logging.INFO,
    "format": "%(asctime)s:%(levelname)s: %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S"
}
