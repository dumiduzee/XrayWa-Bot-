from fastapi import APIRouter

#initialize webhook router
webhook_router = APIRouter(tags=["webhook-trigger"])

@webhook_router.post("/webhook")
def webhook_handler(number:str):
    phone_number = number.split("@s.whatsapp.net")[0]
