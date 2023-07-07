import typing as t

import typing_extensions as te

from seito.monad.func import Matchable


class EmptyError(ValueError):
    """ """

    ...


T_co = t.TypeVar("T_co", covariant=True)
V = t.TypeVar("V")
P = t.ParamSpec("P")


class MappableContainer(t.Protocol[T_co]):
    def map(self, fn: t.Callable[[T_co], V]) -> V:  # pragma: no cover
        ...


class CommonContainer(MappableContainer[T_co], Matchable[T_co], t.Protocol):
    """ """

    __match_args__: tuple[t.Literal["_under"]] = ("_under",)

    def get(self) -> T_co | t.NoReturn:
        """ """
        ...  # pragma: no cover

    def unwrap(self) -> T_co | t.NoReturn:
        return self.get()

    def or_else(
        self, obj: t.Callable[P, V] | V, *args: P.args, **kwargs: P.kwargs
    ) -> T_co | V:
        """ """
        ...  # pragma: no cover

    def unwrap_or_else(
        self, obj: t.Callable[P, V] | V, *args: P.args, **kwargs: P.kwargs
    ) -> T_co | V:
        return self.or_else(obj, *args, **kwargs)

    def or_none(self) -> T_co | None:
        """ """
        ...  # pragma: no cover

    def or_raise(self, exc: Exception | None = None) -> T_co | t.NoReturn:
        """ """
        ...  # pragma: no cover

    def __iter__(self) -> "t.Iterator[T_co]":
        """ """
        ...  # pragma: no cover

    def __getattr__(self, name: str) -> t.Any:
        """ """
        ...  # pragma: no cover

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> te.Self:
        """ """
        return self

    def __str__(self) -> str:
        """ """
        ...  # pragma: no cover
