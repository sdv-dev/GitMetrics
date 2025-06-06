"""Miscellaneous utilities."""

import pandas as pd
import validators
from validators.utils import ValidationError


def to_utc(data):
    """Convert the input data into UTC datetime and make it non-timezone-aware."""
    datetime = pd.to_datetime(data, utc=True)
    if datetime is not None:
        datetime = datetime.tz_convert(None)

    return datetime


def is_url(url_string: str) -> bool:
    """Check if a URL is valid."""
    result = validators.url(url_string)
    if isinstance(result, ValidationError):
        return False
    return result
