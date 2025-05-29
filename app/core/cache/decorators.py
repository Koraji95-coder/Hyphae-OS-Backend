from functools import wraps
from .redis_cache import cache
import hashlib
import json

def cached(expire: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            key = hashlib.md5(json.dumps(key_parts).encode()).hexdigest()

            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(key, result, expire)
            return result
        return wrapper
    return decorator