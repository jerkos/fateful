from enum import Enum
from typing import Type, Any

from aiohttp import ClientSession

from seito.json import try_parse_as, try_parse
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
    response_class: Type[Any] | None,
    **kwargs: Any,
) -> Some | Err[NetworkError]:
    try:
        async with session.request(method.value, url, **kwargs) as resp:
            content_type = resp.headers.get(ContentType.value)
            is_json = content_type == ContentType.APPLICATION_JSON
            resp_as_text = await resp.text()
            if resp.status >= 400:
                return Err(HttpException(400, resp_as_text))
            if is_json:
                if response_class is not None:
                    return try_parse_as(resp_as_text)
                else:
                    return try_parse(resp_as_text)
            return Some(resp_as_text)
    except:
        return Err(NetworkError())
