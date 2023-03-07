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

from .middlewares import Cache, Config
from .models import Article, Category, BlogData
from .loader import load_blog_data


JWT_ALGORITHM = 'HS256'

CUSTOM_KEY = 'I_AM'
CUSTOM_VALUE = 'ENDAAMAN'


logger = logging.getLogger('uvicorn')


@lru_cache
def get_config():
    return Config()

async def get_is_bearer_token(
    request: Request,
    authorization: str|None = Header(default=None),
) -> str|None:
    token = None
    if authorization:
        m = re.match(r'Bearer\s+(.*)$', authorization)
        if m:
            token = m[1]
    return token


async def get_is_authorized(
    request: Request,
    config: Config = Depends(get_config),
    token: str|None = Depends(get_is_bearer_token),
) -> bool:
    if not token:
        return False

    try:
        decoded = jwt.decode(token, config.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        raise HTTPException(status_code=401, detail='Invalid authorization') from e

    print(decoded)

    exp = decoded.get('exp', None)
    if not exp:
        raise HTTPException(status_code=401, detail='Invalid payload in JWT')

    if decoded.get(CUSTOM_KEY) == CUSTOM_VALUE:
        raise HTTPException(status_code=401, detail='You are not me')

    diff = datetime.now() - datetime.fromtimestamp(exp)
    if diff > config.expiration_duration():
        raise HTTPException(status_code=401, detail='Your JWT token is expired')
    return True


class LoginService:
    def __init__(self, config = Depends(get_config)):
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


class BlogService:
    def __init__(self, config=Depends(get_config)):
        self.config = config
        self.cache = Cache.acquire('blog')

    async def get_data(self) -> BlogData:
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
