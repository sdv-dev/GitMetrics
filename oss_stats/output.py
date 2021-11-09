"""Functions to create the output spreadsheet."""

import logging
from datetime import date

import pandas as pd

LOGGER = logging.getLogger(__name__)


def _add_sheet(writer, data, sheet):
    data.to_excel(writer, sheet_name=sheet, index=False)

    for column in data:
        column_width = max(data[column].astype(str).map(len).max(), len(column))
        col_idx = data.columns.get_loc(column)
        writer.sheets[sheet].set_column(col_idx, col_idx, column_width + 2)


def create_spreadsheet(filename, issues, users, stargazers):
    """Create a spreadsheet with the indicated name and data.

    If the ``filename`` variable ends in ``xlsx`` it is interpreted as
    a path to where the file must be created. Otherwise, it is interpreted
    as a name to use when constructing the final filenam, which will be
    ``github-stats-{name}-{today}.xlsx``.

    The created spreadsheet contains 3 sheets:
        - Issues:
            Where all the issues are listed, including data about
            the users who created them.
        - Unique Issue Users:
            Where the unique users that created issues
            are listed with all the information existing in their profile
        - Unique Stargazers:
            Where the unique users that stargazed the repositories
            are listed with all the information existing in their profile

    Args:
        filename (str):
            Path to where the file must be created, including the filename
            ending in ``.xlsx``, or name to be used to construct a filename.
        issues (pandas.DataFrame):
            Table of issues.
        users (pandas.DataFrame):
            Table of unique users that created issues.
        stargazers (pandas.DataFrame):
            Table of unique users that stargazed the libraries.
    """
    today = date.today().isoformat()
    if isinstance(filename, str) and not filename.endswith('.xlsx'):
        filename = f'github-stats-{filename}-{today}.xlsx'

    LOGGER.info('Creating file %s', filename)

    with pd.ExcelWriter(filename, mode='w') as writer:  # pylint: disable=E0110
        _add_sheet(writer, issues, 'Issues')
        _add_sheet(writer, users, 'Unique Issue Users')
        _add_sheet(writer, stargazers, 'Unique Stargazers')
