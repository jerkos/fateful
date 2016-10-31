import unittest
import types

from seito.seq import seq
from seito.underscore import underscore as _, seito_rdy


class A(object):
    def __init__(self, x):
        self.x = x

    def get_x(self):
        print(self.x)
        return self.x

    def power(self, p):
        print(self.x ** p)
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
            seq(A(4), A(5), A(6)).stream().for_each(_.get_x()),
            None)
        self.assertEqual(
            seq(A(4), A(5), A(6)).stream().for_each(_.power(2)),
            None
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

    def test_for_each_with_arguments(self):
        def print_sum(x, y):
            print(x + y)

        self.assertEqual(seq(1, 2, 3).stream().for_each(print_sum, 1, _), None)
        self.assertEqual(seq(1, 2, 3).stream().for_each(print_sum, _, 1), None)
        self.assertEqual(seq(1, 2, 3).stream().for_each(print), None)
        self.assertEqual(seq(1, 2, 3).stream().for_each(print, _), None)
        self.assertEqual(seq(1, 2, 3).stream().for_each(print_sum, 2), None)

    def test_decorator(self):
        @seito_rdy
        def print_sum(x, y):
            print(x + y)

        seq(1, 2, 3).stream().for_each(print_sum(_, 2))
        seq(A(1), A(2), A(3)).stream().for_each(_.get_x())

    def test_dict(self):
        def print_x_y(x, y):
            print(x, y)

        print_x_y = seito_rdy(print_x_y)

        seq({1: 2, 3: 4}).for_each(print_x_y(_._1, _._2))
        seq({1: A(2), 3: A(4)}).for_each(_._2.get_x())

    def test_dict_to_dict(self):
        a = seq({1: 2, 3: 4}).map(_((_._1, _._2))).to_dict()
        print(a)

    def test_complex(self):
        # a = seq(A(1), A(2), A(3)).stream().map(_.get_x() + 4).to_list()
        # print(a)

        a = seq(1, 2, 3).stream().map(_ + 4).to_list()
        print(a)