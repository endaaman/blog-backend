import asyncio
import logging
from functools import lru_cache

from fastapi import Depends, FastAPI
from pydantic.dataclasses import dataclass

from .config import get_config
from .middlewares import read_cache, update_cache
from .models import Article, Category
from .loader import load_blog_data


logger = logging.getLogger('uvicorn')

async def do_update_cache():
    config = get_config()
    data = await load_blog_data(articles_dir=config.ARTICLES_DIR)
    print('cate', data.categories)
    for a in data.articles:
        print(a)
    print('tt', data.tags)
    print('ee', data.errors)
    print('ww', data.warnings)
    return data

async def reload_blog_data():
    logger.info('start reload data')
    await update_cache(do_update_cache)
    logger.info('done reload data')


async def get_articles():
    data = await read_cache()
    return data.articles

async def get_tags():
    data = await read_cache()
    return data.tags

async def get_categories():
    data = await read_cache()
    return data.categories
