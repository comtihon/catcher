from abc import abstractmethod

from jinja2 import Template


class Step:
    def __init__(self, body: dict) -> None:
        self._register = None
        if 'register' in body:
            self._register = body['register']

    @abstractmethod
    def action(self, includes: dict, variables: dict) -> dict:
        pass

    @property
    def register(self) -> dict or None:
        return self._register

    def process_register(self, variables, output: dict or None = None) -> dict:
        if self.register is not None:
            for key in self.register.keys():
                if output:
                    out = Template(self.register[key]).render({'OUTPUT': output})
                else:
                    out = Template(self.register[key]).render(variables)
                variables[key] = out
        return variables
