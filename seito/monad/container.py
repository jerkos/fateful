import abc
from dataclasses import dataclass
from typing import Any, TypeVar, Generic, Callable, NoReturn

from seito.monad.func import Matchable, apply


class EmptyError(ValueError):
    """ """

    ...


class ContainerCommon(Matchable, abc.ABC):
    """ """

    @abc.abstractmethod
    def get(self) -> Any:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def or_else(self, obj: Callable[..., Any] | Any, *args: Any, **kwargs: Any) -> Any:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def or_none(self) -> Any:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def or_raise(self, exc: Exception | None = None):
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def for_each(self, f: Callable[..., Any]):
        ...  # pragma: no cover

    @abc.abstractmethod
    def map(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> "ContainerCommon":
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def __iter__(self):
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def __getattr__(self, name: str) -> Any:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def __call__(self, *args: Any, **kwargs: Any):
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def __str__(self) -> str:
        """ """
        ...  # pragma: no cover


class ResultContainer(ContainerCommon, abc.ABC):
    @abc.abstractmethod
    def is_result(self):
        ...

    @abc.abstractmethod
    def is_error(self):
        ...


class OptionContainer(ContainerCommon, abc.ABC):
    @abc.abstractmethod
    def is_some(self):
        ...

    @abc.abstractmethod
    def is_empty(self):
        ...

    @abc.abstractmethod
    def or_if_falsy(
        self, obj: Callable[..., Any] | Any, *args: Any, **kwargs: Any
    ) -> Any:
        """ """
        ...  # pragma: no cover


T = TypeVar("T")
M = TypeVar("M")


@dataclass(unsafe_hash=True)
class Some(ContainerCommon, Generic[T]):
    """ """

    __match_args__ = ("_under",)

    _under: T

    def get(self) -> T:
        return self._under

    def is_some(self):
        return True

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
        value, _ = unravel_container(self)
        return opt(apply(f, value, *args, **kwargs))

    def for_each(self, f: Callable[..., Any], *args: Any, **kwargs: Any):
        return f(*args, **kwargs)

    def __iter__(self):
        val, _ = unravel_container(self)
        yield val

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


@dataclass(unsafe_hash=True)
class Empty(ContainerCommon):
    """ """

    _under = None

    def get(self) -> NoReturn:
        raise EmptyError("Option is empty")

    @staticmethod
    def is_some():
        return False

    @staticmethod
    def is_empty() -> bool:
        return True

    def or_else(self, obj: Callable[..., M] | M, *args: Any, **kwargs: Any) -> M:
        return apply(obj, *args, **kwargs)

    @staticmethod
    def or_if_falsy(obj: Callable[..., M] | M, *args, **kwargs) -> M:
        return apply(obj, *args, **kwargs)

    def or_none(self) -> None:
        return None

    def or_raise(self, exc: Exception | None = None) -> NoReturn:
        if exc is None:
            raise ValueError("Empty value !")
        raise exc

    def map(self, func, *args, **kwargs) -> "Empty":
        return self

    def for_each(self, f: Callable[..., Any], *args: Any, **kwargs: Any):
        return None

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


@dataclass(unsafe_hash=True)
class Result(Some[T], ResultContainer):
    _under: T | None

    def is_some(self) -> bool:
        raise NotImplementedError()

    def is_empty(self) -> bool:
        raise NotImplementedError()

    def is_error(self):
        return False

    def is_result(self):
        return True

    def for_each(self, f: Callable[..., Any], *args: Any, **kwargs: Any):
        return f(*args, **kwargs)

    def __str__(self):
        return f"<Result {repr(self._under)}>"


E = TypeVar("E", bound=Exception)


@dataclass(unsafe_hash=True)
class Err(Empty, ResultContainer, Generic[E]):
    """ """

    __match_args__ = ("_under",)

    _under: E

    def __post_init__(self):
        if not issubclass(self._under.__class__, Exception):
            raise ValueError("Err should carry an exception class")

    def is_error(self):
        return True

    def is_result(self):
        return False

    def __str__(self):
        return f"<Err {repr(self._under)}>"

    def get(self):
        raise self._under

    def or_raise(self, exc: Exception | None = None) -> NoReturn:
        if exc is not None:
            raise exc from self._under
        raise self._under


def unravel_container(value, container=None) -> tuple[Any, ContainerCommon]:
    """ """
    match value:
        case Some(under) | Err(under) | Empty(under) | Result(under) as container:
            return unravel_container(under, container)
        case _:
            return value, container


def option(value: Any) -> Some[Any] | Empty:
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
err = Err

OPT_MATCHABLE_CLASSES = {Some, Empty}
RESULT_MATCHABLE_CLASSES = {Result, Err}

Some.__matchable_classes__ = OPT_MATCHABLE_CLASSES
Empty.__matchable_classes__ = OPT_MATCHABLE_CLASSES
Result.__matchable_classes__ = RESULT_MATCHABLE_CLASSES
Err.__matchable_classes__ = RESULT_MATCHABLE_CLASSES
