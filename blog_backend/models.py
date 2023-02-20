# pylint: disable=no-name-in-module
from pydantic import BaseModel


class Tag(BaseModel):
    slug: str
    name: str

class Blog(BaseModel):
    title: str
    slug: str
    body: str
    tags: list[Tag] = []

    def from_text(self, text):
        return Blog(
            title='HOGE',
            slug='hoge',
            body='hoge hoge fuga fuga',
            tags=[Tag(slug='tag', title='TAG')],
            category=Category(slug='category', title=''),
        )

class Category(BaseModel):
    slug: str
    name: str
    blogs: list[Blog]
