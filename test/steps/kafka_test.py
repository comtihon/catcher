import json
from os.path import join

from pykafka import KafkaClient
from pykafka.common import OffsetType

from catcher.core.runner import Runner
from test.abs_test_class import TestClass


class KafkaTest(TestClass):
    def __init__(self, method_name):
        super().__init__('kafka', method_name)

    @property
    def server(self):
        return '127.0.0.1:9092'

    def test_consume_message(self):
        self.produce_message({'id': 'uuid', 'action': {'withdraw': 100}}, 'test_consume_message')
        self.populate_file('main.yaml', '''---
            steps:
                - kafka: 
                    consume: 
                        server: '127.0.0.1:9092'
                        topic: 'test_consume_message'
                    register: {money: '{{ OUTPUT.action.withdraw }}'}
                - check:
                    equals: {the: '{{ money }}', is: 100}
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_consume_with_filter(self):
        self.produce_message({'id': 'uuid1', 'name': 'foo'}, 'test_consume_with_filter')
        self.produce_message({'id': 'uuid2', 'name': 'baz'}, 'test_consume_with_filter')
        self.produce_message({'id': 'uuid3', 'name': 'bar'}, 'test_consume_with_filter')
        self.produce_message({'id': 'uuid4', 'name': 'baf'}, 'test_consume_with_filter')
        self.populate_file('main.yaml', '''---
            steps:
                - kafka: 
                    consume: 
                        server: '127.0.0.1:9092'
                        topic: 'test_consume_with_filter'
                        where: 
                            equals: {the: '{{ MESSAGE.id }}', is: 'uuid3'}
                    register: {user: '{{ OUTPUT }}'}
                - check:
                    equals: {the: '{{ user.name }}', is: 'bar'}
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_consume_with_timestamp(self):
        self.produce_message({'id': 'uuid1', 'timestamp': 1234}, 'test_consume_with_timestamp')
        self.produce_message({'id': 'uuid2', 'timestamp': 1235}, 'test_consume_with_timestamp')
        self.populate_file('main.yaml', '''---
            steps:
                - kafka: 
                    consume: 
                        server: '127.0.0.1:9092'
                        topic: 'test_consume_with_timestamp'
                        where: 
                            equals: '{{ MESSAGE.timestamp > 1000 }}'
                    register: {uuid: '{{ OUTPUT.id }}'}
                - check:
                    equals: {the: '{{ uuid }}', is: 'uuid1'}
                - kafka: 
                    consume: 
                        server: '127.0.0.1:9092'
                        topic: 'test_consume_with_timestamp'
                        where: 
                            equals: '{{ MESSAGE.timestamp > 1000 }}'
                    register: {uuid: '{{ OUTPUT.id }}'}
                - check:
                    equals: {the: '{{ uuid }}', is: 'uuid2'}
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_produce_message(self):
        self.populate_file('main.yaml', '''---
            steps:
                - kafka: 
                    produce: 
                        server: '127.0.0.1:9092'
                        topic: 'test_produce_message'
                        data: {'user': 'John Doe'}
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertEqual('{\'user\': \'John Doe\'}', self.consume_message('test_produce_message'))

    def test_produce_json(self):
        self.populate_file('main.yaml', '''---
            variables:
                data: {'key1': 'value1', 'key2': [1,2,3,4]}
            steps:
                - kafka: 
                    produce: 
                        server: '127.0.0.1:9092'
                        topic: 'test_produce_json'
                        data: '{{ data|tojson }}'
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        msg = self.consume_message('test_produce_json')
        self.assertEqual({'key1': 'value1', 'key2': [1, 2, 3, 4]}, json.loads(msg))

    def test_skip_same_message(self):
        self.produce_message({'id': 'uuid1'}, 'test_skip_same_message')
        self.produce_message({'id': 'uuid2'}, 'test_skip_same_message')
        self.populate_file('main.yaml', '''---
            steps:
                - kafka: 
                    consume: 
                        server: '127.0.0.1:9092'
                        topic: 'test_skip_same_message'
                    register: {uuid: '{{ OUTPUT.id }}'}
                - check:
                    equals: {the: '{{ uuid }}', is: 'uuid1'}
                - kafka: 
                    consume: 
                        server: '127.0.0.1:9092'
                        topic: 'test_skip_same_message'
                    register: {uuid: '{{ OUTPUT.id }}'}
                - check:
                    equals: {the: '{{ uuid }}', is: 'uuid2'}
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def produce_message(self, message: bytes or dict, topic='test'):
        client = KafkaClient(hosts=self.server)
        topic = client.topics[topic.encode('utf-8')]
        if not isinstance(message, bytes):
            message = str(message).encode('utf-8')
        with topic.get_sync_producer() as producer:
            producer.produce(message)

    def consume_message(self, topic):
        client = KafkaClient(hosts=self.server)
        topic = client.topics[topic.encode('utf-8')]
        consumer = topic.get_simple_consumer(consumer_group=b'test',
                                             auto_offset_reset=OffsetType.EARLIEST,
                                             reset_offset_on_start=False,
                                             consumer_timeout_ms=5000)
        message = consumer.consume(True)
        consumer.commit_offsets()
        return message.value.decode('utf-8')
