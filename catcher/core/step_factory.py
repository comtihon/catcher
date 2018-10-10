from typing import Union, Dict, Callable

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


def get_action(path: str, action, body: dict or str, modules: Dict[str, Callable]) -> Step:
    module = modules.get(action, None)
    if module is not None:
        if isinstance(module, str):  # external module (some third party script)
            body = ensure_body_dict(body, path, modules)
            body['_module'] = module
            return External(**body)
        else:  # python module
            body = ensure_body_dict(body, path, modules)
            return module(**body)
    raise FileNotFoundError('Can\'t find module for action: ' + action)


def ensure_body_dict(body: Union[str, dict], path, modules) -> dict:
    def get_actions_fun(act):
        return get_actions(path, act, modules)

    def get_action_fun(x):
        return get_action(path, x[0], x[1], modules)

    if isinstance(body, str):
        body = {'_body': body}
    body['_get_actions'] = get_actions_fun
    body['_get_action'] = get_action_fun
    body['_path'] = path
    return body
