import datetime
from pydantic import BaseModel, Field, validator


class Category(BaseModel):
    slug: str
    label: str
    hidden: bool = True

class Article(BaseModel):
    category: Category
    slug: str
    title: str
    date: datetime.date
    body: str
    digest: str = ''
    image: str = ''
    tags: list[str]
    special: bool = False
    private: bool = False

    @validator('date', pre=True)
    def parse_date(cls, value):
        if isinstance(value, str):
            try:
                return datetime.date.fromisoformat(value)
            except ValueError:
                raise ValueError('Invalid date format. Expected YYYY-MM-DD.')
        return value


class BlogData(BaseModel):
    articles: list[Article]
    categories: list[Category]
    tags: list[str]
    warnings: dict[str, str]
    errors: dict[str, str]
