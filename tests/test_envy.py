# coding: utf-8
import os
import json
from decimal import Decimal
from unittest import TestCase
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse


from envy import Environment, env, ImproperlyConfigured


# Test main class

class TestEnvironment(TestCase):

    # Init

    def test_init_no_environ(self):
        e = Environment()
        self.assertIs(os.environ, e.environ)

    def test_init_custom_environ(self):
        environ = {'test': True}
        e = Environment(environ)
        self.assertIs(environ, e.environ)

    # Contains

    def test_contains(self):
        e = Environment({'x': 1})
        self.assertTrue('x' in e)
        self.assertFalse('y' in e)

    # Function interface

    def test_call_returns_value(self):
        e = Environment({'x': 1})
        self.assertEqual(e('x'), 1)

    def test_call_returns_default_on_missing(self):
        e = Environment({})
        self.assertEqual(e('missing', default=1), 1)

    def test_call_raises_on_missing(self):
        e = Environment({})
        with self.assertRaises(ImproperlyConfigured):
            e('missing')

    # Casting

    def test_default_value_casted_by_default(self):
        e = Environment({})
        self.assertEqual(e('x', cast=int, default="1"), 1)

    def test_default_value_not_forced(self):
        e = Environment({})
        self.assertEqual(e('x', cast=int, default="1", force=False), "1")

    def test_default_value_none(self):
        e = Environment({})
        self.assertEqual(e('x', cast=int, default=None), None)


class CastingTestCase(TestCase):

    def assertEqualAndType(self, left, right):  # noqa
        self.assertEqual(left, right)
        self.assertIs(type(left), type(right))


class TestStringCasting(CastingTestCase):

    def test_str_method_from_str(self):
        e = Environment({'s': 'x'})
        self.assertEqualAndType(e.str('s'), u'x')

    def test_str_method_from_unicode(self):
        e = Environment({'s': u'\u2603'})
        self.assertEqualAndType(e.str('s'), u'\u2603')


class TestBoolCasting(CastingTestCase):

    def test_bool_true_returns_true(self):
        e = Environment({'x': 'true'})
        self.assertEqualAndType(e('x', cast=bool), True)
        self.assertEqualAndType(e.bool('x'), True)

    def test_bool_false_returns_false(self):
        e = Environment({'x': 'false'})
        self.assertEqualAndType(e('x', cast=bool), False)
        self.assertEqualAndType(e.bool('x'), False)

    def test_bool_is_case_insensitive(self):
        e = Environment({'x': 'trUE'})
        self.assertEqualAndType(e('x', cast=bool), True)
        self.assertEqualAndType(e.bool('x'), True)

        e = Environment({'x': 'FAlse'})
        self.assertEqualAndType(e('x', cast=bool), False)
        self.assertEqualAndType(e.bool('x'), False)

    def test_bool_returns_default_on_missing(self):
        e = Environment({})
        self.assertEqualAndType(e('missing', cast=bool, default=True), True)
        self.assertEqualAndType(e.bool('missing', True), True)

        self.assertEqualAndType(e('missing', cast=bool, default=False), False)
        self.assertEqualAndType(e.bool('missing', False), False)

    def test_bool_error_raises(self):
        e = Environment({'x': '1'})

        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=bool)
        with self.assertRaises(ImproperlyConfigured):
            e.bool('x')

    def test_bool_error_message(self):
        e = Environment({'XXX': 'YYY'})
        try:
            e('XXX', cast=bool)
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('YYY', str(exc), "message should contain value")
            self.assertIn('bool', str(exc), "message should contain type")

        try:
            e.bool('XXX')
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('YYY', str(exc), "message should contain value")
            self.assertIn('bool', str(exc), "message should contain type")


class TestIntCasting(CastingTestCase):

    def test_int_from_string(self):
        e = Environment({'x': '1'})
        self.assertEqualAndType(e('x', cast=int), 1)
        self.assertEqualAndType(e.int('x'), 1)

    def test_int_from_int(self):
        e = Environment({'x': 1})
        self.assertEqualAndType(e('x', cast=int), 1)
        self.assertEqualAndType(e.int('x'), 1)

    def test_int_from_float(self):
        e = Environment({'x': 1.0})
        self.assertEqualAndType(e('x', cast=int), 1)
        self.assertEqualAndType(e.int('x'), 1)

    def test_int_casts_default(self):
        e = Environment({})
        self.assertEqualAndType(e('x', cast=int, default='1'), 1)
        self.assertEqualAndType(e.int('x', default='1'), 1)

    def test_int_underscore_separator(self):
        e = Environment({'x': '1_000_000'})
        self.assertEqualAndType(e('x', cast=int), 1000000)
        self.assertEqualAndType(e.int('x'), 1000000)

    def test_int_error_raises(self):
        e = Environment({'x': 'y'})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=int)
        with self.assertRaises(ImproperlyConfigured):
            e.int('x')

    def test_int_error_message(self):
        e = Environment({'XXX': 'YYY'})
        try:
            e('XXX', cast=int)
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('YYY', str(exc), "message should contain value")
            self.assertIn('int', str(exc), "message should contain type")

        try:
            e.int('XXX')
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('YYY', str(exc), "message should contain value")
            self.assertIn('int', str(exc), "message should contain type")


