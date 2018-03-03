from catcher.steps.step import Step
from catcher.steps.echo import Echo


def get_step(path: str, step: dict) -> Step:
    [action] = step.keys()
    if action == 'echo':
        return Echo(path, step[action])
    return None
