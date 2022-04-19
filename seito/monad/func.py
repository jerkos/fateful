from typing import Any


def identity(x: Any) -> Any:
    return x


def raise_err(err):
    def inner():
        raise err

    return inner


def raise_error(error: Exception):
    raise error
