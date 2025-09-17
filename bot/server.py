from fastapi import FastAPI
from bot.cache.redis import Redis
from bot.core.routes import webhook_router


#initialize app
app = FastAPI(title="Whatsapp Xray core bot",version="1.0")


app.include_router(webhook_router,prefix="/api")






