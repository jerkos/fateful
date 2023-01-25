import dataclasses
from typing import TypeVar, Any, Callable

from seito.monad.container import MappableContainer
from seito.monad.func import apply

T_wrapped_type = TypeVar("T_wrapped_type")


@dataclasses.dataclass
class Effect(MappableContainer[T_wrapped_type]):
    _under: T_wrapped_type

    def map(self, func: Callable[[T_wrapped_type], Any]) -> "Effect[Any]":
        return Effect(apply(func, self._under))

    def __str__(self) -> str:
        return f"<Impure {repr(self._under)}/>"


def lift_effect(f):
    """ """

    def wrapper(*args, **kwargs):
        return Effect(f(*args, **kwargs))

    return wrapper
