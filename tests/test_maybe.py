import unittest
from seito import attempt, attempt_dec, F


def error(x):
    return x / 0


def success(x):
    return x / 1


class Test(unittest.TestCase):
    def test_maybe(self):
        (attempt(lambda: error(1)).on_error(ZeroDivisionError, cb=lambda e: print(e))())

    def test_all(self):
        value = attempt(lambda: error(1))()
        print("value: ", value)

    def test_opt(self):
        value = attempt(lambda: error(1))().or_else('failure here')
        print("value: ", value)
        value = attempt(lambda: success(1))().or_else('failure here')
        print("value: ", value)

    def test_through(self):
        value = attempt(error)(1).or_else('failure here')
        print("value: ", value)
        value = attempt(success)(1).or_else('failure here')
        print("value: ", value)

    def test_underscore(self):
        value = (
          attempt(F(error)(1))()
          .or_else('failure here')
        )
        print("value: ", value)

    def test_decorator(self):

      @attempt_dec(errors=(ZeroDivisionError,), as_opt=False)
      def test_error(x):
        return x / 1

      print("here: ,", test_error(1))


