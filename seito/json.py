import typing
from typing import Any, Mapping, Type

from seito.monad.option import Empty, Some, none, opt
from seito.monad.result import sync_try

try:
    import orjson as json  # type: ignore
except ImportError:
    import json  # type: ignore

from json.decoder import JSONDecodeError


class JsArray(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @typing.overload
    def __getitem__(self, index: typing.SupportsIndex) -> Any:  # pragma: no cover
        ...

    @typing.overload
    def __getitem__(self, index: slice) -> list:  # pragma: no cover
        ...

    def __getitem__(self, index):
        item = super().__getitem__(index)
        if isinstance(item, Mapping):
            return JsObject(**item)
        return item


class JsObject(dict):
    """ """

    def __init__(self, *args, **kwargs):
        super(JsObject, self).__init__(*args, **kwargs)

    def stringify(self, **kwargs: Any):
        return json.dumps(self, **kwargs)

    def map_to(self, clazz: Type):
        """expected a dataclass or a basemodel"""
        return clazz(**self)

    def __getitem__(self, item: str) -> Some | Empty:
        try:
            v = super(JsObject, self).__getitem__(item)
            return opt(v)
        except KeyError:
            return none

    def __getattr__(self, item: str) -> Some | Empty:
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def __str__(self):
        return json.dumps(self)


def js(*args, **kwargs):
    """ """
    return JsObject(*args, **kwargs)


def parse(string: str | bytes | bytearray, *, response_class=None, **kwargs: Any):
    """ """
    value = json.loads(string, **kwargs)
    is_list = isinstance(value, list)
    if response_class is None:
        if is_list:
            return JsArray(value)
        return JsObject(value)
    if is_list:
        return [response_class(**val) for val in value]
    return response_class(**value)


try_parse = sync_try(parse, exc=(JSONDecodeError,))
