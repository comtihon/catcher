import psycopg2
from psycopg2._psycopg import ProgrammingError

from catcher.steps.step import Step
from catcher.utils.misc import fill_template, fill_template_str


class Postgres(Step):
    def __init__(self, body: dict) -> None:
        super().__init__(body)
        method = Step.filter_predefined_keys(body)  # request
        conf = body[method.lower()]
        self._conf = conf.get('conf', {})
        self._query = conf['query']

    @property
    def conf(self) -> str or dict:
        return self._conf

    @property
    def query(self) -> str:
        return self._query

    def action(self, includes: dict, variables: dict) -> dict:
        if isinstance(self.conf, str):
            conf = fill_template(self.conf, variables)
        else:
            conf = self.conf
        if isinstance(conf, str):
            conn = psycopg2.connect(conf)
        else:
            conn = psycopg2.connect(**conf)
        cur = conn.cursor()
        request = fill_template_str(self.query, variables)
        cur.execute(request)
        response = Postgres.gather_response(cur)
        conn.commit()
        cur.close()
        conn.close()
        return self.process_register(variables, response)

    @staticmethod
    def gather_response(cursor):
        try:
            response = cursor.fetchall()
            if len(response) == 1:  # for only one value select * from .. where id = 1 -> [('a', 1, 2)]
                response = response[0]
                if len(response) == 1:  # for only one value select count(*) from ... -> (2,)
                    response = response[0]
            return response
        except ProgrammingError:
            return None

