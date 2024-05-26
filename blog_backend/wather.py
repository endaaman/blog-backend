import asyncio
from functools import wraps

from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

# from .utils import debounce
from .loader import load_blog_data
from .store import global_store


def debounce(delay):
    def decorator(func):
        task = None

        @wraps(func)
        def debounced(*args, **kwargs):
            nonlocal task
            if task:
                task.cancel()
            task = asyncio.create_task(delayed_execute(func, delay, *args, **kwargs))

        return debounced

    async def delayed_execute(func, delay, *args, **kwargs):
        await asyncio.sleep(delay)
        await func(*args, **kwargs)

    return decorator


class WatchedFileHandler(FileSystemEventHandler):
    def __init__(self, dir):
        self.dir = dir
        self.loop = asyncio.get_running_loop()
        # asyncio.set_event_loop(self.loop)
        # result = loop.run_until_complete(run_async_func())

    def on_modified(self, event):
        # if self.loop is None:
        #     self.loop = asyncio.new_event_loop()
        #     asyncio.set_event_loop(self.loop)
        # self.loop.run_until_complete(self.reload())
        f = asyncio.run_coroutine_threadsafe(self.reload(), self.loop)

    async def reload(self):
        blog_data = await load_blog_data(self.dir)
        global_store.set_blog_data(blog_data)


global_observer = PollingObserver()

async def start_watcher(dir):
    handler = WatchedFileHandler(dir=dir)
    global_observer.schedule(handler, path=dir, recursive=True)
    global_observer.start()
    await handler.reload()
    # global_observer.join()
