"""Main script."""

import logging

import pandas as pd

from oss_metrics.github.repository import RepositoryClient
from oss_metrics.github.users import UsersClient
from oss_metrics.output import create_spreadsheet

LOGGER = logging.getLogger(__name__)


def get_github_metrics(token, repositories, name):
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
    issues = pd.DataFrame()
    stargazers = pd.DataFrame()

    for repository in repositories:
        LOGGER.info('Getting issues and stargazers for %s', repository)
        repo_client = RepositoryClient(token, repository)
        issues = issues.append(repo_client.get_issues(), ignore_index=True)
        stargazers = stargazers.append(repo_client.get_stargazers(), ignore_index=True)

    LOGGER.info('Getting users')
    users_client = UsersClient(token)
    unique_users = issues.user.dropna().unique().tolist()
    users = users_client.get_users(unique_users)

    issues = issues.merge(users, how='left', on='user')

    create_spreadsheet(name, issues, users, stargazers)
