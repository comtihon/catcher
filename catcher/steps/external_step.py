import json
from abc import abstractmethod

from catcher.steps.step import Step
from catcher.utils.misc import fill_template_str, try_get_objects


class ExternalStep(Step):
    """
    Implement this step in case you are adding external python module to
    catcher-modules project
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        method = Step.filter_predefined_keys(kwargs)
        self.data = {method: kwargs[method]}

    def simple_input(self, variables):
        """
        Use this method to get simple input as python object, with all
        templates filled in

        :param variables:
        :return: python object

        """
        json_args = fill_template_str(json.dumps(self.data), variables)
        return try_get_objects(json_args)

    @abstractmethod
    def action(self, includes: dict, variables: dict) -> dict or tuple:
        """
        Perform an action.

        :param includes: Script includes.
        :param variables: Script variables.
        :return: variables and step's output. Output is optional.

        For code above
        ::

            postgres:
                request:
                    conf:
                        dbname: test
                        user: test
                        password: test
                        host: localhost
                        port: 5433
                    query: 'select count(*) from test'
            register: {documents: '{{ OUTPUT }}'}

        in_data will be
        ::

            {'request' : {'conf': {'dbname': 'test', 'user': 'test', 'password': 'test', 'host': 'localhost', 'port': 5433},
                          'query': 'select count(*) from test'}
            }

        """
        pass
