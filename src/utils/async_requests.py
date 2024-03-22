import asyncio
from functools import partial

import requests


async def http_get(*args, **kwargs):
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(
        None, partial(requests.get, *args, **kwargs))
    response = await future
    return response


async def http_post(*args, **kwargs):
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(
        None, partial(requests.post, *args, **kwargs))
    response = await future
    return response
