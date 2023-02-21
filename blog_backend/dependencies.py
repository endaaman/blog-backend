from functools import lru_cache
from fastapi import Depends, FastAPI

from pydantic.dataclasses import dataclass

from .config import get_config
from .middlewares import read_cache, update_cache
from .models import Blog, Category, Tag
from .loader import BlogContent, load_blog_contents


@dataclass
class CachedData:
    blogs: list[Blog]
    categories: list[Category]
    tags: list[Tag]



async def do_update_cache():
    config = get_config()
    blog_contents = await load_blog_contents(blogs_dir=config.BLOGS_DIR)
    # for blog_content in blog_contents:
    #     blog_contents

    return CachedData(
        blogs=[],
        categories=[],
        tags=[],
    )

async def reload_data():
    await update_cache(do_update_cache)



async def get_blogs():
    data = await read_cache()
    return data.blogs

async def get_tags():
    data = await read_cache()
    return data.tags

async def get_categories():
    data = await read_cache()
    return data.categories

