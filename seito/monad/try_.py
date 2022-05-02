from dataclasses import dataclass, field
from typing import Callable, Any, TypeVar, Tuple

from deprecated import deprecated

from seito.monad.opt import opt, Some, Empty, err

E = TypeVar("E", bound=Exception)
T = TypeVar("T")


@deprecated(reason="Use 'opt_from_call' instead, from the opt module")
@dataclass
class Try:
    f: Callable[..., T]
    cb: Callable[[E], Any] = None
    errors: Tuple[E, ...] = field(default=(Exception,))

    def on_error(self, *errors: E, cb: Callable[[E], Any] = lambda: None):
        if not all(issubclass(e, Exception) for e in errors):
            raise ValueError("Error")
        self.cb = cb
        self.errors = errors or Exception
        return self

    def __call__(self, *args, **kwargs) -> Some[T] | Empty | Any:
        try:
            value = self.f(*args, **kwargs)
            return opt(value)
        except self.errors as e:
            if self.cb:
                return self.cb(e)
            return err(e)


def attempt(*args, **kwargs):
    return Try(*args, **kwargs)


try_ = attempt


@deprecated(reason="Use 'opt_from_call' instead, from the opt module")
def attempt_to(errors=(Exception,)):
    def wrapper(f):
        try_ = Try(f=f, errors=errors)

        def inner(*args, **kwargs):
            return try_(*args, **kwargs)

        return inner

    return wrapper
