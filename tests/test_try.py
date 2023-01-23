import pytest
from assertpy import assert_that
from loguru import logger

from seito import attempt_to
from seito.monad.container import Err, Result
from seito.monad.try_ import Try


def error(x):
    return x / 0


def success(x):
    return x / 1


def test_maybe():
    logger.debug(Try.of(lambda: error(1)))
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
