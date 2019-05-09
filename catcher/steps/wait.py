import itertools
import time
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from time import sleep
from catcher.steps.step import Step, update_variables
from catcher.utils.time_utils import to_seconds
from catcher.utils.logger import debug


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
    :for: (list of actions) will repeat them till they all finishes successfully or time ends.

    :Examples:

    Wait for 1 minute 30 seconds
    ::

        wait: {minutes: 1, seconds: 30}

    Wait for http to be ready. Will run the http for 5 seconds or till it finishes successfully
    ::

        wait:
            seconds: 5
            for:
                http:
                    put:
                        url: 'http://localhost:8000/mockserver/expectation'
                        body:
                            httpRequest: {'path': '/some/path'}
                            httpResponse: {'body': 'hello world'}
                        response_code: 201

    Wait for postgres to be populated
    ::

        wait:
            seconds: 30
            for:
                - postgres:
                      request:
                          conf: '{{ pg_conf }}'
                          query: 'select count(*) from users'
                      register: {documents: '{{ OUTPUT }}'}
                - check: {equals: {the: '{{ documents }}', is_not: 0}}
    """

    def __init__(self, _get_action=None, _get_actions=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.delay = to_seconds(kwargs)
        self._actions = None
        if 'for' in kwargs:
            wait_for = kwargs['for']
            if len(wait_for) == 1:
                if isinstance(wait_for, list):
                    wait_for = wait_for[0]
                [loop_action] = wait_for.keys()
                self._actions = [_get_action((loop_action, wait_for[loop_action]))]
            elif len(wait_for) > 1:
                self._actions = list(itertools.chain.from_iterable([_get_actions(act) for act in wait_for]))

    @update_variables
    def action(self, includes: dict, variables: dict) -> dict:
        if self._actions is not None:
            # run thread and either exit on success or wait fixed time
            pool = ThreadPoolExecutor(max_workers=1)
            future = pool.submit(self.run_loop, includes, variables)
            try:
                return future.result()
            except TimeoutError:
                return variables
        else:  # wait fixed time
            sleep(self.delay)
            return variables

    def run_loop(self, includes, variables):
        output = variables
        repeat = True
        start = time.time()
        while repeat:
            if time.time() > start + self.delay:  # time limit reached
                raise TimeoutError
            loop_vars = deepcopy(output)  # start every loop from the same variables
            try:
                for action in self._actions:
                    loop_vars = action.action(includes, loop_vars)
                repeat = False
                output = loop_vars  # if loop was successful - return modified variables
            except Exception as e:
                debug('wait step failure {}'.format(e))
        return output
