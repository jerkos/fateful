from typing import Any, List

try:
    import orjson as json
except ImportError:
    import json
from json.decoder import JSONDecodeError

from seito.monad.opt import none, Some, Empty, opt
from seito.monad.try_ import attempt_to


class JsObject(dict):
    def __init__(self, *args, **kwargs):
        super(JsObject, self).__init__(*args, **kwargs)

    def stringify(self, **kwargs: Any):
        return json.dumps(self, **kwargs)

    def __getitem__(self, item: str) -> Some[Any] | Empty:
        try:
            v = super(JsObject, self).__getitem__(item)
            return opt(v)
        except KeyError:
            return none

    def __getattr__(self, item: str) -> Some[Any] | Empty:
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def __str__(self):
        return json.dumps(self)


def js(*args, **kwargs):
    return JsObject(*args, **kwargs)


def parse(string: str | bytes | bytearray, *, response_class=None, **kwargs: Any):
    value = json.loads(string, **kwargs)
    is_list = isinstance(value, List)
    if response_class is None:
        if is_list:
            return [js(val) for val in value]
        return js(value)
    if is_list:
        return [response_class(**val) for val in value]
    return response_class(**value)


try_parse = attempt_to(errors=(JSONDecodeError,))(parse)
