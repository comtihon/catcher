import json
from time import sleep, time

from kafka import KafkaConsumer, KafkaProducer, TopicPartition, OffsetAndMetadata
from kafka.consumer.fetcher import ConsumerRecord
from kafka.errors import KafkaError

from catcher.steps.check import Operator
from catcher.steps.step import Step
from catcher.utils.file_utils import read_file
from catcher.utils.logger import warning
from catcher.utils.time_utils import to_seconds


class Kafka(Step):
    def __init__(self, body: dict) -> None:
        super().__init__(body)
        [method] = [k for k in body.keys() if k != 'register']  # produce/consume
        self._method = method.lower()
        conf = body[method]
        self._group_id = conf.get('group_id', 'catcher')
        self._server = conf['server']
        self._topic = conf['topic']
        timeout = conf.get('timeout', {})
        self._timeout = to_seconds(timeout)
        self._where = conf.get('where', None)
        self._data = None
        if self.method != 'consume':
            self._data = conf.get('data', None)
            if self.data is None:
                file = conf['data_from_file']
                self._data = read_file(file)

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
    def data(self) -> bytes or dict:
        if isinstance(self._data, bytes) or isinstance(self._data, dict):
            return self._data
        return str(self._data).encode('utf-8')

    @property
    def where(self) -> dict or None:
        return self._where

    @property
    def timeout(self) -> int:
        return self._timeout

    @timeout.setter
    def timeout(self, new_timeout):
        self._timeout = new_timeout

    def action(self, includes: dict, variables: dict) -> dict:
        # TODO templating in topics and in consume body!
        if self.method == 'consume':
            out = self.consume(variables)
        elif self.method == 'produce':
            out = self.produce()
        else:
            raise AttributeError('unknown method: ' + self.method)
        return self.process_register(variables, out)

    def consume(self, variables: dict) -> list:
        start = time()
        consumer = self.__connect_consumer()
        if self.where is not None:
            operator = Operator.find_operator(self.where)
        else:
            operator = None
        messages = Kafka.get_messages(consumer, operator, variables)
        spent = time() - start
        if not messages:
            if self.timeout > 0 and spent < self.timeout:
                sleep(1)
                self.timeout -= (spent + 1)
                return self.consume(variables)
            raise RuntimeError('No messages available')
        [message] = messages
        return message

    def produce(self) -> dict:
        producer = self.__connect_producer()
        future = producer.send(self.topic, self.data)
        try:
            return future.get(timeout=self.timeout)
        except KafkaError as e:
            warning('Can\'t produce message to topic ' + self.topic + ' with ' + str(e))
            raise KafkaError('Producing message failed for ' + self.topic)

    def __filter_message(self, message: dict, variables: dict) -> dict or None:
        operator = Operator.find_operator(self.where)
        variables = dict(variables)
        variables['MESSAGE'] = message
        if operator.operation(variables) is False:
            return None
        return operator

    def __connect_consumer(self):
        start = time()
        try:
            return KafkaConsumer(self.topic,
                                 group_id=self.group_id,
                                 bootstrap_servers=self.server,
                                 auto_offset_reset='earliest',
                                 enable_auto_commit=False)
        except:
            spent = time() - start
            if self.timeout > 0 and spent < self.timeout:
                sleep(1)
                self.timeout -= (spent + 1)
                return self.__connect_consumer()
            raise Exception('No kafka brokers available')

    def __connect_producer(self):
        start = time()
        try:
            if isinstance(self.data, dict):
                return KafkaProducer(bootstrap_servers=self.server,
                                     value_serializer=lambda m: json.dumps(m).encode('ascii'))
            else:
                return KafkaProducer(bootstrap_servers=self.server, api_version=(0, 10, 1))
        except:
            spent = time() - start
            if self.timeout > 0 and spent < self.timeout:
                sleep(1)
                self.timeout -= (spent + 1)
                return self.__connect_consumer()
            raise Exception('No kafka brokers available')

    @staticmethod
    def get_messages(consumer: KafkaConsumer, where: Operator or None, variables) -> [dict]:
        for message in consumer:
            print('REPEAT')
            variables = dict(variables)
            value = message.value.decode('utf-8')
            variables['MESSAGE'] = value
            print(value)
            tp = TopicPartition(message.topic, message.partition)
            consumer.commit({tp: OffsetAndMetadata(message.offset, None)})
            if where.operation(variables) is True:
                print('bingo! ' + value)
                return value
        return []

    @staticmethod
    def parse_value(c: ConsumerRecord) -> dict:
        return json.loads(c.value.decode())
