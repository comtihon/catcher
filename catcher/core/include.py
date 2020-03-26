import networkx as nx

from typing import Tuple, Optional

from catcher.utils.logger import debug


class Include:
    """
    Include another testcase in include section:

    ::
        include:
            - file: simple_file.yaml
              run_on_include: false
            - other_simple_file.yaml

    each include file has it's own Include object and attached Test
    """

    def __init__(self, ignore_errors=False, **keywords) -> None:
        if 'file' not in keywords:
            raise RuntimeError('Can\'t include unknown file.')
        self.file = keywords['file']
        self.variables = keywords.get('variables', {})
        self.alias = keywords.get('as', None)
        self.run_on_include = keywords.get('run_on_include', self.alias is None)
        self.ignore_errors = ignore_errors

    @staticmethod
    def check_circular(parent: str,
                       all_includes: Optional[nx.DiGraph],
                       current_include: dict) -> Tuple[nx.DiGraph, 'Include']:
        if all_includes is None:
            all_includes = nx.DiGraph()
        path = current_include['file']
        all_includes.add_edge(parent, path)
        if list(nx.simple_cycles(all_includes)):
            debug(str(all_includes.edges))
            raise Exception('Circular dependencies for ' + path)
        include = Include(**current_include)
        return all_includes, include
