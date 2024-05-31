import os
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Header, Response
from fastapi.params import Query

from .store import global_store as store



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
        aa.append(a)
    return aa

@router.get('/categories')
async def get_articles_by_category():
    data = store.get_blog_data()
    return data.categories

@router.get('/tags')
async def get_articles_by_category():
    data = store.get_blog_data()
    return data.tags

@router.get('/status')
async def get_status():
    data = store.get_blog_data()
    return {
        'warnings': data.warnings,
        'errors': data.errors,
    }

@router.get('/data')
async def get_status():
    data = store.get_blog_data()
    return data
