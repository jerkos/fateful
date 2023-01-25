from typing import Callable, TypeVar, Generic, Type, Any

from seito.monad.result import Result, Err

T = TypeVar("T")


class Try(Generic[T]):
    def __init__(
        self,
        f: Callable[..., T],
        *args: Any,
        errors: tuple[Type[Exception], ...] = (Exception,),
        **kwargs: Any,
    ):
        self.f = f
        self.args = args
        self.errors: tuple[Type[Exception], ...] = errors
        self.kwargs = kwargs

    def on_error(self, *errors: Type[Exception]) -> "Try[T]":
        if not all(issubclass(e, Exception) for e in errors):
            raise ValueError("Error")
        self.errors = errors or (Exception,)
        return self

    def __call__(self) -> Result[T] | Err[Exception]:
        try:
            value = self.f(*self.args, **self.kwargs)
        except self.errors as e:
            return Err(e)
        else:
            return Result(value)

    @staticmethod
    def of(
        f: Callable[..., T],
        *args: Any,
        errors: tuple[Type[Exception], ...] = (Exception,),
        **kwargs: Any,
    ) -> Result[T] | Err[Exception]:
        return Try[T](f, *args, errors=errors, **kwargs)()


def attempt_to(errors=(Exception,)):
    def wrapper(f):
        def inner(*args, **kwargs):
            return Try(f, *args, errors=errors, **kwargs)()

        return inner

    return wrapper
