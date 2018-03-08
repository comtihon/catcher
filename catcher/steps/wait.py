from time import sleep

from catcher.steps.step import Step
from catcher.utils.time_utils import to_seconds


class Wait(Step):
    def __init__(self, body: dict) -> None:
        super().__init__(body)
        self._delay = to_seconds(body)

    @property
    def delay(self) -> int:
        return self._delay

    def action(self, includes: dict, variables: dict) -> dict:
        sleep(self.delay)
        return self.process_register(variables)
