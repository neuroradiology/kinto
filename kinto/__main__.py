from __future__ import print_function
import argparse
import os
import sys

from six.moves import input
from kinto.core import scripts
from pyramid.scripts import pserve
from pyramid.paster import bootstrap
from kinto import __version__
from kinto.config import init

CONFIG_FILE = 'config/kinto.ini'


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Kinto commands")
    parser.add_argument('--ini',
                        help='Application configuration file',
                        dest='ini_file',
                        required=False,
                        default=CONFIG_FILE)
    parser.add_argument('--backend',
                        help='Specify backend',
                        dest='backend',
                        required=False,
                        default=None)

    parser.add_argument('-v', '--version',
                        action='version', version=__version__,
                        help='Print the Kinto version and exit.')

    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       dest='subcommand',
                                       help='init/start/migrate')
    subparsers.required = True

    parser_init = subparsers.add_parser('init')
    parser_init.set_defaults(which='init')

    parser_migrate = subparsers.add_parser('migrate')
    parser_migrate.set_defaults(which='migrate')

    parser_start = subparsers.add_parser('start')
    parser_start.add_argument('--reload',
                              action='store_true',
                              help='Restart when code or config changes',
                              required=False,
                              default=False)
    parser_start.set_defaults(which='start')

    parsed_args = vars(parser.parse_args(args))

    config_file = parsed_args['ini_file']

    if parsed_args['which'] == 'init':
        if os.path.exists(config_file):
            print("%s already exists." % config_file, file=sys.stderr)
            return 1

        backend = parsed_args['backend']
        if not backend:
            while True:
                prompt = ("Select the backend you would like to use: "
                          "(1 - postgresql, 2 - redis, default - memory) ")
                answer = input(prompt).strip()
                try:
                    backends = {"1": "postgresql", "2": "redis", "": "memory"}
                    backend = backends[answer]
                    break
                except KeyError:
                    pass

        init(config_file, backend)

        # Install postgresql libraries if necessary
        if backend == "postgresql":
            try:
                import psycopg2  # NOQA
            except ImportError:
                import pip
                pip.main(['install', "kinto[postgresql]"])

    elif parsed_args['which'] == 'migrate':
        env = bootstrap(config_file)
        scripts.migrate(env)

    elif parsed_args['which'] == 'start':
        pserve_argv = ['pserve', config_file]
        if parsed_args['reload']:
            pserve_argv.append('--reload')
        pserve.main(pserve_argv)

    return 0
