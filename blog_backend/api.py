import os
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Header, Response
from fastapi.params import Query

from .store import global_store as store
from .utils import purge_cf_cache


class BlogService:
    def __init__(self):
        pass

    def get_articles(self):
        return []

router = APIRouter(
    prefix='/api',
    tags=['api'],
)

@router.get('/articles')
async def get_articles(category:str=Query(None), tag:str=Query(None)):
    data = store.get_blog_data()
    aa = []
    for a in data.articles:
        if category:
            if category != a.category.slug:
                continue
        if tag:
            if tag not in a.tags:
                continue
        aa.append(a.dict(exclude={'body'}))
    return aa

@router.get('/articles/{c}/{s}')
async def get_article(c:str, s:str):
    data = store.get_blog_data()
    for a in data.articles:
        if a.category.slug == c:
            if a.slug == s:
                return a
    raise HTTPException(404)

@router.get('/categories')
async def get_articles_by_category():
    data = store.get_blog_data()
    return data.categories

@router.get('/tags')
async def get_articles_by_category():
    data = store.get_blog_data()
    return data.tags

@router.get('/data')
async def get_status():
    data = store.get_blog_data()
    return data.dict(exclude={'articles': {'__all__': {'body'}}})

@router.get('/purge')
async def root():
    error = await purge_cf_cache()
    if error is None:
        return { 'message': 'Successfully purged Cloudflare cache'}
    return { 'message': f'Cache purge failed: {error}', }

@router.get('/')
async def get_status():
    data = store.get_blog_data()
    return {
        'message': 'Hey there, this is endaaman.com API server.',
        'warnings': data.warnings,
        'errors': data.errors,
    }
