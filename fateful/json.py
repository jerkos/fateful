import typing as t

from fateful.container import opt_dict, opt_list
from fateful.monad.result import sync_try

try:
    import orjson as json  # type: ignore
except ImportError:
    import json  # type: ignore

from json.decoder import JSONDecodeError

js_object: t.TypeAlias = opt_dict[str, t.Any | "js_array"]

js_array: t.TypeAlias = opt_list[js_object | t.Any | "js_array"]


T = t.TypeVar("T")


def parse(
    string: str | bytes | bytearray,
    *,
    object_hook: type[T] | None = None,
    **kwargs: t.Any,
) -> js_array | js_object | list[T] | T:
    """Parse a JSON string into a JsObject or JsArray or
    a sequence of arbitrary objects."""
    value = json.loads(string, **kwargs)
    is_list = isinstance(value, t.Sequence)
    if object_hook is None:
        if is_list:
            return js_array(value)
        return js_object(value)
    if is_list:
        return [object_hook(**val) for val in value]
    return object_hook(**value)


try_parse = sync_try(parse, exc=JSONDecodeError)
