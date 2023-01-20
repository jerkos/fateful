from typing import Any


def flip(f):
    flipper = getattr(f, "__flipback__", None)
    if flipper is not None:
        return flipper

    def _flipper(a, b):
        return f(b, a)

    setattr(_flipper, "__flipback__", f)
    return _flipper


def identity(x: Any) -> Any:
    """ """
    return x


def raise_err(err):
    """ """

    def inner():
        raise err

    return inner


def raise_error(error: Exception):
    """ """
    raise error
