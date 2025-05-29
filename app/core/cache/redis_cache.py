import aioredis
from typing import Any, Optional
from shared.config.env_loader import get_env_variable

class RedisCache:
    def __init__(self):
        self.pool = aioredis.ConnectionPool(
            host=get_env_variable("REDIS_HOST", "localhost"),
            port=int(get_env_variable("REDIS_PORT", "6379")),
            db=0,
            decode_responses=True,
            max_connections=10,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        self.redis = aioredis.Redis(connection_pool=self.pool)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with connection pooling"""
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 3600):
        """Set value in cache with expiration in seconds"""
        try:
            await self.redis.setex(
                key,
                expire,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    async def delete(self, key: str):
        """Delete key from cache"""
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    async def close(self):
        """Close all connections in the pool"""
        await self.pool.disconnect()

# Global cache instance
cache = RedisCache()