import logging
import typing as t
from enum import Enum
from functools import partial
from json import JSONDecodeError
try:
    from aiohttp import ClientError, ClientSession
    from yarl import URL
except ImportError:
    logging.warning("aiohttp and yarl are not installed")
    raise

from fateful.json import js_array, js_object, try_parse
from fateful.monad.async_result import async_try
from fateful.monad.result import Err, Ok


class HttpMethods(str, Enum):
    """A list of basic HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"


class ContentType:
    """Content-Type header values."""

    value = "Content-Type"
    APPLICATION_JSON = "application/json"


T = t.TypeVar("T")


async def request(
    method: HttpMethods,
    url: str | URL,
    /,
    *,
    session: ClientSession,
    object_hook: type[T] | None = None,
    **kwargs: t.Any,
) -> Ok[str | js_array | js_object | T | list[T]] | Err[ClientError | JSONDecodeError]:
    """
    Generic method for making a request
    """
    try:
        async with session.request(method.value, url, **kwargs) as resp:
            try:
                content_type = resp.headers.getall(ContentType.value)
                is_json = ContentType.APPLICATION_JSON in content_type
                resp.raise_for_status()
                resp_as_text = await resp.text()
                if is_json:
                    return try_parse(resp_as_text, object_hook=object_hook)
                return Ok(resp_as_text)
            except ClientError as e:  # pragma: no cover
                logging.error(e)
                return Err(e)
    except ClientError as e:
        logging.exception(e)
        return Err(e)


get = partial(request, HttpMethods.GET)


def try_get(url: str | URL, **kwargs):
    """
    return an async try of get

    Args:
        url: url to get

    Returns:
        : async try
    """
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
