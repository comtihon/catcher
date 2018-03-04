from catcher.steps import step_factory


class Test:
    def __init__(self, path: str, includes: dict, variables: dict, config: dict, steps: list) -> None:
        self._includes = includes
        self._variables = variables
        self._config = config
        self._steps = steps
        self._path = path

    @property
    def includes(self) -> dict:
        return self._includes

    @property
    def variables(self) -> dict:
        return self._variables

    @variables.setter
    def variables(self, variables):
        self._variables = variables

    @property
    def config(self) -> dict:
        return self._config

    @property
    def steps(self) -> list:
        return self._steps

    @property
    def path(self) -> str:
        return self._path

    # TODO return registered variables
    def run(self) -> {bool, dict}:
        for step in self.steps:
            actions = step_factory.get_actions(self.path, step)
            for action in actions:
                self.variables = action.action(self.variables)
        return True, self.variables  # TODO update variables from steps
