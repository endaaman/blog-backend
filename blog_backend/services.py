import time
import asyncio
import logging
from functools import lru_cache

from fastapi import Depends, FastAPI
from pydantic.dataclasses import dataclass

from .config import acquire_config
from .middlewares import read_cache, update_cache
from .models import Article, Category, BlogData
from .loader import load_blog_data


logger = logging.getLogger('uvicorn')

async def get_data() -> BlogData:
    return await read_cache()

async def do_update_cache():
    config = acquire_config()
    data = await load_blog_data(articles_dir=config.ARTICLES_DIR)
    return data

async def reload_blog_data():
    start_time = time.perf_counter()
    logger.info('start reload data')
    data = await update_cache(do_update_cache)
    duration = time.perf_counter() - start_time
    count = len(data.articles)
    logger.info(f'{count} articles reloaded ({duration*1000:.2f}ms)')

async def get_articles():
    data = await get_data()
    return data.articles

async def get_tags():
    data = await read_cache()
    return data.tags

async def get_categories():
    data = await read_cache()
    return data.categories

async def get_errors() -> list[str]:
    data = await read_cache()
    return data.errors

async def get_warnings() -> list[str]:
    data = await read_cache()
    return data.warnings
