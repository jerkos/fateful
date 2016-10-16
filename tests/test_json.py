import unittest

from seito.john import obj


class Test(unittest.TestCase):
    def test_john_object(self):
        i = obj({'z-index': 1000})

        self.assertEqual(i['z-index'].or_else(0), 1000)
        i['toto'] = [1, 2, 3]
        i.toto = [4, 5, 6]
        self.assertEqual(i.toto.or_none(), [4, 5, 6])

    def test_stringify(self):
        i = obj({'z-index': 1000})
        self.assertEqual(i.stringify(sort_keys=True),
                         '''{"z-index": 1000}''')
        self.assertEqual(str(i, sort_keys=True),
                         '''{"z-index": 1000}''')

