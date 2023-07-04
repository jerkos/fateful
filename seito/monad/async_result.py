import asyncio
import functools
import typing as t
from inspect import isawaitable

from seito.monad.func import Default, Matchable, When, flip
from seito.monad.result import Err, Ok, ResultContainer, unravel_container

P_mapper = t.ParamSpec("P_mapper")
P = t.ParamSpec("P")
U = t.TypeVar("U")
V = t.TypeVar("V")

T_output = t.TypeVar("T_output")
T_err = t.TypeVar("T_err", bound=Exception, covariant=True)


async def _exec(
    fn: t.Callable[P_mapper, U] | t.Callable[P_mapper, t.Awaitable[U]] | U,
    *a: P_mapper.args,
    **kw: P_mapper.kwargs,
) -> U:
    if not callable(fn):
        return t.cast(U, fn)
    fn = t.cast(t.Callable[P_mapper, U] | t.Callable[P_mapper, t.Awaitable[U]], fn)
    current_result: U | t.Awaitable[U] = fn(*a, **kw)
    while asyncio.iscoroutine(current_result) or isawaitable(current_result):
        current_result = await current_result
    return t.cast(U, current_result)


class AsyncResult(
    ResultContainer[t.Callable[P, t.Awaitable[V]]], t.Generic[P, V, T_err]
):
    """ """

    def __init__(
        self,
        aws: t.Callable[P, t.Awaitable[V]],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        self._under = aws
        self.args = args
        self.kwargs = kwargs
        self.errors: tuple[type[T_err], ...] = t.cast(
            tuple[type[T_err], ...], (Exception,)
        )

    def on_error(self, errors: tuple[type[T_err], ...]) -> "AsyncResult":
        self.errors = errors
        return self

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> "AsyncResult":
        self.args = args
        self.kwargs = kwargs
        return self

    async def _exec(
        self,
        fn: t.Callable[P_mapper, T_output]
        | t.Callable[P_mapper, t.Awaitable[T_output]]
        | T_output,
        *args: P_mapper.args,
        **kwargs: P_mapper.kwargs,
    ) -> Ok[T_output] | Err[T_err]:
        try:
            r = await _exec(fn, *args, **kwargs)
        except Exception as e:
            for err in self.errors:
                if isinstance(e, err):
                    return Err(e)
            raise
        else:
            return Ok(r)

    async def _execute(self) -> Ok[V] | Err[T_err]:
        return await self._exec(self._under, *self.args, **self.kwargs)

    async def execute(self) -> Ok[V] | Err[T_err]:
        result = await self._execute()
        _, container = unravel_container(result)
        return container

    async def is_ok(self):
        return (await self._execute()).is_ok()

    async def is_error(self):
        return (await self._execute()).is_error()

    async def _execute_or_clause_if(
        self,
        predicate,
        or_f: t.Callable[P_mapper, T_output]
        | t.Callable[P_mapper, t.Awaitable[T_output]]
        | T_output,
        *args: P_mapper.args,
        **kwargs: P_mapper.kwargs,
    ) -> T_output | t.Any:
        """ """
        result = await self._execute()
        if predicate(result):
            return await _exec(or_f, *args, **kwargs)
        _, container = unravel_container(result)
        return container.get()

    def map(
        self,
        fn: t.Callable[[V], T_output]
        | t.Callable[[V], t.Awaitable[T_output]]
        | T_output,
    ) -> "AsyncResult[P, T_output, T_err]":
        """ """

        async def compose(*args: P.args, **kwargs: P.kwargs) -> T_output:
            result = await _exec(self._under, *args, **kwargs)
            result = await _exec(fn, result)
            return result

        return AsyncResult(compose, *self.args, **self.kwargs)

    async def for_each(self, fn: t.Callable[[V | T_err], None]) -> None:
        result = await self._execute()
        result, _ = unravel_container(result)
        fn(result)

    def recover(
        self,
        obj: t.Callable[P_mapper, V] | t.Callable[P_mapper, t.Awaitable[V]] | V,
        *a: P_mapper.args,
        **kw: P_mapper.kwargs,
    ) -> "AsyncResult[P, V, T_err]":
        async def compose(*args: P.args, **kwargs: P.kwargs) -> V:
            try:
                result = await _exec(self._under, *args, **kwargs)
            except Exception:
                result = await _exec(obj, *a, **kw)
            return result

        return AsyncResult(compose, *self.args, **self.kwargs)

    async def get(self):
        """ """
        result = await self._execute()
        _, container = unravel_container(result)
        return container.get()

    async def or_none(self):
        """ """
        result = await self._execute()
        return result.or_none()

    async def or_(self, obj: T_output) -> V | T_output | None:
        result = await self._execute()
        _, container = unravel_container(result)
        return container.or_(obj)

    async def or_else(
        self,
        obj: t.Callable[P_mapper, T_output]
        | t.Callable[P_mapper, t.Awaitable[T_output]],
        *args: P_mapper.args,
        **kwargs: P_mapper.kwargs,
    ) -> T_output:
        """ """

        def check_value(step_result: t.Any):
            return isinstance(step_result, (Err, Exception)) or (step_result is None)

        return await self._execute_or_clause_if(check_value, obj, *args, **kwargs)

    unwrap_or = or_else

    async def or_raise(self, exc: Exception | None = None) -> t.Any | None:
        """ """
        result = await self._execute()
        _, container = unravel_container(result)
        return container.or_raise(exc if exc is not None else ValueError())

    async def __aiter__(self):
        """ """
        r = await self._execute()
        for val in r:
            yield val

    def __str__(self) -> str:
        """ """
        return f"<AsyncTry {repr(self._under)}>"

    def __iter__(self):
        """ """
        raise NotImplementedError()  # pragma: no cover

    def __getattr__(self, name: str) -> "AsyncResult":
        """ """

        async def compose(*args: P.args, **kwargs: P.kwargs) -> t.Any:
            result = await _exec(self._under, *args, **kwargs)
            result = await _exec(functools.partial(flip(getattr)), (name,), {})
            return result

        return AsyncResult(compose, *self.args, **self.kwargs)

    async def match(self, *whens: When | Default | Matchable):
        """ """
        result = await self._execute()
        _, container = unravel_container(result)
        return container.match(*whens)

    @staticmethod
    def of(f: t.Callable[P, t.Awaitable[V]]):
        """
        >>>import asyncio
        >>>async def test(x: int):
        >>>    await asyncio.sleep(0.3)
        >>>    return x + 100
        >>>
        >>> val = 1
        >>>await (
        >>>    AsyncResult.of(test, 1)
        >>>    .map(lambda x: x - 100)
        >>>    .for_each(lambda x: print(x == val))
        >>>)

        """
        return AsyncResult(f)  # type: ignore


async_try = AsyncResult
Future = AsyncResult


def lift_future(
    f: t.Callable[P_mapper, t.Awaitable[U]]
) -> t.Callable[..., AsyncResult[P_mapper, U, Exception]]:
    if not asyncio.iscoroutinefunction(f):
        raise TypeError("Can only be used on async function")

    def wrapper(*args: P_mapper.args, **kwargs: P_mapper.kwargs):
        return AsyncResult.of(f)(*args, **kwargs)

    return wrapper
