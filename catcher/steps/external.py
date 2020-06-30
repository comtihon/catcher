import json

from catcher.steps.step import Step, update_variables
from catcher.utils.misc import fill_template_str
from catcher.utils import external_utils


class External(Step):
    def __init__(self, _module: str = None, **kwargs) -> None:
        super().__init__(**kwargs)
        method = Step.filter_predefined_keys(kwargs)
        self.data = {method: kwargs[method]}
        self.module = _module

    @update_variables
    def action(self, includes: dict, variables: dict) -> tuple:
        """
        Call external script.

        :param includes: testcase's includes
        :param variables: variables
        :return: script's output
        """
        json_args = fill_template_str(json.dumps(self.data), variables)
        return variables, external_utils.run_cmd_simple(self.module, variables, args=[json_args])
