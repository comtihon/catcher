from time import sleep

from kafka import KafkaConsumer

from catcher.steps.step import Step


class Kafka(Step):
    def __init__(self, body: dict) -> None:
        super().__init__(body)
        [method] = [k for k in body.keys() if k != 'register']  # produce/consume
        self._method = method.lower()
        conf = body[method]
        self._group_id = conf.get('group_id', 'catcher')
        self._host = conf.get('host')
        self._port = conf.get('port', 9092)
        self._headers = conf.get('headers', {})
        self._body = None
        self._code = conf.get('response_code', 200)
        if self.method != 'get':
            self._body = conf.get('body', None)
            if self.body is None:
                json = conf['body_from_file']
                self._body = read_file(json)

    @property
    def method(self):
        return self._method

    def action(self, includes: dict, variables: dict) -> dict:
        pass

    # TODO need to save offset to var to avoid consuming message twice (or save consumer to static?)
    def connect_consumer(self, host, port, topic, retry=True):
        try:
            return KafkaConsumer(topic,
                                 group_id='tester',
                                 bootstrap_servers=host + ':' + port,
                                 auto_offset_reset='earliest',
                                 api_version=(0, 10, 1))
        except:
            if retry:
                sleep(5)
                return self.connect_consumer(host, port, topic, False)
            raise Exception('No kafka brokers available')
