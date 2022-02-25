from asyncio import iscoroutinefunction
from typing import Awaitable, Callable, Any

from aflowey import aflow, partial, CANCEL_FLOW
from aflowey.single_executor import _exec
from loguru import logger

from seito.monad.opt import T, Option, identity, opt, When, Default


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
        # currently, a bug exists in aflowey, have to check the return value
        # of the first call
        value = await init_f()
        if value is CANCEL_FLOW or value is None:
            return value
        flow = aflow.from_args(value) >> identity
        for (f, a, kw) in self._mappers:
            flow = flow >> breaker_wrapper(partial(f, *a, **kw))
        try:
            return await flow.run()
        except Exception as e:
            logger.error(e)
            return e

    async def _execute_or_clause(self, or_f, *args, **kwargs):
        if iscoroutinefunction(or_f):
            return await or_f(*args, **kwargs)
        elif callable(or_f):
            return or_f(*args, **kwargs)
        return or_f

    async def _execute_or_clause_if(self, predicate, or_f, *args, **kwargs):
        value = await self._execute()
        if predicate(value):
            return await self._execute_or_clause(or_f, *args, **kwargs)
        return value

    def map(self, f, *args, **kwargs):
        self._mappers.append((f, args, kwargs))
        return self

    async def get(self) -> Any:
        result = await self._execute()
        return opt(result).get()

    async def or_none(self) -> Any:
        value = await self._execute()
        return opt(value).or_none()

    async def or_else(self, or_f: Callable[..., Any] | T, *args: Any, **kwargs: Any) -> T:
        predicate = lambda value: value is None or value is CANCEL_FLOW or isinstance(value, Exception)
        return await self._execute_or_clause_if(predicate, or_f, *args, **kwargs)

    async def or_if_falsy(self, or_f: Callable[..., Any] | Any, *args: Any, **kwargs: Any) -> Any:
        return await self._execute_or_clause_if(lambda value: not value, or_f, *args, **kwargs)

    async def or_raise(self, exc: Exception):
        value = await self._execute()
        return opt(value).or_raise(exc)

    async def is_empty(self) -> bool:
        value = await self._execute()
        return opt(value).is_empty()

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

    async def match(self, *whens: When | Default):
        result = await self._execute()
        return opt(result).match(*whens)


aopt = AsyncOption