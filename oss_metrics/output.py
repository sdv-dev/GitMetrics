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


def create_spreadsheet(output_path, sheets):
    """Create a spreadsheet with the indicated name and data.

    If the ``filename`` variable ends in ``xlsx`` it is interpreted as
    a path to where the file must be created. Otherwise, it is interpreted
    as a name to use when constructing the final filename, which will be
    ``github-metrics-{name}-{today}.xlsx`` within the current working
    directory.

    The ``sheets`` must be passed as as dictionary that contains sheet
    titles as keys and sheet contents as values, passed as pandas.DataFrames.

    Args:
        filename (str):
            Path to where the file must be created, including the filename
            ending in ``.xlsx``, or name to be used to construct a filename.
        sheets (dict[str, pandas.DataFrame]):
            Sheets to created, passed as a dict that contains sheet titles as
            keys and sheet contents as values, passed as pandas.DataFrames.
    """
    today = date.today().isoformat()
    if isinstance(filename, str) and not filename.endswith('.xlsx'):
        filename = f'github-metrics-{filename}-{today}.xlsx'

    LOGGER.info('Creating file %s', filename)

    with pd.ExcelWriter(output_path, mode='w') as writer:  # pylint: disable=E0110
        for title, data in sheets.items():
            _add_sheet(writer, data, title)
