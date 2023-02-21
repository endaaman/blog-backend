import os
import threading
import logging
import asyncio

import click
import uvicorn
import watchdog
from fastapi import Depends, FastAPI

from .config import get_config
from .middlewares import debounce
from .watcher import require_watcher, start_watcher
from .dependencies import reload_data
from .routers import blogs

logger = logging.getLogger('uvicorn')

app = FastAPI()
app.include_router(blogs.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


loop = asyncio.get_event_loop()

@debounce(0.01)
def debounced(path):
    print('bounced!')
    loop.create_task(reload_data())

async def callback(event):
    if event.event_type in ['created', 'closed']:
        return

    logger.info('Watcher: %s is %s', event.src_path, event.event_type)
    debounced(event.src_path)

@app.on_event("startup")
async def startup_event():
    config = get_config()

    require_watcher(
        target_dir=config.BLOGS_DIR,
        regexes=[r'.*\.md$', r'.*meta\.json$'],
        # regexes=[r'.*\d\d\d\d-\d\d-\d\d_.*\.md$'],
        callback=callback)
    start_watcher()
    await reload_data()
