import psycopg2
import pytest
import responses

from bookinglog import config
from bookinglog import scrape


@pytest.fixture
def cursor():
    with psycopg2.connect(**config.pg_kwargs) as conn:
        cursor = conn.cursor()
        yield cursor

        # Clear _everything_.
        cursor.execute("delete from arrests")
        cursor.execute("delete from inmates")
        cursor.execute("delete from charges")
        cursor.execute("delete from booking cascade")
        conn.commit()

@pytest.fixture(scope="module")
def html():
    with open("tests/data/mock.html") as fh:
        mock_html = fh.read()
    return mock_html


class TestScraper(object):
    @pytest.mark.integration
    @responses.activate
    def test_db_integration(self, html, cursor):
        # Ignore the search type - it only effects the search results.
        responses.add(
            method="POST",
            url="http://apps.marincounty.org/BookingLog/Booking/Action",
            body=html,
        )

        expected_count = 2

        scrape.main("latest")

        cursor.execute("select count(*) from booking")
        booking_count = cursor.fetchone()[0]
        assert booking_count == expected_count

        cursor.execute("select count(*) from arrests")
        arrests_count = cursor.fetchone()[0]
        assert arrests_count == expected_count

        cursor.execute("select count(*) from inmates")
        inmates_count = cursor.fetchone()[0]
        assert inmates_count == expected_count

        cursor.execute("select count(*) from charges")
        charges_count = cursor.fetchone()[0]
        assert charges_count == expected_count
