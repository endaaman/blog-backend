import os

from functools import lru_cache
from pydantic import BaseSettings, validator


class Config(BaseSettings):
    ARTICLES_DIR: str

    class Config:
        env_file = '.env'

    # @classmethod
    @validator("ARTICLES_DIR", pre=True)
    def validate_ARTICLES_DIR(cls, v):
        return os.path.abspath(v)


@lru_cache()
def get_config():
    return Config()
