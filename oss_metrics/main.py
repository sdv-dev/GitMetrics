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


def _get_users(token, issues, pull_requests, stargazers):
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
    users = _get_users(token, all_issues, all_pull_requests, stargazers)

    issues = all_issues.merge(users, how='left', on='user').drop_duplicates()
    pull_requests = all_pull_requests.merge(users, how='left', on='user').drop_duplicates()
    contributors = pull_requests[USER_COLUMNS].drop_duplicates()
    contributors = contributors.sort_values('user').reset_index(drop=True)

    if name:
        create_spreadsheet(name, issues, pull_requests, users, contributors, stargazers)
        return None

    return issues, pull_requests, users, contributors, stargazers
