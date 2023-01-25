import abc
from dataclasses import dataclass
from typing import Any, Callable, Iterator, NoReturn

from seito.monad.container import (
    T_wrapped_type,
    Func,
    unravel_container,
    EmptyError,
    CommonContainer,
)
from seito.monad.func import apply


class OptionContainer(CommonContainer[T_wrapped_type], abc.ABC):
    @abc.abstractmethod
    def is_some(self) -> bool:  # pragma: no cover
        ...

    @abc.abstractmethod
    def is_empty(self) -> bool:  # pragma: no cover
        ...

    @abc.abstractmethod
    def or_if_falsy(self, obj: Func | Any, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """ """
        ...


@dataclass(unsafe_hash=True)
class Some(OptionContainer[T_wrapped_type]):
    """ """

    _under: T_wrapped_type

    def get(self) -> T_wrapped_type:
        return self._under

    def is_some(self) -> bool:
        return True

    def is_empty(self) -> bool:
        return False

    def or_else(self, obj: Func, *args: Any, **kwargs: Any) -> T_wrapped_type:
        return self._under

    def or_if_falsy(self, obj: Func, *args: Any, **kwargs: Any) -> T_wrapped_type | Any:
        return self._under or apply(obj, *args, **kwargs)

    def or_none(self) -> T_wrapped_type:
        return self._under

    def or_raise(self, exc: Exception | None = None) -> T_wrapped_type:
        return self._under

    def map(self, func: Callable[[T_wrapped_type], Any]) -> OptionContainer[Any]:
        value, _ = unravel_container(self)
        return opt(apply(func, value))

    def __iter__(self) -> Iterator[T_wrapped_type]:
        val, _ = unravel_container(self)
        yield val

    def __getattr__(self, name: str) -> "OptionContainer[Any] | Any":
        try:
            attr = getattr(self._under, name)
        except AttributeError:
            return none
        if callable(attr):

            def wrapper(*args: Any, **kwargs: Any) -> "OptionContainer[Any | None]":
                return opt(attr(*args, **kwargs))

            return wrapper
        return opt(attr)

    def __call__(self, *args: Any, **kwargs: Any) -> "Some[T_wrapped_type]":
        return self

    def __str__(self) -> str:
        return f"<Some {str(self._under)}>"


@dataclass(unsafe_hash=True)
class Empty(OptionContainer[None]):
    """ """

    _under: None = None

    def get(self) -> NoReturn:
        raise EmptyError("Option is empty")

    def is_some(self) -> bool:
        return False

    def is_empty(self) -> bool:
        return True

    def or_else(self, obj: Callable[..., Any] | Any, *args: Any, **kwargs: Any) -> Any:
        return apply(obj, *args, **kwargs)

    def or_if_falsy(self, obj: Callable[..., Any] | Any, *args, **kwargs) -> Any:
        return apply(obj, *args, **kwargs)

    def or_none(self) -> None:
        return None

    def or_raise(self, exc: Exception | None = None) -> NoReturn:
        if exc is None:
            raise ValueError("Empty value !")
        raise exc

    def map(self, func) -> "Empty":
        return self

    def __iter__(self) -> "Iterator[Empty]":
        return self

    def __next__(self):
        raise StopIteration()

    def __getattr__(self, name: str) -> "Empty":
        return self

    def __call__(self, *args: Any, **kwargs: Any) -> "Empty":
        return self

    def __str__(self) -> str:
        return "<Empty>"


OPT_MATCHABLE_CLASSES = {Some, Empty}
Some.__matchable_classes__ = OPT_MATCHABLE_CLASSES
Empty.__matchable_classes__ = OPT_MATCHABLE_CLASSES


def option(value: Any) -> OptionContainer[Any | None]:
    """ """
    new_val, _ = unravel_container(value)
    return none if new_val is None else Some(new_val)


def lift_opt(f):
    """ """

    def wrapper(*args, **kwargs):
        return opt(f(*args, **kwargs))

    return wrapper


# aliases
none = nope = empty = Empty()
opt = option
