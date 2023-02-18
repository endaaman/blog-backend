from functools import lru_cache
from pydantic import BaseSettings


class Config(BaseSettings):
    blogs_dir: str

    class Config:
        env_file = '.env'


@lru_cache()
def get_config():
    return Config()
