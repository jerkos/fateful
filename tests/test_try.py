import unittest

from seito import option
from seito import underscore as _
from seito.underscore import seito_rdy, F


class Test(unittest.TestCase):

    def test_lift(self):
        def add(x, y): return x / y

        f2 = F(add).lift(option).lift(option).end()
        print(f2(1, 2))
        print(f2(1, 2).get())
