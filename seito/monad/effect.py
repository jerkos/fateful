import dataclasses
import typing as t

from seito.monad.container import MappableContainer
from seito.monad.func import apply

T_wrapped_type = t.TypeVar("T_wrapped_type")
T_output = t.TypeVar("T_output")
P = t.ParamSpec("P")


@dataclasses.dataclass
class Effect(MappableContainer[T_wrapped_type]):
    _under: T_wrapped_type

    def map(self, func: t.Callable[[T_wrapped_type], T_output]) -> "Effect[T_output]":
        return Effect(apply(func, self._under))

    def __str__(self) -> str:
        return f"<Impure {repr(self._under)}/>"


def lift_effect(
    f: t.Callable[P, T_wrapped_type]
) -> t.Callable[P, Effect[T_wrapped_type]]:
    """ """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Effect[T_wrapped_type]:
        return Effect(f(*args, **kwargs))

    return wrapper
