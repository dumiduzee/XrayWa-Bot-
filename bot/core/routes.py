import decouple
from fastapi import APIRouter,Depends,status,HTTPException
from typing import Annotated
from supabase import Client
from bot.supabase.client import getClient
from bot.supabase.handlers import (CheckUserHaveConfig, deleteConfig, get_configs,
    getMarzbanUsername, getUserPackage, SaveConfig, user_status)
from bot.core.schema import WhatsAppEvent
from bot.core.utils import config_Created_message, send_message
from bot.core.dummy import messages, PACKAGES, stages
from bot.cache.redis import Redis
from bot.config.env import env
from bot.core.marzban_handlers import getUsageMarzban, marzban_config_create, marzban_login
import uuid

#initialize webhook router
webhook_router = APIRouter(tags=["webhook-trigger"])

@webhook_router.post("/webhook",status_code=status.HTTP_200_OK)
def webhook_handler(payload:WhatsAppEvent,db=Depends(getClient)):
    msg = payload.data.messages.message

    # Handle both conversation and extendedTextMessage
    if msg.conversation:
        MESSAGE = msg.conversation
    elif msg.extendedTextMessage:
        MESSAGE = msg.extendedTextMessage.text
    else:
        MESSAGE = None  # fallback if unknown message type

    NUMBER = payload.data.messages.key.remoteJid.split("@s.whatsapp.net")[0]
   
    user = user_status(phone_number=NUMBER,db=db)
    if user is False:
        #send respond to the the he is banned
        send_message(NUMBER,messages["BANNED_USER"])
         #continue with the process


    



    user_stage = Redis.cache_getter(f"stage_{NUMBER}")
    if user_stage == stages["MAIN_MENU"]:
        match MESSAGE:
            case "1":
                #check user already have a config
                hasConfig = CheckUserHaveConfig(number=NUMBER,db=db)
                if hasConfig:
                    send_message(NUMBER,content="*You already have a config! you cannot create anymore!! 😤*")
                    Redis.cache_setter(f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                    return
                else:
                    send_message(NUMBER,messages["MAIN_MENU_01_MESSAGE"])
                    Redis.cache_setter(f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["MAIN_MENU_01_STAGE"])

            case "2":
                
                #get all the configs related to a user
                configs = get_configs(phone=NUMBER,db=db)
                if configs.data[0]["config"] is None:
                    send_message(NUMBER,messages["MAIN_MENU_02_MESSAGE_WHEN_NO_CONFIGS"])
                    Redis.cache_setter(f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                else:
                    #get the config and pass it to the user
                    send_message(NUMBER,
                    f"""
                    ⚙️ DragonForce Bot – Get all configs
                                 
                    *Here is you config👇*
                                
                    *`{configs.data[0]["config"]}`*
                    """)
                    Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
            case "3":
                #delete config user have
                isConfigHave = CheckUserHaveConfig(number=NUMBER,db=db)
                if not isConfigHave:
                    send_message(NUMBER,content="*You don't have a config to delete! please create a config first😤*")
                    Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                    return
                #get users package
                package = getUserPackage(number=NUMBER,db=db)
                if not package:
                    send_message(NUMBER,content="*Something went wrong on our side!😳*")
                    Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                    return
                #asking from user he really want to delete the config
                send_message(NUMBER,
                             content=(
                                "*⚙️ DragonForce Bot – Config Delete!! 😍*\n\n"
                                f"*You have a {package} config.Do you need to delete it ? ⚠️*\n\n"
                                "*1️⃣ Yes i need to delete!*\n"
                                "*2️⃣ Hell nooo!*\n"
                            ))
                Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["MAIN_MENU_03_STAGE"])
                return



            case "4":
                #get usage of a config
                #check user have a config or not
                haveConfig = CheckUserHaveConfig(number=NUMBER,db=db)
                if not haveConfig:
                    send_message(number=NUMBER,content="*You don't have a config to check usage🙂‍↕️*")
                    Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                else:
                #get marzban username of the user
                    username = getMarzbanUsername(number=NUMBER,db=db)
                    if not username:
                        send_message(number=NUMBER,content="*Something went went wrong in our side!🙂‍↕️*")
                        Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                    else:
                        #get the username and check via marzban pannel usage
                        usage = getUsageMarzban(usernameArg=username)
                        if not usage:
                            send_message(number=NUMBER,content="*Something went went wrong in our side!🙂‍↕️*")
                            Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                        else:
                            send_message(number=NUMBER,content=(
                                "*⚙️ DragonForce Bot – Config Usage!! 😍*\n\n"
                                f"*You used {usage}GB out of 100GB.😍*\n\n"
                                f"*Remaining Quota - {100-usage} 🫴*\n"
                                "*Expire - In 6 days 🫴*\n"
                            ))
                            Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])

            case "5":
                #return all the package details and prices
                send_message(NUMBER,messages["MAIN_MENU_05_MESSAGE"])
                Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])


    elif(user_stage == stages["MAIN_MENU_01_STAGE"]):
        match MESSAGE:
            case "1":
                #create config via marzban
                config,username = marzban_config_create(package=PACKAGES["DIALOG_ROUTER"],username=f"{NUMBER}_{str(uuid.uuid4()).split("-")[2]}")
                if config is not None and user is not None:
                    #save config and config username into database
                    result = SaveConfig(config=config,username=username,number=NUMBER,package="Dialog Router",db=db)
                    if not result:
                        send_message(number=NUMBER,content="*Something went wrong on our side!😳*")
                        Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                    config_Created_message(NUMBER,config,username)
                    Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                    
            case "2":
                #create config via marzban
                config,username = marzban_config_create(package=PACKAGES["MOBITEL"],username=f"{NUMBER}_{str(uuid.uuid4()).split("-")[2]}")
                if config is not None and user is not None:
                    #save config and config username into database
                    result = SaveConfig(config=config,username=username,number=NUMBER,package="Mobitel",db=db)
                    if result:
                        config_Created_message(NUMBER,config,username)
                        Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                        return
                    send_message(number=NUMBER,content="*Something went wrong on our side!😳*")
                    Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
            case "3":
                #create config via marzban
                config,username = marzban_config_create(package=PACKAGES["AIRTEL"],username=f"{NUMBER}_{str(uuid.uuid4()).split("-")[2]}")
                if config is not None and user is not None:
                    #save config and config username into database
                    result = SaveConfig(config=config,username=username,number=NUMBER,package="Airtel",db=db)
                    if result:
                        config_Created_message(NUMBER,config,username)
                        Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                        return
                    send_message(number=NUMBER,content="*Something went wrong on our side!😳*")
                    Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
            case "4":
                #create config via marzban
                config,username = marzban_config_create(package=PACKAGES["HUTCH"],username=f"{NUMBER}_{str(uuid.uuid4()).split("-")[2]}")
                if config is not None and user is not None:
                    #save config and config username into database
                    result = SaveConfig(config=config,username=username,number=NUMBER,package="Hutch",db=db)
                    if result:
                        config_Created_message(NUMBER,config,username)
                        Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                        return
                    send_message(number=NUMBER,content="*Something went wrong on our side!😳*")
                    Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
            case "5":
                #create config via marzban
                config,username = marzban_config_create(package=PACKAGES["SLT-ZOOM"],username=f"{NUMBER}_{str(uuid.uuid4()).split("-")[2]}")
                if config is not None and user is not None:
                    #save config and config username into database
                    result = SaveConfig(config=config,username=username,number=NUMBER,package="Slt zoom",db=db)
                    if result:
                        config_Created_message(NUMBER,config,username)
                        Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                        return
                    send_message(number=NUMBER,content="*Something went wrong on our side!😳*")
                    Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
            case "6":
                #create config via marzban
                config,username = marzban_config_create(package=PACKAGES["SLT-NETFLIX"],username=f"{NUMBER}_{str(uuid.uuid4()).split("-")[2]}")
                if config is not None and user is not None:
                    #save config and config username into database
                    result = SaveConfig(config=config,username=username,number=NUMBER,package="Slt Netflix",db=db)
                    if result:
                        config_Created_message(NUMBER,config,username)
                        Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
                        return
                    send_message(number=NUMBER,content="*Something went wrong on our side!😳*")
                    Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
            case _ :
                send_message(NUMBER,content="*Invalid choice please choose number between 1 to 6!🖖*")
                Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])

    elif(user_stage == stages["MAIN_MENU_03_STAGE"]):
        #delete config stage 2 delete or not delete
        match MESSAGE:
            case "1":
                deleteConfig(number=NUMBER,db=db)
                send_message(NUMBER,content="*Your config deleted!👊*")
                Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
            case "2":
                send_message(NUMBER,content="*Config deletion process intrupted!😶*")
                Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])
            case _:
                send_message(NUMBER,content="*Invalid choice please choose number between 1 to 2!🖖*")
                Redis.cache_setter(key=f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["START"])




    if MESSAGE == "start" or Redis.cache_getter(key=f"stage_{NUMBER}") == stages["START"]:
        send_message(NUMBER,messages["MAIN_MENU_MESSAGE"])
        Redis.cache_setter(f"stage_{NUMBER}",ex=env.REDIS_EXPIRE_TIME,value=stages["MAIN_MENU"])

                    



    
    
    

