import os

from functools import lru_cache
from pydantic import BaseSettings, validator


class Config(BaseSettings):
    BLOGS_DIR: str

    class Config:
        env_file = '.env'

    @validator("BLOGS_DIR", pre=True)
    def validate_BLOGS_DIR(cls, v):
        return os.path.abspath(v)


@lru_cache()
def get_config():
    return Config()
