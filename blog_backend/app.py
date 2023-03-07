import os
import re
import threading
import logging
import asyncio
from functools import lru_cache

import click
from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.cors import CORSMiddleware

from .dependencies import get_is_authorized, get_config, LoginService, BlogService
from .models import Article
from .middlewares import debounce, Config
from .watcher import require_watcher, start_watcher


logger = logging.getLogger('uvicorn')


class CB:
    def __init__(self, loop, handler):
        self.loop = loop
        self.handler = handler

    @debounce(0.01)
    def debounced(self, path):
        self.loop.call_soon_threadsafe(asyncio.create_task, self.handler)

    def __call__(self, event):
        if event.event_type in ['created', 'closed']:
            return
        self.debounced(event.src_path)

__initialized = False

async def init_watcher(
    config:Config=Depends(get_config),
    S:BlogService=Depends()
):
    global __initialized
    if __initialized:
        return
    callback = CB(asyncio.get_event_loop(), S.reload_blog_data)
    require_watcher(
        target_dir=config.ARTICLES_DIR,
        regexes=[r'.*\.md$'],
        # regexes=[r'.*\d\d\d\d-\d\d-\d\d_.*\.md$'],
        callback=callback)
    start_watcher()
    await S.reload_blog_data()
    __initialized = True

app = FastAPI(
    dependencies=[Depends(init_watcher)]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get("/")
async def root(
    config:Config=Depends(),
    S:BlogService=Depends()
):
    return {
        'errors': await S.get_errors(),
        'warnings': await S.get_warnings(),
    }



class SessionPayload(BaseModel):
    password: str

@app.post('/sessions')
async def post_sessions(
    payload:SessionPayload,
    authorized=Depends(get_is_authorized),
    config=Depends(get_config),
    login_service:LoginService=Depends(),
):
    token = login_service.login(payload.password)

    if not token:
        raise HTTPException(status_code=401, detail='Invalid password')

    return {'token': token}


@app.get('/articles')
async def get_articles(
    category:str=None,
    tag:str=None,
    authorized:any=Depends(get_is_authorized),
    S:BlogService=Depends(),
):
    aa:list[Article] = await S.get_articles()
    r = []
    for a in aa:
        if category and a.category.slug != category:
            continue
        if tag and tag not in a.tags:
            continue
        r.append(a)
    return aa


@app.get('/articles/{category_slug}/{slug}')
async def get_article(
    category_slug:str,
    slug:str=None,
    S=Depends(BlogService),
):
    aa:list[Article] = await S.get_articles()
    for a in aa:
        if a.category.slug == category_slug and a.slug == slug:
            return a

    raise HTTPException(status_code=404, detail="Article not found")

@app.get('/categories')
async def get_categories(
    S=Depends(BlogService),
):
    return await S.get_categories()

@app.get('/tags')
async def get_tags(
    S=Depends(BlogService),
):
    return await S.get_tags()
