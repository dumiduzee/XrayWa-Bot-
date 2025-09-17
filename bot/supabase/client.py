from supabase import Client,create_client
from bot.config.env import env
from typing import Annotated
from fastapi import Depends


SUPABASE_URL = env.SUPABASE_URL
SUPABASE_KEY = env.SUPABASE_KEY


supabase_client : Client = create_client(SUPABASE_URL,SUPABASE_KEY)



#getter function for supabase client
def getClient() -> Client :
    return supabase_client


