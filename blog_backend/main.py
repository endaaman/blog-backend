from fastapi import Depends, FastAPI

from .dependencies import get_query_token, get_token_header
from .internal import admin
from .routers import items, users

app = FastAPI()

app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


def start():
    app()
