import aiohttp
import pytest
from assertpy import assert_that
from loguru import logger

from seito.http import request, HttpMethods, get, get_opt
from seito.monad.async_opt import aopt
from seito.monad.func import identity
from seito.monad.opt import Some, _, default, Err


@pytest.mark.asyncio
async def test_request():
    session = aiohttp.ClientSession()
    result = await request(HttpMethods.GET, "https://google.com", session=session)
    value = result.match(Some(_) >> identity, default() >> None)
    assert_that(value).is_not_none()

    result = await aopt(
        request, HttpMethods.GET, "https://google.com", session=session
    ).get()
    await session.close()


@pytest.mark.asyncio
async def test_request_2():
    async with aiohttp.ClientSession() as session:
        result = await get("https://google.com", session=session)
        value = result.match(Some(_) >> identity, default() >> None)
        assert_that(value).is_not_none()

        result = await get_opt("https://google.com", session=session).get()
        assert_that(result).is_not_none()


@pytest.mark.asyncio
async def test_request_json():
    session = aiohttp.ClientSession()
    result = await get("https://jsonplaceholder.typicode.com/todos/1", session=session)
    assert_that(result).is_not_none()
    await session.close()


@pytest.mark.asyncio
async def test_request_client_connect_error():
    session = aiohttp.ClientSession()
    result = await get("https://jsonplaceholde.typicode.com/todos/0", session=session)
    assert_that(result).is_instance_of(Err)
    await session.close()


@pytest.mark.asyncio
async def test_request_fetch_error():
    session = aiohttp.ClientSession()
    result = await get("https://jsonplaceholder.typicode.com/todos/0", session=session)
    assert_that(result).is_instance_of(Err)
    await session.close()
