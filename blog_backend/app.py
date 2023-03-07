import os
import re
import threading
import logging
import asyncio

import click
from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.cors import CORSMiddleware

from .dependencies import get_is_authorized, get_config, LoginService
from .models import Article
from .middlewares import debounce
from .watcher import require_watcher, start_watcher
from . import services as S


logger = logging.getLogger('uvicorn')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get("/")
async def root():
    return {
        'errors': await S.get_errors(),
        'warnings': await S.get_warnings(),
    }



class SessionPayload(BaseModel):
    password: str

@app.post('/sessions')
async def post_sessions(
    payload:SessionPayload,
    authorized:any=Depends(get_is_authorized),
    config:any=Depends(get_config),
    login_service=Depends(LoginService),
):
    token = login_service.login(payload.password)

    if not token:
        raise HTTPException(status_code=401, detail='Invalid password')

    return {'token': token}


@app.get('/articles')
async def get_articles(
    category:str=None, tag:str=None,
    authorized:any=Depends(get_is_authorized),
):
    print(authorized)
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
async def get_article(category_slug:str, slug:str=None):
    aa:list[Article] = await S.get_articles()
    for a in aa:
        if a.category.slug == category_slug and a.slug == slug:
            return a

    raise HTTPException(status_code=404, detail="Article not found")

@app.get('/categories')
async def get_categories():
    return await S.get_categories()

@app.get('/tags')
async def get_tags():
    return await S.get_tags()


loop = asyncio.get_event_loop()

@debounce(0.01)
def debounced(path):
    loop.call_soon_threadsafe(asyncio.create_task, S.reload_blog_data())

def callback(event):
    if event.event_type in ['created', 'closed']:
        return
    debounced(event.src_path)

@app.on_event("startup")
async def startup_event():
    config = get_config()
    require_watcher(
        target_dir=config.ARTICLES_DIR,
        regexes=[r'.*\.md$'],
        # regexes=[r'.*\d\d\d\d-\d\d-\d\d_.*\.md$'],
        callback=callback)
    start_watcher()
    await S.reload_blog_data()