class TestFloatCasting(CastingTestCase):

    def test_float_from_string(self):
        e = Environment({'x': '1.0'})
        self.assertEqualAndType(e('x', cast=float), 1.0)
        self.assertEqualAndType(e.float('x'), 1.0)

    def test_float_from_float(self):
        e = Environment({'x': 1.0})
        self.assertEqualAndType(e('x', cast=float), 1.0)
        self.assertEqualAndType(e.float('x'), 1.0)

    def test_float_from_int(self):
        e = Environment({'x': 1})
        self.assertEqualAndType(e('x', cast=float), 1.0)
        self.assertEqualAndType(e.float('x'), 1.0)

    def test_float_casts_default(self):
        e = Environment({})
        self.assertEqualAndType(e('x', cast=float, default='1.1'), 1.1)
        self.assertEqualAndType(e.float('x', default='1.1'), 1.1)

    def test_float_underscore_separator(self):
        e = Environment({'x': '1_000_000.0'})
        self.assertEqualAndType(e('x', cast=float), 1000000.0)
        self.assertEqualAndType(e.float('x'), 1000000.0)

    def test_float_error_raises(self):
        e = Environment({'x': 'y'})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=float)
        with self.assertRaises(ImproperlyConfigured):
            e.float('x')

    def test_float_error_message(self):
        e = Environment({'XXX': 'YYY'})
        try:
            e('XXX', cast=float)
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('YYY', str(exc), "message should contain value")
            self.assertIn('float', str(exc), "message should contain type")

        try:
            e.float('XXX')
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('YYY', str(exc), "message should contain value")
            self.assertIn('float', str(exc), "message should contain type")


class TestDecimalCasting(CastingTestCase):

    def test_decimal_returns_decimal(self):
        e = Environment({'x': '1'})
        self.assertEqualAndType(e('x', cast=Decimal), Decimal('1'))
        self.assertEqualAndType(e.decimal('x'), Decimal('1'))

    def test_decimal_casts_default(self):
        e = Environment({})
        self.assertEqualAndType(e('x', cast=Decimal, default='1.1'),
                                Decimal('1.1'))
        self.assertEqualAndType(e.decimal('x', default='1.1'),
                                Decimal('1.1'))

    def test_decimal_error_raises(self):
        e = Environment({'x': 'y'})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=Decimal)
        with self.assertRaises(ImproperlyConfigured):
            e.decimal('x')

    def test_decimal_error_message(self):
        e = Environment({'XXX': 'YYY'})
        try:
            e('XXX', cast=Decimal)
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('YYY', str(exc), "message should contain value")
            self.assertIn('Decimal', str(exc), "message should contain type")

        try:
            e.decimal('XXX')
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('YYY', str(exc), "message should contain value")
            self.assertIn('Decimal', str(exc), "message should contain type")


class TestTupleCasting(CastingTestCase):

    def test_tuple_from_string(self):
        e = Environment({'x': '1, 2'})
        self.assertEqualAndType(e('x', cast=tuple), ('1', '2'))
        self.assertEqualAndType(e.tuple('x'), ('1', '2'))

    def test_tuple_from_collection(self):
        e = Environment({
            't': (1, 2),
            'l': [1, 2],
            's': {1, 2}
        })
        self.assertEqualAndType(e('t', cast=tuple), (1, 2))
        self.assertEqualAndType(e.tuple('t'), (1, 2))

        self.assertEqualAndType(e('l', cast=tuple), (1, 2))
        self.assertEqualAndType(e.tuple('l'), (1, 2))

        self.assertEqualAndType(e('s', cast=tuple), (1, 2))
        self.assertEqualAndType(e.tuple('s'), (1, 2))

    def test_tuple_from_other_raises(self):
        e = Environment({'x': 1})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=tuple)
        with self.assertRaises(ImproperlyConfigured):
            e.tuple('x')

    def test_tuple_incorrect_cast_raises(self):
        e = Environment({'x': 1})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=(int, int,))
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=tuple())

    def test_tuple_item_casts(self):
        e = Environment({'x': '1, 2, 3'})
        self.assertEqualAndType(e('x', cast=(int,)), (1, 2, 3))
        self.assertEqualAndType(e.tuple('x', cast=int), (1, 2, 3))

    def test_tuple_nested_collection_raises(self):
        e = Environment({'x': '1, 2, 3'})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=(tuple,))
        with self.assertRaises(ImproperlyConfigured):
            e.tuple('x', cast=tuple)

    def test_tuple_error_message(self):
        e = Environment({'XXX': 1})
        try:
            e('XXX', cast=tuple)
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('int', str(exc), "message should contain type")

        try:
            e.tuple('XXX')
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('int', str(exc), "message should contain type")


