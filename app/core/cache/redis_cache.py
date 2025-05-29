import redis
import json
from typing import Any, Optional
from shared.config.env_loader import get_env_variable

class RedisCache:
    def __init__(self):
        self.redis = redis.Redis(
            host=get_env_variable("REDIS_HOST", "localhost"),
            port=int(get_env_variable("REDIS_PORT", "6379")),
            db=0,
            decode_responses=True
        )

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, expire: int = 3600):
        """Set value in cache with expiration in seconds"""
        try:
            self.redis.setex(
                key,
                expire,
                json.dumps(value)
            )
        except Exception as e:
            print(f"Redis set error: {e}")

    def delete(self, key: str):
        """Delete key from cache"""
        try:
            self.redis.delete(key)
        except Exception as e:
            print(f"Redis delete error: {e}")

cache = RedisCache()