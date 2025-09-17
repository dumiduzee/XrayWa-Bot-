from pydantic_settings import BaseSettings
from decouple import config


class Env(BaseSettings):
    """BAse class for all the env variables"""
    REDIS_EXPIRE_TIME: int = config("REDIS_EXPIRE_TIME")

env = Env()