class TestListCasting(CastingTestCase):

    def test_list_from_string(self):
        e = Environment({'x': '1, 2'})
        self.assertEqualAndType(e('x', cast=list), ['1', '2'])
        self.assertEqualAndType(e.list('x'), ['1', '2'])

    def test_list_from_collection(self):
        e = Environment({
            't': (1, 2),
            'l': [1, 2],
            's': {1, 2}
        })
        self.assertEqualAndType(e('t', cast=list), [1, 2])
        self.assertEqualAndType(e.list('t'), [1, 2])

        self.assertEqualAndType(e('l', cast=list), [1, 2])
        self.assertEqualAndType(e.list('l'), [1, 2])

        self.assertEqualAndType(e('s', cast=list), [1, 2])
        self.assertEqualAndType(e.list('s'), [1, 2])

    def test_list_from_other_raises(self):
        e = Environment({'x': 1})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=list)
        with self.assertRaises(ImproperlyConfigured):
            e.list('x')

    def test_list_type_error_message(self):
        e = Environment({'XXX': 1})
        try:
            e('XXX', cast=list)
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('int', str(exc), "message should contain type")

        try:
            e.list('XXX')
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('int', str(exc), "message should contain type")

    def test_list_incorrect_cast_raises(self):
        e = Environment({'x': 1})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=[int, int])
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=[])

    def test_list_incorrect_cast_error_message(self):
        e = Environment({'XXX': 1})
        try:
            e('XXX', cast=[int, float])
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('list', str(exc), "message should contain type")

    def test_list_item_casts(self):
        e = Environment({'x': '1, 2, 3'})
        self.assertEqualAndType(e('x', cast=[int]), [1, 2, 3])
        self.assertEqualAndType(e.list('x', cast=int), [1, 2, 3])

    def test_list_nested_collection_raises(self):
        e = Environment({'x': '1, 2, 3'})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=[list])
        with self.assertRaises(ImproperlyConfigured):
            e.list('x', cast=list)

    def test_list_nested_error_message(self):
        e = Environment({'XXX': '1, 2, 3'})
        try:
            e('XXX', cast=[list])
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('nested', str(exc), "message should contain nested")

        try:
            e.list('XXX', cast=list)
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('nested', str(exc), "message should contain nested")


class TestSetCasting(CastingTestCase):

    def test_dict_from_string(self):
        e = Environment({'x': '1, 2'})
        self.assertEqualAndType(e('x', cast=set), {'1', '2'})
        self.assertEqualAndType(e.set('x'), {'1', '2'})

    def test_set_from_collection(self):
        e = Environment({
            't': (1, 2),
            'l': [1, 2],
            's': {1, 2}
        })
        self.assertEqualAndType(e('t', cast=set), {1, 2})
        self.assertEqualAndType(e.set('t'), {1, 2})

        self.assertEqualAndType(e('l', cast=set), {1, 2})
        self.assertEqualAndType(e.set('l'), {1, 2})

        self.assertEqualAndType(e('s', cast=set), {1, 2})
        self.assertEqualAndType(e.set('s'), {1, 2})

    def test_set_from_other_raises(self):
        e = Environment({'x': 1})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=set)
        with self.assertRaises(ImproperlyConfigured):
            e.set('x')

    def test_set_type_error_message(self):
        e = Environment({'XXX': 1})
        try:
            e('XXX', cast=set)
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('int', str(exc), "message should contain type")

        try:
            e.set('XXX')
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('int', str(exc), "message should contain type")

    def test_set_incorrect_cast_raises(self):
        e = Environment({'x': 1})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast={int, float})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=set())

    def test_set_incorrect_cast_error_message(self):
        e = Environment({'XXX': 1})
        try:
            e('XXX', cast={int, float})
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('set', str(exc), "message should contain type")

    def test_set_item_casts(self):
        e = Environment({'x': '1, 2, 3'})
        self.assertEqualAndType(e('x', cast={int}), {1, 2, 3})
        self.assertEqualAndType(e.set('x', cast=int), {1, 2, 3})

    def test_set_nested_collection_raises(self):
        e = Environment({'x': '1, 2, 3'})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast={set})
        with self.assertRaises(ImproperlyConfigured):
            e.set('x', cast=set)

    def test_set_nested_collection_error_message(self):
        e = Environment({'XXX': '1, 2, 3'})
        try:
            e('XXX', cast={list})
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('nested', str(exc), "message should contain nested")

        try:
            e.set('XXX', cast=list)
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('nested', str(exc), "message should contain nested")


class TestDictCasting(CastingTestCase):

    def test_dict_from_string(self):
        e = Environment({'d': 'x=1, y=2'})
        self.assertEqualAndType(e('d', cast=dict), {'x': '1', 'y': '2'})
        self.assertEqualAndType(e.dict('d'), {'x': '1', 'y': '2'})

    def test_dict_from_dict(self):
        e = Environment({'d': {'x': 1, 'y': 2}})
        self.assertEqualAndType(e('d', cast=dict), {'x': 1, 'y': 2})
        self.assertEqualAndType(e.dict('d'), {'x': 1, 'y': 2})

    def test_dict_from_other_raises(self):
        e = Environment({'x': 1})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=dict)
        with self.assertRaises(ImproperlyConfigured):
            e.dict('x')

    def test_dict_type_error_message(self):
        e = Environment({'XXX': 1})
        try:
            e('XXX', cast=dict)
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('int', str(exc), "message should contain type")

        try:
            e.dict('XXX')
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('int', str(exc), "message should contain type")

    def test_dict_incorrect_cast_raises(self):
        e = Environment({'x': 'x=1, y=2'})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast={int: float, str: int})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast=dict())

    def test_dict_incorrect_cast_error_message(self):
        e = Environment({'XXX': 'x=1, y=2'})
        try:
            e('XXX', cast={int: float, str: int})
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('dict', str(exc), "message should contain type")

    def test_dict_item_casts(self):
        e = Environment({'d': 'x=1, y=2'})
        self.assertEqualAndType(e('d', cast={str: int}), {'x': 1, 'y': 2})
        self.assertEqualAndType(e.dict('d', cast=int), {'x': 1, 'y': 2})

    def test_dict_nested_collection_raises(self):
        e = Environment({'x': '1, 2, 3'})
        with self.assertRaises(ImproperlyConfigured):
            e('x', cast={str: dict})
        with self.assertRaises(ImproperlyConfigured):
            e.dict('x', cast=dict)

    def test_dict_nested_collection_error_message(self):
        e = Environment({'XXX': '1, 2, 3'})
        try:
            e('XXX', cast={str: dict})
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('nested', str(exc), "message should contain nested")

        try:
            e.dict('XXX', cast=dict)
        except ImproperlyConfigured as exc:
            self.assertIn('XXX', str(exc), "message should contain var")
            self.assertIn('nested', str(exc), "message should contain nested")


class TestJsonCasting(CastingTestCase):

    def test_json_from_string(self):
        e = Environment({'j': '{"x": 1}'})
        self.assertEqualAndType(e('j', cast=json.loads), {'x': 1})
        self.assertEqualAndType(e.json('j'), {'x': 1})

    def test_json_parse_error(self):
        e = Environment({'j': '{"x": 1'})
        with self.assertRaises(ImproperlyConfigured):
            e('j', cast=json.loads)
        with self.assertRaises(ImproperlyConfigured):
            e.json('j')

    def test_json_type_error(self):
        e = Environment({'j': 1})
        with self.assertRaises(ImproperlyConfigured):
            e('j', cast=json.loads)
        with self.assertRaises(ImproperlyConfigured):
            e.json('j')


class TestUrlCasting(CastingTestCase):

    def test_url_from_string(self):
        e = Environment({'u': 'http://example.com'})
        p = urlparse.urlparse('http://example.com')
        self.assertEqualAndType(e('u', cast=urlparse.urlparse), p)
        self.assertEqualAndType(e.url('u'), p)

    def test_url_type_error(self):
        e = Environment({'u': 1})
        with self.assertRaises(ImproperlyConfigured):
            e('u', cast=urlparse.urlparse)
        with self.assertRaises(ImproperlyConfigured):
            e.url('u')


# Test convenience exports

class TestInitializedEnv(TestCase):

    def test_uses_os_environ(self):
        self.assertIs(os.environ, env.environ)

    def test_env_is_environment(self):
        self.assertTrue(isinstance(env, Environment))
