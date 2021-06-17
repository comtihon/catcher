import datetime

from catcher.utils.misc import try_get_object, fill_template

from test.abs_test_class import TestClass


class MiscTest(TestClass):
    def __init__(self, method_name):
        super().__init__('misc_test', method_name)

    # read and parse yaml file
    def test_try_get_object(self):
        not_an_object = 'not an not_an_object'
        self.assertEqual(not_an_object, try_get_object(not_an_object))

        python_term = '{\'key\': \'string\', \'int_key\': 1, \'sub_term\': {\'k\':[1,2,3]}, \'non_existent\':None}'
        python_object = {'key': 'string', 'int_key': 1, 'sub_term': {'k': [1, 2, 3]}, 'non_existent': None}
        self.assertEqual(python_object, try_get_object(python_term))

        json_object = '{"key": "string", "int_key": 1, "sub_term": {"k":[1,2,3]}, "non_existent":null}'
        self.assertEqual(python_object, try_get_object(json_object))

    # date is parsed without problems
    def test_try_get_date(self):
        data = datetime.datetime(2020, 3, 20, 17, 56, 34, 74807)
        self.assertEqual(data, try_get_object(data.__repr__()))

        obj_str = "{'key':'value','date':" + data.__repr__() + '}'
        self.assertEqual({'key': 'value', 'date': data}, try_get_object(obj_str))

    # primitives are parsed and returned
    def test_try_get_primitives(self):
        self.assertEqual(True, try_get_object('True'))
        self.assertEqual(True, try_get_object('true'))
        self.assertEqual(11, try_get_object('11'))
        self.assertEqual(7.3, try_get_object('7.3'))
        self.assertEqual('string', try_get_object('string'))
        self.assertEqual('id', try_get_object('id'))
        self.assertEqual('2020-03-20', try_get_object('2020-03-20'))

    # complex objects are parsed and returned
    def test_try_json(self):
        my_dict = {'key': 'value', 'inner': {'key': 'value'}}
        self.assertEqual(my_dict, try_get_object('{"key":"value","inner":{"key":"value"}}'))
        my_list = [1, 2, 3, [1, 2, 3]]
        self.assertEqual(my_list, try_get_object('[1, 2, 3, [1, 2, 3]]'))

    # date with compound object should be rendered as a string
    def test_render_date_nested(self):
        now = datetime.datetime.now()
        res = fill_template('{{ OUTPUT }}', {'OUTPUT': {'key': 'value1', 'date': now}})
        self.assertEqual(res['date'], now.strftime('%Y-%m-%d %H:%M:%S.%f'))
        self.assertEqual(res['key'], 'value1')

    # templates are being filled in correctly with primitives
    def test_template_with_simple_object(self):
        self.assertEqual(True, fill_template('{{ OUTPUT }}', {'OUTPUT': True}))
        self.assertEqual(17, fill_template('{{ OUTPUT }}', {'OUTPUT': 17}))
        self.assertEqual(4.2, fill_template('{{ OUTPUT }}', {'OUTPUT': 4.2}))
        self.assertEqual('string', fill_template('{{ OUTPUT }}', {'OUTPUT': 'string'}))
        self.assertEqual('id', fill_template('{{ OUTPUT }}', {'OUTPUT': 'id'}))
        self.assertEqual('2020-03-11', fill_template('{{ OUTPUT }}', {'OUTPUT': '2020-03-11'}))

    # templates are being filled in correctly with complex objects
    def test_template_with_complex_object(self):
        my_dict = {'key': 'value', 'inner': {'key': 'value'}}
        self.assertEqual(my_dict, fill_template('{{ OUTPUT }}', {'OUTPUT': my_dict}))
        my_list = [1, 2, 3, [1, 2, 3]]
        self.assertEqual(my_list, fill_template('{{ OUTPUT }}', {'OUTPUT': my_list}))
        my_tuple = (1, 2, (1, 2))
        self.assertEqual(my_tuple, fill_template('{{ OUTPUT }}', {'OUTPUT': my_tuple}))
        my_complex = [(1, {'foo': [1, 2, 3]}, [1, 2, {1: 'a'}])]
        self.assertEqual(my_complex, fill_template('{{ OUTPUT }}', {'OUTPUT': my_complex}))
