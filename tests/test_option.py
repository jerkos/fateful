import unittest

from seito.option import option, none, opt


class Test(unittest.TestCase):
    def test_option_none_get(self):
        with self.assertRaises(ValueError):
            r = none.get()

    def test_option_is_empty(self):
        self.assertTrue(none.is_empty())
        value = 'hello world'
        self.assertFalse(option(value).is_empty())

    def test_option_or_else(self):
        value = 1
        self.assertEqual(none.or_else(value), 1)
        self.assertEqual(none.or_else(lambda: 1), 1)
        self.assertEqual(option(value).map(lambda v: v + 1).or_else(0), 2)

    def test_option_map(self):
        none_value = None
        one_value = 1
        with self.assertRaises(ValueError):
            option(none_value).map(lambda v: v + 1).get()
        self.assertEqual(option(none_value).map(lambda v: v + 1).or_else(2), 2)
        self.assertEqual(option(one_value).map(lambda v: v + 1).get(), 2)

        uppercase = 'VALUE'
        self.assertEqual(option(uppercase).map(lambda value: value.lower()).or_else(''), 'value')

    def test_option_iteration(self):
        value = 1
        for v in option(value):
            self.assertEqual(v, 1)

    def test_option_forwarding(self):
        value = 'VALUE'
        self.assertEqual(option(value).lower().or_else(''), 'value')
        self.assertEqual(none.lower().or_else(''), '')
        self.assertEqual(none.toto().or_else('titi'), 'titi')
        self.assertEqual(option('TOTO').capitalizes().or_else('t'), 't')
        self.assertEqual(option('toto').capitalize().or_else('failed'), 'Toto')
        self.assertEqual(option('riri').count('ri').get(), 2)

    def test_nested_option(self):
        nested_none = option(option(option('tata')))
        for n in nested_none:
            self.assertEqual(n, 'tata')

    def test_if_false(self):
        op = opt('value').or_else('')
        self.assertEqual(len(op), 5)
        print(option('value').get_or('') is none)

        self.assertEqual(option([]).or_if_false([1, 2, 3]), [1, 2, 3])
