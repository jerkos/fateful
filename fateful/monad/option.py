import abc
import typing as t
from dataclasses import dataclass

from fateful.monad.container import CommonContainer, EmptyError

T_co = t.TypeVar("T_co", covariant=True)
V = t.TypeVar("V")
P = t.ParamSpec("P")


class OptionContainer(CommonContainer[T_co], abc.ABC):
    @abc.abstractmethod
    def is_some(self) -> bool:  # pragma: no cover
        ...

    @abc.abstractmethod
    def is_empty(self) -> bool:  # pragma: no cover
        ...

    @abc.abstractmethod
    def or_if_falsy(self, obj: V) -> T_co | V:  # pragma: no cover
        """ """
        ...

    @abc.abstractmethod
    def or_else_if_falsy(
        self, obj: t.Callable[P, V], *args: P.args, **kwargs: P.kwargs
    ) -> T_co | V:  # pragma: no cover
        """ """
        ...


Q = t.TypeVar("Q")

Nested: t.TypeAlias = "Some[Q | Nested[Q]]"


@dataclass(unsafe_hash=True, frozen=True)
class Some(OptionContainer[T_co]):
    """ """

    _under: T_co

    def get(self) -> T_co:
        """
        get the value of the Some container

        Returns:
            T: value of the container

        ```python
        x: Some[int] = opt(1).get()
        assert Some(1).get() == 1

        x: Empty = Null
        x.get()  # raises EmptyError !


        ```
        """
        return self._under

    def is_some(self) -> bool:
        """
        Check if the container is a Some.

        Returns:
            bool: true if the container is a Some, false otherwise.

        ```python
        x: Some[int] = opt(1)
        assert x.is_some() == True

        y = Null
        assert y.is_some() == False
        ```
        """
        return True

    def is_empty(self) -> bool:
        """
        Check if the container is empty.

        Returns:
            bool: True if the container is empty, False otherwise.

         ```python
        x = Null
        assert x.is_empty() == True

        y = Some(1)
        assert y.is_empty() == False
        ```
        """
        return False

    @t.overload
    def flatten(self: "Nested[Empty]") -> "Empty":  # type: ignore[misc]
        ...

    @t.overload
    def flatten(self: "Nested[Q]") -> "Some[Q]":
        ...

    def flatten(self) -> "Some | Empty":
        """
        Flatten the container i.e. transform Some(Some(x)) into Some(x).

        Returns:
            Some | Empty: the flattened container.

        ```python
        x: Some[Some[int]] = Some(Some(1))
        y: Some[int] = x.flatten()  # Some(1)
        assert y == Some(1)

        z: Some[Some[Empty]] = Some(Some(Null))
        a = z.flatten()  # Empty
        assert a == Null
        ```
        """
        x = self._under
        while isinstance(x, (Some, Empty)):
            x = x._under  # type: ignore
        return opt(x)

    def or_(self, obj: t.Any) -> T_co:
        """
        Return the value of the container.
        Args:
            obj (t.Any): an object

        Returns:
            T_co: the value of the container.

        ```python
        x: Some[int] = opt(1)
        y = x.or_(2)  # 1
        assert y == 1

        z = Null
        assert z.or_(2) == 2
        ```
        """
        return self._under

    def or_else(self, obj: t.Callable[P, V], *args: P.args, **kwargs: P.kwargs) -> V:
        """
        Apply a function to the value of the container.
        Args:
            obj (t.Callable[P, t.Any]): _description_

        Returns:
            T: return the value of the container.

        ```python
        x: Some[int] = opt(1)
        assert x.or_else(lambda z: z + 100, 1) == 1

        y = Null
        assert x.or_else(lambda z: z + 100, 1) == 101
        ```
        """
        return t.cast(V, self._under)

    unwrap_or_else = or_else  # type: ignore[assignment]

    def or_if_falsy(self, obj: V) -> T_co | V:
        """
        Return the value of the container or provided value if it is falsy.

        Args:
            obj (V): value to return if the container is falsy.

        Returns:
            T_co | V: value of the container or provided value if it is falsy.

        ```python
        x: Some[int] = opt(0)
        assert x.or_if_falsy(1) == 1
        ```
        """
        return self._under or obj

    def or_else_if_falsy(
        self, obj: t.Callable[P, V], *args: P.args, **kwargs: P.kwargs
    ) -> T_co | V:
        """
        Apply a function to the value of the container if it is falsy.

        Args:
            obj (t.Callable[P, U]): function to apply if contained value is falsy.

        Returns:
            T | U: value of the container or result of the function if it is falsy.

        ```python
        x: Some[int] = opt(0)
        assert x.or_else_if_falsy(lambda x: x + 101, 1) == 101
        ```
        """
        return self._under or obj(*args, **kwargs)

    def or_none(self) -> T_co:
        """
        Return the value of the container if it is not None.

        Returns:
            T: returns the value of the container.

        ```python
        x: Some[int] = opt(0)
        assert x.or_none() == 0  # 0
        ```
        """
        return self._under

    def or_raise(self, exc: Exception | None = None) -> T_co:
        """
        Return the value of the container if it is not None.

        Args:
            exc (Exception | None, optional): Exception to raise. Defaults to None.

        Returns:
            T: the underlying value of the container.

        ```python
        x: Some[int] = opt(0)
        assert x.or_raise() == 0  # 0
        ```
        """
        return self._under

    def map(self, func: t.Callable[[T_co], V]) -> "Some[V]":
        """
        Apply a function to the value of the container.

        Args:
            func (t.Callable[[T], U]): function to apply on the underlying value.

        Returns:
            Some[V]: Some if the function returns a value

        ```python
        x: Some[int] = opt(0)
        assert x.map(lambda c: c + 1).get() == 1  # 1

        y: Some[str] = opt(1).map(lambda c: str(c))
        ```
        """
        result = func(self._under)
        opt_result = opt(result)
        return opt_result

    def __iter__(self) -> t.Generator[T_co, t.Any, None]:
        """
        Iterate over the value of the container.

        Yields:
            Iterator[t.Iterator[T]]: _description_

        ```python
        for i in opt(0):
            print(i)  # 0
        ```
        """
        yield self.flatten().get()

    def __getattr__(self, name: str) -> "Some | Empty | t.Callable":
        """
        Get an attribute of the value of the container.

        Args:
            name (str): name of the attribute.

        Returns:
            Some | Empty | t.Callable: Some if the attribute exists, Empty otherwise.

        ```python
        class Foo:
            foo: int = 1
        x: Some[Foo] = opt(Foo())
        x.foo.get() == 1
        assert x.bar.is_empty()  # True
        ```
        """
        try:
            attr = getattr(self._under, name)
        except AttributeError:
            return none
        if callable(attr):

            def wrapper(*args: t.Any, **kwargs: t.Any) -> "Some[t.Any] | Empty":
                return opt(attr(*args, **kwargs))

            return wrapper
        return opt(attr)

    def __str__(self) -> str:
        """
        Return the string representation of the container.

        Returns:
            str: a string representation of the container.

        ```python
        str(Some(1)) # "<Some 1>"
        ```
        """
        return f"<Some {str(self._under)}>"


