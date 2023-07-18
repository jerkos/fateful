# Http utils

Little module dealing with http call in an asynchronous way, wrapped
in `Option` monads.

## Basic api

`get_opt` and all associated method accept `kwargs` for dealing with timeout, ssl etc...

```python
from fateful.http import try_get
from fateful.monad.opt import Some, Err, _, default
from fateful.monad.func import raise_error, identity
from aiohttp import ClientSession


async def http_call():
    async with ClientSession() as session:
        return (
            await try_get("http://google.com", session=session)
            .match(
                Some(_) >> identity,
                Err(_) >> raise_error,
                default() >> None
            )
        )
```

Without the match api:

```python
from fateful.http import try_get
from aiohttp import ClientSession


async def http_call():
    async with  ClientSession() as session:
        return (
            await try_get("http://google.com", session=session)
            .or_none()
        )
```

## Automatic json conversion

When server sends back a header `Content-Type` which contains `application/json`,
response is automatically converted into a `json` object.

```python
from fateful.http import try_get
from aiohttp import ClientSession
from fn import _


async def http_call():
    async with  ClientSession() as session:
        title = (
            await try_get(
                "https://jsonplaceholder.typicode.com/todos/1",
                session=session
            )
            .map(_.title)
            .or_else("Unknown")
        )
        assert title == "delectus aut autem"
```

## Error management

Throws a client error

## 💻 API reference

::: fateful.http
