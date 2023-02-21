import datetime
# pylint: disable=no-name-in-module
from pydantic import BaseModel


class Tag(BaseModel):
    slug: str
    name: str

class Blog(BaseModel):
    slug: str
    title: str
    date: datetime.date
    body: str
    digest: str = ''
    image: str = ''
    tags: list[Tag] = []
    special: bool = False
    private: bool = False

class Category(BaseModel):
    slug: str
    name: str
    blogs: list[Blog]
