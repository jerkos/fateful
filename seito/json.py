from collections.abc import Iterable
from typing import Any

try:
    import orjson as json
except ImportError:
    import json
import collections
from json.decoder import JSONDecodeError

from seito.monad.opt import none, Some, Empty, opt
from seito.monad.try_ import attempt_dec


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
        try:
            # call get item
            return opt(self[item])
        except KeyError:
            return none

    def __setattr__(self, key, value):
        self[key] = value

    def __str__(self):
        return json.dumps(self)


def js(*args, **kwargs):
    return JsObject(*args, **kwargs)


def parse(string: str | bytes | bytearray, *args: Any, **kwargs: Any):
    return JsObject(json.loads(string, *args, **kwargs))


def parse_as(string: str | bytes | bytearray, /, *, response_class=None, **kwargs: Any):
    if response_class is None:
        return JsObject(json.loads(string, **kwargs))
    value = json.loads(string, **kwargs)
    if isinstance(value, Iterable):
        return [response_class(**subval) for subval in value]
    return value


tryify = lambda func, as_opt: attempt_dec(errors=(JSONDecodeError,), as_opt=as_opt)(
    func
)

try_parse = tryify(parse, False)
try_parse_opt = tryify(parse, True)

try_parse_as = tryify(parse_as, False)
try_parse_as_opt = tryify(parse_as, True)
