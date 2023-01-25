import asyncio
import functools
from inspect import isawaitable
from typing import Callable, Any, TypeVar, Type, Coroutine, NoReturn

from seito.monad.container import (
    unravel_container,
    Func,
)
from seito.monad.func import flip, When, Default, Matchable
from seito.monad.result import Err, Result, ResultContainer


async def _exec(function: Callable[..., Any], *a: Any, **kw: Any) -> Any:
    if not callable(function):
        return function
    current_result = function(*a, **kw)
    while asyncio.iscoroutine(current_result) or isawaitable(current_result):
        current_result = await current_result
    return current_result


T = TypeVar("T")


class AsyncResult(ResultContainer[T]):
    """ """

    def __init__(
        self,
        aws: Callable[..., Coroutine[Any, Any, T]],
        *args: Any,
        **kwargs: Any,
    ):
        self.aws = aws
        self.args = args
        self.kwargs = kwargs
        self.errors: tuple[Type[Exception], ...] = (Exception,)
        self._mappers: list[tuple[Callable[..., Any], Any, Any, bool]] = []

    def on_error(self, *errors: Type[Exception]):
        if not all(issubclass(e, Exception) for e in errors):
            raise ValueError("Error")
        self.errors = errors or (Exception,)
        return self

    def __call__(self, *args, **kwargs) -> "AsyncResult[T]":
        self.args = args
        self.kwargs = kwargs
        return self

    async def _exc_step(self, f, *args: Any, _is_recover: bool = False, **kwargs: Any):
        if _is_recover is True:
            return Result(await _exec(f, *args, **kwargs))
        try:
            r = await _exec(f, *args, **kwargs)
        except self.errors as e:
            return Err(e)
        else:
            return Result(r)

    async def _execute(self) -> Result[T] | Err[Exception]:
        """ """
        result = await self._exc_step(self.aws, *self.args, **self.kwargs)
        match result:  # noqa: E999
            case Err():
                is_error = True
            case _:
                is_error = False

        for f, a, kw, is_recover in self._mappers:
            if is_error and not is_recover:
                # try to find a recover so continue
                continue
            elif is_error and is_recover:
                # execute recover without current holding value
                result = await self._exc_step(f, *a, _is_recover=is_recover, **kw)
            else:
                # not on error execute new mapper on current holding value
                result = await self._exc_step(f, result.get(), *a, _is_recover=is_recover, **kw)
        else:
            print(result, is_error)
            return result

    async def is_result(self):
        return (await self._execute()).is_result()

    async def is_error(self):
        return (await self._execute()).is_error()

    async def _execute_or_clause_if(self, predicate, or_f, *args, **kwargs) -> T:
        """ """
        result = await self._execute()
        if predicate(result):
            return await _exec(or_f, *args, **kwargs)
        _, container = unravel_container(result)
        return container.get()

    def map(self, func: Func, *args: Any, **kwargs: Any) -> "AsyncResult[T]":
        """ """
        self._mappers.append((func, args, kwargs, False))
        return self

    async def for_each(self, f: Func, *args: Any, **kwargs: Any) -> None:
        result = await self._execute()
        result, _ = unravel_container(result)
        f(result, *args, **kwargs)

    def recover(
        self, obj: Callable[..., Any] | Any, *args: Any, **kwargs: Any
    ) -> "AsyncResult[T]":
        self._mappers.append((obj, args, kwargs, True))
        return self

    async def get(self):
        """ """
        result = await self._execute()
        _, container = unravel_container(result)
        return container.get()

    async def or_none(self):
        """ """
        result = await self._execute()
        _, container = unravel_container(result)
        return result.or_none()

    async def or_else(self, obj: Func | Any, *args: Any, **kwargs: Any) -> T:
        """ """

        def check_value(step_result: Any):
            return isinstance(step_result, (Err, Exception)) or (step_result is None)

        return await self._execute_or_clause_if(check_value, obj, *args, **kwargs)

    async def or_raise(self, exc: Exception | None = None) -> T | NoReturn:
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
        return f"<AsyncTry {repr(self._under)}>"

    def __iter__(self):
        """ """
        raise NotImplementedError()  # pragma: no cover

    def __getattr__(self, name: str) -> Any:
        """ """
        self._mappers.append((functools.partial(flip(getattr)), (name,), {}, False))
        return self

    async def match(self, *whens: When | Default | Matchable):
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
        >>>await (
        >>>    AsyncResult.of(test, 1)
        >>>    .map(lambda x: x - 100)
        >>>    .for_each(lambda x: print(x == val))
        >>>)

        """
        future = AsyncResult(f, *args, **kwargs)
        return future


async_try = AsyncResult
Future = AsyncResult


def lift_future(f) -> Callable[..., AsyncResult]:
    if not asyncio.iscoroutinefunction(f):
        raise TypeError("Can only be used on async function")

    def wrapper(*args, **kwargs):
        return AsyncResult.of(f, *args, **kwargs)

    return wrapper
