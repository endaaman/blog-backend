import os
import tomllib
import re
import itertools
import asyncio
import datetime
from glob import glob

import yaml
import aiofiles
from pydantic import validator, Field
from pydantic.dataclasses import dataclass

from .models import Article, Category, BlogData


NO_TAG_NAME = 'タグなし'
META_FILE = 'meta.toml'
HEADER_DELIMITER = '---'

J = os.path.join

def parse_header(text):
    try:
        header = yaml.safe_load(text)
    except yaml.YAMLError as e:
        return {}, str(e)

    if header:
        return header, ''

    return {}, 'Header is empty'


@dataclass
class ArticleLoadContext:
    article: Article|None
    path: str
    message: str


async def load_article(path, category) -> ArticleLoadContext:
    filename = os.path.basename(path)
    m = re.match(r'^(\d\d\d\d-\d\d-\d\d)_(.*)\.md$', filename)
    if not m:
        return ArticleLoadContext(None, path, 'skipped:invalid filename pattern')
    date, slug = m[1], m[2]

    async with aiofiles.open(path, mode='r') as f:
        contents = await f.read()
        lines = contents.split('\n')

    is_yaml = False
    yaml_start_index = -1
    yaml_end_index = -1
    for i, line in enumerate(lines):
        if line == HEADER_DELIMITER:
            if not is_yaml:
                is_yaml = True
                yaml_start_index = i
                continue
            is_yaml = False
            yaml_end_index = i
            break

    if yaml_start_index >= 0 and yaml_end_index >= 0 and yaml_end_index-yaml_start_index>=1:
        yaml_text = '\n'.join(lines[yaml_start_index+1:yaml_end_index])
        data, message = parse_header(yaml_text)
        body = '\n'.join(lines[yaml_end_index+1:-1])
    else:
        data = {}
        data, message = {}, f'No YAML header.'
        print(yaml_start_index, yaml_end_index)
        body = '\n'.join(lines)

    data.setdefault('title', slug)
    data.setdefault('date', date)
    tags = data.get('tags', []) or []
    if len(tags) == 0:
        data['tags'] = [NO_TAG_NAME]
    data['body'] = body
    data['slug'] = slug
    data['category'] = category
    try:
        a = Article(**data)
    except Exception as e:
        warning = None
        if not data['body']:
            warning = 'body is empty'
        return ArticleLoadContext(warning, path, str(e))

    return ArticleLoadContext(a, path, message)


async def load_blog_data(dir) -> BlogData:
    tasks = []
    errors = {}
    warnings = {}

    categories = {}
    meta_path = J(dir, META_FILE)
    if os.path.exists(meta_path):
        async with aiofiles.open(meta_path, mode='rb') as f:
            content = await f.read()
            meta = tomllib.loads(content.decode('utf-8'))

        meta.setdefault('Category', [])
        for i, data in enumerate(meta['Category']):
            try:
                c = Category(**data)
                categories[c.slug] = c
            except Exception as e:
                errors['meta'] = str(e)

    for e in sorted(os.listdir(dir)):
        if not os.path.isdir(J(dir, e)):
            # not dir
            continue

        children = sorted(glob(J(dir, e, '*.md')))
        if len(children) == 0:
            continue

        c = categories.get(e, None)
        if not c:
            c = Category(slug=e, label=e)
            categories[c.slug] = c

        for path in children:
            tasks.append(load_article(path=path, category=c))

    cc: list[ArticleLoadContext] = await asyncio.gather(*tasks)

    articles = []
    for c in cc:
        if not c.article:
            continue
        articles.append(c.article)
        if c.message:
            if c.article:
                warnings[c.path] = c.message
                print(f'Warn[file={c.path}]:', c.message, )
            else:
                errors[c.path] = c.message
                print(f'Error:', c.message)

    articles = sorted(articles, key=lambda a: a.date)

    m = {}
    tags = []
    # dup check and curate tags
    for a in articles:
        k = f'{a.category.slug}/{a.slug}'
        v =  m.get(k, None)
        if v:
            warnings[k] = 'Slug duprication'
        else:
            m[k] = a
        tags += a.tags

    tags = list(set(tags))

    return BlogData(
        categories=list(categories.values()),
        articles=articles[::-1],
        tags=tags,
        warnings=warnings,
        errors=errors,
    )
