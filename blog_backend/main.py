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
from .services import reload_blog_data, get_articles, get_categories, get_tags


logger = logging.getLogger('uvicorn')

app = FastAPI()
# app.include_router(articles.router)

@app.get("/")
async def root():
    return {"message": "Welcome"}

@app.get('/articles')
async def get_all_articles():
    return await get_articles()

@app.get('/categories')
async def get_all_categories():
    return await get_categories()

@app.get('/tags')
async def get_all_tags():
    return await get_tags()


loop = asyncio.get_event_loop()

@debounce(0.01)
def debounced(path):
    loop.call_soon_threadsafe(asyncio.create_task, reload_blog_data())

def callback(event):
    if event.event_type in ['created', 'closed']:
        return

    logger.info('Watcher: %s is %s', event.src_path, event.event_type)
    debounced(event.src_path)

@app.on_event("startup")
async def startup_event():
    config = get_config()

    require_watcher(
        target_dir=config.ARTICLES_DIR,
        regexes=[r'.*\.md$', r'.*meta\.json$'],
        # regexes=[r'.*\d\d\d\d-\d\d-\d\d_.*\.md$'],
        callback=callback)
    start_watcher()
    await reload_blog_data()
