from catcher.steps.echo import Echo
from catcher.steps.run import Run
from catcher.steps.step import Step
from catcher.steps.wait import Wait
from catcher.steps.check import Check
from catcher.steps.http import Http


def get_actions(path: str, step: dict) -> [Step]:
    [action] = step.keys()
    body = step[action]
    steps = []
    if 'actions' in body:
        for action_step in body['actions']:
            steps.append(get_action(path, action, action_step))
    else:
        steps.append(get_action(path, action, body))
    return steps


#  TODO refactor me
def get_action(path: str, action, body: dict or str) -> Step:
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
    return None
