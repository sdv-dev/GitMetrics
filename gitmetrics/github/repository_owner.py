"""GQLClient subclass specialized in repository_owner-related queries."""

from gitmetrics.github.client import GQLClient

REPOSITORIES = """
{{
    repositoryOwner(login: "{repository_owner}") {{
        repositories(isFork: false, first: 100{end_cursor}) {{
            pageInfo {{
                endCursor
                hasNextPage
                hasPreviousPage
                startCursor
            }}
            totalCount
            edges {{
                node {{
                    name
                }}
            }}
        }}
    }}
}}
"""
REPOSITORY_COLUMNS = [
    'repository',
]


class RepositoryOwnerClient(GQLClient):
    """GQLClient subclass specialized in repository_owner-related queries."""

    def __init__(self, token, repository_owner, quiet=False):
        self._repository_owner = repository_owner
        super().__init__(token, quiet)

    @staticmethod
    def _repository_parser(user):
        node = user['node']
        return {
            'repository': node['name'],
        }

    def get_repositories(self):
        """Get the repositories of this repository owner."""
        return self.paginate_collection(
            query=REPOSITORIES,
            prefix='data.repositoryOwner',
            total='repositories.totalCount',
            collection_name='repositories',
            item_parser=self._repository_parser,
            columns=REPOSITORY_COLUMNS,
            repository_owner=self._repository_owner,
        )
