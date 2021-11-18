"""Main script."""

import logging
import pathlib

import pandas as pd

from oss_metrics.github.repository import RepositoryClient
from oss_metrics.github.users import UsersClient
from oss_metrics.output import create_spreadsheet, load_spreadsheet

LOGGER = logging.getLogger(__name__)

USER_COLUMNS = [
    'user',
    'name',
    'email',
    'blog',
    'company',
    'location',
    'twitter',
    'user_created_at',
    'user_updated_at',
    'bio'
]


def _get_repository_data(token, repository, previous=None):
    LOGGER.info('Getting information for repository %s', repository)
    repo_client = RepositoryClient(token, repository)
    if previous:
        prev_issues = previous['Issues']
        prev_issues = prev_issues[prev_issues.repository == repository]
        max_date = max(
            prev_issues['created_at'].max(),
            prev_issues['updated_at'].max(),
            prev_issues['closed_at'].max(),
        )
    else:
        prev_issues = None
        max_date = None

    issues = repo_client.get_issues(since=max_date)
    if issues.empty:
        issues = prev_issues
    else:
        issues.insert(1, 'repository', repository)
        if prev_issues is not None and not prev_issues.empty:
            issues = issues.append(prev_issues)
            issues = issues.sort_values(['created_at', 'closed_at'])
            issues = issues.drop_duplicates(['repository', 'number'], keep='last')

    pull_requests = repo_client.get_pull_requests()
    pull_requests.insert(1, 'repository', repository)

    stargazers = repo_client.get_stargazers()
    stargazers.insert(1, 'repository', repository)

    return issues, pull_requests, stargazers


def _get_profiles(token, issues, pull_requests, stargazers, previous):
    all_users = issues.user.append(pull_requests.user, ignore_index=True)
    unique_users = all_users.dropna().unique().tolist()

    users = stargazers[USER_COLUMNS].drop_duplicates()

    if previous:
        users = users.append(previous['Unique Issue Users'][USER_COLUMNS], ignore_index=True)
        users = users.append(previous['Unique Contributors'][USER_COLUMNS], ignore_index=True)
        users = users.append(previous['Unique Stargazers'][USER_COLUMNS], ignore_index=True)
        users = users.sort_values('user_updated_at').drop_duplicates('user', keep='last')

    known_users = users.user.dropna().unique()

    missing = list(set(unique_users) - set(known_users))
    if missing:
        LOGGER.info('Getting %s missing users', len(missing))
        users_client = UsersClient(token)
        missing_users = users_client.get_users(missing)
        users = users.append(missing_users, ignore_index=True)

    return users.sort_values('user').reset_index(drop=True)


def _get_users(issues, profiles):
    issues_by_date = issues.sort_values('created_at')
    users = issues_by_date[['user', 'created_at']].drop_duplicates(subset='user', keep='first')
    users = users.rename(columns={'created_at': 'first_issue_date'})
    users = users.merge(profiles, how='left', on='user')

    days_between = (users['first_issue_date'] - users['user_created_at']).dt.days
    users.insert(2, 'db_account_issue_creation', days_between)

    return users


def collect_project_metrics(token, repositories, output_path=None):
    """Pull data from Github to create OSS metrics.

    Args:
        token (str):
            Github token to use.
        repositories (list[str]):
            List of repositories to analyze, passed as ``{org_name}/{repo_name}``
        ouptut_path (str):
            Output path, including the ``xlsx`` extension, or name to use
            when creating the final filename
    """
    try:
        previous = load_spreadsheet(output_path)
    except FileNotFoundError:
        previous = None

    all_issues = pd.DataFrame()
    all_pull_requests = pd.DataFrame()
    all_stargazers = pd.DataFrame()

    for repository in repositories:
        issues, pull_requests, stargazers = _get_repository_data(token, repository, previous)
        all_issues = all_issues.append(issues, ignore_index=True)
        all_pull_requests = all_pull_requests.append(pull_requests, ignore_index=True)
        all_stargazers = all_stargazers.append(stargazers, ignore_index=True)

    stargazers = all_stargazers.sort_values('starred_at').drop_duplicates(subset='user')
    profiles = _get_profiles(token, all_issues, all_pull_requests, stargazers, previous)

    users = _get_users(all_issues, profiles)

    issues = all_issues.drop_duplicates()
    issues = issues.merge(profiles, how='left', on='user', suffixes=('', '_DROP'))
    issues = issues.filter(regex='^(?!.*_DROP)')

    pull_requests = all_pull_requests.merge(profiles, how='left', on='user').drop_duplicates()
    contributors = pull_requests[USER_COLUMNS].drop_duplicates()
    contributors = contributors.sort_values('user').reset_index(drop=True)

    if output_path:
        sheets = {
            'Issues': issues,
            'Pull Requests': pull_requests,
            'Unique Issue Users': users,
            'Unique Contributors': contributors,
            'Unique Stargazers': stargazers,
        }
        create_spreadsheet(output_path, sheets)
        return None

    return issues, pull_requests, users, contributors, stargazers


def collect_projects(token, projects, output_path):
    """Collect github metrics for multiple projects.

    Args:
        token (str):
            Github token to use.
        projects (dict[str, List[str]]):
            Projects to collect, passed as a dict of project names
            and lists of repositories.
        ouptut_folder (str):
            Folder in which the metrics will be stored.
    """
    if not projects:
        raise ValueError('No projects have been passed')

    for project, repositories in projects.items():
        if output_path.startswith('gdrive://'):
            project_path = f'{output_path}/{project}'
        else:
            project_path = str(pathlib.Path(output_path) / project)

        collect_project_metrics(token, repositories, project_path)
