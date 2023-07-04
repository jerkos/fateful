import abc
import typing as t
from dataclasses import dataclass

from seito.monad.container import CommonContainer
from seito.monad.func import apply

if t.TYPE_CHECKING:
    from seito.try_ import Try  # noqa: F401

T = t.TypeVar("T", covariant=True)
U = t.TypeVar("U")
P = t.ParamSpec("P")
E = t.TypeVar("E", bound=Exception)


class ResultContainer(CommonContainer[T], t.Protocol):
    @abc.abstractmethod
    def is_ok(self) -> bool:  # pragma: no cover
        ...

    @abc.abstractmethod
    def is_error(self) -> bool:  # pragma: no cover
        ...

    @abc.abstractmethod
    def recover(
        self, obj: t.Callable[P, U] | U, *args: P.args, **kwargs: P.kwargs
    ) -> U:  # pragma: no cover
        ...


@dataclass(unsafe_hash=True)
class Ok(ResultContainer[T]):
    _under: T

    def is_error(self) -> bool:
        return False

    def is_ok(self) -> bool:
        return True

    def or_none(self) -> T | None:
        return self._under

    def get(self) -> T | None:
        return self._under

    def or_(self, obj: t.Any) -> T | None:
        return self._under

    def or_else(
        self, obj: t.Callable[P, t.Any], *args: P.args, **kwargs: P.kwargs
    ) -> T | None:
        return self._under

    unwrap_or = or_else

    def or_raise(self, exc: Exception | None = None) -> T | None:
        return self._under

    def recover(
        self: "Ok[T]",
        obj: t.Callable[P, U] | U,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Ok[T]":
        return self

    def map(self, fn: t.Callable[[T], U]) -> "Ok[U] | Err[Exception]":
        from seito.try_ import Try  # noqa: F811

        return Try.of(fn)(self._under)

    def __iter__(self) -> "t.Iterator[T]":
        val, _ = unravel_container(self)
        yield val

    def __getattr__(
        self, name: str
    ) -> "Ok[T] | Err[AttributeError] | t.Callable[..., t.Any]":
        try:
            attr = getattr(self._under, name)
        except AttributeError as e:
            return Err(e)
        if callable(attr):

            def wrapper(
                *args: P.args, **kwargs: P.kwargs
            ) -> "Ok[t.Any] | Err[Exception]":
                from seito.try_ import Try  # noqa: F811

                return Try.of(attr)(*args, **kwargs)

            return wrapper

        return Ok(attr)

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "Ok[T]":
        return self

    def __str__(self):
        return f"<Ok {repr(self._under)}>"


T_error_co = t.TypeVar("T_error_co", bound=Exception)
T_error = t.TypeVar("T_error", bound=Exception)


@dataclass(unsafe_hash=True)
class Err(ResultContainer[T_error_co]):
    """ """

    _under: T_error_co

    def __post_init__(self):
        if not issubclass(self._under.__class__, Exception):
            raise ValueError("Err should carry an exception class")

    def unwrap(self) -> T_error_co:
        return self._under

    def recover(
        self, obj: t.Callable[P, U] | U, *args: P.args, **kwargs: P.kwargs
    ) -> Ok[U]:
        return Ok(apply(obj, *args, **kwargs))

    def is_error(self):
        return True

    def is_ok(self):
        return False

    def get(self) -> t.NoReturn:
        raise self._under

    def or_(self, obj: U) -> U:
        return obj

    def or_else(self, obj: t.Callable[P, U], *args: P.args, **kwargs: P.kwargs) -> U:
        return apply(obj, *args, **kwargs)

    unwrap_or = or_else

    def or_raise(self, exc: Exception | None = None) -> t.NoReturn:
        if exc is not None:
            raise exc from self._under
        raise self._under

    def or_none(self):
        return None

    def map(self, func: t.Callable[[t.Any], t.Any]) -> "Err[T_error_co]":
        return self

    def __iter__(self) -> "t.Iterator[T_error_co]":
        return self

    def __next__(self) -> t.NoReturn:
        raise StopIteration()

    def __getattr__(self, name: str) -> "Err[T_error_co]":
        return self

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "Err[T_error_co]":
        return self

    def __str__(self) -> str:
        return f"<Err {repr(self._under)}>"


T_err = t.TypeVar("T_err", bound=Exception)


@t.overload
def unravel_container(
    value: Ok[T] | Err[T_err], last_container: Ok[T] | Err[T_err] | None = None
) -> tuple[T | T_err, Ok[T] | Err[T_err]]:
    ...


@t.overload
def unravel_container(
    value: t.Any, last_container: t.Any | None = None
) -> tuple[t.Any, t.Any | None]:
    ...


def unravel_container(value, last_container=None):
    """ """
    match value:  # noqa: E999
        case Ok(under) | Err(under) as c:
            return unravel_container(under, c)
        case _:
            return value, last_container


RESULT_MATCHABLE_CLASSES = {Ok, Err}

Ok.__matchable_classes__ = RESULT_MATCHABLE_CLASSES
Err.__matchable_classes__ = RESULT_MATCHABLE_CLASSES

ResultType = t.Union[Ok[T], Err[T_err]]
