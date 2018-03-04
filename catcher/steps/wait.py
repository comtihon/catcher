from time import sleep

from catcher.steps.step import Step

TIME_MAPPING = [
    ('days', 86400),
    ('hours', 3600),
    ('minutes', 60),
    ('seconds', 1),
    ('microseconds', 0.001),
    ('milliseconds', 0.000001),
    ('nanoseconds', 0.000000001)
]


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


def to_seconds(body: dict) -> int:
    return sum([compute_time(t, body, m) for (t, m) in TIME_MAPPING])


def compute_time(key: str, body: dict, to_second: float) -> int:
    return body.get(key, 0) * to_second
