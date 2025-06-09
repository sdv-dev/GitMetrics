"""Summarize GitHub Analytics."""

import logging
import os

import pandas as pd

from github_analytics.output import create_spreadsheet, load_spreadsheet
from github_analytics.time_utils import get_current_year, get_min_max_dt_in_year

dir_path = os.path.dirname(os.path.realpath(__file__))


LOGGER = logging.getLogger(__name__)

ECOSYSTEM_COLUMN_NAME = 'Ecosystem'
TOTAL_COLUMN_NAME = 'Total Since Beginning'
OUTPUT_FILENAME = 'GitHub_Summary'
SHEET_NAMES = ['Unique users', 'User issues', 'vendor-mapping']
START_YEAR = 2021


def _extract_row(df, date_column):
    row = {TOTAL_COLUMN_NAME: [len(df)]}
    for year in range(START_YEAR, get_current_year() + 1):
        min_datetime, max_datetime = get_min_max_dt_in_year(year)
        matching_df = df[df[date_column] >= min_datetime]
        matching_df = matching_df[matching_df[date_column] <= max_datetime]
        row[year] = [len(matching_df)]
    return row


def summarize_metrics(
    projects,
    vendors,
    input_folder,
    output_folder,
    dry_run=False,
    verbose=False,
):
    """Summarize GitHub analytics.

    Args:
        projects (dict[str, str | list[str]]):
            List of projects/ecosysems to summarize. Must contain
            If it is an ecosystem and download counts needs to be adjusted it must have:
                - base_project (str): This is the base project for the ecosystem.
                - dependency_projects (list[str]): These are direct dependencies of the base project
                    and maintained by the same org.
                    The downlaods counts are subtracted from the base project, since they are
                    direct dependencies.
                - parent_projects (list[str]): These are parent projects maintained by the same org.
                    These parent projects have a core dependency on the base project.
                    Their base project download count is subtracted from each parent parent.
            If the downloads counts should be simply added together, then the following is required:
                - projects (list[list]): The list of projects to add.
        vendors (dict[str, str | list[str]]):
            The vendors and the projects owned by the Vendors.
            FOr each vendor, the following must be defined:
                - ecosystem (str): The user facing name.
                - name (str): The actual name of the vendor.
                - projects (list[str]): The projects owned by the vendor.
                    The downloads counts are summed.

        input_folder (str):
            The folder containing the location collected GitHub metrics.
            The folder must only contain xlsx files.
            The name of each file must match the `github_org` in summarize_config.yaml.
            The GitHub metrics are computed from the xlsx files in this folder.

        output_folder (str):
            Folder in which GitHub_Summary.xlsx will be written.
            It can be passed as a local folder or as a Google Drive path in the format
            `gdrive://{folder_id}`.

        dry_run (bool):
            Whether of not to actually upload the summary results.
            If true, it just calculate the summary results. Defaults to False.

        verbose (bool):
            If true, will output the dataframes of the summary metrics
            (one dataframe for each sheet). Defaults to False.

    """
    vendor_df = pd.DataFrame.from_records(vendors)
    unique_users_df = _create_df()
    users_issues_df = _create_df()

    projects.extend(vendors)
    for project_info in projects:
        ecosystem_name = project_info['ecosystem']

        github_org = project_info.get('github_org', ecosystem_name)
        if not github_org:
            users_issues_df = append_row(users_issues_df, {ECOSYSTEM_COLUMN_NAME: [ecosystem_name]})
            unique_users_df = append_row(unique_users_df, {ECOSYSTEM_COLUMN_NAME: [ecosystem_name]})
            continue
        github_org = github_org.lower()

        filename = f'{github_org}'
        metrics_filepath = os.path.join(input_folder, filename)
        df = load_spreadsheet(metrics_filepath, sheet_name=None)

        unique_issue_users_df = df['Unique Issue Users']
        unique_users_row = _extract_row(
            unique_issue_users_df,
            'first_issue_date',
        )
        unique_users_row[ECOSYSTEM_COLUMN_NAME] = [ecosystem_name]
        unique_users_df = append_row(unique_users_df, unique_users_row)

        issues_df = df['Issues']
        issues_row = _extract_row(
            issues_df,
            'created_at',
        )
        issues_row[ECOSYSTEM_COLUMN_NAME] = [ecosystem_name]
        users_issues_df = append_row(users_issues_df, issues_row)

    vendor_df = vendor_df.rename(columns={vendor_df.columns[0]: ECOSYSTEM_COLUMN_NAME})
    sheets = {
        SHEET_NAMES[0]: unique_users_df,
        SHEET_NAMES[1]: users_issues_df,
        SHEET_NAMES[2]: vendor_df,
    }
    if verbose:
        for sheet_name, df in sheets.items():
            LOGGER.info(f'Sheet Name: {sheet_name}')
            LOGGER.info(df)
    if not dry_run:
        # Write to Google Drive/Output folder
        output_path = os.path.join(output_folder, OUTPUT_FILENAME)
        create_spreadsheet(output_path=output_path, sheets=sheets)

        # Write to local directory
        output_path = os.path.join(dir_path, OUTPUT_FILENAME)
        create_spreadsheet(output_path=output_path, sheets=sheets)


def _create_df():
    columns = [ECOSYSTEM_COLUMN_NAME, TOTAL_COLUMN_NAME]
    for year in range(START_YEAR, get_current_year() + 1):
        columns.append(year)
    return pd.DataFrame(columns=columns)


def append_row(df, row):
    """Append a dictionary as a row to a DataFrame."""
    return pd.concat([df, pd.DataFrame(data=row)], ignore_index=True)
