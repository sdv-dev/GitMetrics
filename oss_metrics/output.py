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

    If the ``output_path`` variable ends in ``xlsx`` it is interpreted as
    a path to where the file must be created. Otherwise, it is interpreted
    as a name to use when constructing the final filename, which will be
    ``github-metrics-{name}-{today}.xlsx`` within the current working
    directory.

    The ``sheets`` must be passed as as dictionary that contains sheet
    titles as keys and sheet contents as values, passed as pandas.DataFrames.

    Args:
        output_path (str):
            Path to where the file must be created, including the filename
            ending in ``.xlsx``, or name to be used to construct a filename.
        sheets (dict[str, pandas.DataFrame]):
            Sheets to created, passed as a dict that contains sheet titles as
            keys and sheet contents as values, passed as pandas.DataFrames.
    """
    today = date.today().isoformat()
    if isinstance(output_path, str) and not output_path.endswith('.xlsx'):
        output_path = f'github-metrics-{output_path}-{today}.xlsx'

    LOGGER.info('Creating file %s', output_path)

    with pd.ExcelWriter(output_path, mode='w') as writer:  # pylint: disable=E0110
        for title, data in sheets.items():
            _add_sheet(writer, data, title)


DATE_COLUMNS = [
    'created_at',
    'updated_at',
    'closed_at',
    'starred_at',
    'user_created_at',
    'user_updated_at',
]


def load_spreadsheet(output_path):
    """Load a spreadsheet previously created by oss-metrics.

    Args:
        output_path (str):
            Path to where the file was stored.

    Return:
        dict[str, pd.DataFrame]:
            Dict of strings and dataframes with the contents
            of the spreadsheet and the date fields properly
            parsed to datetimes.
    """
    sheets = pd.read_excel(
        output_path,
        sheet_name=None,
    )
    for sheet in sheets.values():  # noqa
        for column in DATE_COLUMNS:
            if column in sheet:
                sheet[column] = pd.to_datetime(sheet[column], utc=True).dt.tz_convert(None)

    return sheets
