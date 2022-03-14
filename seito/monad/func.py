from typing import Any


def identity(x: Any) -> Any:
    return x


def raise_err():
    def inner(err):
        raise err

    return inner


def raise_error(error: Exception):
    raise error
