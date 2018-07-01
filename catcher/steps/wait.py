from time import sleep

from catcher.steps.step import Step
from catcher.utils.time_utils import to_seconds


class Wait(Step):
    """
    Wait for some time before the next step

    :Input:

    :days: several days
    :hours: several hours
    :minutes: several minutes
    :seconds: several seconds
    :microseconds: several microseconds
    :milliseconds: several milliseconds
    :nanoseconds: several nanoseconds

    :Examples:

    Wait for 1 minute 30 seconds
    ::
        wait: {minutes: 1, seconds: 30}
    """

    def __init__(self, body: dict) -> None:
        super().__init__(body)
        self._delay = to_seconds(body)

    @property
    def delay(self) -> int:
        return self._delay

    def action(self, includes: dict, variables: dict) -> dict:
        sleep(self.delay)
        return self.process_register(variables)
