import abc
from typing import Any, TypeVar, Callable, NoReturn, Iterator, Generic

from seito.monad.func import Matchable


class EmptyError(ValueError):
    """ """

    ...


T_wrapped_type = TypeVar("T_wrapped_type")

Func = Callable[..., Any]


class MappableContainer(Generic[T_wrapped_type], abc.ABC):
    @abc.abstractmethod
    def map(self, func: Callable[[T_wrapped_type], Any]) -> Any:  # pragma: no cover
        ...


class CommonContainer(Matchable, MappableContainer[T_wrapped_type], abc.ABC):
    """ """

    __match_args__ = ("_under",)

    _under: T_wrapped_type

    @abc.abstractmethod
    def get(self) -> T_wrapped_type | NoReturn:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def or_else(
        self, obj: Func | Any, *args: Any, **kwargs: Any
    ) -> T_wrapped_type | Any:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def or_none(self) -> T_wrapped_type | None:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def or_raise(self, exc: Exception | None = None) -> T_wrapped_type | NoReturn | Any:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def __iter__(self) -> "Iterator[T_wrapped_type | CommonContainer[T_wrapped_type]]":
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


TContainer = TypeVar("TContainer", bound=CommonContainer)


def unravel_container(value, container=None) -> tuple[Any, TContainer]:
    """ """
    match value:  # noqa: E999
        case CommonContainer(under) as container:
            return unravel_container(under, container)
        case _:
            return value, container
