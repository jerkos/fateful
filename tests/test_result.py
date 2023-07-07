import pytest
from assertpy import assert_that

from seito.monad.result import Err, Ok, result_shortcut, sync_try, to_result


def error(x: int) -> float:
    return x / 0


def success(x: int) -> float:
    return x / 1


def test_maybe():
    result = sync_try(lambda: error(1), exc=(ZeroDivisionError,))()
    assert_that(result).is_instance_of(Err)


def test_all():
    result = sync_try(lambda: error(1))()
    assert_that(result).is_instance_of(Err)


def test_opt():
    value = sync_try(error)(1).or_else("failure here")
    assert_that(value).is_equal_to("failure here")
    value = sync_try(success)(1).or_else("failure here")
    assert_that(value).is_equal_to(1)


def test_decorator():
    @to_result((ZeroDivisionError,))
    def test_error(x) -> float:
        return x / 1

    result = test_error(1)
    assert_that(result).is_instance_of(Ok)


def test_fail():
    with pytest.raises(ZeroDivisionError):
        sync_try(error)(1).on_error(TypeError).get()


def test_none():
    r = sync_try(lambda x: (None, 1))(1)
    assert_that(r).is_instance_of(Ok)


def test_on_error():
    r = sync_try(lambda x: x / 0, exc=(ZeroDivisionError,))
    assert_that(r(1)).is_instance_of(Err)

    assert_that(sync_try(lambda x: x / 0)(1).recover(lambda: 1).get()).is_equal_to(1)

    assert_that(sync_try(lambda x: x / 1)(1).recover(lambda: 100).get()).is_equal_to(1)


def tests_misc():
    assert_that(Ok(1).or_none()).is_equal_to(1)
    assert_that(Ok(1).map(lambda x: x * 2).get()).is_equal_to(2)
    assert_that(Ok(1).toto.or_else(1)).is_equal_to(1)
    assert_that(Err(ValueError()).unwrap()).is_instance_of(ValueError)
    assert_that(Err(ValueError()).is_error()).is_true()
    assert_that(Err(ValueError()).is_ok()).is_false()

    class A:
        a: int = 1

        def method(self):
            return 1

    assert_that(Ok(A()).method().get()).is_equal_to(1)
    assert_that(Ok(A()).a.get()).is_equal_to(1)

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


def test_result_shortcut():
    def divide(x: int) -> Ok[float] | Err[ZeroDivisionError]:
        if not x:
            return Err(ZeroDivisionError())
        return Ok(1 / x)

    def square(x: float) -> Ok[float] | Err[ValueError]:
        if x < 0:
            return Err(ValueError())
        return Ok(x * x)

    @result_shortcut
    def test_error(x) -> Ok[float] | Err[ZeroDivisionError | ValueError]:
        val = divide(x)._
        result = square(val)._
        return Ok(result)

    val = test_error(1)
    assert_that(val).is_instance_of(Ok)

    val = test_error(0)
    assert_that(val).is_instance_of(Err)
    assert_that(val.unwrap()).is_instance_of(ZeroDivisionError)
