from enum import Enum
from functools import partial
from typing import Type, Any, Dict

from aiohttp import ClientSession, ClientError
from loguru import logger

from seito.json import try_parse
from seito.monad.async_opt import aopt
from seito.monad.opt import Err, Some


class HttpMethods(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"


class ContentType:
    value = "Content-Type"
    APPLICATION_JSON = "application/json"


class NetworkError(Exception):
    ...


class HttpException(NetworkError):
    def __init__(self, code: int, detail: str):
        self.code = code
        self.detail = detail


class NetworkException(NetworkError):
    ...


async def request(
    method: HttpMethods,
    url,
    /,
    *,
    session: ClientSession,
    response_class: Type[Any] | None = None,
    **kwargs: Any,
) -> Some[str | Dict[str, Any]] | Err[NetworkError | ClientError]:
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
                return Some(resp_as_text)
            except ClientError as e:  # pragma: no cover
                logger.error(e)
                return Err(e)
    except ClientError as e:
        logger.exception(e)
        return Err(e)


get = partial(request, HttpMethods.GET)
get_opt = lambda url, **kwargs: aopt(get, url, **kwargs)

post = partial(request, HttpMethods.POST)
post_opt = lambda url, **kwargs: aopt(post, url, **kwargs)

put = partial(request, HttpMethods.PUT)
put_opt = lambda url, **kwargs: aopt(put, url, **kwargs)

delete = partial(request, HttpMethods.DELETE)
delete_opt = lambda url, **kwargs: aopt(delete, url, **kwargs)

patch = partial(request, HttpMethods.PATCH)
patch_opt = lambda url, **kwargs: aopt(patch, url, **kwargs)

options = partial(request, HttpMethods.OPTIONS)
options_opt = lambda url, **kwargs: aopt(options, url, **kwargs)
