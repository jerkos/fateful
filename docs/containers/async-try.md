# 🚀 Async try

The aim of the class is to provide the same functions as the {==Result container==} class
in an asynchronous way

using asyncio, we often write this, which is fairly convenient

```py linenums="1"
import asyncio

async def wait_for(value, *, time=100):
    await asyncio.sleep(time)
    return value

async def main():
    result = await wait_for("Marco")
    result = f"Hello {result}"
    return result
```

With async result we can do this:

```py linenums="1"
import asyncio
from fateful.monad.async_result import async_try


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

## Handling error

The Async result container is useful especially when dealing with error

Considering this function:

```py linenums="1"
import random
import logging
import asyncio


async def wait_for(value: int, *, time=100):
    await asyncio.sleep(time)
    if value > 50:
        raise ValueError()
    return value


async def main():
    try:
        return await wait_for(random.randint())
    except ValueError as e:
        logging.error(e)
        return 0
```

*main* function could be rewritten as:

```py linenums="1"
import random
from fateful.monad.async_result import AsyncResult

async def main():
    return await AsyncResult.of(wait_for, random.randint()).recover(0)

# or with pattern matching which is really simple to read

async def main():
    return (
        await AsyncResult.of(
            wait_for, random.randint()
        ).match(
            Ok(_),
            Err(_) >> reraise
            default >> 0
        )
    )
```

## 💻 API reference

::: fateful.monad.async_result
