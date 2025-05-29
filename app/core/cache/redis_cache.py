import aioredis
from typing import Any, Optional
from shared.config.env_loader import get_env_variable

REDIS_URL = get_env_variable("REDIS_URL", "redis://localhost:6379")

pool = redis.ConnectionPool.from_url(
    REDIS_URL,
    max_connections=10,
    decode_responses=True
)

redis_client = redis.Redis(connection_pool=pool)


class RedisCache:
    def __init__(self):
        self.redis = redis.Redis(connection_pool=pool)

    def get(self, key: str) -> Optional[Any]:
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, expire: int = 3600):
        try:
            self.redis.setex(key, expire, json.dumps(value))
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    def delete(self, key: str):
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")


cache = RedisCache()
is sq2l