from fastapi import APIRouter,Depends,status,HTTPException
from typing import Annotated
from supabase import Client
from bot.supabase.client import getClient
from bot.supabase.handlers import user_status
from bot.core.schema import WhatsAppEvent
from bot.core.utils import send_message
from bot.core.dummy import messages, stages
from bot.cache.redis import Redis
from bot.config.env import env

#initialize webhook router
webhook_router = APIRouter(tags=["webhook-trigger"])

@webhook_router.post("/webhook",status_code=status.HTTP_200_OK)
def webhook_handler(payload:WhatsAppEvent,db=Depends(getClient)):
    # phone_number = number.split("@s.whatsapp.net")[0]
    #check incoming phone number is in database. if not add to the database
    MESSAGE = payload.data.messages.message.conversation
    NUMBER = payload.data.messages.key.remoteJid.split("@s.whatsapp.net")[0]
    limit = env.RATE_LIMITER_LIMIT if hasattr(env, "RATE_LIMITER_LIMIT") else 10
    period = env.RATE_LIMITER_WINDOW if hasattr(env, "RATE_LIMITER_WINDOW") else 20

    key = f"rl:{NUMBER}" 

    allowed, current = Redis.rate_limit(key, limit=limit, period_seconds=period)
    if not allowed:
        send_message(NUMBER,messages["RATE_LIMIT_NOTE"])
        


    user = user_status(phone_number=NUMBER,db=db)
    if user is False:
        #send respond to the the he is banned
        send_message(NUMBER,messages["BANNED_USER"])
         #continue with the process

    if MESSAGE == "start":
        send_message(NUMBER,messages["MAIN_MENU_MESSAGE"])
        Redis.cache_setter(f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["MAIN_MENU"])


    user_stage = Redis.cache_getter(f"stage_{NUMBER}")
    if user_stage == stages["MAIN_MENU"]:
        match MESSAGE:
            case "1":
                send_message(NUMBER,messages["MAIN_MENU_01_MESSAGE"])
                Redis.cache_setter(f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["MAIN_MENU_01_MESSAGE"])



    
    
    

