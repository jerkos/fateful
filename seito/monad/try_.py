from dataclasses import dataclass, field
from typing import Callable, Any, TypeVar, Tuple

from seito.monad.opt import opt, none, Some, Empty

E = TypeVar("E", bound=Exception)
T = TypeVar("T")

@dataclass
class Try:
    f: Callable[..., T]
    as_opt: bool = True
    cb: Callable[[E], Any] = None
    errors: Tuple[E, ...] = field(default=(Exception,))

    def on_error(self, *errors: E, cb: Callable[[E], Any] = lambda: None):
        if not all(issubclass(e, Exception) for e in errors):
            raise ValueError('Error')
        self.cb = cb
        self.errors = errors or Exception
        return self

    def __call__(self, *args, **kwargs) -> Some[T] | Empty | Any:
        try:
            value = self.f(*args, **kwargs)
            return opt(value) if self.as_opt else value
        except self.errors as e:
            if self.as_opt:
                return none
            if self.cb:
                return self.cb(e)


def attempt(f):
    return Try(f)

def try_(f, **kwargs):
    return Try(**kwargs)

def attempt_dec(errors=(Exception,), as_opt=False):
    def _(f):
        try_ = Try(f=f, errors=errors, as_opt=as_opt)

        def __(*args, **kwargs):
            return try_(*args, **kwargs)

        return __

    return _
