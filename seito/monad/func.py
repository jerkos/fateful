import functools
from typing import Any


def identity(x: Any) -> Any:
    return x


def raise_error(error: Exception):
    raise error


def f(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper
