"""Utility functions for Slack integration."""

import argparse
import os

from slack_sdk import WebClient

GITHUB_URL_PREFIX = 'https://github.com/datacebo/github-analytics/actions/runs/'
DEFAULT_SLACK_CHANNEL = 'sdv-alerts-debug'


def _get_slack_client():
    """Create an authenticated Slack client.

    Returns:
        WebClient:
            An authenticated Slack WebClient instance.
    """
    token = os.getenv('SLACK_TOKEN')
    client = WebClient(token=token)
    return client


def post_slack_message(channel, text):
    """Post a message to a Slack channel.

    Args:
        channel (str):
            The name of the channel to post to.
        text (str):
            The message to send to the channel.

    Returns:
        SlackResponse:
            Response from Slack API call
    """
    client = _get_slack_client()
    response = client.chat_postMessage(channel=channel, text=text)
    if not response['ok']:
        error = response.get('error', 'unknown_error')
        msg = f'{error} occured trying to post message to {channel}'
        raise RuntimeError(msg)

    return response


def post_slack_message_in_thread(channel, text, thread_ts):
    """Post a message as a threaded reply in a Slack channel.

    Args:
        channel (str):
            The name of the channel to post to.
        text (str):
            The message to send as a reply in the thread.
        thread_ts (str):
            The timestamp of the message that starts the thread.

    Returns:
        SlackResponse:
            Response from Slack API call.
    """
    client = _get_slack_client()
    response = client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)
    if not response['ok']:
        error = response.get('error', 'unknown_error')
        msg = f'{error} occurred trying to post threaded message to {channel}'
        raise RuntimeError(msg)

    return response


def send_alert(args):
    """Send an alert message to a slack channel."""
    url = GITHUB_URL_PREFIX + args.run_id
    message = f'Github Analytics build failed :fire: :dumpster-fire: :fire: See errors <{url}|here>'
    post_slack_message(args.channel, message)


def get_parser():
    """Get the parser."""
    parser = argparse.ArgumentParser(description='Function to alert when a Github workflow fails.')
    parser.add_argument('-r', '--run-id', type=str, help='The id of the github run.')
    parser.add_argument(
        '-c',
        '--channel',
        type=str,
        help='The slack channel to post to.',
        default=DEFAULT_SLACK_CHANNEL,
    )
    parser.set_defaults(action=send_alert)

    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    args.action(args)
