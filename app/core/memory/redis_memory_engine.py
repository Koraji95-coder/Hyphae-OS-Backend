import redis
import json

class RedisMemoryEngine:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def save(self, user, key, value):
        compound_key = f"{user}:{key}"
        self.redis.set(compound_key, json.dumps(value))

    def fetch(self, user, key):
        val = self.redis.get(f"{user}:{key}")
        return json.loads(val) if val else None

    def clear(self, user):
        keys = self.redis.keys(f"{user}:*")
        for k in keys:
            self.redis.delete(k)
