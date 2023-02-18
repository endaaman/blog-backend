import time
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler

from .middlewares import load_blogs, update_cache, read_cache


class WatchHandler(RegexMatchingEventHandler):
    def __init__(self, callback):
        super().__init__(regexes=[r'.*\.md$'])
        self.callback = callback

    def on_any_event(self, event):
        self.callback(event)

class Watcher:
    def __init__(self, target_dir):
        self.target_dir = target_dir
        self.observer = Observer()
        self.handler = WatchHandler(callback=self.callback)

    def callback(self, event):
        print('changed', event.src_path)
        return

        blogs = load_blogs()
        update_cache(blogs)

    def start(self):
        self.observer.schedule(self.handler, self.target_dir, recursive=True)
        self.observer.start()

__watcher: Watcher = None

def init_watcher(**kwargs):
    global __watcher
    __watcher = Watcher(**kwargs)

def start_watcher():
    __watcher.start()

def get_watcher():
    return __watcher
