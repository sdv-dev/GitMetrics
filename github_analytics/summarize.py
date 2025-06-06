
import os
import pandas as pd

ECOSYSTEM_COLUMN_NAME = 'Ecosystem'
TOTAL_COLUMN_NAME = 'Total Since Beginning'
from github_analytics.time_utils import get_current_year, get_min_max_dt_in_year
OUTPUT_FILENAME = 'GitHub_Summary'

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

        filename = f'{github_org}.xlsx'
        metrics_filepath = os.path.join(input_folder, filename)
        metrics_df = pd.read_excel(metrics_filepath)

        metrics_dict = pd.Series(metrics_df['value'].values,
                                 index=metrics_df['metric']).to_dict()
        unique_users_row[TOTAL_COLUMN_NAME] = int(metrics_dict['num_issues'])
        user_issues_row[TOTAL_COLUMN_NAME] = int(metrics_dict['num_users'])

        issue_users_df = pd.read_excel(metrics_filepath,
                                  sheet_name="Unique Issue Users",
                                  parse_dates=['first_issue_date'])
        for year in range(2021, get_current_year() + 1):
            min_datetime, max_datetime = get_min_max_dt_in_year(year)
            issue_users = issue_users_df[issue_users_df['first_issue_date'] >= min_datetime]
            issue_users = issue_users[issue_users['first_issue_date'] <= max_datetime]
            unique_users_row[year] = len(issue_users)

        unique_users_df = append_row(unique_users_df, unique_users_row)

        issues_df = pd.read_excel(metrics_filepath,
                                  sheet_name="Issues",
                                  parse_dates=['created_at'])

        for year in range(2021, get_current_year() + 1):
            min_datetime, max_datetime = get_min_max_dt_in_year(year)
            issues_in_year = issues_df[issues_df['created_at'] >= min_datetime]
            issues_in_year = issues_in_year[issues_in_year['created_at'] <= max_datetime]
            user_issues_row[year] = len(issues_in_year)

        users_issues_df = append_row(users_issues_df, user_issues_row)

    print(users_issues_df)
    print(unique_users_df)
    print(vendor_df)


def _create_df():
    columns = [ECOSYSTEM_COLUMN_NAME, TOTAL_COLUMN_NAME]
    for year in range(2021, get_current_year() + 1):
        columns.append(year)
    return pd.DataFrame(columns=columns)

def append_row(df, row):
    """Append a dictionary as a row to a DataFrame."""
    return pd.concat([df, pd.DataFrame(data=row)], ignore_index=True)