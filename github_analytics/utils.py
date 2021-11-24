"""Miscellaneous utilities."""

import pandas as pd


def to_utc(data):
    """Convert the input data into UTC datetime and make it non-timezone-aware."""
    datetime = pd.to_datetime(data, utc=True)
    if datetime is not None:
        datetime = datetime.tz_convert(None)

    return datetime
