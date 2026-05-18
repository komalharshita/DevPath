import os
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Thread-safe connection pool for Flask
redis_pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)

def get_redis_client():
    return redis.Redis(connection_pool=redis_pool)