# Async Optional

The aim of the class is to provide the same functions as the `Optional` classes
in an asynchronous way

Synchronous optional allow this:

```py
import asyncio

async def wait_for(value, *, time=100):
    await asyncio.sleep(time)
    return value

async def main():
    result = await wait_for("Marco")
    result = f"Hello {result}"
    return result
```

but with async optional we can do this:

```py
import asyncio
from seito.monad.async_opt import async_try


async def wait_for(value, *, time=100):
    await asyncio.sleep(time)
    return value


async def main():
    result = await (
        async_try(wait_for, "Marco")
        .map(lambda x: f"Hello {result}")
        .or_else("unknown")
    )
    # result is hello Marco

    result = await (
        async_try(wait_for, None)
        .map(lambda x: f"Hello {result}")
        .or_else("unknown")
    )
    # result is unknown
```