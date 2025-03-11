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
                The traffic API endpoint (e.g., "popular/referrers", "popular/paths", "views" or
                "clones").

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
        df.rename(
            columns={'referrer': 'site', 'count': 'views', 'uniques': 'unique_visitors'},
            inplace=True
        )
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
        df.rename(
            columns={'path': 'content', 'count': 'views', 'uniques': 'unique_visitors'},
            inplace=True
        )
        LOGGER.info(f'Retrieved {len(df)} path records for {repo}.')
        return df

    def get_traffic_views(self, repo: str) -> pd.DataFrame:
        """Fetches the number of views for the given repository over time.

        Args:
            repo (str):
                The repository in the format "owner/repo".

        Returns:
            pd.DataFrame:
                DataFrame containing repository views with columns:
                    - `timestamp`: Date of views.
                    - `count`: Number of views.
                    - `uniques`: Number of unique visitors.
        """
        data = self._get_traffic_data(repo, 'views')
        df = pd.DataFrame(data['views'], columns=['timestamp', 'count', 'uniques'])
        df.rename(columns={'count': 'views', 'uniques': 'unique_visitors'}, inplace=True)
        LOGGER.info(f'Retrieved {len(df)} views for {repo}.')
        return df

    def get_traffic_clones(self, repo: str) -> pd.DataFrame:
        """Fetches the number of repository clones over time.

        Args:
            repo (str):
                The repository in the format "owner/repo".

        Returns:
            pd.DataFrame:
                DataFrame containing repository clones with columns:
                    - `timestamp`: Date of clones.
                    - `count`: Number of clones.
                    - `uniques`: Number of unique cloners.
        """
        data = self._get_traffic_data(repo, 'clones')
        df = pd.DataFrame(data['clones'], columns=['timestamp', 'count', 'uniques'])
        df.rename(columns={'count': 'clones', 'uniques': 'unique_cloners'}, inplace=True)
        LOGGER.info(f'Retrieved {len(df)} clones for {repo}.')
        return df

    def generate_timeframe(cls, traffic_data):
        """Generates a timeframe DataFrame with the start and end timestamps from traffic data.

        Args:
            traffic_data (dict[str, pd.DataFrame]):
                Dictionary containing traffic data, including "Traffic Visitors" and
                "Traffic Git Clones".

        Returns:
            pd.DataFrame:
                A DataFrame with a single row containing 'Start Date' and 'End Date'.
        """
        start_date = None
        end_date = None
        all_timestamps = []

        if 'Traffic Visitors' in traffic_data and not traffic_data['Traffic Visitors'].empty:
            all_timestamps.extend(traffic_data['Traffic Visitors']['timestamp'].tolist())

        if 'Traffic Git Clones' in traffic_data and not traffic_data['Traffic Git Clones'].empty:
            all_timestamps.extend(traffic_data['Traffic Git Clones']['timestamp'].tolist())

        if all_timestamps:
            start_date = min(all_timestamps)
            end_date = max(all_timestamps)

        return pd.DataFrame({'Start Date': [start_date], 'End Date': [end_date]})

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
                    - `"views"`: DataFrame with repository views over time.
                    - `"clones"`: DataFrame with repository clones over time.
        """
        traffic_data = {
            'Traffic Referring Sites': self.get_traffic_referrers(repo),
            'Traffic Popular Content': self.get_traffic_paths(repo),
            'Traffic Visitors': self.get_traffic_views(repo),
            'Traffic Git Clones': self.get_traffic_clones(repo),
        }
        traffic_data['Timeframe'] = self.generate_timeframe(traffic_data)
        return traffic_data
