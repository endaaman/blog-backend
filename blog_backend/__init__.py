from fastapi import FastAPI
from .main import *

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

def start():
    app()
