import os
import json
import asyncio

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Header, File, UploadFile, Response, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
from .const import BLOG_DATA_DIR
from .wather import start_watcher


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        'http://localhost',
        'http://localhost:5173',
        '*',
    ],
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.on_event('startup')
async def on_startup():
    await start_watcher(BLOG_DATA_DIR)


@app.middleware('http')
async def cache_middleware(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path

    response.headers['X-Content-Version'] = '1.0'
    if request.method == 'OPTIONS':
        response.headers['Cache-Control'] = 'no-store'
        return response

    headers = {
        # caching while 1 week
        'Cache-Control': 'public, s-maxage=2592000, stale-while-revalidate=2592000',
        'CDN-Cache-Control': 'public, s-maxage=2592000',
    }

    for key, value in headers.items():
        response.headers[key] = value

    return response


@app.get('/')
async def root():
    return { 'message': 'Hello.'}

app.include_router(api_router)
