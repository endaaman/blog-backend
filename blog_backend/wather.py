from datetime import datetime
import asyncio
from functools import wraps

from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

from .utils import purge_cf_cache
from .loader import load_blog_data
from .store import global_store
from .const import APP_ENV


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
        if APP_ENV == 'prod':
            purge_handle = asyncio.create_task(purge_cf_cache())
        else:
            print('NOTE: APP_ENV==dev, skipping cache purging')

        blog_data = await load_blog_data(self.dir)
        now = datetime.now()

        print('reloaded:', now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
        print('Articles: ', len(blog_data.articles))
        print('Categories: ', len(blog_data.categories))
        print('Tags: ', len(blog_data.tags))
        print('Warnings: ', len(blog_data.warnings))
        print('Errors: ', len(blog_data.errors))
        print()
        global_store.set_blog_data(blog_data)

        if APP_ENV == 'prod':
            error = await purge_handle
            if error is None:
                print('Successfully purged Cloudflare cache')
            else:
                print('Cache purge failed:', error)


global_observer = PollingObserver()

async def start_watcher(dir):
    handler = WatchedFileHandler(dir=dir)
    global_observer.schedule(handler, path=dir, recursive=True)
    global_observer.start()
    await handler.reload()
    # global_observer.join()
