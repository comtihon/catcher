import json
import subprocess

from catcher.steps.step import Step, update_variables
from catcher.utils.logger import debug, warning
from catcher.utils.misc import fill_template_str


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
        p = subprocess.Popen([self.module, json_args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if p.wait() == 0:
            out = p.stdout.read().decode()
            debug(out)
            return variables, json.loads(out)
        else:
            out = p.stdout.read().decode()
            warning(out)
            raise Exception('Execution failed.')
