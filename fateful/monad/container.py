import abc
import typing as t

import typing_extensions as te

from fateful.monad.func import MatchableMixin


class EmptyError(ValueError):
    """ """

    ...


T_co = t.TypeVar("T_co", covariant=True)
V = t.TypeVar("V")
P = t.ParamSpec("P")


class MappableContainerMixin(t.Generic[T_co], abc.ABC):
    @abc.abstractmethod
    def map(
        self, fn: t.Callable[[t.Any], V]
    ) -> "MappableContainerMixin[V | Exception | T_co]":  # pragma: no cover
        ...


class CommonContainer(MappableContainerMixin[T_co], MatchableMixin[T_co], abc.ABC):
    """ """

    __match_args__: tuple[t.Literal["_under"]] = ("_under",)

    def __init__(self, under: T_co) -> None:
        self._under = under

    @abc.abstractmethod
    def get(self) -> T_co:
        """ """
        ...  # pragma: no cover

    def unwrap(self) -> T_co:
        return self.get()

    @abc.abstractmethod
    def or_(self, obj: V | T_co) -> V | T_co:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def or_else(
        self, obj: t.Callable[P, V], *args: P.args, **kwargs: P.kwargs
    ) -> V | T_co:
        """ """
        ...  # pragma: no cover

    def unwrap_or_else(
        self, obj: t.Callable[P, V] | V, *args: P.args, **kwargs: P.kwargs
    ) -> object:
        return self.or_else(obj, *args, **kwargs)  # type: ignore[arg-type]

    @abc.abstractmethod
    def or_none(self) -> T_co | None:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def or_raise(self, exc: Exception | None = None) -> T_co | t.NoReturn:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def __iter__(self) -> "t.Iterator[T_co | te.Self]":
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def __getattr__(self, name: str) -> t.Any:
        """ """
        ...  # pragma: no cover

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> te.Self:
        """ """
        return self

    @abc.abstractmethod
    def __str__(self) -> str:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def flatten(self) -> "CommonContainer":
        ...
