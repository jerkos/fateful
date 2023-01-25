import logging

import pytest
from assertpy import assert_that

from seito import attempt_to
from seito.monad.result import Err, Result
from seito.try_ import Try


def error(x):
    return x / 0


def success(x):
    return x / 1


def test_maybe():
    logging.debug(Try.of(lambda: error(1)))
    result = Try.of(lambda: error(1)).on_error(ZeroDivisionError)()
    assert_that(result).is_instance_of(Err)


def test_all():
    result = Try.of(lambda: error(1))()
    assert_that(result).is_instance_of(Err)


def test_opt():
    value = Try.of(lambda: error(1)).or_else("failure here")
    assert_that(value).is_equal_to("failure here")
    value = Try.of(lambda: success(1)).or_else("failure here")
    assert_that(value).is_equal_to(1)


def test_through():
    value = Try.of(error, 1).or_else("failure here")
    assert_that(value).is_equal_to("failure here")
    value = Try.of(success, 1).or_else("failure here")
    assert_that(value).is_equal_to(1)


def test_decorator():
    @attempt_to(errors=(ZeroDivisionError,))
    def test_error(x):
        return x / 1

    result = test_error(1)
    assert_that(result).is_instance_of(Result)


def test_fail():
    with pytest.raises(ZeroDivisionError):
        Try.of(error, 1).on_error(TypeError).get()


def test_none():
    r = Try.of(lambda x: None, 1)()
    assert_that(r).is_instance_of(Result)


def test_on_error():
    r = Try(lambda x: x / 0, 1).on_error(ZeroDivisionError)
    assert_that(r()).is_instance_of(Err)

    assert_that(Try.of(lambda x: x / 0, 1).recover(1).get()).is_equal_to(1)

    assert_that(Try.of(lambda x: x / 1, 1).recover(100).get()).is_equal_to(1)


def tests_misc():
    assert_that(Result(1).or_none()).is_equal_to(1)
    assert_that(Result(1).map(lambda x: x * 2).get()).is_equal_to(2)
    assert_that(Result(1).toto.or_else(1)).is_equal_to(1)
    assert_that(Err(ValueError()).unwrap()).is_instance_of(ValueError)
    assert_that(Err(ValueError()).is_error()).is_true()
    assert_that(Err(ValueError()).is_result()).is_false()

    class A:
        a: int = 1

        def method(self):
            return 1
    assert_that(Result(A()).method().get()).is_equal_to(1)
    assert_that(Result(A()).a.get()).is_equal_to(1)

    with pytest.raises(ValueError):
        Err(ValueError()).or_raise()

    with pytest.raises(TypeError):
        Err(ValueError()).or_raise(TypeError())
    with pytest.raises(ValueError):
        Err(ValueError()).map(lambda x: 1).get()

    for _ in Err(ValueError()):
        value = "Passed"
    else:
        value = "Not passed"
    assert_that(value).is_equal_to("Not passed")
