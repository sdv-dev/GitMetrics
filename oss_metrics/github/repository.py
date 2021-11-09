"""GraphQLClient subclass specialized in queries related to a specific repository."""

from oss_metrics.github.client import GQLClient

REPO_ENVELOPE = """
{{
    repository(owner: "{owner}", name: "{name}") {{
        {query_body}
    }}
}}
"""
STARGAZER_COUNT = 'stargazerCount'
STARGAZERS = """
stargazers(first: 100{end_cursor}) {{
    pageInfo {{
        endCursor
        hasNextPage
        hasPreviousPage
        startCursor
    }}
    totalCount
    edges {{
        node {{
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
        starredAt
    }}
}}
"""

ISSUE_COUNT = """
issues {{
    totalCount
}}
"""
ISSUES = """
issues(first: 100{end_cursor}) {{
    pageInfo {{
        endCursor
        hasNextPage
        hasPreviousPage
        startCursor
    }}
    totalCount
    edges {{
        node {{
            author {{
                login
            }}
            number
            createdAt
            closedAt
            state
            title
        }}
    }}
}}
"""


class RepositoryClient(GQLClient):
    """GraphQLClient subclass specialized in queries related to a specific repository."""

    def __init__(self, token, repo):
        owner, name = repo.split('/')
        self.owner = owner
        self.name = name
        self.repo = repo
        super().__init__(token)

    @staticmethod
    def _indent_query(query_body, **kwargs):
        if '\n' in query_body:
            query_lines = query_body.split('\n')
            indented = [
                ' ' * 8 + line
                for line in query_lines[2:]
                if line
            ]
            query_body = '\n'.join(query_lines[1:2] + indented)

        return query_body.format(**kwargs)

    def _make_query(self, query_body, **kwargs):
        query_body = self._indent_query(query_body, **kwargs)
        return REPO_ENVELOPE.format(
            owner=self.owner,
            name=self.name,
            query_body=query_body
        )[1:-1]

    def get_stargazer_count(self):
        """Get the number of stargazers of this repository."""
        query = self._make_query(STARGAZER_COUNT)
        response = self.run_query(query, prefix='data.repository')
        return response[STARGAZER_COUNT]

    @staticmethod
    def _stargazer_parser(stargazer):
        node = stargazer['node']
        return {
            'user': node['login'],
            'starred_at': stargazer['starredAt'],
            'name': node['name'],
            'email': node['email'],
            'blog': node['websiteUrl'],
            'company': node['company'],
            'location': node['location'],
            'twitter': node['twitterUsername'],
            'user_created_at': node['createdAt'],
            'user_updated_at': node['updatedAt'],
            'bio': node['bio'],
        }

    def get_stargazers(self):
        """Get the stargazers of this repository."""
        return self.paginate_collection(
            query=STARGAZERS,
            prefix='data.repository',
            total='stargazers.totalCount',
            collection_name='stargazers',
            item_parser=self._stargazer_parser,
            query_maker=self._make_query
        )

    def get_issue_count(self):
        """Get the number of issues of this repository."""
        query = self._make_query(ISSUE_COUNT)
        response = self.run_query(query, prefix='data.repository')
        return response['issues.totalCount']

    @staticmethod
    def _issue_parser(issue):
        node = issue['node']
        author = node['author'] or {}
        return {
            'user': author.get('login'),
            'created_at': node['createdAt'],
            'closed_at': node['closedAt'],
            'number': node['number'],
            'state': node['state'],
            'title': node['title'],
        }

    def get_issues(self):
        """Get the issues of this repository."""
        return self.paginate_collection(
            query=ISSUES,
            prefix='data.repository',
            total='issues.totalCount',
            collection_name='issues',
            item_parser=self._issue_parser,
            query_maker=self._make_query
        )
