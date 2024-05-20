import asyncio
from functools import partial
from typing import Callable


def sync_to_async(function: Callable):
    loop = asyncio.get_event_loop()

    async def wrapper(*args, **kwargs):
        future = loop.run_in_executor(None, partial(function, *args, **kwargs))
        return await future

    return wrapper
