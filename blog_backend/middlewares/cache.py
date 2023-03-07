import asyncio

caches = {}

class Cache():
    flag: asyncio.Event
    data: any

    def __init__(self):
        self.flag = asyncio.Event()
        self.flag.set()
        self.data = None

    @classmethod
    def acquire(cls, name):
        c = caches.get(name)
        if not c:
            c = Cache()
            caches[name] = c
        return c

    async def read(self):
        await self.flag.wait()
        return self.data

    async def update(self, func):
        await self.flag.wait()
        self.flag.clear()
        try:
            self.data = await func()
        finally:
            self.flag.set()
        return self.data
