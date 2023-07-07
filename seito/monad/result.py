import functools
import typing as t
from dataclasses import dataclass

from seito.monad.container import CommonContainer

T_co = t.TypeVar("T_co", covariant=True)
U = t.TypeVar("U")
P = t.ParamSpec("P")


class ResultContainer(CommonContainer[T_co], t.Protocol):  # type: ignore
    def is_ok(self) -> bool:  # pragma: no cover
        ...

    def is_error(self) -> bool:  # pragma: no cover
        ...

    def recover(
        self, obj: t.Callable[P, U] | U, *args: P.args, **kwargs: P.kwargs
    ) -> U:  # pragma: no cover
        ...

    @property
    def _(self) -> T_co | t.NoReturn:
        ...


@dataclass(unsafe_hash=True)
class Ok(ResultContainer[T_co]):
    _under: T_co

    def is_error(self) -> bool:
        return False

    def is_ok(self) -> bool:
        return True

    def or_none(self) -> T_co:
        return self._under

    def get(self) -> T_co:
        return self._under

    @t.overload
    def or_else(
        self, obj: t.Callable[P, T_co] | T_co, *args: P.args, **kwargs: P.kwargs
    ) -> T_co:
        ...

    @t.overload
    def or_else(self, obj: t.Any) -> T_co:
        ...

    def or_else(
        self, obj: t.Callable[P, T_co] | T_co, *args: P.args, **kwargs: P.kwargs
    ) -> T_co:
        return self._under

    def or_raise(self, exc: Exception | None = None) -> T_co:
        return self._under

    def recover(
        self: "Ok[T_co]",
        obj: t.Callable[P, U] | U,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Ok[T_co]":
        return self

    def map(self, fn: t.Callable[[T_co], U]) -> "Ok[U] | Err[Exception]":
        return sync_try(fn)(self._under)

    def __iter__(self) -> "t.Iterator[T_co]":
        val, _ = unravel_container(self)
        yield val

    def __getattr__(
        self, name: str
    ) -> "Ok[T_co] | Err[AttributeError] | t.Callable[..., t.Any]":
        try:
            attr = getattr(self._under, name)
        except AttributeError as e:
            return Err(e)
        if callable(attr):

            def wrapper(
                *args: P.args, **kwargs: P.kwargs
            ) -> "Ok[t.Any] | Err[Exception]":
                return sync_try(attr)(*args, **kwargs)

            return wrapper

        return Ok(attr)

    @property
    def _(self) -> T_co:
        return self._under

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "Ok[T_co]":
        return self

    def __str__(self):
        return f"<Ok {repr(self._under)}>"


T_error = t.TypeVar("T_error", bound=BaseException, covariant=True)


@dataclass(unsafe_hash=True)
class Err(ResultContainer[T_error]):
    """ """

    _under: T_error

    def __post_init__(self):
        if not issubclass(self._under.__class__, Exception):
            raise ValueError("Err should carry an exception class")

    def unwrap(self) -> T_error:
        return self._under

    def recover(
        self, obj: t.Callable[P, U] | U, *args: P.args, **kwargs: P.kwargs
    ) -> Ok[U]:
        return Ok(obj(*args, **kwargs) if callable(obj) else obj)

    def is_error(self):
        return True

    def is_ok(self):
        return False

    def get(self) -> t.NoReturn:
        raise self._under

    @t.overload
    def or_else(self, obj: t.Callable[P, U], *args: P.args, **kwargs: P.kwargs) -> U:
        ...

    @t.overload
    def or_else(self, obj: U) -> U:
        ...

    def or_else(
        self, obj: t.Callable[P, U] | U, *args: P.args, **kwargs: P.kwargs
    ) -> U:
        return obj(*args, **kwargs) if callable(obj) else obj

    def or_raise(self, exc: Exception | None = None) -> t.NoReturn:
        if exc is not None:
            raise exc from self._under
        raise self._under

    def or_none(self):
        return None

    def map(self, func: t.Callable[[t.Any], t.Any]) -> "Err[T_error]":
        return self

    def __iter__(self) -> "t.Iterator[T_error]":
        return self

    def __next__(self) -> t.NoReturn:
        raise StopIteration()

    def __getattr__(self, name: str) -> "Err[T_error]":
        return self

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "Err[T_error]":
        return self

    @property
    def _(self) -> t.NoReturn:
        raise ResultShortcutError(self._under)

    def __str__(self) -> str:
        return f"<Err {repr(self._under)}>"


@t.overload
def unravel_container(
    value: Ok[T_co] | Err[T_error],
    last_container: Ok[T_co] | Err[T_error] | None = None,
) -> tuple[T_co | T_error, Ok[T_co] | Err[T_error]]:
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

ResultType = t.Union[Ok[T_co], Err[T_error]]


def sync_try(
    f: t.Callable[P, T_co],
    exc: type[T_error] | tuple[type[T_error], ...] = (Exception,),  # type: ignore
) -> t.Callable[P, ResultType[T_co, T_error]]:
    """
    Run a function that may raise an exception and return a Result type.
    Args:
        exc (tuple[type[T_err], ...], optional): _description_. Defaults to (Exception,)
    """

    def inner(*args: P.args, **kwargs: P.kwargs) -> ResultType[T_co, T_error]:
        try:
            return Ok(f(*args, **kwargs))
        except Exception as e:
            errors = exc if isinstance(exc, tuple) else (exc,)
            for err in errors:
                if isinstance(e, err):
                    return Err(e)
            raise

    return inner


def to_result(
    exc: type[T_error] | tuple[type[T_error], ...] = (Exception,)  # type: ignore
) -> t.Callable[[t.Callable[P, T_co]], t.Callable[P, ResultType[T_co, T_error]]]:
    """
    Decorator to convert a function that may raise an exception to a Result type.

    Args:
        exc (tuple[type[T_err], ...], optional): _description_. Defaults to (Exception,)

    Returns:
        _type_: _description_
    """
    return functools.partial(sync_try, exc=exc)


class ResultShortcutError(Exception, t.Generic[T_error]):
    """
    Args:
        Exception (_type_): _description_
        t (_type_): _description_
    """

    def __init__(self, error: T_error):
        super().__init__(error)
        self.error = error


def result_shortcut(
    f: t.Callable[P, ResultType[T_co, T_error]]
) -> t.Callable[P, ResultType[T_co, T_error]]:
    """
    _summary_

    Args:
        f (t.Callable[P_mapper, V]): _description_

    Returns:
        t.Callable[P_mapper, Ok[V] | Err[t.Any]]: _description_
    """

    def inner(*args: P.args, **kwargs: P.kwargs) -> Ok[T_co] | Err[T_error]:
        try:
            return Ok(f(*args, **kwargs))
        except Exception as e:
            if isinstance(e, ResultShortcutError):
                return Err(e.error)
            raise

    return inner
