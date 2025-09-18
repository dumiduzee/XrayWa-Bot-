from typing import Tuple
import redis
from bot.config.env import env


redis_client = redis.Redis(
        host=env.REDIS_HOST,
        port=env.REDIS_PORT,
        password=env.REDIS_PASSWORD,
        username=env.REDIS_USERNAME,  
        decode_responses=True
    )


class Redis:
    @staticmethod
    def cache_setter(key: str, value: str, ex: int | None = None) -> bool:
        """Simple set with optional expire."""
        if ex:
            redis_client.set(name=key, value=value, ex=ex)
        else:
            redis_client.set(name=key, value=value)
        return True

    @staticmethod
    def cache_getter(key: str):
        return redis_client.get(name=key)

    @staticmethod
    def rate_limit(key: str, limit: int, period_seconds: int) -> Tuple[bool, int]:
        """
        Rate limit by key.

        Returns (allowed, current_count).
        - allowed: True if request is allowed (current_count <= limit)
        - current_count: current counter value after increment

        Implementation:
        - INCR the key
        - If the value == 1, set EXPIRE to period_seconds
        - If value > limit => not allowed
        """
        try:
            # atomic increment
            current = redis_client.incr(key)
            if current == 1:
                # first request in this window -> set TTL
                redis_client.expire(key, period_seconds)
            allowed = current <= limit
            return allowed, int(current)
        except redis.RedisError as e:
            print("redis error",e)
            # In case redis is down, fail open (allow) or you may choose fail-closed.
            # Returning allowed=True avoids blocking users if Redis is not reachable.
            return True, 0
