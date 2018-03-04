from catcher.steps.echo import Echo
from catcher.steps.step import Step


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


def get_action(path: str, action, body: dict) -> Step:
    if action == 'echo':
        return Echo(path, body)
    return None
