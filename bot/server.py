from fastapi import FastAPI
from bot.cache.redis import Redis
from bot.core.routes import webhook_router


app = FastAPI()


app.include_router(webhook_router,prefix="/api")






