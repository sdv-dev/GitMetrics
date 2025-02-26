"""Function to compute the metrics from the collected data."""

import pandas as pd


def compute_metrics(issues, pull_requests, users, contributors, stargazers):
    """Compute metrics for the given data.

    Args:
        issues (pd.DataFrame):
            Issues table.
        pull_requests (pd.DataFrame):
            Pull Requests table.
        users (pd.DataFrame):
            Unique Issues table.
        contributors (pd.DataFrame):
            Unique Contributors table.
        stargazers (pd.DataFrame):
            Unique Stargazers table.

    Returns:
        pd.DataFrame:
            Table with the compute metrics, in 3 columns containing the
            metric name, the computed value and a short description of
            the metric.
    """
    num_issues = len(issues)
    num_pull_requests = len(pull_requests)
    num_users = len(users)
    num_contributors = len(contributors)
    num_stargazers = len(stargazers)
    non_contrib_users = users[~users.user.isin(contributors.user)]
    num_non_contrib_users = len(non_contrib_users)
    non_contrib_stars = stargazers[~stargazers.user.isin(contributors.user)]
    num_non_contrib_stars = len(non_contrib_stars)

    usr = num_users / num_stargazers if num_stargazers else None
    usrc = (
        num_non_contrib_users / num_non_contrib_stars if num_non_contrib_stars else None
    )

    return pd.DataFrame(
        [
            {
                "metric": "num_issues",
                "value": num_issues,
                "description": "Total number of Issues",
            },
            {
                "metric": "num_pull_requests",
                "value": num_pull_requests,
                "description": "Total number of Pull Requests",
            },
            {
                "metric": "num_users",
                "value": num_users,
                "description": "Total number of Issue Users",
            },
            {
                "metric": "num_contgributors",
                "value": num_contributors,
                "description": "Total number of Contributors",
            },
            {
                "metric": "num_stargazers",
                "value": num_stargazers,
                "description": "Total number of Stargazers",
            },
            {
                "metric": "num_non_contributor_users",
                "value": num_non_contrib_users,
                "description": "Total number of Users that are not Contributors",
            },
            {
                "metric": "num_non_contributor_stargazers",
                "value": num_non_contrib_stars,
                "description": "Total number of Stargazers that are not Contributors",
            },
            {
                "metric": "USR",
                "value": usr,
                "description": "Users / Stargazers ratio",
            },
            {
                "metric": "USR-C",
                "value": usrc,
                "description": "USR Excluding Contributors",
            },
        ]
    )
