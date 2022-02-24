from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Callable, NoReturn

from seito.monad.func import identity


class EmptyError(ValueError):
    ...


def apply(f: Callable[..., Any] | Any = identity, *args: Any, **kwargs: Any) -> Any:
    if callable(f):
        return f(*args, **kwargs)
    return f


class Option(ABC):
    @abstractmethod
    def get(self) -> Any:
        ...

    @abstractmethod
    def is_empty(self) -> bool:
        ...

    @abstractmethod
    def or_else(self, obj: Callable[..., Any] | Any, *args: Any, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def or_if_falsy(self, obj: Callable[..., Any] | Any, *args: Any, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def or_none(self) -> Any:
        ...

    @abstractmethod
    def map(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> "Option":
        ...

    @abstractmethod
    def flat_map(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> "Option":
        ...

    @abstractmethod
    def __iter__(self):
        ...

    @abstractmethod
    def __getattr__(self, name: str) -> Any:
        ...

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any):
        ...

    @abstractmethod
    def __str__(self) -> str:
        ...


T = TypeVar("T")
M = TypeVar("M")


class Some(Generic[T], Option):

    def __init__(self, obj: T) -> None:
        self._under = obj

    def get(self) -> T:
        return self._under

    def is_empty(self) -> bool:
        return False

    def or_else(self, obj: Callable[..., Any], *args: Any, **kwargs: Any) -> T:
        return self._under

    def or_if_falsy(self, obj: Callable[..., Any], *args: Any, **kwargs: Any) -> T | Any:
        return self._under or apply(obj, *args, **kwargs)

    def or_none(self) -> T:
        return self._under

    def map(self, f: Callable[[T, ...], M], *args: Any, **kwargs: Any) -> "Some[M] | Empty":
        return opt(apply(f, self._under, *args, **kwargs))

    def flat_map(self, f: Callable[[T, ...], M], *args: Any, **kwargs: Any) -> "Some[M] | Empty":
        inst = self
        while isinstance(inst._under, Option):
            inst = inst._under
        return inst.map(f, *args, **kwargs)

    def __iter__(self):
        under = self._under
        while under is not None:
            if isinstance(under, Option):
                under = under._under
            else:
                yield under
                under = None

    def __getattr__(self, name: str) -> "Some[Any] | Empty | Callable[..., Any]":
        try:
            attr = getattr(self._under, name)
        except AttributeError:
            return none
        if callable(attr):
            def wrapper(*args: Any, **kwargs: Any) -> "Some | Empty":
                return option(attr(*args, **kwargs))

            return wrapper
        return opt(attr)

    def __call__(self, *args: Any, **kwargs: Any) -> "Some[T]":
        return self

    def __str__(self) -> str:
        return f"<Some {str(self._under)} >"


class Empty(Option):

    def get(self) -> NoReturn:
        raise EmptyError("Option is empty")

    def is_empty(self) -> bool:
        return True

    def or_else(self, obj: Callable[..., M] | M, *args: Any, **kwargs: Any) -> M:
        return apply(obj, *args, **kwargs)

    def or_if_falsy(self, obj: Callable[..., M] | M, *args, **kwargs) -> M:
        return apply(obj, *args, **kwargs)

    def or_none(self) -> None:
        return None

    def map(self, func, *args, **kwargs) -> "Empty":
        return self

    def flat_map(self, func, *args, **kwargs) -> "Empty":
        return self

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration()

    def __getattr__(self, name: str) -> "Empty":
        return self

    def __call__(self, *args: Any, **kwargs: Any) -> "Empty":
        return self

    def __str__(self) -> str:
        return "<Empty>"


def option(value: Any) -> Some[Any] | Empty:
    return none if value is None else Some(value)

def opt_from_call(f, *args, **kwargs):
    exc = kwargs.pop("exc", Exception)
    try:
        return option(f(*args, **kwargs))
    except exc:
        return none

# aliases
none = nope = Empty()
opt = option
