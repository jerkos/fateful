import typing as t
from collections.abc import Iterator

from fateful.monad.option import Empty, Some, none

try:
    import orjson as json  # type: ignore
except ImportError:
    import json  # type: ignore


class _ConverterProtocol(t.Protocol):
    def _convert(
        self,
        value: t.Any,
    ) -> t.Any:
        if isinstance(value, t.Mapping):
            return opt_dict({k: self._convert(v) for k, v in value.items()})
        elif isinstance(value, t.Sequence) and not isinstance(value, str):
            return opt_list([self._convert(value) for value in value])
        else:
            return value


T = t.TypeVar("T")


class opt_list(list[T], _ConverterProtocol):
    """
    Immutable wrapper around a list that converts all dicts to JsObjects and
    all lists to JsArrays.

    Args:
        list (_type_): _description_

    ```python
    x = opt_list([1,2,3])
    v: Some[int] = x.at(0)
    z: Empty = x.at(12)
    ```
    """

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        for i in range(len(self)):
            self[i] = self._convert(self[i])

    def at(self, index: int) -> Some[T] | Empty:
        try:
            item = super().__getitem__(index)
        except IndexError:
            return none
        else:
            return Some(self._convert(item))

    def __iter__(self) -> Iterator[T]:
        for item in super().__iter__():
            yield self._convert(item)

    def __str__(self) -> str:
        return f"<opt_list {super().__str__()} >"


K = t.TypeVar("K")
V = t.TypeVar("V")


class opt_dict(dict[K, V], _ConverterProtocol):
    """ """

    def __init__(self, *args: t.Any, **kwargs: t.Any):
        super().__init__(*args, **kwargs)
        for k, v in self.items():
            self[k] = self._convert(v)

    def stringify(self, *args: t.Any, **kwargs: t.Any) -> str:
        r: str | bytes = json.dumps(self, *args, **kwargs)
        if isinstance(r, bytes):
            return r.decode("utf-8")
        return r

    def map_to(self, clazz: type[T]) -> T:
        """expected a dataclass or a pydantic basemodel"""
        return clazz(**self)

    def maybe(self, item: K) -> Some[V] | Empty:
        try:
            value = super().__getitem__(item)
        except KeyError:
            return none
        else:
            return Some(self._convert(value))

    def __getattr__(self, item: str) -> Some[V] | Empty:
        return self.maybe(t.cast(K, item))

    def __setattr__(self, key: str, value: V) -> None:
        self[t.cast(K, key)] = value

    def __str__(self) -> str:
        return f"<opt_dict {super().__str__()} >"
