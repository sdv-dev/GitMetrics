"""OSS Metrics CLI."""

import argparse
import logging
import os
import pathlib
import sys
import warnings

import yaml

from oss_metrics.main import collect_projects

LOGGER = logging.getLogger(__name__)


def _env_setup(logfile, verbosity):
    warnings.simplefilter('ignore')

    format_ = '%(asctime)s - %(levelname)s - %(message)s'
    level = (3 - verbosity) * 10
    logging.basicConfig(filename=logfile, level=level, format=format_)
    logging.getLogger('oss_metrics').setLevel(level)
    logging.getLogger().setLevel(logging.WARN)


def _collect(args):
    token = args.token or os.getenv('GITHUB_TOKEN')
    if token is None:
        token = input('Please input your Github Token: ')

    config_file = pathlib.Path(args.config_file)
    config = yaml.safe_load(config_file.read_text())
    config_projects = config['projects']

    projects = {}
    if not args.projects:
        projects = config_projects
    else:
        for project in args.projects:
            if project not in config_projects:
                LOGGER.error('Unknown project %s', project)
                return

            projects[project] = config_projects[project]

    output_folder = args.output_folder or config.get('output_folder', '.')

    collect_projects(token, projects, output_folder)


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

    # collect
    collect = action.add_parser('collect', help='Collect github metrics.', parents=[logging_args])
    collect.set_defaults(action=_collect)

    collect.add_argument('-o', '--output-folder', type=str, required=False,
                         help='Output folder path. Defaults to .')
    collect.add_argument('-t', '--token', type=str, required=False,
                         help='Github Token to use.')
    collect.add_argument('-p', '--projects', type=str, nargs='*',
                         help='Projects to collect. Defaults to ALL if not given')
    collect.add_argument('-c', '--config-file', type=str, default='config.yaml',
                         help='Path to the configuration file.')

    return parser


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
