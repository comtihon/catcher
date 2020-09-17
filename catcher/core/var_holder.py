import os
from copy import deepcopy
from typing import Optional

from catcher.utils.logger import debug
from catcher.utils.misc import try_get_object, fill_template_str, report_override, merge_two_dicts


class VariablesHolder:
    """
    Variables override priority:
    1. cmd_env is passed as command line arguments
    2. newly registered variables
    3. test-local variables
    4. inventory variables
    5. environment variables
    """

    def __init__(self,
                 path: str,
                 system_environment=None,
                 inventory_vars: dict = None,
                 cmd_env: Optional[dict] = None,
                 resources: Optional[dict] = None) -> None:
        system_vars = system_environment or {}
        if system_vars:
            debug('Use system variables: ' + str(list(system_vars.keys())))
            self._variables = system_vars
        else:
            self._variables = {}
        inventory = try_get_object(fill_template_str(inventory_vars, self._variables))  # fill env vars
        self._cmd_env = cmd_env or {}
        self._variables.update(inventory)
        self._variables['CURRENT_DIR'] = path
        self._variables['RESOURCES_DIR'] = resources or os.path.join(path, 'resources')

    @property
    def variables(self) -> dict:
        """
        deep copy of inventory & environment variables
        """
        return deepcopy(self._variables)

    def prepare_variables(self, test, global_variables: dict):
        """
        Create variables for test
        :param global_variables:
        :param test: test with test variables
        """
        # system env + inventory
        # (test template is filled in based on system, inventory & cmd vars)
        test.variables = try_get_object(fill_template_str(test.variables,
                                                          merge_two_dicts(global_variables, self._cmd_env)))
        # test local
        global_variables.update(test.variables)
        # include vars override test local
        global_variables.update(self._prepare_include_vars(test, global_variables))
        # cmd_env override everything
        global_variables.update(self._cmd_env)
        test.variables = global_variables

    @staticmethod
    def _prepare_include_vars(test, global_variables):
        if test.include:
            include_vars = try_get_object(fill_template_str(test.include.variables, global_variables))
        else:
            include_vars = {}
        override_keys = report_override(test.variables, include_vars)
        if override_keys:
            debug('Include variables override these variables: ' + str(override_keys))
        return include_vars
