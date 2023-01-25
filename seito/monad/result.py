import abc
from dataclasses import dataclass
from typing import Any, TypeVar, NoReturn, Callable, Iterator

from seito.monad.container import (
    CommonContainer,
    T_wrapped_type,
    Func,
    unravel_container,
)
from seito.monad.func import apply


class ResultContainer(CommonContainer[T_wrapped_type], abc.ABC):
    @abc.abstractmethod
    def is_result(self) -> bool:  # pragma: no cover
        ...

    @abc.abstractmethod
    def is_error(self) -> bool:  # pragma: no cover
        ...

    @abc.abstractmethod
    def recover(self, obj: Callable[..., Any] | Any, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        ...


@dataclass(unsafe_hash=True)
class Result(ResultContainer[T_wrapped_type | None]):

    _under: T_wrapped_type | None

    def is_error(self) -> bool:
        return False

    def is_result(self) -> bool:
        return True

    def or_none(self) -> T_wrapped_type | None:
        return self._under

    def get(self) -> T_wrapped_type | None:
        return self._under

    def or_else(
        self, obj: Func | Any, *args: Any, **kwargs: Any
    ) -> T_wrapped_type | None:
        return self._under

    def or_raise(self, exc: Exception | None = None) -> T_wrapped_type | None:
        return self._under

    def recover(
        self: "Result[T_wrapped_type | None]",
        obj: Callable[..., Any] | Any,
        *args: Any,
        **kwargs: Any,
    ) -> "Result[T_wrapped_type | None]":
        return self

    def map(
        self, func: Callable[[T_wrapped_type], Any]
    ) -> "Result[T_wrapped_type] | Err":
        from seito.try_ import Try

        return Try.of(func, self._under)

    def __iter__(self) -> "Iterator[T_wrapped_type]":
        val, _ = unravel_container(self)
        yield val

    def __getattr__(
        self, name: str
    ) -> "Result[T_wrapped_type] | Err[AttributeError] | Callable[..., Any]":
        try:
            attr = getattr(self._under, name)
        except AttributeError as e:
            return Err(e)
        if callable(attr):

            def wrapper(*args: Any, **kwargs: Any) -> "Result[Any] | Err[Exception]":
                from seito.try_ import Try

                return Try.of(attr, *args, **kwargs)

            return wrapper

        return Result(attr)

    def __call__(self, *args: Any, **kwargs: Any) -> "Result[T_wrapped_type]":
        return self

    def __str__(self):
        return f"<Result {repr(self._under)}>"


T_error = TypeVar("T_error", bound=Exception)


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
        self, obj: Callable[..., Any] | Any, *args: Any, **kwargs: Any
    ) -> Result[Any]:
        return Result(apply(obj, *args, **kwargs))

    def is_error(self):
        return True

    def is_result(self):
        return False

    def get(self) -> NoReturn:
        raise self._under

    def or_else(self, obj: Func | Any, *args: Any, **kwargs: Any) -> Any:
        return apply(obj, *args, **kwargs)

    def or_raise(self, exc: Exception | None = None) -> NoReturn:
        if exc is not None:
            raise exc from self._under
        raise self._under

    def or_none(self):
        return None

    def map(self, func: Callable[[T_wrapped_type], Any]) -> "Err[T_error]":
        return self

    def __iter__(self) -> "Iterator[T_error]":
        return self

    def __next__(self) -> NoReturn:
        raise StopIteration()

    def __getattr__(self, name: str) -> "Err[T_error]":
        return self

    def __call__(self, *args: Any, **kwargs: Any) -> "Err[T_error]":
        return self

    def __str__(self) -> str:
        return f"<Err {repr(self._under)}>"


RESULT_MATCHABLE_CLASSES = {Result, Err}

Result.__matchable_classes__ = RESULT_MATCHABLE_CLASSES
Err.__matchable_classes__ = RESULT_MATCHABLE_CLASSES
