import json
import subprocess

from catcher.steps.step import Step
from catcher.utils.logger import debug, warning
from catcher.utils.misc import fill_template_str, try_get_objects


class External(Step):
    def __init__(self, body: dict, module) -> None:
        super().__init__(body)
        method = Step.filter_predefined_keys(body)
        self._data = {method: body[method]}
        self._module = module

    @property
    def module(self):
        return self._module

    @property
    def data(self) -> any:
        return self._data

    def action(self, includes: dict, variables: dict) -> dict:
        if isinstance(self.module, str):
            return self.__call_external_script(variables)
        else:
            return self.__call_python_module(variables)

    def __call_external_script(self, variables) -> dict:
        """
        Call external script.

        :param variables: variables
        :return: script's output
        """
        json_args = fill_template_str(json.dumps(self.data), variables)
        p = subprocess.Popen([self.module, json_args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if p.wait() == 0:
            out = p.stdout.read().decode()
            debug(out)
            return self.process_register(variables, json.loads(out))
        else:
            out = p.stdout.read().decode()
            warning(out)
            raise Exception('Execution failed.')

    def __call_python_module(self, variables) -> dict:
        """
        Call external python module. Most likely from catcher-modules

        :param variables:
        :return:
        """
        json_args = fill_template_str(json.dumps(self.data), variables)
        return self.process_register(variables, self.module().action(try_get_objects(json_args)))
