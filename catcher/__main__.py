"""Catcher - Microservices automated test tool.

Usage:
  catcher [-i INVENTORY] <tests> [-l LEVEL] [-e VARS...] [-m MODS...]... [-r RES] [-p FORMAT] [-s SYS_ENV] [-f FILTER]... [--q | --qq] [--no-color]
  catcher -v | --version
  catcher -h | --help

Options:
  -h --help                          show this help message and exit
  -v --version                       print version and exit
  -l LEVEL --log-level LEVEL         set log level. Options: debug, info, warning, error, critical [default: info]
  -i INVENTORY --inventory INVENTORY inventory file with environment configuration
  -e VARIABLE --environment VARIABLE set variable (will override inventory).
  -s SYS_ENV --system_env SYS-ENV    use system environment variables as variables [default: true]
  -m MODULES --modules MODULES       specify directories or python packages to search for external modules
  -r RESOURCES --resources RESOURCES set the resources dir [default: ./resources]
  -p FORMAT --format FORMAT          set the format (json) for the resulting file, which includes all steps
                                     execution results, variables and outputs. It is created in the `reports` directory.
                                     Is not created by default.
  -f FILTER --filter FILTER          Path to python file with custom filters implementation or python module's path if
                                     installed in the system.
  --q                                Do not print steps output
  --qq                               Do not print steps and tests output
  --no-color                         Do not use colorful output.
"""
import os
import sys
from distutils.util import strtobool

from docopt import docopt, DocoptExit

from catcher import APPVSN
from catcher.core.runner import Runner
from catcher.utils import logger
from catcher.utils.logger import warning
from catcher.utils.module_utils import load_external_actions
from colorama import init

init()


def main(args=None):
    try:
        arguments = docopt(__doc__, argv=args, version=APPVSN)
    except DocoptExit as usage:
        print(usage)
        sys.exit(1)
    path = os.getcwd()
    logger.configure(arguments['--log-level'], not arguments['--no-color'])
    result = run_tests(path, arguments)
    if result:
        sys.exit(0)
    else:
        sys.exit(1)


def run_tests(path: str, arguments: dict):
    file_or_dir = arguments['<tests>']
    inventory = arguments['--inventory']
    environment = arguments['--environment']
    modules = arguments['--modules']
    resources = arguments['--resources']
    output_format = arguments['--format']
    filters = arguments['--filter']
    use_sys_vars = arguments['--system_env']
    output = 'full' if not arguments['--q'] else 'limited'
    if arguments['--qq']:
        output = 'final'
    if strtobool(use_sys_vars):
        sys_vars = dict(os.environ)
    else:
        sys_vars = None
    __load_modules(modules)
    runner = Runner(path, file_or_dir, inventory,
                    modules=modules,
                    cmd_env=__env_to_variables(environment),
                    resources=resources,
                    system_environment=sys_vars,
                    output_format=output_format,
                    filter_list=filters)
    return runner.run_tests(output=output)


def __env_to_variables(environment: list) -> dict:
    variables = {}
    for env in environment:
        if '=' not in env:
            warning('Skip not kv env param ' + env)
        else:
            [k, v] = env.split('=')
            variables[k] = v
    return variables


def __load_modules(modules):
    """
    Load catcher core modules, carcher-modules extensions (if available) and try to load all modules from cmd args
    """
    load_external_actions('catcher.steps')
    load_external_actions('catcher_modules')
    [load_external_actions(m) for m in modules]


if __name__ == "__main__":
    main()
