from fastapi import APIRouter,Depends,status
from typing import Annotated
from supabase import Client
from bot.supabase.client import getClient
from bot.supabase.handlers import user_status
from bot.core.schema import WhatsAppEvent
from bot.core.utils import send_message

#initialize webhook router
webhook_router = APIRouter(tags=["webhook-trigger"])

@webhook_router.post("/webhook",status_code=status.HTTP_200_OK)
def webhook_handler(payload:WhatsAppEvent,db=Depends(getClient)):
    # phone_number = number.split("@s.whatsapp.net")[0]
    #check incoming phone number is in database. if not add to the database
    MESSAGE = payload.data.messages.message.conversation
    NUMBER = payload.data.messages.key.remoteJid.split("@s.whatsapp.net")[0]
    user = user_status(phone_number=NUMBER,db=db)
    if user is False:
        #send respond to the the he is banned
        send_message(NUMBER,"YOU ARE BANNED BROOO")
        pass
    return True
    #continue with the process
    
    
    

