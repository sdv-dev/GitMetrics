"""GraphQLClient subclass specialized in queries related to a specific repository."""

import pandas as pd

from github_analytics.github.client import GQLClient
from github_analytics.utils import to_utc

REPO_ENVELOPE = """
{{
    repository(owner: "{owner}", name: "{name}") {{
        {query_body}
    }}
}}
"""
STARGAZERS_COUNT = "stargazerCount"
STARGAZERS = """
stargazers(first: 100{end_cursor}{filter_by}) {{
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
STARGAZERS_COLUMNS = [
    "user",
    "starred_at",
    "name",
    "email",
    "blog",
    "company",
    "location",
    "twitter",
    "user_created_at",
    "user_updated_at",
    "bio",
]

ISSUES_COUNT = """
issues {{
    totalCount
}}
"""
ISSUES = """
issues(first: 100{end_cursor}{filter_by}) {{
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
            updatedAt
            closedAt
            state
            title
            comments {{
                totalCount
            }}
        }}
    }}
}}
"""
ISSUES_COLUMNS = [
    "user",
    "number",
    "comments",
    "created_at",
    "closed_at",
    "updated_at",
    "state",
    "title",
]

PULL_REQUESTS_COUNT = """
pullRequests {{
    totalCount
}}
"""
PULL_REQUESTS = """
pullRequests(first: 100{end_cursor}{filter_by}) {{
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
            updatedAt
            closedAt
            state
            title
            comments {{
                totalCount
            }}
        }}
    }}
}}
"""
PULL_REQUESTS_COLUMNS = [
    "user",
    "number",
    "comments",
    "created_at",
    "closed_at",
    "updated_at",
    "state",
    "title",
]

SINCE = ', filterBy: {{since: "{since}"}}'


class RepositoryClient(GQLClient):
    """GraphQLClient subclass specialized in queries related to a specific repository."""

    def __init__(self, token, repo, quiet):
        owner, name = repo.split("/")
        self.owner = owner
        self.name = name
        self.repo = repo
        super().__init__(token, quiet)

    @staticmethod
    def _indent_query(query_body, **kwargs):
        if "\n" in query_body:
            query_lines = query_body.split("\n")
            indented = [" " * 8 + line for line in query_lines[2:] if line]
            query_body = "\n".join(query_lines[1:2] + indented)

        return query_body.format(**kwargs)

    def _make_query(self, query_body, since=None, **kwargs):
        if pd.notna(since):
            kwargs["filter_by"] = SINCE.format(since=since.isoformat())
        else:
            kwargs.setdefault("filter_by", "")

        query_body = self._indent_query(query_body, **kwargs)
        return REPO_ENVELOPE.format(
            owner=self.owner, name=self.name, query_body=query_body
        )[1:-1]

    def get_stargazer_count(self):
        """Get the number of stargazers of this repository."""
        query = self._make_query(STARGAZERS_COUNT)
        response = self.run_query(query, prefix="data.repository")
        return response[STARGAZERS_COUNT]

    @staticmethod
    def _stargazer_parser(stargazer):
        node = stargazer["node"]
        return {
            "user": node["login"],
            "starred_at": to_utc(stargazer["starredAt"]),
            "name": node["name"],
            "email": node["email"],
            "blog": node["websiteUrl"],
            "company": node["company"],
            "location": node["location"],
            "twitter": node["twitterUsername"],
            "user_created_at": to_utc(node["createdAt"]),
            "user_updated_at": to_utc(node["updatedAt"]),
            "bio": node["bio"],
        }

    def get_stargazers(self, since=None):
        """Get the stargazers of this repository."""
        return self.paginate_collection(
            query=STARGAZERS,
            prefix="data.repository",
            total="stargazers.totalCount",
            collection_name="stargazers",
            item_parser=self._stargazer_parser,
            query_maker=self._make_query,
            since=since,
            columns=STARGAZERS_COLUMNS,
        )

    def get_issue_count(self):
        """Get the number of issues of this repository."""
        query = self._make_query(ISSUES_COUNT)
        response = self.run_query(query, prefix="data.repository")
        return response["issues.totalCount"]

    @staticmethod
    def _issue_parser(issue):
        node = issue["node"]
        author = node["author"] or {}
        return {
            "user": author.get("login"),
            "number": node["number"],
            "comments": node["comments.totalCount"],
            "created_at": to_utc(node["createdAt"]),
            "closed_at": to_utc(node["closedAt"]),
            "updated_at": to_utc(node["updatedAt"]),
            "state": node["state"],
            "title": node["title"],
        }

    def get_issues(self, since=None):
        """Get the issues of this repository."""
        return self.paginate_collection(
            query=ISSUES,
            prefix="data.repository",
            total="issues.totalCount",
            collection_name="issues",
            item_parser=self._issue_parser,
            query_maker=self._make_query,
            since=since,
            columns=ISSUES_COLUMNS,
        )

    def get_pull_requests_count(self):
        """Get the number of pull requests of this repository."""
        query = self._make_query(PULL_REQUESTS_COUNT)
        response = self.run_query(query, prefix="data.repository")
        return response["pullRequests.totalCount"]

    @staticmethod
    def _pull_request_parser(pull_request):
        node = pull_request["node"]
        author = node["author"] or {}
        return {
            "user": author.get("login"),
            "number": node["number"],
            "comments": node["comments.totalCount"],
            "created_at": to_utc(node["createdAt"]),
            "closed_at": to_utc(node["closedAt"]),
            "updated_at": to_utc(node["updatedAt"]),
            "state": node["state"],
            "title": node["title"],
        }

    def get_pull_requests(self, since=None):
        """Get the pull requests of this repository."""
        return self.paginate_collection(
            query=PULL_REQUESTS,
            prefix="data.repository",
            total="pullRequests.totalCount",
            collection_name="pullRequests",
            item_parser=self._pull_request_parser,
            query_maker=self._make_query,
            since=since,
            columns=PULL_REQUESTS_COLUMNS,
        )
