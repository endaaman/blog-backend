import os
import json
import asyncio

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Header, File, UploadFile, Response, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
from .const import BLOG_DATA_DIR, STATIC_DIR
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
app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')

@app.on_event('startup')
async def on_startup():
    await start_watcher(BLOG_DATA_DIR)

@app.get('/')
async def root():
    return { 'message': 'Hello.'}

app.include_router(api_router)
