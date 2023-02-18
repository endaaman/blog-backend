import asyncio
from dataclasses import dataclass, field


@dataclass
class Cache():
    locked: bool = False
    flag: asyncio.Event
    value: any

# init cache
__cache = Cache(False, asyncio.Event(), [])
__cache.flag.set()

async def wait_cache():
    if not __cache.locked:
        return
    # wait until unlocked
    await __cache.flag.wait()

async def read_cache():
    await wait_cache()
    return __cache

async def start_lock_cache(func):
    await wait_cache()
    async def inner(flag):
        await func()
        flag.set()

    __cache.flag = asyncio.Event()
    asyncio.create_task(inner(__cache.flag))

async def update_cache(value):
    await wait_cache()
    __cache = CacheEntry(locked=False, value=value)

