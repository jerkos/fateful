try:
    import orjson as json
except ImportError:
    import json
import collections
from json.decoder import JSONDecodeError

from seito.option import none, option, Option
from seito.seq import Seq
from seito.maybe import attempt_dec


class JsObject(dict):
    def __init__(self, *args):
        super(JsObject, self).__init__(*args)

    def stringify(self, **kwargs):
        return json.dumps(self, **kwargs)

    def __getitem__(self, item: str) -> Option:
        try:
            v = super(JsObject, self).__getitem__(item)
            if isinstance(v, collections.abc.Iterable):
                return option(Seq(v))
            return option(v)
        except KeyError:
            return none

    def __getattr__(self, item: str) -> Option:
        try:
            # call get item
            return self[item]
        except KeyError:
            return none

    def __setattr__(self, key, value):
        self[key] = value


def obj(*args):
    return JsObject(*args)


def parse(string, *args, **kwargs):
    assert(type(string) in {str, bytes, bytearray})
    return JsObject(json.loads(string, *args, **kwargs))


def parse_as(string, /, response_class=None, **kwargs):
    assert(type(string) in {str, bytes, bytearray})
    if response_class is None:
        return JsObject(json.loads(string, **kwargs))
    value = json.loads(string, **kwargs)
    if isinstance(value, collections.abc.Iterable):
        return [response_class(**subval) for subval in value]
    return value

tryify = lambda func, as_opt: attempt_dec(
    errors=(JSONDecodeError,), as_opt=as_opt
)(func)

try_parse = tryify(parse, False)
try_parse_opt = tryify(parse, True)

try_parse_as = tryify(parse_as, False)
try_parse_as_opt = tryify(parse_as, True)
