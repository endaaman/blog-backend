import asyncio
from dataclasses import dataclass, field


@dataclass
class Cache():
    lock: asyncio.Lock
    value: any

# init cache
__cache = Cache(asyncio.Event(), [])
__cache.lock.release()


async def read_cache():
    await __cache.lock.acquire()
    return __cache

async def update_cache(func):
    await __cache.lock.acquire()
    async with lock:
        __cache.value = await func()

async def update_cache(value):
    await wait_cache()
    __cache = CacheEntry(locked=False, value=value)

