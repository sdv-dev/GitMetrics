"""Consolidate Overview Function."""

import logging
import os

import pandas as pd
from tqdm import tqdm

from github_analytics.constants import (
    ECOSYSTEM_COLUMN_NAME,
    METRIC_COLUMN_NAME,
    METRICS_SHEET_NAME,
    VALUE_COLUMN_NAME,
)
from github_analytics.output import create_spreadsheet, load_spreadsheet

OUTPUT_FILENAME = 'Consolidated_Overview'
SHEET_NAME = 'Overview'

LOGGER = logging.getLogger(__name__)


def consolidate_metrics(projects, output_folder, dry_run=False, verbose=True):
    """Consolidate GitHub Metrics from multiple spreadsheets on Google Drive.

    Args:
        projects (list[str]):
            List of projects/ecosysems to consolidate. The project must
            exactly match the file in the Google Drive folder.

        output_path (str):
            Output path on Google Drive that contains the Google Spreasheets.

        dry_run (bool):
            Whether of not to actually upload the results to Google Drive.
            If True, it just calculate the results. Defaults to False.

        verbose (bool):
            If True, will output the dataframes of the summary metrics
            (one dataframe for each sheet). Defaults to False.
    """
    rows = []
    for project in tqdm(projects):
        row_info = {ECOSYSTEM_COLUMN_NAME: project}
        filepath = os.path.join(output_folder, project)
        df = load_spreadsheet(filepath, sheet_name=METRICS_SHEET_NAME)
        row = df[[METRIC_COLUMN_NAME, VALUE_COLUMN_NAME]].T
        row = row.reset_index(drop=True)

        row = row.rename(columns=row.iloc[0])
        row = row.drop(labels=row.index[0])

        row_values = row.to_dict(orient='records')
        row_values = row_values[0]
        row_info.update(row_values)
        if verbose:
            LOGGER.info(f' {project} values: {row_info}')
        rows.append(row_info)

    consolidated_df = pd.DataFrame(rows)
    sheets = {SHEET_NAME: consolidated_df}
    if verbose:
        LOGGER.info(f'Sheet Name: {SHEET_NAME}')
        LOGGER.info(consolidated_df.to_string())
    if not dry_run:
        output_path = os.path.join(output_folder, OUTPUT_FILENAME)
        create_spreadsheet(output_path=output_path, sheets=sheets)
