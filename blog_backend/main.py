import os
import threading
import logging

import click
import uvicorn
import watchdog
from fastapi import Depends, FastAPI

from .routers import blogs
from .watcher import require_watcher, start_watcher
from .middlewares import debounce
from .services import update_data
from .config import get_config


logger = logging.getLogger('uvicorn')

app = FastAPI()
app.include_router(blogs.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}




@debounce(0.01)
def debounced(path):
    print('bounced!')
    update_data()

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
        regexes=[r'.*\.md$', r'.*\meta\.json$'],
        # regexes=[r'.*\d\d\d\d-\d\d-\d\d_.*\.md$'],
        callback=callback)
    start_watcher()
