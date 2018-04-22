from time import sleep

from pykafka import KafkaClient, SimpleConsumer
from pykafka.common import OffsetType

from catcher.steps.check import Operator
from catcher.steps.step import Step
from catcher.utils.file_utils import read_file
from catcher.utils.misc import try_get_object, fill_template_str
from catcher.utils.time_utils import to_seconds
from catcher.utils.logger import debug


class Kafka(Step):
    def __init__(self, body: dict) -> None:
        super().__init__(body)
        method = Step.filter_predefined_keys(body)  # produce/consume
        self._method = method.lower()
        conf = body[method]
        self._group_id = conf.get('group_id', 'catcher')
        self._server = conf['server']
        self._topic = conf['topic']
        timeout = conf.get('timeout', {'seconds': 1})
        self._timeout = to_seconds(timeout)
        self._where = conf.get('where', None)
        self._data = None
        if self.method != 'consume':
            self._data = conf.get('data', None)
            if self.data is None:
                self._file = conf['data_from_file']

    @property
    def group_id(self):
        return self._group_id

    @property
    def server(self):
        return self._server

    @property
    def method(self):
        return self._method

    @property
    def topic(self):
        return self._topic

    @property
    def file(self) -> str:
        return self._file

    @property
    def data(self) -> bytes or dict or str:
        return self._data

    @property
    def where(self) -> dict or None:
        return self._where

    @property
    def timeout(self) -> int:
        return self._timeout

    def action(self, includes: dict, variables: dict) -> dict:
        client = KafkaClient(hosts=fill_template_str(self.server, variables))
        topic = client.topics[fill_template_str(self.topic, variables).encode('utf-8')]
        out = {}
        if self.method == 'consume':
            out = self.consume(topic, variables)
            if out is None:
                raise RuntimeError('No kafka messages were consumed')
        elif self.method == 'produce':
            self.produce(topic, variables)
        else:
            raise AttributeError('unknown method: ' + self.method)
        return self.process_register(variables, out)

    def consume(self, topic, variables: dict) -> dict:
        consumer = topic.get_simple_consumer(consumer_group=self.group_id.encode('utf-8'),
                                             auto_offset_reset=OffsetType.EARLIEST,
                                             reset_offset_on_start=False,
                                             consumer_timeout_ms=self.timeout * 1000)
        if self.where is not None:
            operator = Operator.find_operator(self.where)
        else:
            operator = None
        return Kafka.get_messages(consumer, operator, variables, self.timeout)

    def produce(self, topic, variables):
        message = self.__form_body(variables)
        with topic.get_sync_producer() as producer:
            producer.produce(message.encode('utf-8'))

    def __form_body(self, variables):
        data = self.data
        if data is None:
            data = read_file(fill_template_str(self.file, variables))
        return fill_template_str(data, variables)

    @staticmethod
    def get_messages(consumer: SimpleConsumer, where: Operator or None, variables, timeout) -> dict or None:
        try:
            while True:
                consumer.fetch()
                for message in consumer:
                    value = try_get_object(message.value.decode('utf-8'))
                    debug(value)
                    if Kafka.check_message(where, value, variables):
                        return value
                if timeout > 0:
                    sleep(1)
                    timeout -= 1
                else:
                    return None
        finally:
            consumer.commit_offsets()

    @staticmethod
    def check_message(where: Operator, message: str, variables: dict) -> bool:
        if where is None:
            return True
        variables = dict(variables)
        variables['MESSAGE'] = message
        return where.operation(variables)
