import abc
import asyncio
import typing as t
from inspect import isawaitable

import typing_extensions as te

from seito.monad.func import Default, MatchableMixin, When
from seito.monad.result import Err, Ok, Result, ResultShortcutError

P_mapper = t.ParamSpec("P_mapper")
P = t.ParamSpec("P")
U = t.TypeVar("U")
V_co = t.TypeVar("V_co", covariant=True)

T_err = t.TypeVar("T_err", bound=Exception, covariant=True)


async def _exec(
    fn: t.Callable[P_mapper, U | t.Awaitable[U]],
    *a: P_mapper.args,
    **kw: P_mapper.kwargs,
) -> U:
    current_result = fn(*a, **kw)
    while asyncio.iscoroutine(current_result) or isawaitable(current_result):
        current_result = t.cast(U, await current_result)
    return t.cast(U, current_result)


class AsyncTryBase(abc.ABC, t.Generic[P, V_co, T_err]):
    @abc.abstractmethod
    async def is_ok(self) -> bool:
        ...

    @abc.abstractmethod
    async def is_error(self) -> bool:
        ...

    @abc.abstractmethod
    async def execute(self) -> Result[V_co, T_err]:
        ...

    @abc.abstractmethod
    def map(
        self,
        fn: t.Callable[[V_co], U] | t.Callable[[V_co], t.Awaitable[U]],
    ) -> "AsyncTryBase[P, U, T_err]":
        ...

    @abc.abstractmethod
    async def for_each(self, fn: t.Callable[[V_co | T_err], None]) -> None:
        ...

    @abc.abstractmethod
    def recover(
        self,
        fn: t.Callable[P_mapper, t.Awaitable[V_co] | V_co],
        *args: P_mapper.args,
        **kwargs: P_mapper.kwargs,
    ) -> "AsyncTryBase[P, V_co, T_err]":
        ...

    @abc.abstractmethod
    def recover_with(
        self,
        fn: U | V_co,
    ) -> "AsyncTryBase[P, V_co | U, T_err]":
        ...

    @abc.abstractmethod
    async def or_(self, obj: U) -> V_co | U:
        ...

    @abc.abstractmethod
    async def or_else(
        self,
        fn: t.Callable[P_mapper, t.Awaitable[U] | U],
        *args: t.Any,
        **kwargs: t.Any,
    ) -> U | V_co:
        ...

    @abc.abstractmethod
    async def or_none(self) -> V_co | None:
        ...

    @abc.abstractmethod
    async def or_raise(self, exc: Exception | None = None) -> t.Any | None:
        ...

    @abc.abstractmethod
    async def match(
        self, *whens: When[t.Any, t.Any] | MatchableMixin[t.Any] | Default[t.Any]
    ):
        """ """

    @abc.abstractmethod
    async def _(self):
        ...

    @abc.abstractmethod
    def __getattr__(self, name: str) -> "AsyncTryBase[P, t.Any, T_err]":
        ...

    @abc.abstractmethod
    async def get(self) -> V_co:
        ...


