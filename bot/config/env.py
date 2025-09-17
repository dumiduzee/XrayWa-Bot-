from pydantic_settings import BaseSettings
from decouple import config


class Env(BaseSettings):
    """BAse class for all the env variables"""
    REDIS_EXPIRE_TIME: int = config("REDIS_EXPIRE_TIME")
    SUPABASE_URL: str = config("SUPABASE_URL")
    SUPABASE_KEY: str = config("SUPABASE_KEY")
    WASENDER_BASE_URL:str = config("WASENDER_BASE_URL")
    WASENDER_API_KEY:str = config("WASENDER_API_KEY")


env = Env()