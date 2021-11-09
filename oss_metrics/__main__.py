"""OSS Metrics CLI."""

import argparse
import logging
import sys
import warnings

from oss_metrics.main import get_github_metrics


def _env_setup(logfile, verbosity):
    warnings.simplefilter('ignore')

    format_ = '%(asctime)s - %(process)d - %(levelname)s - %(name)s - %(module)s - %(message)s'
    level = (3 - verbosity) * 10
    logging.basicConfig(filename=logfile, level=level, format=format_)
    logging.getLogger('oss_metrics').setLevel(level)
    logging.getLogger().setLevel(logging.WARN)


def _get_parser():
    # Logging
    logging_args = argparse.ArgumentParser(add_help=False)
    logging_args.add_argument('-v', '--verbose', action='count', default=1)
    logging_args.add_argument('-l', '--logfile')

    parser = argparse.ArgumentParser(
        prog='oss-metrics',
        description='OSS metrics Command Line Interface',
        parents=[logging_args]
    )
    parser.set_defaults(action=None)
    action = parser.add_subparsers(title='action')
    action.required = True

    # run
    github = action.add_parser('github', help='Collect github metrics.', parents=[logging_args])
    github.set_defaults(action=_github)

    github.add_argument('-o', '--output', type=str, required=False,
                        help='Path or name to use for the output file.')
    github.add_argument('-t', '--token', type=str, required=False,
                        help='Github Token to use.')
    github.add_argument('repositories', type=str, nargs='+',
                        help='Name of the repositories to collect.')

    return parser


def _github(args):
    token = args.token
    if token is None:
        token = input('Please input your Github Token: ')

    repositories = args.repositories
    output = args.output
    if output is None:
        output = repositories[0].split('/', 1)[0]

    get_github_metrics(token, repositories, output)


def main():
    """Run OSS Metrics CLI."""
    parser = _get_parser()
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    _env_setup(args.logfile, args.verbose)
    args.action(args)


if __name__ == '__main__':
    main()