class AsyncTry(AsyncTryBase[P, V_co, T_err]):
    """
    AsyncResult is a monad that represents a computation that may either result in an
    error, or return a successfully computed value.

    example:
    ```python linenums="1"

    async def f(x: int) -> float:
        # simple function that returns 1 / x but may fail when x == 0
        return 1 / x

    x: AsyncTry[int, float, ZeroDivisionError] = AsyncResult(f, ZeroDivisionError)
    y = await x(1).execute()  # Ok(1.0)

    z = await async_try(f, ZeroDivisionError)(0).execute()  # Err(ZeroDivisionError)
    assert z == Err(ZeroDivisionError)

    z = await async_try(f, ZeroDivisionError)(0).or_(0)
    assert z == 0
    ```
    """

    def __init__(
        self,
        aws: t.Callable[P, t.Awaitable[V_co]],
        exc: type[T_err]
        | tuple[type[T_err], ...] = t.cast(tuple[type[T_err], ...], (Exception,)),
    ):
        """

        Args:
            aws (t.Callable[P, t.Awaitable[V]]):


        ```python linenums="1"
        y = AsyncResult(f, ArithmeticError)
        # inferred as AsyncResult[int, float, ArithmeticError]

        x = AsyncResult(f, (ZeroDivisionError, ArithmeticError))
        # inferred as AsyncResult[int, float, ZeroDivisionError | ArithmeticError]

        await y(0).execute() # 💥 because y does not catch ZeroDivisionError

        await x(0).execute() # Err(ZeroDivisionError)

        ```
        """
        self._under = aws
        self.args: tuple[t.Any, ...] = ()
        self.kwargs: dict[str, t.Any] = {}
        self.errors = exc if isinstance(exc, tuple) else (exc,)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> te.Self:
        """
        Set the arguments that will be passed to the underlying function.

        Returns:
            AsyncResult: new instance of AsyncResult with the given arguments

        ```python linenums="1"
        x = AsyncResult(f, ZeroDivisionError)
        # x is new function accepting the same arguments as f

        x(1) # inferred as AsyncResult[int, float, ZeroDivisionError]
        # this statement does not call the underlying function

        # to get the result of the underlying function call `execute`
        await x(1).execute() # Ok(1.0)

        # or use termination operation
        await x(1).or_(0) # 1.0

        z = 100
        await x(1).or_else(lambda : z + 100) # 1.0

        ```
        """
        self.args = args
        self.kwargs = kwargs
        return self

    async def _exec(
        self,
        fn: t.Callable[P_mapper, t.Awaitable[U] | U],
        *args: P_mapper.args,
        **kwargs: P_mapper.kwargs,
    ) -> Result[U, T_err]:
        try:
            r: U = await _exec(fn, *args, **kwargs)
        except Exception as e:
            for err in self.errors:
                if isinstance(e, err):
                    return Err(e)
            raise
        else:
            return Ok(r)

    async def _execute(self) -> Result[V_co, T_err]:
        return await self._exec(self._under, *self.args, **self.kwargs)

    async def execute(self) -> Result[V_co, T_err]:
        """
        Execute the underlying function and return the result.

        Returns:
            Ok[V] | Err[T_err]: Ok or Err depending on the result of the underlying
            function.

        ```python linenums="1"
        x = AsyncResult(f, ZeroDivisionError)

        y = await x(1).execute() # Ok(1.0)

        z = await x(0).execute() # Err(ZeroDivisionError)
        ```
        """
        result = await self._execute()
        return result

    async def is_ok(self):
        """
        Check if the underlying function returned an Ok.

        Returns:
            bool: True if the underlying function returned an Ok, False otherwise.

        ```python linenums="1"

        x = await AsyncResult(f, ZeroDivisionError)(1).is_ok() # True

        x = await AsyncResult(f, ZeroDivisionError)(0).is_ok() # False
        ```
        """
        return (await self._execute()).is_ok()

    async def is_error(self):
        """
        Check if the underlying function returned an Err.

        Returns:
            bool: True if the underlying function returned an Err, False otherwise.

        ```python linenums="1"

        x = await AsyncResult(f, ZeroDivisionError)(1).is_error() # False

        x = await AsyncResult(f, ZeroDivisionError)(0).is_error() # True
        ```
        """
        return (await self._execute()).is_error()

    async def _execute_or_clause_if(
        self,
        predicate: t.Callable[[t.Any], bool],
        or_f: t.Callable[P_mapper, t.Awaitable[U] | U],
        *args: P_mapper.args,
        **kwargs: P_mapper.kwargs,
    ) -> U | V_co:
        """ """
        result = await self._execute()
        if predicate(result):
            if not callable(or_f):
                return t.cast(U, or_f)
            r: U = await _exec(or_f, *args, **kwargs)
            return r
        return t.cast(V_co, result.get())

    def map(
        self,
        fn: t.Callable[[V_co], U] | t.Callable[[V_co], t.Awaitable[U]],
    ) -> "AsyncTry[P, U, T_err]":
        """
        Map the result of the underlying function to a new value.

        Args:
            fn (t.Callable[[V], T_output] | t.Callable[[V],
            t.Awaitable[T_output]] | T_output):

        Returns:
            AsyncResult[P, T_output, T_err]: new instance of AsyncResult with the

        ```python linenums="1"
        # define an async result
        x = AsyncResult(f, ZeroDivisionError)

        r = x(1).map(lambda x: x + 1)
        # ⚠️ does not execute the function, only composition occurs
        # to call the function use `execute` or other termination operation
        await r.execute() # Ok(2.0)

        y: float = await x(1).map(lambda x: x + 1).or_(0)
        z: str = await x(0).map(lambda x: str(x)).or_("")
        ```
        """

        async def compose(*args: P.args, **kwargs: P.kwargs) -> U:
            result: V_co = await _exec(self._under, *args, **kwargs)
            r: U = await _exec(fn, result)
            return r

        r: AsyncTry[P, U, T_err] = AsyncTry(compose, self.errors)
        r.args = self.args
        r.kwargs = self.kwargs
        return r

    async def for_each(self, fn: t.Callable[[V_co | T_err], None]) -> None:
        """


        Args:
            fn (t.Callable[[V  |  T_err], None]): _description_

        ```python linenums="1"

        # print the result of the underlying function
        await async_result(f, ZeroDivisionError)(1).for_each(print)
        ```
        """
        result = await self._execute()
        flattened = result.flatten()
        fn(flattened.get())

    def recover_with(self, fn: V_co | U) -> "AsyncTry[P, V_co | U, T_err]":
        """
        Recover from an error by returning a new AsyncResult.

        Args:
            fn (V_co | U): _description_

        Returns:
            AsyncTry[P, V_co | U, T_err]: _description_

        ```python linenums="1"
        x: AsyncTry[int, int, Exception] = AsyncTry(lambda: 1 / 0)
        y = await x().recover_with(1).execute()  # Ok(1)
        assert y.is_ok()
        assert y == Ok(1)
        ```
        """

        async def compose(*p_args: P.args, **p_kwargs: P.kwargs) -> V_co | U:
            try:
                result: V_co = await _exec(self._under, *p_args, **p_kwargs)
            except Exception:
                return fn
            return result

        r: AsyncTry[P, V_co | U, T_err] = AsyncTry(compose, self.errors)
        r.args = self.args
        r.kwargs = self.kwargs
        return r

    def recover(
        self,
        fn: t.Callable[P_mapper, t.Awaitable[V_co] | V_co],
        *a: P_mapper.args,
        **kw: P_mapper.kwargs,
    ) -> "AsyncTry[P, V_co, T_err]":
        """
        Recover from an error by executing a new function.

        Args:
            obj (t.Callable[P_mapper, V | t.Awaitable[V]]): function to execute

        Returns:
            AsyncResult[P, V, T_err]: new AsyncResult

        ```python linenums="1"
        x: AsyncTry[int, int, Exception] = async_try(lambda: 1 / 0)
        y = await x().recover(lambda: 1).execute()  # Ok(1)

        assert y.is_ok()
        assert y == Ok(1)
        ```
        """

        async def compose(*p_args: P.args, **p_kwargs: P.kwargs) -> V_co:
            try:
                result: V_co = await _exec(self._under, *p_args, **p_kwargs)
            except Exception:
                result = await _exec(fn, *a, **kw)
            return result

        r: AsyncTry[P, V_co, T_err] = AsyncTry(compose, self.errors)
        r.args = self.args
        r.kwargs = self.kwargs
        return r

    async def get(self):
        """
        Get the result of the underlying function.

        ```python linenums="1"
        x = AsyncResult(f, ZeroDivisionError)
        await x(1).get() # 2.0
        ```
        """
        result = await self._execute()
        return result.get()

    async def or_none(self):
        """
        Get the result of the underlying function or None if the result is an Err.

        Returns:
            _type_: _description_

        ```python linenums="1"
        x = AsyncResult(f, ZeroDivisionError)
        await x(1).or_none() # 2.0

        await x(0).or_none() # None
        ```
        """
        result = await self._execute()
        return result.or_none()

    async def or_(
        self,
        fn: V_co | U,
    ) -> U | V_co:
        """
        Get the result of the underlying function or the given value if the result is an
        Args:
            fn (V_co | U): _description_

        Returns:
            U | V_co: _description_

        ```python linenums="1"
        x = AsyncResult(f, ZeroDivisionError)
        await x(1).or_(0) # 1.0

        await x(0).or_(0) # 0
        ```
        """
        return fn

    async def or_else(
        self,
        fn: t.Callable[P_mapper, t.Awaitable[U] | U],
        *args: P_mapper.args,
        **kwargs: P_mapper.kwargs,
    ) -> U | V_co:
        """
        Get the result of the underlying function or the result of the given function if
        the result is an Err.

        ```python linenums="1"
        x = AsyncResult(f, ZeroDivisionError)
        await x(1).or_else(lambda: 0) # 1.0

        z: float = compute_something()
        await x(0).or_else(lambda: z + 1000) # z + 1000
        ```
        """

        def check_value(step_result: t.Any) -> bool:
            return isinstance(step_result, (Err, Exception))

        return await self._execute_or_clause_if(check_value, fn, *args, **kwargs)

    async def or_raise(self, exc: Exception | None = None) -> t.Any | None:
        """
        Get the result of the underlying function or raise the given exception if the
        result is an Err.

        ```python linenums="1"

        x = AsyncResult(f, ZeroDivisionError)
        await x(1).or_raise() # 1.0

        await x(0).or_raise() # 🔥 ZeroDivisionError
        ```
        """
        result = await self._execute()
        return result.flatten().or_raise(exc if exc is not None else ValueError())

    async def __aiter__(self):
        """
        Iterate over the result of the underlying function.

        ```python linenums="1"
        async for x in async_result(f, ZeroDivisionError)(1):
            print(x) # 2.0

        async for x in async_result(f, ZeroDivisionError)(1):
            print(x) # ZeroDivisionError
        ```
        """
        r = await self._execute()
        for val in r:
            yield val

    def __str__(self) -> str:
        """
        String representation of the AsyncResult.
        """
        return f"<AsyncTry {repr(self._under)}>"

    def __getattr__(self, name: str) -> "AsyncTry[P, t.Any, T_err]":
        """
        Get an attribute of the result of the underlying function.

        ```python linenums="1"
        class Foo:
            foo: int = 1

        async def f() -> Foo:
            return Foo()

        x = AsyncResult(f, ZeroDivisionError)
        assert await x().foo.execute() == Ok(1)

        assert await x().foo.or_(0) == 1

        assert await x().bar.execute() == Err(AttributeError())

        ```
        """

        async def compose(*args: P.args, **kwargs: P.kwargs) -> t.Any:
            result: V_co = await _exec(self._under, *args, **kwargs)
            r: t.Any = await _exec(getattr, result, name)
            return r

        r = AsyncTry(compose, self.errors)
        r.args = self.args
        r.kwargs = self.kwargs
        return r

    async def match(
        self, *whens: When[t.Any, t.Any] | MatchableMixin[t.Any] | Default[t.Any]
    ):
        """
        Match the result of the underlying function.

        Returns:
            _type_: _description_

        ```python linenums="1"
        x = AsyncResult(f, ZeroDivisionError)
        r = await x(1).match(
            Ok(_),
            default >> 0

        assert r == 1.0

        # replace the default with a matchable
        match await x(1):
            case Ok(val):
                result = val
            case Err(e):
                result = e
            case _:
                result = 0
        ```
        """
        result: Ok[V_co] | Err[T_err] = await self._execute()
        return result.match(*whens)

    async def _(self) -> V_co:
        """
        Get the result of the underlying function or raise a ResultShortcutError if the
        underlying function returns an Err.

        Raises:
            ResultShortcutError: _description_
            ValueError: _description_

        Returns:
            V_co: _description_
        """
        result: Ok[V_co] | Err[T_err] = await self._execute()
        match result:
            case Err(e):
                raise ResultShortcutError(e)
            case Ok(v):
                return v
            case _:
                raise ValueError("Invalid result")


async_try = AsyncTry
Future = AsyncTry


def lift_future(
    f: t.Callable[P_mapper, t.Awaitable[U]]
) -> t.Callable[..., AsyncTry[P_mapper, U, Exception]]:
    """
    Lift a function to a Future or AsyncTry.

    Args:
        f (t.Callable[P_mapper, t.Awaitable[U]]): Async function to lift

    Raises:
        TypeError: type error is raised if the function is not async

    Returns:
        a function that originally take f parameters and return an AsyncTry object

    ```python linenums="1"
    @lift_future
    async may_fail(a: int) -> int:
        return a / 0

    assert await may_fail(0).execute() == Err(ZeroDivisionError())
    assert await may_fail(1).execute() == Ok(1)

    ```
    """
    if not asyncio.iscoroutinefunction(f):
        raise TypeError("Can only be used on async function")

    def wrapper(*args: P_mapper.args, **kwargs: P_mapper.kwargs):
        return async_try(f)(*args, **kwargs)

    return wrapper
