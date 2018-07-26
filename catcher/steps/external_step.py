from abc import abstractmethod

from catcher.steps.step import MetaStep


class ExternalStep(object, metaclass=MetaStep):
    """
    Implement this step in case you are adding external python module to
    catcher-modules project
    """

    @abstractmethod
    def action(self, in_data: dict) -> any:
        """
        Perform an action.

        :param in_data: Script input.
        :return: step output

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
