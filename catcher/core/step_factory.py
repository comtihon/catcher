from typing import Union, Dict, Callable

from catcher.steps.external import External
from catcher.steps.step import Step
from utils.singleton import Singleton


class StepFactory(metaclass=Singleton):

    def __init__(self, modules: Dict[str, Callable] = None) -> None:
        self.modules = modules

    def get_actions(self, path: str, step: dict) -> [Step]:
        [action] = step.keys()
        body = step[action]
        steps = []
        if 'actions' in body:
            for action_step in body['actions']:
                steps.append(self.get_action(path, action, action_step))
        else:
            steps.append(self.get_action(path, action, body))
        return steps

    def get_action(self, path: str, action, body: dict or str) -> Step:
        module = self.modules.get(action, None)
        if module is not None:
            if isinstance(module, str):  # external module (some third party script)
                body = self.ensure_body_dict(body, path)
                body['_module'] = module
                return External(**body)
            else:  # python module
                body = self.ensure_body_dict(body, path)
                return module(**body)
        raise FileNotFoundError('Can\'t find module for action: ' + action)

    def ensure_body_dict(self, body: Union[str, dict], path) -> dict:
        def get_actions_fun(act):
            return self.get_actions(path, act)

        def get_action_fun(x):
            return self.get_action(path, x[0], x[1])

        if isinstance(body, str):
            body = {'_body': body}
        body['_get_actions'] = get_actions_fun
        body['_get_action'] = get_action_fun
        body['_path'] = path
        return body
