import requests
from bot.config.env import env

#send message to the user back with wasender api

def send_message(number,content):
    try:

        params = {
            "Authorization":f"Bearer {env.WASENDER_API_KEY}",
            "Content-Type":"application/json"
        }
        print(params)
        data = {
            "to": f"+{number}",
            "text": f"{content}"
            }

        res = requests.post(f"{env.WASENDER_BASE_URL}/api/send-message",headers=params,json=data)
        if res.ok:
            return True
        return
        
    except Exception:
        return False