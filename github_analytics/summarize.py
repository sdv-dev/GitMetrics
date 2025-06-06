
import os
import pandas as pd
import logging

from github_analytics.time_utils import get_current_year, get_min_max_dt_in_year
from github_analytics.output import create_spreadsheet, load_spreadsheet

dir_path = os.path.dirname(os.path.realpath(__file__))


LOGGER = logging.getLogger(__name__)

ECOSYSTEM_COLUMN_NAME = 'Ecosystem'
TOTAL_COLUMN_NAME = 'Total Since Beginning'
OUTPUT_FILENAME = 'GitHub_Summary'
SHEET_NAMES = [
    'Unique users',
    'User issues',
    'vendor-mapping'
]

def summarize_metrics(
    projects,
    vendors,
    input_folder,
    output_folder,
    dry_run=False,
    verbose=False,
):
    vendor_df = pd.DataFrame.from_records(vendors)
    unique_users_df = _create_df()
    users_issues_df = _create_df()

    projects.extend(vendors)
    for project_info in projects:
        ecosystem_name = project_info['ecosystem']

        unique_users_row = {ECOSYSTEM_COLUMN_NAME: [ecosystem_name]}
        user_issues_row = unique_users_row.copy()

        github_org = project_info.get('github_org', ecosystem_name)
        if not github_org:
            users_issues_df = append_row(users_issues_df, user_issues_row)
            unique_users_df = append_row(unique_users_df, unique_users_row)
            continue
        github_org = github_org.lower()

        filename = f'{github_org}'
        metrics_filepath = os.path.join(input_folder, filename)
        df = load_spreadsheet(metrics_filepath)

        metrics_df = df['Metrics']
        metrics_dict = pd.Series(metrics_df['value'].values,
                                 index=metrics_df['metric']).to_dict()
        unique_users_row[TOTAL_COLUMN_NAME] = int(metrics_dict['num_issues'])
        user_issues_row[TOTAL_COLUMN_NAME] = int(metrics_dict['num_users'])

        issue_users_df = df['Unique Issue Users']
        for year in range(2021, get_current_year() + 1):
            min_datetime, max_datetime = get_min_max_dt_in_year(year)
            issue_users = issue_users_df[issue_users_df['first_issue_date'] >= min_datetime]
            issue_users = issue_users[issue_users['first_issue_date'] <= max_datetime]
            unique_users_row[year] = len(issue_users)
        unique_users_df = append_row(unique_users_df, unique_users_row)

        issues_df = df['Issues']
        for year in range(2021, get_current_year() + 1):
            min_datetime, max_datetime = get_min_max_dt_in_year(year)
            issues_in_year = issues_df[issues_df['created_at'] >= min_datetime]
            issues_in_year = issues_in_year[issues_in_year['created_at'] <= max_datetime]
            user_issues_row[year] = len(issues_in_year)

        users_issues_df = append_row(users_issues_df, user_issues_row)

    vendor_df = vendor_df.rename(columns={vendor_df.columns[0]: ECOSYSTEM_COLUMN_NAME})
    sheets = {
        SHEET_NAMES[0]: unique_users_df,
        SHEET_NAMES[1]: users_issues_df,
        SHEET_NAMES[2]: vendor_df
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
    for year in range(2021, get_current_year() + 1):
        columns.append(year)
    return pd.DataFrame(columns=columns)

def append_row(df, row):
    """Append a dictionary as a row to a DataFrame."""
    return pd.concat([df, pd.DataFrame(data=row)], ignore_index=True)