import os
from datetime import timedelta

from functools import lru_cache
from pydantic import BaseSettings, validator


class Config(BaseSettings):
    ARTICLES_DIR: str
    PASSWORD_HASH: str
    SECRET_KEY: str
    EXPIRATION_HOURS: int

    class Config:
        env_file = '.env'
        frozen = True

    def __init__(self):
        super().__init__()

    @validator('ARTICLES_DIR', pre=True)
    def validate_ARTICLES_DIR(cls, v):
        return os.path.abspath(v)

    def expiration_duration(self):
        return timedelta(self.EXPIRATION_HOURS)
