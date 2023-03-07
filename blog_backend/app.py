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

from .dependencies import get_is_authorized, LoginService, BlogService, Config, boot_watcher
from .models import Article


logger = logging.getLogger('uvicorn')

app = FastAPI(
    dependencies=[Depends(boot_watcher)]
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
    config:Config=Depends(),
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
