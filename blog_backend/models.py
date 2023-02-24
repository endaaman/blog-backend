import datetime
# pylint: disable=no-name-in-module
from pydantic import BaseModel, Field, validator
from pydantic.datetime_parse import parse_date


class Category(BaseModel):
    priority: int
    slug: str
    name: str

class Article(BaseModel):
    category: Category
    slug: str
    title: str
    date: datetime.date
    body: str
    digest: str = ''
    image: str = ''
    tags: list[str] = Field(default_factory=list)
    special: bool = False
    private: bool = False

    # @classmethod
    @validator("date")
    def validate_date(cls, v):
        return parse_date(v)


class BlogData(BaseModel):
    articles: list[Article]
    categories: list[Category]
    tags: list[str]
    warnings: dict[str, str]
    errors: dict[str, str]


# Category.update_forward_refs()
