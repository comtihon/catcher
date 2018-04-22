from abc import abstractmethod

from catcher.utils.misc import try_get_object, merge_two_dicts, fill_template


class Step:
    def __init__(self, body: dict or str) -> None:
        if isinstance(body, str):
            self._register = None
            self._name = None
        else:
            self._register = body.get('register', None)
            self._name = body.get('name', None)

    @abstractmethod
    def action(self, includes: dict, variables: dict) -> dict:
        pass

    @property
    def register(self) -> dict or None:
        return self._register

    @property
    def name(self) -> str or None:
        return self._name

    @staticmethod
    def filter_predefined_keys(data: dict):
        [action] = [k for k in data.keys() if k != 'register' and k != 'ignore_errors' and k != 'name' and k != 'tag']
        return action

    def process_register(self, variables, output: dict or list or str or None = None) -> dict:
        if self.register is not None:
            for key in self.register.keys():
                if output is not None:
                    out = fill_template(self.register[key],
                                        merge_two_dicts(variables, {'OUTPUT': try_get_object(output)}))
                else:
                    out = fill_template(self.register[key], variables)
                variables[key] = out
        return variables
