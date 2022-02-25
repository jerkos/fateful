import aiohttp
import pytest
from assertpy import assert_that
from loguru import logger

from seito.http import request, HttpMethods
from seito.monad.async_opt import aopt
from seito.monad.func import identity
from seito.monad.opt import Some, _, default


@pytest.mark.asyncio
async def test_request():
    session = aiohttp.ClientSession()
    result = await request(HttpMethods.GET, "https://google.com", session=session)
    value = result.match(
        Some(_) >> identity,
        default() >> None
    )
    assert_that(value).is_not_none()

    result = await aopt(request, HttpMethods.GET, "https://google.com", session=session).get()