"""Traffic client for retrieving github information."""

import logging

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

GITHUB_API_URL = 'https://api.github.com'


class TrafficClient:
    """Client to fetch traffic data (popular referrers & paths) for a given repository.

    Args:
        token (str):
            GitHub personal access token for authentication.
        quiet (bool, optional):
            If True, suppresses output logging. Defaults to False.
    """

    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
        }

    def _get_traffic_data(self, repo: str, endpoint: str) -> list:
        """Helper method to fetch traffic data from GitHub's REST API.

        Args:
            repo (str):
                The repository in the format "owner/repo".
            endpoint (str):
                The traffic API endpoint (e.g., "popular/referrers" or "popular/paths").

        Returns:
            list:
                The JSON response containing traffic data.

        Raises:
            RuntimeError:
                If the API request fails.
        """
        url = f'{GITHUB_API_URL}/repos/{repo}/traffic/{endpoint}'
        LOGGER.info(f'Fetching traffic data from: {url}')

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            LOGGER.info(f'Successfully retrieved {endpoint} data for {repo}.')
            return response.json()
        else:
            LOGGER.error(f'GitHub API Error ({response.status_code}): {response.json()}')
            raise RuntimeError(f'GitHub API Error ({response.status_code}): {response.json()}')

    def get_traffic_referrers(self, repo: str) -> pd.DataFrame:
        """Fetches the top referring domains that send traffic to the given repository.

        Args:
            repo (str):
                The repository in the format "owner/repo".

        Returns:
            pd.DataFrame:
                DataFrame containing referrer traffic details with columns:
                    - `referrer`: Source domain.
                    - `count`: Number of views.
                    - `uniques`: Number of unique visitors.
        """
        LOGGER.info(f'Fetching traffic referrers for {repo}.')
        data = self._get_traffic_data(repo, 'popular/referrers')
        df = pd.DataFrame(data, columns=['referrer', 'count', 'uniques'])
        LOGGER.info(f'Retrieved {len(df)} referrer records for {repo}.')
        return df

    def get_traffic_paths(self, repo: str) -> pd.DataFrame:
        """Fetches the most visited paths in the given repository.

        Args:
            repo (str):
                The repository in the format "owner/repo".

        Returns:
            pd.DataFrame: DataFrame containing popular paths with columns:
                - `path`: The visited path.
                - `title`: Page title.
                - `count`: Number of views.
                - `uniques`: Number of unique visitors.
        """
        LOGGER.info(f'Fetching traffic paths for {repo}.')
        data = self._get_traffic_data(repo, 'popular/paths')
        df = pd.DataFrame(data, columns=['path', 'title', 'count', 'uniques'])
        LOGGER.info(f'Retrieved {len(df)} path records for {repo}.')
        return df

    def get_all_traffic(self, repo: str) -> dict[str, pd.DataFrame]:
        """Fetches all available traffic data for the given repository.

        Args:
            repo (str):
                The repository in the format "owner/repo".

        Returns:
            dict[str, pd.DataFrame]:
                A dictionary containing traffic data:
                    - `"referrers"`: DataFrame with referrer traffic.
                    - `"paths"`: DataFrame with popular paths.
        """
        LOGGER.info(f'Fetching all traffic data for {repo}.')
        traffic_data = {
            'Traffic Referrers': self.get_traffic_referrers(repo),
            'Traffic Paths': self.get_traffic_paths(repo),
        }
        LOGGER.info(f'Successfully retrieved all traffic data for {repo}.')
        return traffic_data
