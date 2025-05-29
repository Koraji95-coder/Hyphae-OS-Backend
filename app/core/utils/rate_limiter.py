from fastapi import HTTPException, Request, Depends
from typing import Tuple
import time, logging, redis
from backend.app.shared.config.env_loader import get_env_variable
from backend.app.services.token_service import verify_token
from fastapi.security import HTTPBearer
from jose.exceptions import JWTError

logger = logging.getLogger(__name__)
security = HTTPBearer()

class RateLimiter:
    def __init__(self):
        self.redis = redis.Redis(
            host=get_env_variable("REDIS_HOST", "localhost"),
            port=int(get_env_variable("REDIS_PORT", "6379")),
            db=0,
            decode_responses=True
        )

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

    def _get_client_id(self, request: Request) -> str:
        """
        📛 Determine the client identity via token or fallback to IP.
        """
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header:
                token = auth_header.split(" ")[1]
                payload = verify_token(token)
                return f"user:{payload.get('sub')}"
        except (IndexError, JWTError, Exception):
            pass

        return f"ip:{request.client.host}"

    def _get_key(self, client_id: str, method: str, endpoint: str) -> str:
        return f"ratelimit:{client_id}:{method}:{endpoint}"

    def check_rate_limit(self, request: Request) -> Tuple[bool, int, int]:
        """
        Returns (allowed: bool, remaining: int, reset_in: int seconds)
        """
        client_id = self._get_client_id(request)
        method = request.method
        endpoint = request.url.path
        limit = self.endpoint_limits.get(endpoint, self.default_limits.get(method, 60))

        key = self._get_key(client_id, method, endpoint)

        try:
            current = self.redis.incr(key)

            if current == 1:
                self.redis.expire(key, 60)

            ttl = self.redis.ttl(key)

            if current > limit:
                logger.warning(f"🚫 Rate limit exceeded for {client_id} on {method} {endpoint}")
                return False, 0, ttl

            return True, limit - current, ttl

        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiter: {e}")
            return True, 0, 60  # fallback

rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    is_allowed, remaining, reset_in = rate_limiter.check_rate_limit(request)

    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Too many requests",
                "retry_after": f"{reset_in} seconds"
            }
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + reset_in)
    return response
