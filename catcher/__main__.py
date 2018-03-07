"""Catcher - Microservices automated test tool.

Usage:
  catcher [-i INVENTORY] <tests> [-l LEVEL]
  catcher -v | --version
  catcher -h | --help

Options:
  -h --help                          show this help message and exit
  -v --version                       print version and exit
  -l LEVEL --log-level LEVEL         set log level. Options: debug, info, warning, error, critical [default: info]
  -i INVENTORY --inventory INVENTORY inventory file with environment configuration
"""
import os
import sys

from docopt import docopt, DocoptExit

from catcher import APPVSN
from catcher.core.runner import Runner
from catcher.utils import logger


# TODO variables from cmd
def main(args=None):
    try:
        arguments = docopt(__doc__, argv=args, version=APPVSN)
    except DocoptExit as usage:
        print(usage)
        sys.exit(1)
    path = os.getcwd()
    logger.configure(arguments['--log-level'])
    result = run_tests(path, arguments)
    if result:
        sys.exit(0)
    else:
        sys.exit(1)


def run_tests(path: str, arguments: dict):
    file_or_dir = arguments['<tests>']
    inventory = arguments['--inventory']
    runner = Runner(path, file_or_dir, inventory)
    return runner.run_tests()


if __name__ == "__main__":
    main()
