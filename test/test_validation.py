import confit
import os
from . import _root, unittest

class TypeCheckTest(unittest.TestCase):
    def test_str_type_correct(self):
        config = _root({'foo': 'bar'})
        value = config['foo'].get(str)
        self.assertEqual(value, 'bar')

    def test_str_type_incorrect(self):
        config = _root({'foo': 2})
        with self.assertRaises(confit.ConfigTypeError):
            config['foo'].get(str)

    def test_int_type_correct(self):
        config = _root({'foo': 2})
        value = config['foo'].get(int)
        self.assertEqual(value, 2)

    def test_int_type_incorrect(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.ConfigTypeError):
            config['foo'].get(int)

class BuiltInValidatorTest(unittest.TestCase):
    def test_as_filename_with_non_file_source(self):
        config = _root({'foo': 'foo/bar'})
        value = config['foo'].as_filename()
        self.assertEqual(value, os.path.join(os.getcwd(), 'foo', 'bar'))

    def test_as_filename_with_file_source(self):
        source = confit.ConfigSource({'foo': 'foo/bar'},
                                     filename='/baz/config.yaml')
        config = _root(source)
        config.config_dir = lambda: '/config/path'
        value = config['foo'].as_filename()
        self.assertEqual(value, os.path.realpath('/config/path/foo/bar'))

    def test_as_filename_with_default_source(self):
        source = confit.ConfigSource({'foo': 'foo/bar'},
                                     filename='/baz/config.yaml',
                                     default=True)
        config = _root(source)
        config.config_dir = lambda: '/config/path'
        value = config['foo'].as_filename()
        self.assertEqual(value, os.path.realpath('/config/path/foo/bar'))

    def test_as_filename_wrong_type(self):
        config = _root({'foo': None})
        with self.assertRaises(confit.ConfigTypeError):
            config['foo'].as_filename()

    def test_as_choice_correct(self):
        config = _root({'foo': 'bar'})
        value = config['foo'].as_choice(['foo', 'bar', 'baz'])
        self.assertEqual(value, 'bar')

    def test_as_choice_error(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.ConfigValueError):
            config['foo'].as_choice(['foo', 'baz'])

    def test_as_choice_with_dict(self):
        config = _root({'foo': 'bar'})
        res = config['foo'].as_choice({
            'bar': 'baz',
            'x': 'y',
        })
        self.assertEqual(res, 'baz')

    def test_as_number_float(self):
        config = _root({'f': 1.0})
        config['f'].as_number()

    def test_as_number_int(self):
        config = _root({'i': 2})
        config['i'].as_number()

    @unittest.skipIf(confit.PY3, "long only present in Python 2")
    def test_as_number_long_in_py2(self):
        config = _root({'l': long(3)})
        config['l'].as_number()

    def test_as_number_string(self):
        config = _root({'s': 'a'})
        with self.assertRaises(confit.ConfigTypeError):
            config['s'].as_number()

    def test_as_str_seq_str(self):
        config = _root({'k': 'a b c'})
        self.assertEqual(
            config['k'].as_str_seq(),
            ['a', 'b', 'c']
        )

    def test_as_str_seq_list(self):
        config = _root({'k': ['a b', 'c']})
        self.assertEqual(
            config['k'].as_str_seq(),
            ['a b', 'c']
        )
