from abc import abstractmethod

from catcher.utils.misc import try_get_object, merge_two_dicts, fill_template


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

    def process_register(self, variables, output: dict or str or None = None) -> dict:
        if self.register is not None:
            for key in self.register.keys():
                if output is not None:
                    out = fill_template(self.register[key],
                                        merge_two_dicts(variables, {'OUTPUT': try_get_object(output)}))
                else:
                    out = fill_template(self.register[key], variables)
                variables[key] = out
        return variables
