import time
import re
import logging
import asyncio
from datetime import datetime, timedelta
from functools import lru_cache

import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, Request, Header, HTTPException
from pydantic.dataclasses import dataclass
from pydantic import BaseModel

from ..middlewares import Cache, debounce, Config, start_watcher
from ..models import Article, Category, BlogData
from ..loader import load_blog_data


JWT_ALGORITHM = 'HS256'

CUSTOM_KEY = 'I_AM'
CUSTOM_VALUE = 'ENDAAMAN'


logger = logging.getLogger('uvicorn')




class LoginService:
    def __init__(self, config:Config=Depends()):
        self.config = config

    def login(self, password) -> bool:
        ok = bcrypt.checkpw(password.encode('utf-8'), self.config.PASSWORD_HASH.encode('utf-8'))
        if not ok:
            return None

        data = {
            CUSTOM_KEY: CUSTOM_VALUE,
            'exp': datetime.utcnow() + self.config.expiration_duration()
        }

        return jwt.encode(data, self.config.SECRET_KEY, algorithm=JWT_ALGORITHM)




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


class BlogService:
    watcher_started = False

    def __init__(self, config:Config=Depends()):
        self.config = config
        self.cache = Cache.acquire('blog')

    async def start_watcher(self):
        if BlogService.watcher_started:
            return
        callback = CB(asyncio.get_event_loop(), self.reload_blog_data)
        start_watcher(
            target_dir=self.config.ARTICLES_DIR,
            regexes=[r'.*\.md$'],
            # regexes=[r'.*\d\d\d\d-\d\d-\d\d_.*\.md$'],
            callback=callback)
        await self.reload_blog_data()
        BlogService.watcher_started = True
        logger.info('Watcher started')

    async def get_data(self) -> BlogData:
        if not BlogService.watcher_started:
            raise RuntimeError('Watcher did not start.')
        return await self.cache.read()

    async def do_update_cache(self):
        data = await load_blog_data(articles_dir=self.config.ARTICLES_DIR)
        return data

    async def reload_blog_data(self):
        start_time = time.perf_counter()
        logger.info('start reload data')
        data = await self.cache.update(self.do_update_cache)
        duration = time.perf_counter() - start_time
        count = len(data.articles)
        logger.info(f'{count} articles reloaded ({duration*1000:.2f}ms)')

    async def get_articles(self):
        data = await self.get_data()
        return data.articles

    async def get_tags(self):
        data = await self.get_data()
        return data.tags

    async def get_categories(self):
        data = await self.get_data()
        return data.categories

    async def get_errors(self) -> list[str]:
        data = await self.get_data()
        return data.errors

    async def get_warnings(self) -> list[str]:
        data = await self.get_data()
        return data.warnings


async def boot_watcher(blog_service:BlogService=Depends()):
    await blog_service.start_watcher()
