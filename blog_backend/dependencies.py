from functools import lru_cache

from fastapi import Depends, FastAPI

from .watcher import get_watcher as gw

@lru_cache()
def get_watcher():
    return gw()
