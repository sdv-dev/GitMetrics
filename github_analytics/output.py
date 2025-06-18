"""Functions to create the output spreadsheet."""

import io
import logging
import pathlib

import pandas as pd

from github_analytics import drive

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
        column_length = None
        if isinstance(column, (int, float)):
            column_length = len(str(column))
        else:
            column_length = len(column)

        column_width = max(data[column].astype(str).map(len).max(), column_length)
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
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:  # pylint: disable=E0110
        for title, data in sheets.items():
            _add_sheet(writer, data, title)

    if drive.is_drive_path(output_path):
        LOGGER.info('Creating file %s', output_path)
        folder, filename = drive.split_drive_path(output_path)
        drive.upload_spreadsheet(output, filename, folder)
    else:
        if not output_path.endswith('.xslx'):
            output_path += '.xlsx'

        LOGGER.info('Creating file %s', output_path)
        output_path = pathlib.Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(output.getbuffer())


def load_spreadsheet(spreadsheet, sheet_name=None):
    """Load a spreadsheet previously created by github-analytics.

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
        path = spreadsheet
        folder, filename = drive.split_drive_path(spreadsheet)
        spreadsheet = drive.download_spreadsheet(folder, filename)
    elif not spreadsheet.endswith('.xslx'):
        spreadsheet += '.xlsx'
        path = spreadsheet

    sheets = pd.read_excel(spreadsheet, sheet_name=sheet_name)
    if not sheet_name:
        for sheet in sheets.values():  # noqa
            for column in DATE_COLUMNS:
                if column in sheet:
                    sheet[column] = pd.to_datetime(sheet[column], utc=True).dt.tz_convert(None)
    else:
        for column in DATE_COLUMNS:
            if column in sheets:
                sheets[column] = pd.to_datetime(sheets[column], utc=True).dt.tz_convert(None)

    LOGGER.info('Loaded spreadsheet %s', path)

    return sheets
