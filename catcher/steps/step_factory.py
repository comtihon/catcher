from catcher.steps.check import Check
from catcher.steps.echo import Echo
from catcher.steps.external import External
from catcher.steps.http import Http
from catcher.steps.kafka import Kafka
from catcher.steps.postgres import Postgres
from catcher.steps.run import Run
from catcher.steps.step import Step
from catcher.steps.wait import Wait
from catcher.steps.stop import Stop


def get_actions(path: str, step: dict, modules: dict) -> [Step]:
    [action] = step.keys()
    body = step[action]
    steps = []
    if 'actions' in body:
        for action_step in body['actions']:
            steps.append(get_action(path, action, action_step, modules))
    else:
        steps.append(get_action(path, action, body, modules))
    return steps


#  TODO refactor me
def get_action(path: str, action, body: dict or str, modules: dict) -> Step:
    if action == 'echo':
        return Echo(path, body)
    if action == 'wait':
        return Wait(body)
    if action == 'run':
        if isinstance(body, str):
            return Run(**{'include': body})
        else:
            return Run(**body)
    if action == 'check':
        return Check(body)
    if action == 'http':
        return Http(body)
    if action == 'kafka':
        return Kafka(body)
    if action == 'postgres':
        return Postgres(body)
    if action == 'stop':
        return Stop(body)
    if action in modules:
        return External(body, modules[action])
    raise FileNotFoundError('Can\'t find module for action: ' + action)
