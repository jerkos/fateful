import asyncio

import pytest
from assertpy import assert_that

from seito.monad.async_result import AsyncResult, async_try, lift_future
from seito.monad.func import _, default
from seito.monad.option import Some, opt
from seito.monad.result import Ok


class A:
    x = 1


async def add_async(a, b):
    await asyncio.sleep(0.1)
    return a + b


async def async_none():
    await asyncio.sleep(0.1)
    return None


async def async_raise():
    await asyncio.sleep(0.1)
    return 1 / 0


async def async_identity(x):
    await asyncio.sleep(0.1)
    return x


async def async_opt():
    await asyncio.sleep(0.1)
    return opt(opt(1))


async def async_a():
    await asyncio.sleep(0.1)
    return A()


@pytest.mark.asyncio
async def test_async_opt():
    value = await async_try(add_async)(1, 1).or_else(obj=lambda: 4)
    assert_that(value).is_equal_to(2)

    value = await async_try(async_none).or_else(lambda: 1)
    assert_that(value).is_equal_to(None)

    value = await async_try(add_async)(1, 2).map(lambda x: x * 2).get()
    assert_that(value).is_equal_to(6)

    value = (
        await async_try(add_async)(1, 2).map(lambda x: x * 2).map(lambda x: x / 2).get()
    )
    assert_that(value).is_equal_to(3)
    #
    value = (
        await async_try(async_none).map(lambda x: 2).map(lambda x: 4).or_else(lambda: 1)
    )
    assert_that(value).is_equal_to(4)

    #
    async for __ in async_try(async_none):
        ...
    else:
        value = "Not passed"

    assert_that(value).is_equal_to("Not passed")

    #
    async for val in async_try(add_async)(1, 2):
        value = val
    assert_that(value).is_equal_to(3)
    #
    value = (
        await AsyncResult(add_async)(1, 2)
        .map(lambda x: x * 2)
        .map(lambda x: x / 2)
        .match(Ok(_), default >> 1)
    )
    assert_that(value).is_equal_to(3.0)

    assert_that(await async_try(add_async)(1, 2).is_error()).is_false()
    #
    assert_that(await async_try(add_async)(1, 2).or_raise(ValueError())).is_equal_to(3)
    #
    str(async_try(add_async)(1, 2))
    #
    assert_that(await async_try(async_raise).or_else(lambda: 1)).is_equal_to(1)
    #
    assert_that(await async_try(async_raise).or_none()).is_none()
    #
    with pytest.raises(ZeroDivisionError):
        await async_try(async_raise).get()
    #
    assert_that(
        await async_try(async_identity)(1).map(lambda x: x / 0).or_else(lambda: 1)
    ).is_equal_to(1)
    #
    async for val in async_try(async_identity)(1):
        assert_that(val).is_equal_to(1)
    #
    assert_that(await async_try(async_raise).or_else(1)).is_equal_to(1)
    #
    assert_that(await async_try(async_raise).or_else(add_async, 1, 2)).is_equal_to(3)
    #
    assert_that(await async_try(async_opt).get()).is_equal_to(Some(Some(1)))
    #
    val = await async_try[..., Some[Some[int]], Exception](async_opt).get()
    match val:
        case Some(_) as v:
            result = v.flatten().get()
        case _:
            result = None
    assert_that(result).is_equal_to(1)
    #
    assert_that(await async_try(async_a).y.or_else(lambda: 1)).is_equal_to(1)
    #
    value = await AsyncResult(async_raise).on_error((ZeroDivisionError,)).or_none()
    assert_that(value).is_none()

    assert_that(await async_try(async_identity)(1).is_ok()).is_true()

    v = []
    await async_try(async_identity)(1).for_each(lambda r: v.append(r))
    assert_that(v).is_equal_to([1])

    @lift_future
    async def test_async_(a, b) -> float:
        await asyncio.sleep(0.1)
        return a / b

    assert_that(await test_async_(1, 1).get()).is_equal_to(1.0)
    assert_that(await test_async_(1, 0).recover(lambda: 1).get()).is_equal_to(1)
    assert_that(
        await test_async_(1, 0).map(lambda x: x + 1).recover(lambda: 1).get()
    ).is_equal_to(1)

    with pytest.raises(TypeError):

        @lift_future  # type: ignore
        def test_async(a, b) -> float:
            return a / b

    async def test_22(a, b) -> float:
        await asyncio.sleep(0.1)
        return a / b

    result = await async_try(add_async)(1, 1).map(lambda x: x / 0).or_else(lambda: 1)
    print(result)

    class A:
        pass

    a_test: AsyncResult[..., float, ZeroDivisionError | ArithmeticError] = AsyncResult(
        test_22
    )(1, 1)

    a_test = a_test.on_error((ZeroDivisionError,))

    result = await a_test.execute()
