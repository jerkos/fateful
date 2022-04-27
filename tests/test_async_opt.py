import asyncio

import pytest
from assertpy import assert_that
from loguru import logger

from seito.monad.async_opt import aopt
from seito.monad.func import identity
from seito.monad.opt import when, Some, _, default, opt


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


@pytest.mark.asyncio
async def test_async_opt():
    value = await aopt(add_async, 1, 1).or_else(4)
    assert_that(value).is_equal_to(2)

    value = await aopt(async_none).or_else(1)
    assert_that(value).is_equal_to(1)

    value = await aopt(add_async, 0, 0).or_if_falsy(1)
    assert_that(value).is_equal_to(1)

    value = await aopt(add_async, 1, 2).map(lambda x: x * 2).get()
    assert_that(value).is_equal_to(6)

    value = await aopt(add_async, 1, 2).map(lambda x: x * 2).map(lambda x: x / 2).get()
    assert_that(value).is_equal_to(3)

    value = await aopt(async_none).map(lambda x: x * 2).map(lambda x: x / 2).or_else(1)
    assert_that(value).is_equal_to(1)

    async for __ in aopt(async_none):
        ...
    else:
        value = "Not passed"

    assert_that(value).is_equal_to("Not passed")

    async for val in aopt(add_async, 1, 2):
        value = val
    assert_that(value).is_equal_to(3)

    value = (
        await aopt(add_async, 1, 2)
        .map(lambda x: x * 2)
        .map(lambda x: x / 2)
        .match(when(Some(_)).then(identity), default() >> 1)
    )
    assert_that(value).is_equal_to(3)

    assert_that(await aopt(add_async, 1, 2).is_empty()).is_false()

    assert_that(await aopt(add_async, 1, 2).or_raise(ValueError())).is_equal_to(3)

    str(aopt(add_async, 1, 2))

    assert_that(await aopt(async_raise).or_else(1)).is_equal_to(1)

    assert_that(await aopt(async_raise).or_none()).is_none()

    assert_that(await aopt(async_raise)()).is_not_none()

    assert_that(
        await aopt(async_identity, 1).map(lambda x: x / 0).or_else(1)
    ).is_equal_to(1)

    async for val in aopt(async_identity, 1):
        logger.debug(val)

    assert_that(await aopt(async_raise).or_else(lambda: 1)).is_equal_to(1)

    assert_that(await aopt(async_raise).or_else(add_async, 1, 2)).is_equal_to(3)

    assert_that(await aopt(async_opt).get()).is_equal_to(1)
