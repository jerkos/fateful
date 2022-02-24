from asyncio import iscoroutinefunction
from asyncio import iscoroutinefunction
from typing import Awaitable, Callable, Any

from aflowey import aflow, partial, CANCEL_FLOW
from aflowey.single_executor import _exec
from loguru import logger

from seito.monad.opt import T, Option, identity, opt


def breaker_wrapper(f):
    async def w(*args, **kwargs):
        value = await _exec(f, *args, **kwargs)
        if value is None:
            return CANCEL_FLOW
        return value

    return w


class AsyncOption(Option):

    def __init__(self, aws: Awaitable[Any] | Any, *args: Any, **kwargs: Any) -> None:
        self._under = aws
        self.args = args
        self.kwargs = kwargs
        self._mappers = []

    async def _execute(self):
        init_f = partial(self._under, *self.args, **self.kwargs) if callable(self._under) else self._under
        value = await init_f()
        logger.debug(value)
        if value is CANCEL_FLOW or value is None:
            return value
        flow = aflow.from_args(value) >> identity
        for (f, a, kw) in self._mappers:
            flow = flow >> breaker_wrapper(partial(f, *a, **kw))
        return await flow.run()

    async def _execute_or_clause(self, or_f, *args, **kwargs):
        if iscoroutinefunction(or_f):
            return await or_f(*args, **kwargs)
        elif callable(or_f):
            return or_f(*args, **kwargs)
        return or_f

    async def _execute_or_clause_if(self, predicate, or_f, *args, **kwargs):
        value = await self._execute()
        logger.debug(value)
        if predicate(value):
            return await self._execute_or_clause(or_f, *args, **kwargs)
        return value

    def map(self, f, *args, **kwargs):
        self._mappers.append((f, args, kwargs))
        return self

    async def get(self) -> Any:
        return await self._execute()

    async def or_none(self) -> Any:
        value = await self._execute()
        return opt(value).or_none()

    async def or_else(self, or_f: Callable[..., Any] | T, *args: Any, **kwargs: Any) -> T:
        return await self._execute_or_clause_if(lambda value: value is None or value is CANCEL_FLOW, or_f, *args,
                                                **kwargs)

    async def or_if_falsy(self, or_f: Callable[..., Any] | Any, *args: Any, **kwargs: Any) -> Any:
        return await self._execute_or_clause_if(lambda value: not value, or_f, *args, **kwargs)

    async def is_empty(self) -> bool:
        value = await self._execute()
        return opt(value).is_empty()

    async def flat_map(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> "Option":
        value = await self._execute()
        return opt(value).flat_map(func, *args, **kwargs)

    def __aiter__(self):
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
        value = await self._execute()
        return opt(value)(*args, **kwargs)

    def __str__(self) -> str:
        return f"<AsyncOption {self._under}>"

    def __iter__(self):
        raise NotImplementedError()

    def __getattr__(self, name: str) -> Any:
        raise NotImplementedError()


aopt = AsyncOption
