"""Functions to create the output spreadsheet."""

import io
import logging
import pathlib

import pandas as pd

from oss_metrics import drive

LOGGER = logging.getLogger(__name__)

DATE_COLUMNS = [
    'created_at',
    'updated_at',
    'closed_at',
    'starred_at',
    'user_created_at',
    'user_updated_at',
]


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
        output_path (str or stream):
            Path to where the file must be created, or open stream to write to.
        sheets (dict[str, pandas.DataFrame]):
            Sheets to created, passed as a dict that contains sheet titles as
            keys and sheet contents as values, passed as pandas.DataFrames.
    """
    LOGGER.info('Creating file %s', output_path)

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:  # pylint: disable=E0110
        for title, data in sheets.items():
            _add_sheet(writer, data, title)

    if drive.is_drive_path(output_path):
        folder, filename = drive.split_drive_path(output_path)
        drive.upload_spreadsheet(output, filename, folder)
    else:
        pathlib.Path(output_path).write_bytes(output.getbuffer())


def load_spreadsheet(spreadsheet):
    """Load a spreadsheet previously created by oss-metrics.

    Args:
        spreadsheet (str or stream):
            Path to where the file is stored, or open stream
            to read from.

    Return:
        dict[str, pd.DataFrame]:
            Dict of strings and dataframes with the contents
            of the spreadsheet and the date fields properly
            parsed to datetimes.
    """
    if drive.is_drive_path(spreadsheet):
        folder, filename = drive.split_drive_path(spreadsheet)
        spreadsheet = drive.download_spreadsheet(folder, filename)

    sheets = pd.read_excel(spreadsheet, sheet_name=None)
    for sheet in sheets.values():  # noqa
        for column in DATE_COLUMNS:
            if column in sheet:
                sheet[column] = pd.to_datetime(sheet[column], utc=True).dt.tz_convert(None)

    return sheets
