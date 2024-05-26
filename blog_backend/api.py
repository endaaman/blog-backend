import os
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Header, File, UploadFile, Response, Form

from .loader import load_blog_data




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
async def get_articles():
    return { 'message': 'Hello.'}


