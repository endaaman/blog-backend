import threading

import click
import uvicorn
import watchdog
from fastapi import Depends, FastAPI

from .routers import blogs
from .watcher import require_watcher, start_watcher
from .config import get_config


app = FastAPI()
app.include_router(blogs.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


def callback(event):
    print('ev', event.event_type, event.src_path)
    ['modified', 'created', 'deleted']
    print()

@app.on_event("startup")
async def startup_event():
    config = get_config()
    print('sub')
    require_watcher(
        target_dir=config.blogs_dir,
        regexes=[r'.*\.md$'],
        callback=callback)
    start_watcher()
