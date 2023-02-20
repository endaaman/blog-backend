import os
import itertools
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
    date: str
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

    return header, ''

async def load_blog_content(path) -> BlogContent:
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

    header, header_error = parse_header('\n'.join(yaml_lines))

    header.setdefault('title', 100)
    header.setdefault('date', 100)
    header.setdefault('slug', 100)

    return BlogContent(
        category_slug='',
        slug='',
        title=header.get('title', 'TITLE'),
        tag_slugs=header.get('tags', []),
        body='\n'.join(yaml_lines),
    )


async def load_blog_contents(blogs_dir) -> list[BlogContent]:
    paths = glob(os.path.join(blogs_dir, '**', '*.md'), recursive=True)
    blog_contents_tasks = []
    for path in paths:
        # get last item
        blog_contents_tasks = load_blog(path)
    blog_contents = await blog_contents_tasks

    tag_slugs = list(set(itertools.chain(c.tag_slugs for c in blog_contents)))
    category_slugs = list(set(c.category_name for c in blog_contents))

    tags = {n:Tag(slug=n, name=n) for n in tag_slugs}
    categories = {Category(slug=n, name=n) for n in category_slugs}

    # for glob(os.path.join(blogs_dir, '*.md')):
    #     load_blogs
    return []
