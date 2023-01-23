import asyncio
import functools
from asyncio import iscoroutinefunction
from inspect import isawaitable
from typing import Callable, Any, TypeVar, Generic, Type, Coroutine

from mypy_extensions import VarArg, KwArg

from seito.monad.container import ResultContainer, Result, unravel_container
from seito.monad.container import (
    opt,
    Err,
)
from seito.monad.func import flip, When, Default


async def _exec(function: Callable[..., Any], *a: Any, **kw: Any) -> Any:
    current_result = function(*a, **kw)
    while asyncio.iscoroutine(current_result) or isawaitable(current_result):
        current_result = await current_result
    return current_result


T = TypeVar("T")
E = TypeVar("E", bound=Type[Exception])


class AsyncTry(ResultContainer, Generic[T]):
    """ """

    def __init__(
        self,
        aws: Callable[[...], Coroutine[Any, Any, T]],
        *args: VarArg,
        **kwargs: KwArg,
    ):
        self.aws = aws
        self.args = args
        self.kwargs = kwargs
        self.errors: tuple[E, ...] = (Exception,)
        self._mappers: list[tuple[Callable[[T, ...], Any], VarArg, KwArg]] = []

    def on_error(self, *errors: E):
        if not all(issubclass(e, Exception) for e in errors):
            raise ValueError("Error")
        self.errors = errors or Exception
        return self

    def __call__(self, *args, **kwargs) -> "AsyncTry[T]":
        self.args = args
        self.kwargs = kwargs
        return self

    @staticmethod
    async def _exc_step(f, *args, **kwargs):
        try:
            r = await _exec(f, *args, **kwargs)
        except Exception as e:
            return Err(e)
        else:
            return Result(r)

    async def _execute(self) -> Result[T] | Err[E]:
        """ """
        result = await self._exc_step(self.aws, *self.args, **self.kwargs)
        match result:
            case Err():
                return result
        for f, a, kw in self._mappers:
            result = await self._exc_step(f, result.get(), *a, **kw)
            match result:
                case Err():
                    return result
        else:
            return result

    async def is_result(self) -> bool:
        return (await self._execute()).is_result()

    async def is_error(self):
        return (await self._execute()).is_error()

    @staticmethod
    async def _execute_or_clause(or_f, *args, **kwargs):
        """ """
        if iscoroutinefunction(or_f):
            return await or_f(*args, **kwargs)
        elif callable(or_f):
            return or_f(*args, **kwargs)
        return or_f

    async def _execute_or_clause_if(self, predicate, or_f, *args, **kwargs) -> T:
        """ """
        result = await self._execute()
        if predicate(result):
            return await self._execute_or_clause(or_f, *args, **kwargs)
        _, container = unravel_container(result)
        return container.get()

    def map(self, f: Callable[[T, ...], Any], *args: VarArg, **kwargs: KwArg):
        """ """
        self._mappers.append((f, args, kwargs))
        return self

    async def for_each(
        self, f: Callable[..., Any], *args: VarArg, **kwargs: KwArg
    ) -> None:
        result = await self._execute()
        result, _ = unravel_container(result)
        f(result, *args, **kwargs)

    async def get(self) -> Any:
        """ """
        result = await self._execute()
        _, container = unravel_container(result)
        return container.get()

    async def or_none(self) -> Any:
        """ """
        result = await self._execute()
        _, container = unravel_container(result)
        return result.or_none()

    async def or_else(
        self, or_f: Callable[..., Any] | T | Any, *args: Any, **kwargs: Any
    ) -> T:
        """ """

        def check_value(step_result: Any):
            return isinstance(step_result, (Err, Exception)) or (step_result is None)

        return await self._execute_or_clause_if(check_value, or_f, *args, **kwargs)

    async def or_raise(self, exc: Exception | None = None):
        """ """
        result = await self._execute()
        _, container = unravel_container(result)
        return container.or_raise(exc)

    async def __aiter__(self):
        """ """
        r = await self._execute()
        for val in r:
            yield val

    def __str__(self) -> str:
        """ """
        return f"<AsyncOption {repr(self._under)}>"

    def __iter__(self):
        """ """
        raise NotImplementedError()  # pragma: no cover

    def __getattr__(self, name: str) -> Any:
        """ """
        self._mappers.append((functools.partial(flip(getattr)), (name,), {}))
        return self

    async def match(self, *whens: When | Default):
        """ """
        result = await self._execute()
        _, container = unravel_container(result)
        return container.match(*whens)

    @staticmethod
    def of(f, *args, **kwargs):
        """
        >>>import asyncio
        >>>async def test(x: int):
        >>>    await asyncio.sleep(0.3)
        >>>    return x + 100
        >>>
        >>> val = 1
        >>>(
        >>>    AsyncTry.of(test, 1)
        >>>         .map(lambda x: x - 100)
        >>>         .for_each(lambda x: print(x == val))
        >>>)

        """
        return AsyncTry(f, *args, **kwargs)


async_try = AsyncTry
