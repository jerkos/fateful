import typing as t
from dataclasses import dataclass

from seito.monad.container import CommonContainer, EmptyError
from seito.monad.func import apply

T_co = t.TypeVar("T_co", covariant=True)
U = t.TypeVar("U")
V = t.TypeVar("V")
P = t.ParamSpec("P")


class OptionContainer(CommonContainer[T_co], t.Protocol):
    def is_some(self) -> bool:  # pragma: no cover
        ...

    def is_empty(self) -> bool:  # pragma: no cover
        ...

    def or_if_falsy(
        self, obj: t.Callable[P, t.Any] | t.Any, *args: P.args, **kwargs: P.kwargs
    ) -> t.Any:  # pragma: no cover
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
            T: _description_
        """
        return self._under

    def is_some(self) -> bool:
        """
        Check if the container is a Some.

        Returns:
            bool: _description_
        """
        return True

    def is_empty(self) -> bool:
        """
        Check if the container is empty.

        Returns:
            bool: True if the container is empty, False otherwise.
        """
        return False

    @t.overload
    def flatten(self: "Nested[Empty]") -> "Empty":
        ...

    @t.overload
    def flatten(self: "Nested[Q]") -> "Some[Q]":
        ...

    def flatten(self) -> "Some | Empty":
        """
        Flatten the container i.e. transform Some(Some(x)) into Some(x).

        Returns:
            Some | Empty: _description_
        """
        x = self._under
        while isinstance(x, (Some, Empty)):
            x = x._under  # type: ignore
        return opt(x)

    @t.overload
    def or_else(
        self, obj: t.Callable[P, t.Any], *args: P.args, **kwargs: P.kwargs
    ) -> T_co:
        ...

    @t.overload
    def or_else(self, obj: t.Any) -> T_co:
        ...

    def or_else(
        self, obj: t.Callable[P, t.Any] | t.Any, *args: P.args, **kwargs: P.kwargs
    ) -> T_co:
        """
        Apply a function to the value of the container.
        Args:
            obj (t.Callable[P, t.Any]): _description_

        Returns:
            T: _description_
        """
        return self._under

    unwrap_or_else = or_else

    def or_if_falsy(
        self, obj: t.Callable[P, U], *args: P.args, **kwargs: P.kwargs
    ) -> T_co | U:
        """
        Apply a function to the value of the container if it is falsy.

        Args:
            obj (t.Callable[P, U]): _description_

        Returns:
            T | U: _description_
        """
        return self._under or apply(obj, *args, **kwargs)

    def or_none(self) -> T_co:
        """
        Return the value of the container if it is not None.

        Returns:
            T: _description_
        """
        return self._under

    def or_raise(self, exc: Exception | None = None) -> T_co:
        """
        Return the value of the container if it is not None.

        Args:
            exc (Exception | None, optional): _description_. Defaults to None.

        Returns:
            T: _description_
        """
        return self._under

    def map(self, func: t.Callable[[T_co], U]) -> "Some[U]":
        """
        Apply a function to the value of the container.

        Args:
            func (t.Callable[[T], U]): _description_

        Returns:
            Some[U]: _description_
        """
        result = apply(func, self._under)
        result = opt(result)
        return result

    def __iter__(self) -> t.Generator[T_co, t.Any, None]:
        """
        Iterate over the value of the container.

        Returns:
            t.Iterator[T]: _description_

        Yields:
            Iterator[t.Iterator[T]]: _description_
        """
        yield self.flatten().get()

    def __getattr__(self, name: str) -> "Some | Empty | t.Callable":
        """
        Get an attribute of the value of the container.

        Args:
            name (str): _description_

        Returns:
            Some | Empty | t.Callable: _description_
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
            str: _description_
        """
        return f"<Some {str(self._under)}>"


@dataclass(unsafe_hash=True)
class Empty(OptionContainer[None]):
    """ """

    _under: None = None

    def get(self) -> t.NoReturn:
        raise EmptyError("Option is empty")

    def is_some(self) -> bool:
        return False

    def is_empty(self) -> bool:
        return True

    def or_(self, obj: U) -> U:
        return obj

    @t.overload
    def or_else(self, obj: t.Callable[P, U], *args: P.args, **kwargs: P.kwargs) -> U:
        ...

    @t.overload
    def or_else(self, obj: U) -> U:
        ...

    def or_else(
        self, obj: t.Callable[P, U] | U, *args: P.args, **kwargs: P.kwargs
    ) -> U:
        return apply(obj, *args, **kwargs)

    def unwrap_or_else(
        self, obj: t.Callable[P, U], *args: P.args, **kwargs: P.kwargs
    ) -> U:
        return self.or_else(obj, *args, **kwargs)

    def or_if_falsy(
        self, obj: t.Callable[P, U] | U, *args: P.args, **kwargs: P.kwargs
    ) -> U:
        x = apply(obj, *args, **kwargs)
        return x

    def or_none(self) -> None:
        return None

    def or_raise(self, exc: Exception | None = None) -> t.NoReturn:
        if exc is None:
            raise EmptyError("Option is empty")
        raise exc

    def map(
        self,
        func: t.Callable,
    ) -> "Empty":
        return self

    def __iter__(self) -> "t.Iterator[Empty]":
        return self

    def __next__(self):
        raise StopIteration()

    def __getattr__(self, name: str) -> "Empty":
        return self

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "Empty":
        return self

    def __str__(self) -> str:
        return "<Empty>"


T_err = t.TypeVar("T_err", bound=Exception, covariant=True)


# @t.overload
# def unravel_container(
#    value: T,  # not a some
#    last_container: T | None = None,
# ) -> tuple[T, T | None]:
#    ...


# @t.overload
# def unravel_container(
#    value: Some[Some[Some[U]]],
# ) -> tuple[U, Some[U]]:
#    ...


# @t.overload
# def unravel_container(
#    value: t.Any,
#    last_container: t.Any | None = None,
# ) -> tuple[t.Any, t.Any]:
#    ...


# @t.overload
# def unravel_container(
#    value: Some[Some[T]],
# ) -> Some[T]:
#    ...


def unravel_container(value):
    match value:
        case Some(under) | Empty(under):
            return unravel_container(under)
        case _:
            return value


OPT_MATCHABLE_CLASSES = {Some, Empty}
Some.__matchable_classes__ = OPT_MATCHABLE_CLASSES
Empty.__matchable_classes__ = OPT_MATCHABLE_CLASSES


T_opt = t.TypeVar("T_opt")


@t.overload
def option(value: None) -> Empty:
    ...


@t.overload
def option(value: T_opt) -> Some[T_opt]:
    ...


def option(value: T_opt) -> Some[T_opt] | Empty:
    """ """
    return Null if value is None else Some(value)


def lift_opt(f: t.Callable[P, U]) -> t.Callable[P, Some[U] | Empty]:
    """ """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Some[U] | Empty:
        val: U = f(*args, **kwargs)
        return opt(val)

    return wrapper


# aliases
none = nope = empty = Null = Empty(None)
opt = option
