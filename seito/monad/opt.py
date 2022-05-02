from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, TypeVar, Generic, Callable, NoReturn

import pampy
from aflowey import lift
from pampy.pampy import match_dict as pampy_dict_matcher

from seito.monad.func import identity


class EmptyError(ValueError):
    ...


class MatchError(TypeError):
    ...


def apply(f: Callable[..., Any] | Any = identity, *args: Any, **kwargs: Any) -> Any:
    if callable(f):
        return f(*args, **kwargs)
    return f


_ = pampy._


class When:
    def __init__(self, value):
        self.value = value
        self.action = None

    def then(self, f):
        self.action = f
        return self

    def __repr__(self):
        return repr(self.value)


when = When


@dataclass
class Default:
    def __init__(self):
        self.action = None

    def __rshift__(self, other) -> "Default":
        self.action = other
        return self


default = Default


class Option(ABC):
    @abstractmethod
    def get(self) -> Any:
        ...  # pragma: no cover

    @abstractmethod
    def is_empty(self) -> bool:
        ...  # pragma: no cover

    @abstractmethod
    def or_else(self, obj: Callable[..., Any] | Any, *args: Any, **kwargs: Any) -> Any:
        ...  # pragma: no cover

    @abstractmethod
    def or_if_falsy(
        self, obj: Callable[..., Any] | Any, *args: Any, **kwargs: Any
    ) -> Any:
        ...  # pragma: no cover

    @abstractmethod
    def or_none(self) -> Any:
        ...  # pragma: no cover

    @abstractmethod
    def or_raise(self, exc: Exception | None = None):
        ...  # pragma: no cover

    @abstractmethod
    def map(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> "Option":
        ...  # pragma: no cover

    @abstractmethod
    def __iter__(self):
        ...  # pragma: no cover

    @abstractmethod
    def __getattr__(self, name: str) -> Any:
        ...  # pragma: no cover

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any):
        ...  # pragma: no cover

    @abstractmethod
    def __str__(self) -> str:
        ...  # pragma: no cover

    def __rshift__(self, other) -> When:
        return when(self).then(other)

    def match(self, *whens: When | Default):
        for w in whens:
            if isinstance(w, when):
                if w.value.__class__ == self.__class__:
                    match_dict, self_dict = w.value.__dict__, self.__dict__
                    is_a_match, extracted = pampy_dict_matcher(match_dict, self_dict)
                    if not is_a_match:
                        continue
                    if extracted:
                        return apply(w.action, *extracted)
                    return apply(w.action)
            else:
                return apply(w.action)
        raise MatchError(f"No default guard found, enable to match {self}")


T = TypeVar("T")
M = TypeVar("M")


@dataclass
class Some(Generic[T], Option):
    _under: T

    def get(self) -> T:
        return self._under

    def is_empty(self) -> bool:
        return False

    def or_else(self, obj: Callable[..., Any], *args: Any, **kwargs: Any) -> T:
        return self._under

    def or_if_falsy(
        self, obj: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> T | Any:
        return self._under or apply(obj, *args, **kwargs)

    def or_none(self) -> T:
        return self._under

    def or_raise(self, exc: Exception | None = None) -> T:
        return self._under

    def map(
        self, f: Callable[[T, ...], M], *args: Any, **kwargs: Any
    ) -> "Some[M] | Empty":
        inst = self
        while isinstance(inst._under, Option):
            inst = inst._under
        return opt(apply(f, inst._under, *args, **kwargs))

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
                return opt(attr(*args, **kwargs))

            return wrapper
        return opt(attr)

    def __call__(self, *args: Any, **kwargs: Any) -> "Some[T]":
        return self

    def __str__(self) -> str:
        return f"<Some {str(self._under)}>"


@dataclass
class Empty(Option):
    _under = None

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

    def or_raise(self, exc: Exception | None = None) -> NoReturn:
        if exc is None:
            raise ValueError("Empty value !")
        raise exc

    def map(self, func, *args, **kwargs) -> "Empty":
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
        return "<Empty >"


E = TypeVar("E", bound=Exception)


@dataclass
class Err(Empty, Generic[E]):
    _under: E

    def __str__(self):
        return f"<Err {repr(self._under)} >"

    def unwrap(self):
        return self._under

    recover_with = Empty.or_else

    def or_raise(self, exc: Exception | None = None) -> NoReturn:
        if exc is not None:
            raise exc from self._under
        raise self._under


def unravel_opt(value):
    if not isinstance(value, Option):
        return value
    inst = value._under
    while isinstance(inst, Option):  # pragma: no cover
        inst = inst._under
    return inst


def option(value: Any) -> Some[Any] | Empty:
    if isinstance(value, Exception):
        return Err(value)
    new_val = unravel_opt(value)
    return none if new_val is None else Some(new_val)


def opt_from_call(f, *args, **kwargs):
    exc = kwargs.pop("exc", Exception)
    try:
        return opt(f(*args, **kwargs))
    except exc:
        return Err(exc)


def lift_opt(f):
    return lift(f, opt_from_call)


# aliases
none = nope = empty = Empty()
opt = option
err = Err
