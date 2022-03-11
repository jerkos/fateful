# Http utils

Little module dealing with http call in an asynchronous way, wrapped
in `Option` monads.

```python
from seito.http import get_opt
from seito.monad.opt import Some, Err, _, default
from seito.monad.func import raise_error, identity
from aiohttp import ClientSession

# grab a session
session = ClientSession()

async def http_call():
    return (
        await get_opt("http://google.com", session=session)
        .match(
            Some(_) >> identity,
            Err(_) >> raise_error,
            default() >> None
        )
    )
```

Without the match api:

```python
from seito.http import get_opt
from aiohttp import ClientSession

session = ClientSession()

async def http_call():
    return await get_opt("http://google.com", session=session).or_none()
```

