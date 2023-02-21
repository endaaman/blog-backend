import os
import re
import itertools
import asyncio
import datetime
from glob import glob

import yaml
import aiofiles
from pydantic import validator, Field
from pydantic.datetime_parse import parse_date
from pydantic.dataclasses import dataclass

from .models import Blog, Category, Tag


@dataclass
class BlogContent:
    category_slug: str
    slug: str
    title: str
    date: datetime.date
    body: str
    digest: str = ''
    image: str = ''
    tags: list[str] = Field(default_factory=list)
    special: bool = False
    private: bool = False

    @classmethod
    @validator("date")
    def validate_date(cls, v):
        return parse_date(v)


HEADER_SYMBOL = '---'

def parse_header(text):
    try:
        header = yaml.safe_load(text)
    except yaml.YAMLError as e:
        return {}, str(e)

    return header or {}, ''

async def load_blog_content(blogs_dir, path) -> BlogContent:
    rel = os.path.normpath(os.path.relpath(path, blogs_dir))
    splitted = os.path.split(rel)

    match splitted:
        case [filename]:
            category_slug = '-'
        case [category_slug, filename]:
            pass
        case _:
            return None, 'skipped'
    m = re.match(r'^(\d\d\d\d-\d\d-\d\d)_(.*)\.md$', filename)
    if not m:
        return None, 'skipped'

    date = m[0]
    slug = m[1]

    is_yaml = False
    yaml_lines = []
    body_lines = []
    async with aiofiles.open(path, mode='r') as f:
        i = 0
        async for line in f:
            if i == 0 and line == HEADER_SYMBOL:
                is_yaml = True
                continue
            if is_yaml and line == HEADER_SYMBOL:
                is_yaml = False
                continue
            if is_yaml:
                yaml_lines.append(line)
            else:
                body_lines.append(line)
            i += 1

    if is_yaml:
        header, header_error = {}, f'yaml tag (`{HEADER_SYMBOL}`) is not closed.'
    else:
        header, header_error = parse_header('\n'.join(yaml_lines))

    header.setdefault('title', slug)
    header.setdefault('date', date)
    header.setdefault('slug', slug)
    header['category_slug'] = category_slug
    header['body'] = '\n'.join(body_lines)

    c = BlogContent(**header)
    print(c)
    return c, header_error


async def load_blog_contents(blogs_dir) -> list[BlogContent]:
    paths = glob(os.path.join(blogs_dir, '**', '*.md'), recursive=True)
    tasks = []
    for path in paths:
        # get last item
        tasks.append(load_blog_content(blogs_dir, path))
    tt = await asyncio.gather(*tasks)

    tag_map = {}
    category_map = {}

    for c, error in tt:
        if not c:
            continue
        for t in c.tags:
            tag_map

        blog = Blog(
            slug=c.slug,
            title=c.title
            date=c.date,
            body=c.body,
            digest=c.digest
            image=c.image,
            tags: list[Tag] = []
            special: bool = False
            private: bool = False
        )

    tag_slugs = list(set(itertools.chain(*[c.tags for c in blog_contents])))
    category_slugs = list(set(c.category_slug for c in blog_contents))

    tags = {n:Tag(slug=n, name=n) for n in tag_slugs}
    categories = {Category(slug=n, name=n) for n in category_slugs}

    # for glob(os.path.join(blogs_dir, '*.md')):
    #     load_blogs
    return []
