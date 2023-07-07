import asyncio
import typing as t
from inspect import isawaitable

import typing_extensions as te

from seito.monad.func import Default, Matchable, When
from seito.monad.result import (
    Err,
    Ok,
    ResultContainer,
    ResultShortcutError,
    unravel_container,
)

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
    current_result: U | t.Awaitable[U] = fn(*a, **kw)
    while asyncio.iscoroutine(current_result) or isawaitable(current_result):
        current_result = await current_result
    return t.cast(U, current_result)


class AsyncResult(
    ResultContainer[t.Callable[P, t.Awaitable[V]]], t.Generic[P, V, T_err]
):
    """
    AsyncResult is a monad that represents a computation that may either result in an
    error, or return a successfully computed value.
    """

    def __init__(
        self,
        aws: t.Callable[P, t.Awaitable[V]],
    ):
        """

        Args:
            aws (t.Callable[P, t.Awaitable[V]]):
        """
        self._under = aws
        self.args: tuple[t.Any, ...] = ()
        self.kwargs: dict[str, t.Any] = {}
        self.errors: tuple[type[T_err], ...] = t.cast(
            tuple[type[T_err], ...], (Exception,)
        )

    def on_error(self, errors: tuple[type[T_err], ...]) -> "AsyncResult":
        """
        Set the errors that will be caught by this AsyncResult.
        Args:
            errors (tuple[type[T_err], ...]): _description_

        Returns:
            AsyncResult: _description_
        """
        self.errors = errors
        return self

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> te.Self:
        """
        Set the arguments that will be passed to the underlying function.

        Returns:
            AsyncResult: _description_
        """
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
        """
        Execute the underlying function and return the result.

        Returns:
            Ok[V] | Err[T_err]: Ok or Err depending on the result of the underlying
            function.
        """
        result = await self._execute()
        _, container = unravel_container(result)
        return container

    async def is_ok(self):
        """
        Check if the underlying function returned an Ok.

        Returns:
            bool: True if the underlying function returned an Ok, False otherwise.
        """
        return (await self._execute()).is_ok()

    async def is_error(self):
        """
        Check if the underlying function returned an Err.

        Returns:
            bool: True if the underlying function returned an Err, False otherwise.
        """
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
        """
        Map the result of the underlying function to a new value.

        Args:
            fn (t.Callable[[V], T_output] | t.Callable[[V],
            t.Awaitable[T_output]] | T_output):

        Returns:
            AsyncResult[P, T_output, T_err]: _description_
        """

        async def compose(*args: P.args, **kwargs: P.kwargs) -> T_output:
            result: V = await _exec(self._under, *args, **kwargs)
            r: T_output = await _exec(fn, result)
            return r

        r = AsyncResult(compose)
        r.args = self.args
        r.kwargs = self.kwargs
        return r

    async def for_each(self, fn: t.Callable[[V | T_err], None]) -> None:
        """


        Args:
            fn (t.Callable[[V  |  T_err], None]): _description_
        """
        result = await self._execute()
        result, _ = unravel_container(result)
        fn(result)

    def recover(
        self,
        obj: t.Callable[P_mapper, V] | t.Callable[P_mapper, t.Awaitable[V]] | V,
        *a: P_mapper.args,
        **kw: P_mapper.kwargs,
    ) -> "AsyncResult[P, V, T_err]":
        """
        Recover from an error by executing a new function.

        Args:
            obj (t.Callable[P_mapper, V] | t.Callable[P_mapper, t.Awaitable[V]] | V):

        Returns:
            AsyncResult[P, V, T_err]:
        """

        async def compose(*args: P.args, **kwargs: P.kwargs) -> V:
            try:
                result = await _exec(self._under, *args, **kwargs)
            except Exception:
                result = await _exec(obj, *a, **kw)
            return result

        r = AsyncResult(compose)
        r.args = self.args
        r.kwargs = self.kwargs
        return r

    async def get(self):
        """
        Get the result of the underlying function.
        """
        result = await self._execute()
        _, container = unravel_container(result)
        return container.get()

    async def or_none(self):
        """
        Get the result of the underlying function or None if the result is an Err.

        Returns:
            _type_: _description_
        """
        result = await self._execute()
        return result.or_none()

    @t.overload
    async def or_else(
        self,
        obj: t.Callable[P_mapper, t.Awaitable[T_output]],
        *args: P_mapper.args,
        **kwargs: P_mapper.kwargs,
    ) -> T_output:
        ...

    @t.overload
    async def or_else(
        self,
        obj: t.Callable[P_mapper, T_output],
        *args: P_mapper.args,
        **kwargs: P_mapper.kwargs,
    ) -> T_output:
        ...

    @t.overload
    async def or_else(
        self,
        obj: T_output,
    ) -> T_output:
        ...

    async def or_else(
        self,
        obj: t.Callable[P_mapper, T_output]
        | t.Callable[P_mapper, t.Awaitable[T_output]]
        | T_output,
        *args: P_mapper.args,
        **kwargs: P_mapper.kwargs,
    ) -> T_output:
        """
        Get the result of the underlying function or the result of the given function if
        the result is an Err.
        """

        def check_value(step_result: t.Any) -> bool:
            return isinstance(step_result, (Err, Exception)) or (step_result is None)

        return await self._execute_or_clause_if(  # type: ignore
            check_value, obj, *args, **kwargs
        )

    async def or_raise(self, exc: Exception | None = None) -> t.Any | None:
        """
        Get the result of the underlying function or raise the given exception if the
        result is an Err.
        """
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

    def __iter__(self) -> t.NoReturn:
        """ """
        raise NotImplementedError()  # pragma: no cover

    def __getattr__(self, name: str) -> "AsyncResult[P, t.Any, T_err]":
        """ """

        async def compose(*args: P.args, **kwargs: P.kwargs) -> t.Any:
            result: V = await _exec(self._under, *args, **kwargs)  # type: ignore
            r: t.Any = await _exec(getattr, result, name)  # type: ignore
            return r

        return AsyncResult(compose)

    async def match(
        self, *whens: When[t.Any, t.Any] | Matchable[t.Any] | Default[t.Any]
    ):
        """ """
        result: Ok[V] | Err[T_err] = await self._execute()
        _, container = unravel_container(result)
        return container.match(*whens)

    async def _(self):
        result: Ok[V] | Err[T_err] = await self._execute()
        match result:
            case Err(e):
                raise ResultShortcutError(e)
            case Ok(v):
                return v
            case _:
                raise ValueError("Invalid result")


async_try = AsyncResult
Future = AsyncResult


def lift_future(
    f: t.Callable[P_mapper, t.Awaitable[U]]
) -> t.Callable[..., AsyncResult[P_mapper, U, Exception]]:
    if not asyncio.iscoroutinefunction(f):
        raise TypeError("Can only be used on async function")

    def wrapper(*args: P_mapper.args, **kwargs: P_mapper.kwargs):
        return async_try(f)(*args, **kwargs)

    return wrapper
