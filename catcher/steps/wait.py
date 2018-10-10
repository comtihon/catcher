from time import sleep

from catcher.steps.step import Step, update_variables
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

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.delay = to_seconds(kwargs)

    @update_variables
    def action(self, includes: dict, variables: dict) -> dict:
        sleep(self.delay)
        return variables
