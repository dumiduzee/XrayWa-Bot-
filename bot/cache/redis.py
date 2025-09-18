# bot/cache/redis.py
import redis
from typing import Tuple

# Create a single redis client for the app lifetime (adjust host/port/db as needed)
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

class Redis:
    @staticmethod
    def cache_setter(key: str, value: str, ex: int | None = None) -> bool:
        """Simple set with optional expire."""
        if ex:
            r.set(name=key, value=value, ex=ex)
        else:
            r.set(name=key, value=value)
        return True

    @staticmethod
    def cache_getter(key: str):
        return r.get(name=key)

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
            current = r.incr(key)
            if current == 1:
                # first request in this window -> set TTL
                r.expire(key, period_seconds)
            allowed = current <= limit
            return allowed, int(current)
        except redis.RedisError as e:
            print("redis error",e)
            # In case redis is down, fail open (allow) or you may choose fail-closed.
            # Returning allowed=True avoids blocking users if Redis is not reachable.
            return True, 0
