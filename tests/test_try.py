import unittest

from seito import option
from seito import underscore as _
from seito.maybe import _try
from seito.underscore import seito_rdy, F


class Test(unittest.TestCase):
    def test_maybe_decorator(self):

        def may_raise_exception():
            raise ValueError('error occured')

        maybe_value = _try(may_raise_exception).or_else(0)
        self.assertEqual(maybe_value, 0)
        print(maybe_value)

    def test_lift(self):
        def add(x, y): return x / y

        f = F(add).lift(_try)
        f2 = F(add).lift(option)
        print(f(1, 0).or_else(0))
        print(f2(1, 2).get())
