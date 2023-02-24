import asyncio
import logging

from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler


logger = logging.getLogger('uvicorn')


class WatchHandler(RegexMatchingEventHandler):
    def __init__(self, regexes, callback):
        super().__init__(regexes=regexes)
        self.callback = callback

    def on_any_event(self, event):
        self.callback(event)

class Watcher:
    def __init__(self, target_dir, regexes, callback):
        self.target_dir = target_dir
        self.observer = Observer()
        self.handler = WatchHandler(regexes=regexes, callback=callback)

    def start(self):
        self.observer.schedule(self.handler, self.target_dir, recursive=True)
        self.observer.start()
        logger.info(f'Watcher starts on {self.target_dir}')

__watcher: Watcher = None

def require_watcher(**kwargs):
    global __watcher
    if __watcher:
        logger.info('Watcher is already instanciated')
        return
    __watcher = Watcher(**kwargs)

def start_watcher():
    __watcher.start()

def get_watcher():
    return __watcher
