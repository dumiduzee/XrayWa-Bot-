import redis
from bot.config.env import env

#initializing redis client
r = redis.Redis(host="localhost",port=6379,db=0)


#setter method for redis

class Redis:
    def cache_setter(key:str,value:str):
        """Reture true if ok | else false | arguments - key,value"""
        r.setex(name=key,time=env.REDIS_EXPIRE_TIME,value=value)
        return True

    def cache_getter(key:str):
        """Return value data | argument - key"""
        result = r.get(name=key)
        return result