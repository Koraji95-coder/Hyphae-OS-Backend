"""
redis_client.py 🔌
------------------
Redis interface module for HyphaeOS.

Responsibilities:
- Establish a connection to a local Redis instance
- Expose a reusable Redis client for imports
- Provide a test method to verify availability

Usage:
    from backend.app.redis_client import redis_client
"""

import redis

# 🔗 Connect to local Redis server
redis_client = redis.StrictRedis(
    host="localhost",     # 🏠 Redis server (local)
    port=6379,            # 🔌 Default Redis port
    db=0,                 # 🧱 Redis database index (0 by default)
    decode_responses=True  # 🔡 Automatically decode bytes to strings
)

def test_redis_connection():
    """
    ✅ Ping Redis to confirm connectivity.

    Useful for diagnostics during startup or setup.
    """
    try:
        redis_client.ping()
        print("[+] Redis connection test successful.")
    except redis.exceptions.ConnectionError:
        print("[!] Failed to connect to Redis. Make sure it's running.")
