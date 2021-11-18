"""GraphQL client that handles requests and collection pagination."""

import logging

import pandas as pd
import requests
from benedict import benedict
from tqdm.auto import tqdm

LOGGER = logging.getLogger(__name__)


GRAPHQL_URL = 'https://api.github.com/graphql'


class GQLClient:
    """Generic Github API v4 client that handles pagination.

    Args:
        token (str):
            Github token to use.
    """

    def __init__(self, token, quiet):
        self.token = token
        self.quiet = quiet
        self.headers = {'Authorization': f'token {token}'}

    def run_query(self, query, query_maker=None, prefix=None, **kwargs):
        """Execute the given query and extract the body from the prefix key.

        Args:
            query (str):
                Query to execute.
            query_maker (function):
                If given, pass the given query to this function to make the
                final query.
            prefix (str):
                If given, pull the body from the response using the given key.
            **kwargs:
                Any additional quargs are passed down to the query_maker.

        Returns:
            benedict:
                The body of the response.

        Raises:
            RuntimeError:
                If the HTTP request failed.
        """
        if query_maker:
            query = query_maker(query, **kwargs)
        elif kwargs:
            query = query.format(**kwargs)

        LOGGER.debug(query)

        response = requests.post(
            GRAPHQL_URL,
            json={'query': query},
            headers=self.headers
        )

        if response.status_code != 200:
            raise RuntimeError(f'Query fail ({response.status_code}): {response.content}')

        response = benedict(response.json())
        if 'errors' in response:
            LOGGER.error(response.to_json(indent=4))
            raise ValueError(response['errors'][0]['message'])

        LOGGER.debug(response.to_json(indent=4))

        if prefix:
            return response[prefix]

        return response

    def paginate_collection(self, query, prefix, total, item_parser, query_maker=None,
                            collection_name=None, pbar=None, **kwargs):
        """Run the given query and paginate the corresponding collection.

        Args:
            query (str):
                Query to execute.
            prefix (str):
                Key where the response body is found.
            total (str or int):
                Total number of elements in the collection or key where the
                corresponding value can be found inside the response.
            item_parser (function):
                Apply this function to each element in the collection
                to parse it and build the output.
            query_maker (function):
                Function to use to build the query. Optional.
            collection_name (str):
                If given, pull the collection contents from the body using the
                indicated key.
            pbar (tqdm):
                tqdm progress bar to update. If not given, one is initialized.
            **kwargs:
                Any additional keyword arguments are passed to the query_maker.

        Returns:
            pandas.DataFrame:
                Table with the collection contents.
        """
        response = self.run_query(query, query_maker, prefix, end_cursor='', **kwargs)
        if isinstance(total, str):
            total = response[total]

        message = f'Collecting {total} {collection_name}'
        if self.quiet:
            LOGGER.info(message)

        data = []
        if pbar is None:
            _pbar = tqdm(total=total, disable=self.quiet, desc=message, unit=' ' + collection_name)
        else:
            _pbar = pbar

        while True:
            if collection_name:
                collection = response[collection_name]
            else:
                collection = response

            page_info = collection['pageInfo']
            has_next_page = page_info['hasNextPage']
            end_cursor = f', after: "{page_info["endCursor"]}"'

            for item in collection['edges']:
                try:
                    data.append(item_parser(item))
                except (TypeError, KeyError):
                    # Possibly a bot, like dependabot
                    pass

                _pbar.update(1)

            if not has_next_page:
                break

            response = self.run_query(query, query_maker, prefix,
                                      end_cursor=end_cursor, **kwargs)

        if pbar is None:
            _pbar.close()

        return pd.DataFrame(data)
