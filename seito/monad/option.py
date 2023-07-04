import abc
import typing as t
from dataclasses import dataclass

from seito.monad.container import CommonContainer, EmptyError
from seito.monad.func import apply

T = t.TypeVar("T", covariant=True)
U = t.TypeVar("U")
V = t.TypeVar("V")
P = t.ParamSpec("P")


class OptionContainer(CommonContainer[T], t.Protocol):
    @abc.abstractmethod
    def is_some(self) -> bool:  # pragma: no cover
        ...

    @abc.abstractmethod
    def is_empty(self) -> bool:  # pragma: no cover
        ...

    @abc.abstractmethod
    def or_if_falsy(
        self, obj: t.Callable[P, t.Any] | t.Any, *args: P.args, **kwargs: P.kwargs
    ) -> t.Any:  # pragma: no cover
        """ """
        ...


Q = t.TypeVar("Q")
R = t.TypeVar("R")


Nested: t.TypeAlias = "Some[Q | Nested[Q]]"


@dataclass(unsafe_hash=True)
class Some(OptionContainer[T]):
    """ """

    _under: T

    def get(self) -> T:
        return self._under

    def is_some(self) -> bool:
        return True

    def is_empty(self) -> bool:
        return False

    @t.overload
    def flatten(self: "Nested[Q]") -> "Some[Q]":
        ...

    @t.overload
    def flatten(self: "Some[T]") -> "Some[T]":
        ...

    def flatten(self):
        x = self._under
        while isinstance(x, Some):
            x = t.cast(Some, x)
            x = x._under
        return Some(x)

    def or_(self, obj: t.Any) -> T:
        return self._under

    unwrap_or = or_

    def or_else(
        self, obj: t.Callable[P, t.Any], *args: P.args, **kwargs: P.kwargs
    ) -> T:
        return self._under

    unwrap_or_else = or_else

    def or_if_falsy(
        self, obj: t.Callable[P, U], *args: P.args, **kwargs: P.kwargs
    ) -> T | U:
        return self._under or apply(obj, *args, **kwargs)

    def or_none(self) -> T:
        return self._under

    def or_raise(self, exc: Exception | None = None) -> T:
        return self._under

    def map(self, func: t.Callable[[T], U]) -> "Some[U]":  # type: ignore
        result = apply(func, self._under)
        result = opt(result)
        return result

    def __iter__(self) -> t.Iterator[T]:
        yield self.flatten().get()

    def __getattr__(self, name: str) -> "Some | Empty | t.Callable":
        try:
            attr = getattr(self._under, name)
        except AttributeError:
            return none
        if callable(attr):

            def wrapper(*args: t.Any, **kwargs: t.Any) -> "Some[t.Any] | Empty":
                return opt(attr(*args, **kwargs))

            return wrapper
        return opt(attr)

    def __call__(self, *args: t.Any, **kwargs: t.Any):
        return self

    def __str__(self) -> str:
        return f"<Some {str(self._under)}>"


@dataclass(unsafe_hash=True)
class Empty(OptionContainer[None]):
    """ """

    _under: None = None

    def get(self) -> t.NoReturn:
        raise EmptyError("Option is empty")

    def is_some(self) -> bool:
        return False

    def is_empty(self) -> bool:
        return True

    def or_(self, obj: U) -> U:
        return obj

    def or_else(self, obj: t.Callable[P, U], *args: P.args, **kwargs: P.kwargs) -> U:
        return apply(obj, *args, **kwargs)

    unwrap_or = or_else

    def or_if_falsy(
        self, obj: t.Callable[P, U] | U, *args: P.args, **kwargs: P.kwargs
    ) -> U:
        return apply(obj, *args, **kwargs)

    def or_none(self) -> None:
        return None

    def or_raise(self, exc: Exception | None = None) -> t.NoReturn:
        if exc is None:
            raise EmptyError("Option is empty")
        raise exc

    def map(
        self,
        func: t.Callable,
    ) -> "Empty":
        return self

    def __iter__(self) -> "t.Iterator[Empty]":
        return self

    def __next__(self):
        raise StopIteration()

    def __getattr__(self, name: str) -> "Empty":
        return self

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "Empty":
        return self

    def __str__(self) -> str:
        return "<Empty>"


T_err = t.TypeVar("T_err", bound=Exception, covariant=True)

T_optional = t.TypeVar("T_optional", bound=Some | Empty)


# @t.overload
# def unravel_container(
#    value: T,  # not a some
#    last_container: T | None = None,
# ) -> tuple[T, T | None]:
#    ...


# @t.overload
# def unravel_container(
#    value: Some[Some[Some[U]]],
# ) -> tuple[U, Some[U]]:
#    ...


# @t.overload
# def unravel_container(
#    value: t.Any,
#    last_container: t.Any | None = None,
# ) -> tuple[t.Any, t.Any]:
#    ...


# @t.overload
# def unravel_container(
#    value: Some[Some[T]],
# ) -> Some[T]:
#    ...


def unravel_container(value):
    match value:
        case Some(under) | Empty(under):
            return unravel_container(under)
        case _:
            return value


OPT_MATCHABLE_CLASSES = {Some, Empty}
Some.__matchable_classes__ = OPT_MATCHABLE_CLASSES
Empty.__matchable_classes__ = OPT_MATCHABLE_CLASSES


T_opt = t.TypeVar("T_opt")


@t.overload
def option(value: None) -> Empty:
    ...


@t.overload
def option(value: T_opt) -> Some[T_opt]:
    ...


@t.overload
def option(value: Some[T_opt]) -> Some[Some[T_opt]]:
    ...


def option(value: T_opt) -> Some[T_opt] | Empty:
    """ """
    return Null if value is None else Some(value)


def lift_opt(f: t.Callable[P, U]) -> t.Callable[P, Some[U] | Empty]:
    """ """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Some[U] | Empty:
        val: U = f(*args, **kwargs)
        return opt(val)

    return wrapper


# aliases
none = nope = empty = Null = Empty(None)
opt = option
