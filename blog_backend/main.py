import os
import threading
import logging
import asyncio

import click
import uvicorn
import watchdog
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware # 追加

from .config import get_config
from .middlewares import debounce
from .watcher import require_watcher, start_watcher
from .services import reload_blog_data, get_articles, get_categories, get_tags, get_errors, get_warnings


logger = logging.getLogger('uvicorn')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {
        'errors': await get_errors(),
        'warnings': await get_warnings(),
    }

@app.get('/articles')
async def get_all_articles(category:str=None, tag:str=None):
    aa:list[Article] = await get_articles()
    r = []
    for a in aa:
        if category and a.category.slug != category:
            continue
        if tag and tag not in a.tags:
            continue
        r.append(a)
    return r

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
