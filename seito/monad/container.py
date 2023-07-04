import abc
import typing as t

from seito.monad.func import Matchable


class EmptyError(ValueError):
    """ """

    ...


T_input_mappable = t.TypeVar("T_input_mappable", covariant=True)
T_output_mappable = t.TypeVar("T_output_mappable")
P = t.ParamSpec("P")


class MappableContainer(t.Protocol[T_input_mappable]):
    def map(
        self, fn: t.Callable[[T_input_mappable], T_output_mappable]
    ) -> T_output_mappable:  # pragma: no cover
        ...


T_input = t.TypeVar("T_input", covariant=True)
T_output = t.TypeVar("T_output")


class CommonContainer(Matchable, MappableContainer[T_input], t.Protocol):
    """ """

    __match_args__ = ("_under",)

    @abc.abstractmethod
    def get(self) -> T_input | t.NoReturn:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def or_(obj: T_output) -> T_input | T_output:
        ...

    @abc.abstractmethod
    def or_else(
        self, obj: t.Callable[P, T_output], *args: P.args, **kwargs: P.kwargs
    ) -> T_input | T_output:
        """ """
        ...  # pragma: no cover

    unwrap_or = or_else

    @abc.abstractmethod
    def or_none(self) -> T_input | None:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def or_raise(self, exc: Exception | None = None) -> T_input | t.NoReturn:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def __iter__(self) -> "t.Iterator[T_input | CommonContainer[T_input]]":
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def __getattr__(self, name: str) -> t.Any:
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def __call__(self, *args: t.Any, **kwargs: t.Any):
        """ """
        ...  # pragma: no cover

    @abc.abstractmethod
    def __str__(self) -> str:
        """ """
        ...  # pragma: no cover
