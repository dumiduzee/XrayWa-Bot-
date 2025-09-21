from bot.config.env import env
import requests
from bot.cache.redis import Redis
import uuid
from datetime import datetime, timedelta, timezone

domain = env.MARZBAN_BASE_DOMAIN
port = env.MARZBAN_PORT
username = env.MARZBAN_USERNAME
password = env.MARZBAN_PASSWORD

#Login to the pannel and save session in redis
def marzban_login():
    
    url = f"https://{domain}:{port}/api/admin/token"



    payload = {
    "grant_type": "password",
    "username": username,
    "password": password,
    "scope": "",
    "client_id": "string",
    "client_secret": "string"
    }

    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200 and response.ok:
            data = response.json()
            Redis.cache_setter(key="marzban_token",value=data["access_token"],ex=1800)

            return True
    except Exception as e:
        print(e)
        return False


#get package and create a user
def marzban_config_create(package:str,username:str):
    #get the token from redis
    token  = Redis.cache_getter(key="marzban_token")
    id = str(uuid.uuid4())
    #get now time 
    now_utc = datetime.now(timezone.utc)
    #calculate 7nth date utc timestamp for expire time
    seventh_day_timestamp = int((now_utc + timedelta(days=7)).timestamp())
    if not token:
        #if cache not available in redis re call the login func and retrive token
        marzban_login()
    token  = Redis.cache_getter(key="marzban_token")

    url = url = f"https://{domain}:{port}/api/user"

    data = {
    "data_limit": 107374182400,
    "data_limit_reset_strategy": "no_reset",
    "expire": seventh_day_timestamp,
    "inbounds": {
        "vless": [
        f"{package}",
        ],
    },
    "next_plan": {
        "add_remaining_traffic": False,
        "data_limit": 100,
        "expire": 7,
        "fire_on_either": False
    },
    "note": "",
    "on_hold_expire_duration": 0,
    "on_hold_timeout": "2023-11-03T20:30:00",
    "proxies": {
        "vless": {
        "id": f"{id}"
        },
    },
    "status": "active",
    "username": f"{username}"
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(url=url,json=data,headers=headers)
        if response.ok:
            data = response.json()
            return data["links"][0],username
        else:
            return None,None
    except Exception as e:
        return None,None
        print(e)



#check usage of a user with help of username
def getUsageMarzban(usernameArg:str):
    #get token in redis database
    token = Redis.cache_getter(key="marzban_token")
    if not token:
        #if not available it re fetch via marz login function
        marzban_login()
    token = Redis.cache_getter(key="marzban_token")

    url = f"https://{domain}:{port}/api/user/{usernameArg}/usage"
    print(url)
    print(usernameArg)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url=url,headers=headers)
        res = response.json()
        byte = int(res["usages"][0]["used_traffic"])
        gb = byte / (1024 * 1024 * 1024)
        return round(gb, 2)
    except Exception:
        return False

    
  
      

    
    