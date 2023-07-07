import logging
from enum import Enum
from functools import partial
from json import JSONDecodeError
from typing import Any, Type

from aiohttp import ClientError, ClientSession

from seito.json import JsArray, JsObject, try_parse
from seito.monad.async_result import async_try
from seito.monad.result import Err, Ok


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
) -> Ok[str | JsArray | JsObject | Any] | Err[
    NetworkError | ClientError | JSONDecodeError | Exception
]:
    """
    Generic method for making a request
    """
    try:
        async with session.request(method.value, url, **kwargs) as resp:
            try:
                content_type = resp.headers.getall(ContentType.value)
                is_json = ContentType.APPLICATION_JSON in content_type
                resp_as_text = await resp.text()
                if resp.status >= 400:
                    return Err(HttpException(resp.status, resp_as_text))
                if is_json:
                    return try_parse(resp_as_text, response_class=response_class)
                return Ok(resp_as_text)
            except ClientError as e:  # pragma: no cover
                logging.error(e)
                return Err(e)
    except ClientError as e:
        logging.exception(e)
        return Err(e)


get = partial(request, HttpMethods.GET)


def try_get(url, **kwargs):
    return async_try(get)(url, **kwargs)


post = partial(request, HttpMethods.POST)


def try_post(url, **kwargs):  # pragma: no cover
    return async_try(post)(url, **kwargs)


put = partial(request, HttpMethods.PUT)


def try_put(url, **kwargs):  # pragma: no cover
    return async_try(put)(url, **kwargs)


delete = partial(request, HttpMethods.DELETE)


def try_delete(url, **kwargs):  # pragma: no cover
    return async_try(delete)(url, **kwargs)


patch = partial(request, HttpMethods.PATCH)


def try_patch(url, **kwargs):  # pragma: no cover
    return async_try(patch)(url, **kwargs)


options = partial(request, HttpMethods.OPTIONS)


def try_options(url, **kwargs):  # pragma: no cover
    return async_try(options)(url, **kwargs)
