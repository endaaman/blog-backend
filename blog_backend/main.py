import time
import click
from fastapi import Depends, FastAPI

from .routers import blogs
from .watcher import init_watcher, start_watcher
from .config import get_config


app = FastAPI()
app.include_router(blogs.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

def start():
    config = get_config()
    init_watcher(target_dir=config.blogs_dir)
    start_watcher()
    app()
