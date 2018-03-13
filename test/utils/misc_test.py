from catcher.utils.misc import try_get_object

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
