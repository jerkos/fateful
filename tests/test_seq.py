import unittest
import types
import time
import operator

from seito.seq import seq, AND_BOOLEAN, OR_BOOLEAN
from seito.underscore import underscore as _, seito_rdy


class A(object):
    def __init__(self, x):
        self.x = x

    def get_new_a(self, z):
        return A(z)

    def get_x(self):
        # print(self.x)
        return self.x

    def get_z(self, z):
        return A(self.x + z)

    def power(self, p):
        print(self.x ** p)
        return self.x ** p


class Test(unittest.TestCase):
    def test_constructor(self):
        self.assertEqual(seq(1, 2, 3).to_list(), [1, 2, 3])
        self.assertEqual(seq([1, 2, 3]).to_list(), [1, 2, 3])

        a = [1, 2, 3]
        self.assertIsInstance(seq(i for i in a).sequence, types.GeneratorType)
        self.assertEqual(seq(i for i in a).to_list(), [1, 2, 3])

    def test_stream(self):
        print(seq(1, 2, 3).stream().sequence)
        self.assertIsInstance(seq(1, 2, 3).stream().sequence, types.GeneratorType)
        print(seq(1, 2, 3).sequence)
        self.assertIsInstance(seq(1, 2, 3).sequence, list)

        self.assertIsInstance(seq(1, 2, 3).map(_ * 3).sequence, list)

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
        self.assertEqual(seq({1: A(2), 3: A(4)}).map(_._2.get_x() + 2).to_list(), [4, 6])
        self.assertEqual(seq({1: A(2), 3: A(4)}).map((_._2.get_x() + 2) ** 2).to_list(), [16, 36])

    def test_dict_to_dict(self):
        a = seq({1: 2, 3: 4}).map(_((_._1, _._2))).to_dict()
        self.assertEqual(a, {1: 2, 3: 4})

    def test_complex(self):
        self.assertEqual(seq(A(1), A(2), A(3)).stream().map(_.get_x() + 4).to_list(), [5, 6, 7])
        self.assertEqual(seq(1, 2, 3).stream().map(_ + 4).to_list(), [5, 6, 7])

    def test_chaining_underscore(self):
        self.assertEqual(seq(A(1), A(2), A(3), A(4)).stream().map(_.get_new_a(4).get_z(4).get_x()).to_list(),
                         [8, 8, 8, 8])

    def test_plus(self):
        a = seq(A(1), A(2), A(3)).stream().map(_.get_x() + A(2).get_x()).to_list()
        self.assertEqual(a, [3, 4, 5])

    def test_sort_by(self):
        a = seq(3, 2, 1).stream().sort().to_list()
        self.assertEqual(a, [1, 2, 3])
        b = seq(A(3), A(2), A(1)).stream().sort_by(_.get_x()).map(_.get_x()).to_list()
        self.assertEqual(b, [1, 2, 3])

    def test_bench(self):
        a = time.clock()
        for i in range(10000):
            seq(range(1000, 1, -1)).sort()
        c = time.clock() - a
        print('time elapsed seq: ' + str(c))
        b = time.clock()
        for i in range(10000):
            sorted(range(1000, 1, -1))
        d = time.clock() - b
        print('time elapsed builtins: ' + str(d))
        print('diff :' + str(max(c, d) / min(c, d)))

    def test_bench_map(self):
        a = time.clock()
        for i in range(100):
            seq(list(range(1000, 1, -1))).map(_ + 1)
        c = time.clock() - a
        print('time elapsed seq: ' + str(c))

    def test_sort_by_bis(self):
        a = seq(A(3), A(2), A(1)).sort_by(_.get_x()).map(_.get_x()).to_list()
        self.assertEqual(a, [1, 2, 3])

    def test_filter(self):
        a = seq(A(3), A(2), A(1)).filter(_.get_x() < 2).map(_.get_x()).to_list()
        self.assertEqual(a, [1])

    def test_first_opt(self):
        a = seq(A(3), A(2), A(1)).filter(_.get_x() < 1).first_opt().or_else([1, 2, 3])
        self.assertEqual(a, [1, 2, 3])
        a = seq(A(3), A(2), A(1)).filter(_.get_x() < 3).first_opt().map(_.get_x()).or_else(0)
        self.assertEqual(a, 2)

    def test_func_composition(self):
        f1 = lambda x: x > 5
        f2 = lambda x: x > 8

        print(seq(1, 2, 3).stream().reduce(operator.add))

        f = seq(f1, f2).reduce(OR_BOOLEAN)
        print(f(6))
