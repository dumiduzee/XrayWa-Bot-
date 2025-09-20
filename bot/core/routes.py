from fastapi import APIRouter,Depends,status,HTTPException
from typing import Annotated
from supabase import Client
from bot.supabase.client import getClient
from bot.supabase.handlers import get_configs, user_status
from bot.core.schema import WhatsAppEvent
from bot.core.utils import send_message
from bot.core.dummy import messages, stages
from bot.cache.redis import Redis
from bot.config.env import env

#initialize webhook router
webhook_router = APIRouter(tags=["webhook-trigger"])

@webhook_router.post("/webhook",status_code=status.HTTP_200_OK)
def webhook_handler(payload:WhatsAppEvent,db=Depends(getClient)):
    MESSAGE = payload.data.messages.message.conversation
    NUMBER = payload.data.messages.key.remoteJid.split("@s.whatsapp.net")[0]
   


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
                Redis.cache_setter(f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["MAIN_MENU_01_STAGE"])

            case "2":
                
                #get all the configs related to a user
                configs = get_configs(phone=NUMBER,db=db)
                if configs.data[0]["config"] is None:
                    send_message(NUMBER,messages["MAIN_MENU_02_MESSAGE_WHEN_NO_CONFIGS"])
                    Redis.cache_setter(f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["MAIN_MENU"])
                else:
                    #get the config and pass it to the user
                    send_message(NUMBER,
                    f"""
                    ⚙️ DragonForce Bot – Get all configs
                                 
                    *Here is you config👇*
                                
                    *`{configs.data[0]["config"]}`*
                    """)
            case "3":
                pass

            case "4":
                pass
            case "5":
                #return all the package details and prices
                send_message(NUMBER,messages["MAIN_MENU_05_MESSAGE"])
                Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["MAIN_MENU"])

                    



    
    
    

