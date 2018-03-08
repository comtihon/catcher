import json
from time import sleep, time

from kafka import KafkaConsumer, KafkaProducer
from kafka.consumer.fetcher import ConsumerRecord
from kafka.errors import KafkaError

from catcher.steps.step import Step
from catcher.utils.file_utils import read_file
from catcher.utils.time_utils import to_seconds
from utils.logger import warning


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
            out = self.consume()
        elif self.method == 'produce':
            out = self.produce()
        else:
            raise AttributeError('unknown method: ' + self.method)
        return self.process_register(variables, out)

    def consume(self) -> list:
        consumer = self.__connect_consumer()
        messages = Kafka.get_messages(consumer)
        if self.where is not None:
            # TODO filter messages. If none found - use timeout to wait for.
            return messages
        else:
            return messages

    def produce(self) -> dict:
        producer = self.__connect_producer()
        future = producer.send(self.topic, self.data)
        try:
            return future.get(timeout=self.timeout)
        except KafkaError as e:
            warning('Can\'t produce message to topic ' + self.topic + ' with ' + str(e))
            raise KafkaError('Producing message failed for ' + self.topic)

    def __connect_consumer(self):
        start = time()
        try:
            return KafkaConsumer(self.topic,
                                 group_id=self.group_id,
                                 bootstrap_servers=self.server,
                                 auto_offset_reset='earliest',
                                 api_version=(0, 10, 1))
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
                                     api_version=(0, 10, 1),
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
    def get_messages(consumer: KafkaConsumer) -> [dict]:
        consumer_records = consumer.poll(10000).values()
        records = [item for sublist in consumer_records for item in sublist]
        return [Kafka.parse_value(c) for c in records]

    @staticmethod
    def parse_value(c: ConsumerRecord) -> dict:
        return json.loads(c.value.decode())
