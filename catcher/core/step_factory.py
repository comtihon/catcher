from catcher.steps.external import External
from catcher.steps.step import Step


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


def get_action(path: str, action, body: dict or str, modules: dict) -> Step:
    module = modules.get(action, None)
    if module is not None:
        if isinstance(module, str):  # external module (some third party script)
            return External(body, module)
        else:   # python module
            return module.construct_step(body,
                                         path,
                                         get_actions=lambda act: get_actions(path, act, modules),
                                         get_action=lambda x: get_action(path, x[0], x[1], modules))
    raise FileNotFoundError('Can\'t find module for action: ' + action)
