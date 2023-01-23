from typing import Callable, TypeVar, Tuple, Generic, Type

from mypy_extensions import VarArg, KwArg

from seito.monad.container import Result, Err

E = TypeVar("E", bound=Type[Exception])
T = TypeVar("T")


class Try(Generic[T, E]):
    def __init__(
        self,
        f: Callable[..., T],
        *args: VarArg,
        errors: tuple[E, ...] = (Exception,),
        **kwargs: KwArg
    ):
        self.f = f
        self.args = args
        self.errors: Tuple[E, ...] = errors
        self.kwargs = kwargs

    def on_error(self, *errors: E):
        if not all(issubclass(e, Exception) for e in errors):
            raise ValueError("Error")
        self.errors = errors or Exception
        return self

    def __call__(self) -> Result[T] | Err[E]:
        try:
            value = self.f(*self.args, **self.kwargs)
        except self.errors as e:
            return Err(e)
        else:
            return Result(value)

    @staticmethod
    def of(f, *args, errors=(Exception,), **kwargs) -> Result[T] | Err[E]:
        return Try(f, *args, errors=errors, **kwargs)()


def attempt_to(errors=(Exception,)):
    def wrapper(f):
        def inner(*args, **kwargs):
            return Try(f, *args, errors=errors, **kwargs)()

        return inner

    return wrapper
