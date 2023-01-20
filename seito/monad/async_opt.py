import asyncio
import functools
from asyncio import iscoroutinefunction
from inspect import isawaitable
from typing import Awaitable, Callable, Any
from loguru import logger

from seito.monad.func import flip
from seito.monad.opt import (
    T,
    Option,
    opt,
    When,
    Default,
    unravel_opt,
    none,
    err,
    Err,
    Empty,
)


async def _exec(function: Callable[..., Any], *a: Any, **kw: Any) -> Any:
    current_result = function(*a, **kw)
    while asyncio.iscoroutine(current_result) or isawaitable(current_result):
        current_result = await current_result
    return current_result


class AsyncOption(Option):
    """ """

    def __init__(self, aws: Awaitable[Any] | Any, *args: Any, **kwargs: Any) -> None:
        self._under = aws
        self.args = args
        self.kwargs = kwargs
        self._mappers = []

    @staticmethod
    def _inner(value):
        """ """
        return unravel_opt(value)

    @staticmethod
    async def _exc_step(f, *args, **kwargs):
        try:
            r = await _exec(f, *args, **kwargs)
        except Exception as e:
            return err(e)
        else:
            if r is None:
                return none
            return r

    async def _execute(self):
        """ """
        result = await self._exc_step(self._under, *self.args, **self.kwargs)
        match result:
            case Err() | Empty():
                return result
        logger.debug(result)
        for f, a, kw in self._mappers:
            logger.debug("{}, {}, {}", f, a, kw)
            result = await self._exc_step(f, result, *a, **kw)
            logger.debug(result)
            match result:
                case Err() | Empty():
                    return result
        else:
            return result

    @staticmethod
    async def _execute_or_clause(or_f, *args, **kwargs):
        """ """
        if iscoroutinefunction(or_f):
            return await or_f(*args, **kwargs)
        elif callable(or_f):
            return or_f(*args, **kwargs)
        return or_f

    async def _execute_or_clause_if(self, predicate, or_f, *args, **kwargs):
        """ """
        value = self._inner(await self._execute())
        logger.debug(type(value))
        if predicate(value):
            return await self._execute_or_clause(or_f, *args, **kwargs)
        return value

    def map(self, f, *args, **kwargs):
        """ """
        self._mappers.append((f, args, kwargs))
        return self

    async def get(self) -> Any:
        """ """
        result = await self._execute()
        logger.debug(result)
        return opt(self._inner(result)).get()

    async def or_none(self) -> Any:
        """ """
        value = await self._execute()
        return opt(self._inner(value)).or_none()

    async def or_else(
        self, or_f: Callable[..., Any] | T, *args: Any, **kwargs: Any
    ) -> T:
        """ """

        def check_value(step_result: Any):
            return isinstance(step_result, (Err, Empty, Exception)) or (
                step_result is None
            )

        return await self._execute_or_clause_if(check_value, or_f, *args, **kwargs)

    async def or_if_falsy(
        self, or_f: Callable[..., Any] | Any, *args: Any, **kwargs: Any
    ) -> Any:
        """ """
        return await self._execute_or_clause_if(
            lambda value: not value, or_f, *args, **kwargs
        )

    async def or_raise(self, exc: Exception | None = None):
        """ """
        value = await self._execute()
        return opt(self._inner(value)).or_raise(exc)

    async def is_empty(self) -> bool:
        """ """
        value = await self._execute()
        return opt(self._inner(value)).is_empty()

    def __aiter__(self):
        """ """

        class Aiter:
            def __init__(self, exc):
                self.i = 0
                self.exc = exc

            async def __anext__(self):
                if self.i == 1:
                    raise StopAsyncIteration()
                value = await self.exc()
                as_opt = opt(value)
                for val in as_opt:
                    self.i += 1
                    return val
                else:
                    raise StopAsyncIteration()

        return Aiter(self._execute)

    async def __call__(self, *args: Any, **kwargs: Any):
        """ """
        value = await self._execute()
        return opt(self._inner(value))(*args, **kwargs)

    def __str__(self) -> str:
        """ """
        return f"<AsyncOption {self._under}>"

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
        return opt(self._inner(result)).match(*whens)


aopt = AsyncOption
