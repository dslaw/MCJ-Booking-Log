from setuptools import setup


pkg_name = "bookinglog"

with open("requirements.txt") as fh:
    dependencies = [line.strip() for line in fh]

setup(
    description="Scrape Marin County Jail Booking Log",
    install_requires=dependencies,
    name=pkg_name,
    entry_points={
        "console_scripts": "bookinglog=bookinglog.scrape:main"
    },
    package_data={pkg_name: ["tests/data/*"]},
    packages=[pkg_name]
)

