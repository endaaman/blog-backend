import os
import re
import itertools
import asyncio
import datetime
from collections import OrderedDict
from glob import glob

import yaml
import aiofiles
from pydantic import validator, Field
from pydantic.datetime_parse import parse_date
from pydantic.dataclasses import dataclass

from .models import Article, Category, BlogData


HEADER_DELIMITER = '---'

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
    article: Article
    path: str
    message: str

async def load_article(category, path) -> ArticleLoadContext:
    filename = os.path.basename(path)
    m = re.match(r'^(\d\d\d\d-\d\d-\d\d)_(.*)\.md$', filename)
    if not m:
        return ArticleLoadContext(None, path, 'skipped:invalid filename pattern')
    date, slug = m[1], m[2]

    is_yaml = False
    yaml_lines = []
    body_lines = []
    async with aiofiles.open(path, mode='r') as f:
        i = 0
        contents = await f.read()
        lines = contents.split('\n')
        for line in lines:
            if i == 0 and line == HEADER_DELIMITER:
                is_yaml = True
                continue
            if is_yaml and line == HEADER_DELIMITER:
                is_yaml = False
                continue
            if is_yaml:
                yaml_lines.append(line)
            else:
                body_lines.append(line)
            i += 1

    if is_yaml:
        data, message = {}, f'yaml tag (`{HEADER_DELIMITER}`) is not closed.'
    else:
        data, message = parse_header('\n'.join(yaml_lines))

    data.setdefault('title', slug)
    data.setdefault('date', date)
    data['body'] = '\n'.join(body_lines)
    data['slug'] = slug
    data['category'] = category

    return ArticleLoadContext(Article(**data), path, message)


async def load_blog_data(articles_dir) -> BlogData:
    categories = []
    tasks = []
    for d in sorted(os.listdir(articles_dir)):
        if not os.path.isdir(os.path.join(articles_dir, d)):
            # not dir
            continue
        m = re.match(r'^(\d*)_(.*)_(.*)$', d)
        if not m:
            continue
        children = sorted(glob(os.path.join(articles_dir, d, '*.md')))
        if len(children) == 0:
            continue

        category = Category(priority=int(m[1]), slug=m[2], name=m[3])
        categories.append(category)
        for path in children:
            # get last item
            tasks.append(load_article(category, path))
    cc: list[ArticleLoadContext] = await asyncio.gather(*tasks)

    tag_set = set()
    articles = []
    errors = OrderedDict()
    warnings = OrderedDict()
    for c in cc:
        if not c.article:
            continue
        for t in c.article.tags:
            if not t in tag_set:
                tag_set.add(t)
        articles.append(c.article)
        if c.message:
            if c.article:
                warnings[c.path] = c.message
            else:
                errors[c.path] = c.message

    tags = list(tag_set)
    articles = sorted(articles, key=lambda a: a.date)

    return BlogData(
        categories=categories,
        articles=articles,
        tags=tags,
        warnings=warnings,
        errors=errors,
    )