@dataclass(unsafe_hash=True)
class Empty(OptionContainer[None]):
    """ """

    _under: None = None

    def get(self) -> t.NoReturn:
        """
        Raise an EmptyError.

        Raises:
            EmptyError: because of getting on empty container.

        Returns:
            t.NoReturn: never returns.
        """
        raise EmptyError("Option is empty")

    def is_some(self) -> bool:
        """
        Return False.

        Returns:
            bool: always False.
        """
        return False

    def is_empty(self) -> bool:
        """
        Return True.

        Returns:
            bool: always True.
        """
        return True

    def or_(self, obj: V) -> V:
        """
        Return the provided value.

        Args:
            obj (V): provided value.

        Returns:
            V: provided value.

        ```python
        x: Empty = Null
        assert x.or_(1) == 1
        ```
        """
        return obj

    def or_else(self, obj: t.Callable[P, V], *args: P.args, **kwargs: P.kwargs) -> V:
        """
        Apply a function to produce a result. Computed lazily.

        Args:
            obj (t.Callable[P, V]): function to apply.

        Returns:
            V: return the result of the function.

        ```python
        x: Empty = Null
        x.or_else(lambda: 1) == 1
        ```
        """
        return obj(*args, **kwargs)

    def or_if_falsy(self, obj: V) -> V:
        """
        Return the provided value.

        Args:
            obj (V): provided value.

        Returns:
            V: provided value.

        ```python
        x = Null
        assert x.or_if_falsy(1) == 1
        ```
        """
        return obj

    def or_else_if_falsy(
        self, obj: t.Callable[P, V], *args: P.args, **kwargs: P.kwargs
    ) -> V:
        """
        Apply a function to produce a result. Computed lazily.

        Args:
            obj (t.Callable[P, V]): function to apply.

        Returns:
            V: result of the function.

        ```python
        x = Null
        assert x.or_else_if_falsy(lambda x: 2**4, 1) == 1
        ```
        """
        x = obj(*args, **kwargs) if callable(obj) else obj
        return x

    def or_none(self) -> None:
        """
        Return None.

        Returns:
            None: None.

        ```python
        x = Null
        assert x.or_none() is None
        ```
        """
        return None

    def or_raise(self, exc: Exception | None = None) -> t.NoReturn:
        """
        Raise an exception.

        Args:
            exc (Exception | None, optional): Exception to be raised. Defaults to None.

        Raises:
            EmptyError: if no exception is provided.
            exc: if an exception is provided.

        Returns:
            t.NoReturn: never returns.

        ```python
        x = Null
        x.or_raise()  # raises EmptyError
        x.or_raise(ValueError())  # raises ValueError
        ```
        """
        if exc is None:
            raise EmptyError("Option is empty")
        raise exc

    def map(self, func: t.Callable[[t.Any], t.Any]) -> "Empty":
        """
        Return an empty container.

        Args:
            func (t.Callable[[t.Any], t.Any]): function to apply.

        Returns:
            Empty: an empty container.
        """
        return self

    def __iter__(self) -> "t.Iterator[Empty]":
        """
        Return an empty iterator.

        Returns:
            t.Iterator[Empty]: empty iterator.
        """
        return self

    def __next__(self):
        raise StopIteration()

    def __getattr__(self, name: str) -> "Empty":
        """
        Return an empty container.

        Args:
            name (str): name of the attribute.

        Returns:
            Empty: an empty container.
        """
        return self

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "Empty":
        """
        Return an empty container.

        Returns:
            Empty: return an empty container.
        """
        return self

    def __str__(self) -> str:
        return "<Empty>"

    def flatten(self) -> "Empty":
        """
        Flatten the container.

        Returns:
            Empty: return self
        """
        return self


T_err = t.TypeVar("T_err", bound=Exception, covariant=True)


OPT_MATCHABLE_CLASSES = {Some, Empty}
Some.__matchable_classes__ = OPT_MATCHABLE_CLASSES
Empty.__matchable_classes__ = OPT_MATCHABLE_CLASSES


T_opt = t.TypeVar("T_opt")


@t.overload
def option(value: None) -> Empty:  # type: ignore[misc]
    ...


@t.overload
def option(value: T_opt) -> Some[T_opt]:
    ...


def option(value: T_opt | None) -> Some[T_opt] | Empty:
    return Null if value is None else Some(value)


def lift_opt(f: t.Callable[P, V]) -> t.Callable[P, Some[V] | Empty]:
    """ """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Some[V] | Empty:
        val: V = f(*args, **kwargs)
        return opt(val)

    return wrapper


# aliases
none = nope = empty = Null = Empty(None)
opt = option
