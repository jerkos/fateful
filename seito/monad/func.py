import dataclasses
import typing as t
from dataclasses import dataclass

from pampy import _ as __
from pampy.helpers import UnderscoreType
from pampy.pampy import match_dict as pampy_dict_matcher

_ = __

T = t.TypeVar("T")


def identity(x: T) -> T:
    """ """
    return x


def raise_err(err):
    """ """

    def inner():
        raise err

    return inner


def raise_error(error: Exception):  # pragma: no cover
    """ """
    raise error


class MatchError(TypeError):
    """
    Raised when a match is not found.
    """

    ...


P = t.ParamSpec("P")


# @t.overload
# def apply(f: t.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
#    ...


# @t.overload
# def apply(f: T) -> T:
#    ...


def apply(f: t.Callable[P, T] | T, *args: P.args, **kwargs: P.kwargs) -> T:
    """ """
    if callable(f):
        return f(*args, **kwargs)
    return f


T_co = t.TypeVar("T_co", covariant=True)
S_co = t.TypeVar("S_co", covariant=True)
V = t.TypeVar("V")
Q = t.TypeVar("Q")


class When(t.Generic[T_co, S_co]):
    """ """

    def __init__(self, value: "Matchable[T_co]"):
        self.value = value
        self.action: t.Callable[..., S_co] | None = None

    def then(self, f: t.Callable[..., Q]) -> "When[T_co, Q]":
        """ """
        when: When[T_co, Q] = When(self.value)
        when.action = f
        return when

    def __repr__(self):
        return repr(self.value)


when = When


@dataclass
class Default(t.Generic[V]):
    """ """

    def __init__(self):
        self.action: t.Callable[[], V] | V | None = None

    def __rshift__(self, other: t.Callable[[], T] | T) -> "Default[T]":
        default: Default[T] = Default()
        default.action = other
        return default


default: Default[t.Any] = Default()

U = t.TypeVar("U")

Q = t.TypeVar("Q")

Nested: t.TypeAlias = "Matchable[Q | Nested[Q]]"


def convert_to_dict(obj: dict[str, t.Any]) -> dict[str, t.Any]:
    for key, value in obj.items():
        if dataclasses.is_dataclass(value):
            obj[key] = value.__dict__
            convert_to_dict(obj[key])
    return obj


class Matchable(t.Protocol[T_co]):
    __matchable_classes__: t.ClassVar[set[t.Any]] = set()

    @t.overload
    def __rshift__(
        self: "Matchable[UnderscoreType]", other: t.Callable[[T_co], T_co]
    ) -> When[T, T]:
        ...

    @t.overload
    def __rshift__(self: "Matchable[V]", other: t.Callable[[V], U]) -> When[V, U]:
        ...

    @t.overload
    def __rshift__(
        self: "Matchable[T_co]", other: t.Callable[[T_co], U]
    ) -> When[T_co, U]:
        ...

    def __rshift__(self, other: t.Callable) -> When:
        """ """
        return When(self).then(other)

    @t.overload
    def match(
        self: "Nested[T]",
        *whens: "When[Nested[UnderscoreType], Nested[UnderscoreType]]  | Default[T]",
    ) -> T:
        ...

    @t.overload
    def match(self, *whens: When[UnderscoreType, UnderscoreType]) -> T_co:
        """
        >>> v = opt(1).match(Ok(_under=_) >> identity)
        """
        ...

    @t.overload
    def match(self, *whens: When[UnderscoreType, Q] | Default[t.Any]) -> Q:
        """
        >>> value.match(
        >>>    when(Some(_)).then(lambda x: "match first"),
        >>>    when(Some(_)).then(lambda x: x * 2),
        >>>    default >> (partial(raise_error, MatchError())),
        >>> )
        or
        >>> k = opt(1).match(Some(_) >> (lambda x: str(x)))
        """
        ...

    @t.overload
    def match(self, *whens: When[T_co, T_co] | Default[T_co]) -> T_co:
        """
        >>> opt(1).match(Some(2) >> identity, default >> (lambda: 100))
        """
        ...

    @t.overload
    def match(self, *whens: When[T_co, Q] | Default[V]) -> Q | V:
        """
        >>> opt(1).match(
                *(Some(_under=2) >> (lambda x: str(x)),
                (default >> (lambda: 100)))
            )
        """
        ...

    @t.overload
    def match(self, *whens: "Matchable[UnderscoreType]" | Default[T_co]) -> T_co:
        """
        >>> d = opt(1).match(*(Some(_), default >>  100))
        """
        ...

    @t.overload
    def match(self, *whens: "Matchable[V]") -> V:
        """
        >>> val = opt(ValueError).match(Some(type[ValueError]))
        """
        ...

    @t.overload
    def match(self, *whens: "Matchable[t.Any]" | Default[V]) -> V | t.Any:
        """
        >>> m1, m2 = val.match(*(Some({1: _, 2: _}), default >> (1, 2)))
        """
        ...

    @t.overload
    def match(self, *whens: "When | Matchable | Default") -> t.Any:
        """
        Can not infer other return type !
        """
        ...

    def match(
        self, *whens: "When[t.Any, t.Any] | Matchable[t.Any] | Default[t.Any]"
    ) -> t.Any:
        for w in whens:
            if isinstance(w, Default):
                assert w.action is not None
                return apply(w.action)

            when_inst = w
            if not isinstance(when_inst, When):
                # assert isinstance(when_inst, Matchable)
                when_inst = When(when_inst)

            if isinstance(when_inst, when):
                clazz = when_inst.value.__class__

                if clazz not in self.__matchable_classes__:
                    raise MatchError(
                        f"Incompatible match class found: {when_inst.value} "
                        f"not in {self.__matchable_classes__}"
                    )

                if clazz == self.__class__:
                    match_dict, self_dict = convert_to_dict(
                        when_inst.value.__dict__
                    ), convert_to_dict(self.__dict__)
                    is_a_match, extracted = pampy_dict_matcher(match_dict, self_dict)
                    if not is_a_match:
                        continue
                    if when_inst.action is None:
                        if len(extracted) == 1:
                            return extracted[0]
                        return extracted
                    return apply(when_inst.action, *extracted)
        raise MatchError(f"No default guard found, enable to match {self}")
