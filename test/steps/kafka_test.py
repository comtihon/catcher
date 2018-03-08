import json
from os.path import join

from kafka import KafkaProducer

from catcher.core.runner import Runner
from test.abs_test_class import TestClass


class KafkaTest(TestClass):
    def __init__(self, method_name):
        super().__init__('kafka', method_name)

    @property
    def server(self):
        return '127.0.0.1:9092'

    def test_consume_message(self):
        self.produce_message({'id': 'uuid', 'action': {'withdraw': 100}})
        self.populate_file('test_inventory.yml', '''
        kafka_host: localhost
        ''')

        self.populate_file('main.yaml', '''---
            steps:
                - kafka: 
                    consume: 
                        server: '127.0.0.1:9092'
                        topic: 'test'
                    register: {money: '{{ OUTPUT.action.withdraw }}'}
                - check:
                    the: '{{ money }}'
                    equals: 1000
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_consume_all_messages(self):
        True

    def test_consume_with_filter(self):
        True

    def test_produce_message(self):
        True

    def test_skip_same_message(self):
        True

    def produce_message(self, message: bytes or dict, topic='test'):
        if isinstance(message, bytes):
            producer = KafkaProducer(bootstrap_servers=self.server, api_version=(0, 10, 1))
        else:
            producer = KafkaProducer(bootstrap_servers=self.server,
                                     api_version=(0, 10, 1),
                                     value_serializer=lambda m: json.dumps(m).encode('ascii'))
        future = producer.send(topic, message)
        return future.get(timeout=10)
