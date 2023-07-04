import typing as t
from dataclasses import dataclass

# noinspection PyProtectedMember
from pampy import _ as __  # type: ignore
from pampy.pampy import match_dict as pampy_dict_matcher  # type: ignore

if t.TYPE_CHECKING:
    from seito.monad.option import Empty, Some  # noqa: F401

_ = __


def flip(f):
    flipper = getattr(f, "__flipback__", None)
    if flipper is not None:  # pragma: no cover
        return flipper

    def _flipper(a, b):
        return f(b, a)

    setattr(_flipper, "__flipback__", f)
    return _flipper


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
    """ """

    ...


P = t.ParamSpec("P")


def apply(f: t.Callable[P, T] | T, *args: P.args, **kwargs: P.kwargs) -> T:
    """ """
    if callable(f):
        return f(*args, **kwargs)
    return f


T2 = t.TypeVar("T2")


class When:
    """ """

    def __init__(self, value: "Matchable"):
        self.value: Matchable = value
        self.action: t.Callable[..., t.Any] | None = None

    def then(self, f: t.Callable[..., t.Any]):
        """ """
        self.action = f
        return self

    def __repr__(self):
        return repr(self.value)


when = When


@dataclass
class Default:
    """ """

    def __init__(self):
        self.action = None

    def __rshift__(self, other) -> "Default":
        self.action = other
        return self


default = Default()


class Matchable(t.Protocol):
    __matchable_classes__: t.ClassVar[set[t.Any]] = set()

    def __rshift__(self, other) -> When:
        """ """
        return When(self).then(other)

    def match(self, *whens: "When | Matchable | Default") -> t.Any:
        for w in whens:
            if isinstance(w, Default):
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
                    match_dict, self_dict = when_inst.value.__dict__, self.__dict__
                    is_a_match, extracted = pampy_dict_matcher(match_dict, self_dict)
                    if not is_a_match:
                        continue
                    if when_inst.action is None:
                        if len(extracted) == 1:
                            return extracted[0]
                        return extracted
                    return apply(when_inst.action, *extracted)
        raise MatchError(f"No default guard found, enable to match {self}")
