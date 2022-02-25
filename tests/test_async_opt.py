import asyncio

import pytest
from assertpy import assert_that

from seito.monad.async_opt import aopt


async def add_async(a, b):
    await asyncio.sleep(0.1)
    return a + b

async def async_none():
    await asyncio.sleep(0.1)
    return None

@pytest.mark.asyncio
async def test_async_opt():
    value = await aopt(add_async, 1, 1).or_else(4)
    assert_that(value).is_equal_to(2)

    value = await aopt(async_none).or_else(1)
    assert_that(value).is_equal_to(1)

    value = await aopt(add_async, 0, 0).or_if_falsy(1)
    assert_that(value).is_equal_to(1)

    value = await aopt(add_async, 1, 2).map(lambda x: x *2).get()
    assert_that(value).is_equal_to(6)

    value = await aopt(add_async, 1, 2).map(lambda x: x * 2).map(lambda x: x / 2).get()
    assert_that(value).is_equal_to(3)

    value = await aopt(async_none).map(lambda x: x * 2).map(lambda x: x / 2).or_else(1)
    assert_that(value).is_equal_to(1)

    async for _ in aopt(async_none):
        ...
    else:
        value = "Not passed"

    assert_that(value).is_equal_to("Not passed")


    async for val in aopt(add_async, 1, 2):
        value = val
    assert_that(value).is_equal_to(3)
