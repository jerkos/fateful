import unittest
import types

from seito.seq import seq
from seito.underscore import underscore as _


class A(object):
    def __init__(self, x):
        self.x = x

    def get_x(self):
        return self.x

    def power(self, p):
        return self.x ** p


class Test(unittest.TestCase):
    def test_constructor(self):
        self.assertEqual(seq(1, 2, 3).to_list(), [1, 2, 3])
        self.assertEqual(seq([1, 2, 3]).to_list(), [1, 2, 3])

        a = [1, 2, 3]
        self.assertIsInstance(seq((i for i in a)).sequence, types.GeneratorType)
        self.assertEqual(seq((i for i in a)).to_list(), [1, 2, 3])

    def test_stream(self):
        print(seq(1, 2, 3).stream().sequence)
        self.assertIsInstance(seq(1, 2, 3).stream().sequence, types.GeneratorType)

    def test_for_each(self):
        seq(1, 2, 3).stream().for_each(lambda x: print(x))
        seq(1, 2, 3).for_each(lambda x: print(x))
        seq(1, 2, 3).for_each(print)

    def test_getting_attribute_from_underscore(self):
        self.assertEqual(
            seq(A(4), A(5), A(6)).stream().map(_.get_x()).to_list(),
            [4, 5, 6])
        self.assertEqual(
            seq(A(4), A(5), A(6)).stream().map(_.power(2)).to_list(),
            [16, 25, 36]
        )

    def test_add_element_from_underscore(self):
        self.assertEqual(
            seq(A(4), A(5), A(6)).stream().map(_.power(2) + 1).to_list(),
            [17, 26, 37])

    def test_calling_extern_function(self):
        def power2(p, x):
            return p ** x

        self.assertEqual(
            (seq(4, 5, 6)
             .stream()
             .map(power2, 2)
             .to_list()),
            [16, 25, 36]
        )
