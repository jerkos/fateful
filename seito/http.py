from enum import Enum
from functools import partial
from json import JSONDecodeError
from typing import Type, Any

from aiohttp import ClientSession, ClientError
from loguru import logger

from seito.json import try_parse, JsArray, JsObject
from seito.monad.async_try import async_try
from seito.monad.container import Err, Result


class HttpMethods(str, Enum):
    """ """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"


class ContentType:
    """ """

    value = "Content-Type"
    APPLICATION_JSON = "application/json"


class NetworkError(Exception):
    """ """

    ...


class HttpException(NetworkError):
    """ """

    def __init__(self, code: int, detail: str):
        self.code = code
        self.detail = detail


class NetworkException(NetworkError):
    """ """

    ...


async def request(
    method: HttpMethods,
    url,
    /,
    *,
    session: ClientSession,
    response_class: Type[Any] | None = None,
    **kwargs: Any,
) -> Result[str | dict[str, Any] | JsArray | JsObject] | Err[
    NetworkError | ClientError | JSONDecodeError
]:
    """
    Generic method for making a request
    """
    try:
        async with session.request(method.value, url, **kwargs) as resp:
            try:
                content_type = resp.headers.get(ContentType.value)
                is_json = ContentType.APPLICATION_JSON in content_type
                resp_as_text = await resp.text()
                if resp.status >= 400:
                    return Err(HttpException(resp.status, resp_as_text))
                if is_json:
                    return try_parse(resp_as_text, response_class=response_class)
                return Result(resp_as_text)
            except ClientError as e:  # pragma: no cover
                logger.error(e)
                return Err(e)
    except ClientError as e:
        logger.exception(e)
        return Err(e)


get = partial(request, HttpMethods.GET)
try_get = lambda url, **kwargs: async_try(get, url, **kwargs)

post = partial(request, HttpMethods.POST)
try_post = lambda url, **kwargs: async_try(post, url, **kwargs)

put = partial(request, HttpMethods.PUT)
try_put = lambda url, **kwargs: async_try(put, url, **kwargs)

delete = partial(request, HttpMethods.DELETE)
try_delete = lambda url, **kwargs: async_try(delete, url, **kwargs)

patch = partial(request, HttpMethods.PATCH)
try_patch = lambda url, **kwargs: async_try(patch, url, **kwargs)

options = partial(request, HttpMethods.OPTIONS)
try_options = lambda url, **kwargs: async_try(options, url, **kwargs)
