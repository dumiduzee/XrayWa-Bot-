import decouple
import requests
from bot.config.env import env
from bot.core.marzban_handlers import username

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
        print(res.json())
        
    except Exception as e:
        print(e)
        return False
    

#Send a message after config created
def config_Created_message(number,config,username):
    send_message(number=number,content=(
    "*⚙️ DragonForce Bot – Config created!! 😍*\n\n"
    "*Rules ⚠️*\n\n"
    "• *Do not use torrents 🔗*\n"
    "• *Do not spam 🦠*\n"
    "• *Do not use any illegal tools ❌*\n"
    "• *Play safe, avoid ban 👊*\n\n"
    "*Your config 👇*\n\n"
    f"```{config}```\n\n"
    "*Username:* `" + username + "`"
    ))