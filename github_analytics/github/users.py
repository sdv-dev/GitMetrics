"""GQLClient subclass specialized in user-related queries."""

import logging

import pandas as pd
from tqdm.auto import tqdm

from github_analytics.github.client import GQLClient
from github_analytics.utils import to_utc

LOGGER = logging.getLogger(__name__)

USERS = """
{{
    search(query: "{usernames}", type: USER, first: 100{end_cursor}) {{
        pageInfo {{
            endCursor
            hasNextPage
            hasPreviousPage
            startCursor
        }}
        userCount
        edges {{
            node {{
                ... on User {{
                    login
                    name
                    email
                    websiteUrl
                    company
                    location
                    twitterUsername
                    createdAt
                    updatedAt
                    bio
                }}
            }}
        }}
    }}
}}
"""


class UsersClient(GQLClient):
    """GQLClient subclass specialized in user-related queries."""

    @staticmethod
    def _user_parser(user):
        node = user['node']
        return {
            'user': node['login'],
            'name': node['name'],
            'email': node['email'],
            'blog': node['websiteUrl'],
            'company': node['company'],
            'location': node['location'],
            'twitter': node['twitterUsername'],
            'user_created_at': to_utc(node['createdAt']),
            'user_updated_at': to_utc(node['updatedAt']),
            'bio': node['bio'],
        }

    def get_users(self, usernames):
        """Get the profiles of the indicated usernames."""
        out = pd.DataFrame()
        total = len(usernames)

        desc = f'Collecting {total} users'
        pbar = tqdm(total=total, disable=self.quiet, desc=desc, unit=' users')
        if self.quiet:
            LOGGER.info(desc)

        for index in range(0, total, 100):
            chunk = usernames[index:index + 100]
            usernames_query = ' '.join(f'user:{user}' for user in chunk)
            chunk_users = self.paginate_collection(
                query=USERS,
                prefix='data.search',
                total='userCount',
                item_parser=self._user_parser,
                pbar=pbar,
                usernames=usernames_query
            )
            out = out.append(chunk_users, ignore_index=True)

        pbar.close()

        return out.sort_values('user', ignore_index=True)
