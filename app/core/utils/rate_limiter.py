from fastapi import HTTPException, Request, Depends
from typing import Tuple
import time, logging
from backend.app.core.cache.redis_cache import cache
from backend.app.services.token_service import verify_token
from fastapi.security import HTTPBearer
from jose.exceptions import JWTError

logger = logging.getLogger(__name__)
security = HTTPBearer()

class RateLimiter:
    def __init__(self):
        self.cache = cache
        
        self.default_limits = {
            "GET": 120,
            "POST": 60,
            "PUT": 60,
            "DELETE": 30
        }

        self.endpoint_limits = {
            "/api/chain/execute": 30,
            "/api/neuroweave/ask": 40,
            "/api/rootbloom/generate": 40
        }

    def _get_real_ip(self, request: Request) -> str:
        """Get real IP accounting for proxies"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host

    async def _get_client_id(self, request: Request) -> str:
        """Get client identifier (user ID or IP)"""
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header:
                token = auth_header.split(" ")[1]
                payload = verify_token(token)
                return f"user:{payload.get('sub')}"
        except (IndexError, JWTError):
            pass

        return f"ip:{self._get_real_ip(request)}"

    async def check_rate_limit(self, request: Request) -> Tuple[bool, int, int]:
        """Check if request is within rate limits"""
        client_id = await self._get_client_id(request)
        method = request.method
        endpoint = request.url.path
        
        limit = self.endpoint_limits.get(endpoint, self.default_limits.get(method, 60))
        window = 60  # 1 minute window
        
        key = f"ratelimit:{client_id}:{method}:{endpoint}"
        
        try:
            # Use Redis for atomic increment
            current = await self.cache.incr(key)
            
            if current == 1:
                await self.cache.expire(key, window)
                
            ttl = await self.cache.ttl(key)
            
            if current > limit:
                logger.warning(f"Rate limit exceeded: {client_id} on {method} {endpoint}")
                return False, 0, ttl
                
            return True, limit - current, ttl
            
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            return True, 0, 60  # Fail open with warning

rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Middleware to enforce rate limits"""
    is_allowed, remaining, reset_in = await rate_limiter.check_rate_limit(request)
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Too many requests",
                "retry_after": reset_in
            }
        )
        
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + reset_in)
    
    return response