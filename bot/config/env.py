from pydantic_settings import BaseSettings
from decouple import config


class Env(BaseSettings):
    """BAse class for all the env variables"""
    REDIS_EXPIRE_TIME: int = config("REDIS_EXPIRE_TIME")
    SUPABASE_URL: str = config("SUPABASE_URL")
    SUPABASE_KEY: str = config("SUPABASE_KEY")
    WASENDER_BASE_URL:str = config("WASENDER_BASE_URL")
    WASENDER_API_KEY:str = config("WASENDER_API_KEY")
    RATE_LIMITER_REDIS:int = config("RATE_LIMITER_REDIS")
    RATE_LIMITER_WINDOW:int = config("RATE_LIMITER_WINDOW")
    RATE_LIMITER_LIMIT:int = config("RATE_LIMITER_LIMIT")
    REDIS_HOST:str = config("REDIS_HOST")
    REDIS_PORT:int = config("REDIS_PORT")
    REDIS_PASSWORD:str = config("REDIS_PASSWORD")
    REDIS_USERNAME:str = config("REDIS_USERNAME")
    MARZBAN_BASE_DOMAIN:str = config("MARZBAN_BASE_DOMAIN")
    MARZBAN_PORT:int = config("MARZBAN_PORT")
    MARZBAN_USERNAME:str = config("MARZBAN_USERNAME")
    MARZBAN_PASSWORD:str = config("MARZBAN_PASSWORD")


env = Env()