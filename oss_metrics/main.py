"""Main script."""

import logging

import pandas as pd

from oss_metrics.github.repository import RepositoryClient
from oss_metrics.github.users import UsersClient
from oss_metrics.output import create_spreadsheet

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


def _get_repository_data(token, repository):
    LOGGER.info('Getting information for repository %s', repository)
    repo_client = RepositoryClient(token, repository)

    issues = repo_client.get_issues()
    issues.insert(1, 'repository', repository)

    pull_requests = repo_client.get_pull_requests()
    pull_requests.insert(1, 'repository', repository)

    stargazers = repo_client.get_stargazers()
    stargazers.insert(1, 'repository', repository)

    return issues, pull_requests, stargazers


def _get_profiles(token, issues, pull_requests, stargazers):
    all_users = issues.user.append(pull_requests.user, ignore_index=True)
    unique_users = all_users.dropna().unique().tolist()
    stargazer_users = stargazers.user.dropna().unique()
    missing = list(set(unique_users) - set(stargazer_users))

    users = stargazers[USER_COLUMNS].drop_duplicates()
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


def get_github_metrics(token, repositories, name=None):
    """Pull data from Github to create OSS metrics.

    Args:
        token (str):
            Github token to use.
        repositories (list[str]):
            List of repositories to analyze, passed as ``{org_name}/{repo_name}``
        filename (str):
            Output path, including the ``xlsx`` extension, or name to use
            when creating the final filename
    """
    all_issues = pd.DataFrame()
    all_pull_requests = pd.DataFrame()
    all_stargazers = pd.DataFrame()

    for repository in repositories:
        issues, pull_requests, stargazers = _get_repository_data(token, repository)
        all_issues = all_issues.append(issues, ignore_index=True)
        all_pull_requests = all_pull_requests.append(pull_requests, ignore_index=True)
        all_stargazers = all_stargazers.append(stargazers, ignore_index=True)

    stargazers = all_stargazers.sort_values('starred_at').drop_duplicates(subset='user')
    profiles = _get_profiles(token, all_issues, all_pull_requests, stargazers)

    users = _get_users(all_issues, profiles)

    issues = all_issues.merge(profiles, how='left', on='user').drop_duplicates()
    pull_requests = all_pull_requests.merge(profiles, how='left', on='user').drop_duplicates()
    contributors = pull_requests[USER_COLUMNS].drop_duplicates()
    contributors = contributors.sort_values('user').reset_index(drop=True)

    if name:
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
