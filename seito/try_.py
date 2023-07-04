import typing as t

from seito.monad.result import Err, Ok

T = t.TypeVar("T", covariant=True)
P = t.ParamSpec("P")
P_mapper = t.ParamSpec("P_mapper")
E = t.TypeVar("E", bound=Exception, covariant=True)


class Try(t.Generic[P, T, E]):
    def __init__(
        self,
        f: t.Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        self.f = f
        self.args = args
        self.kwargs = kwargs
        self.errors: tuple[type[E], ...] = t.cast(tuple[type[E], ...], (Exception,))

    def on_error(self, errors: tuple[type[E]]) -> "Try[P, T, E]":
        if not all(issubclass(e, Exception) for e in errors):
            raise ValueError("Error")
        self.errors = errors or (Exception,)
        return self

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Ok[T] | Err[E]:
        self.args = args
        self.kwargs = kwargs
        try:
            value = self.f(*self.args, **self.kwargs)
        except Exception as e:
            for error in self.errors:
                if isinstance(e, error):
                    return Err(e)
            raise
        else:
            return Ok(value)

    @staticmethod
    def of(
        fn: t.Callable[P_mapper, T],
    ) -> "Try[P_mapper, T, E]":
        return Try(fn)


V = t.TypeVar("V")
T_err = t.TypeVar("T_err", bound=Exception)


def attempt_to(
    errors=(Exception,)
) -> t.Callable[[t.Callable[P_mapper, V]], t.Callable[P_mapper, Ok[V] | Err[t.Any]]]:
    def wrapper(f: t.Callable[P_mapper, V]) -> t.Callable[P_mapper, Ok[V] | Err[t.Any]]:
        def inner(
            *args: P_mapper.args, **kwargs: P_mapper.kwargs
        ) -> Ok[V] | Err[t.Any]:
            return Try(f)(*args, **kwargs)

        return inner

    return wrapper
