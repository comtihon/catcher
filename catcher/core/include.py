import os

import networkx as nx

from typing import Tuple, Optional, Union, List

from catcher.utils.logger import debug


class Include:
    """
    Include another testcase in include section:

    - file: test file to include
    - variables: variables to override
    - alias: unique name to run this test later
    - run_on_include: should run as soon as included (before test)
    - ignore_errors: should continue running other tests if this fails

    :Examples:

    Simple include - will run before test
    ::

        include: register_user.yaml

    Will run before test with some variables overridden
    ::

        include:
            file: register_user.yaml
            variables:
                user_email: 'override@email.org'

    Multiple includes. Will run one by one. Variables from the first one will be passed to the next
    ::

        include:
            - simple_form.yaml
            - file: long_form.yaml
              variables: {user_email: 'override@email.org'}

    Include with alias and run later
    ::

        include:
            file: register_user.yaml
            as: sign_up
        steps:
            # .... some steps
            - run:
                include: sign_up
            # .... some steps

    See `includes <https://catcher-test-tool.readthedocs.io/en/latest/source/includes.html>`_ for more info.
    """

    def __init__(self, ignore_errors=False, file=None, **kwargs) -> None:
        if 'file' is None:
            raise RuntimeError('Can\'t include unknown file.')
        self.file = file
        self.variables = kwargs.get('variables', {})
        self.alias = kwargs.get('as', None)
        self.run_on_include = kwargs.get('run_on_include', self.alias is None)
        self.ignore_errors = ignore_errors

    @staticmethod
    def check_circular(parent: str,
                       all_includes: nx.DiGraph,
                       current_include: dict) -> 'Include':
        path = current_include['file']
        all_includes.add_edge(parent, path)
        if list(nx.simple_cycles(all_includes)):
            debug(str(all_includes.edges))
            raise Exception('Circular dependencies for ' + path)
        return Include(**current_include)

    @staticmethod
    def read_includes(path: str,
                      parent: str,
                      includes: Union[dict, list, str],
                      all_includes: Optional[nx.DiGraph]) -> Tuple[nx.DiGraph, List['Include']]:
        if all_includes is None:
            all_includes = nx.DiGraph()
        if isinstance(includes, str) or isinstance(includes, dict):  # single include
            raw = [Include.read_include(path, parent, includes, all_includes)]
        elif isinstance(includes, list):  # an array of includes
            raw = [Include.read_include(path, parent, include, all_includes) for include in includes]
        else:
            raw = []
        return all_includes, raw

    @staticmethod
    def read_include(path=None, parent=None, include_file=None, all_includes=None):
        include_file = Include.path_from_root(include_file, path)
        return Include.check_circular(parent, all_includes, include_file)

    @staticmethod
    def path_from_root(include_file: str or dict, path: str) -> dict:
        if isinstance(include_file, str):
            return {'file': os.path.join(path, include_file)}
        else:
            include_file['file'] = os.path.join(path, include_file['file'])
            return include_file
