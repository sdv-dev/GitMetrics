"""Time utility functions."""

from datetime import datetime


def get_current_year(tz=None):
    """Get the current year."""
    return datetime.now(tz=tz).year


def get_first_datetime_in_year(year, tzinfo=None):
    """Get the first possible datetime value in a given year."""
    min_date = datetime(year, day=1, month=1).date()
    return datetime.combine(min_date, time=datetime.min.time(), tzinfo=tzinfo)


def get_last_datetime_in_year(year, tzinfo=None):
    """Get the last possible datetime value in a given year."""
    max_date = datetime(year, day=31, month=12).date()
    return datetime.combine(max_date, time=datetime.max.time(), tzinfo=tzinfo)


def get_min_max_dt_in_year(year):
    """Get the max/min datetime values in a given year."""
    min_datetime = get_first_datetime_in_year(year)
    max_datetime = get_last_datetime_in_year(year)
    return min_datetime, max_datetime
