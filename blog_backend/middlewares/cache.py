import asyncio
from pydantic.dataclasses import dataclass


@dataclass
class Cache():
    flag: asyncio.Event
    data: any

# init cache
__cache = Cache(asyncio.Event(), [])
__cache.flag.set()


async def read_cache():
    await __cache.flag.wait()
    return __cache

async def update_cache(func):
    await __cache.flag.wait()
    __cache.flag.clear()
    try:
        __cache.data = await func()
    finally:
        __cache.flag.set()
