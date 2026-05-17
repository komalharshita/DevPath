# utils/rate_limiter.py
import os
from functools import wraps
from flask import request, jsonify
import redis

# Initialize Redis connection pool
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"[Warning] Failed to connect to Redis for Rate Limiter: {e}")
    redis_client = None

def limit_rate(limit: int, period: int = 60):
    """
    Flask decorator to apply sliding/fixed window rate limiting using Redis.

    :param limit: Maximum number of allowed requests.
    :param period: Time window in seconds.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not redis_client:
                # Fallback: if Redis is down, fail open so users aren't locked out
                return f(*args, **kwargs)

            # Track rate limit by IP address and endpoint string
            user_id = request.remote_addr
            endpoint = request.endpoint
            redis_key = f"rate_limit:{user_id}:{endpoint}"
            
            try:
                # Increment the request count for this specific window
                current_requests = redis_client.incr(redis_key)
                
                # If it's the first request in the window, set the TTL
                if current_requests == 1:
                    redis_client.expire(redis_key, period)
                    
                if current_requests > limit:
                    ttl = redis_client.ttl(redis_key)
                    response = jsonify({
                        "error": "Too many requests. Please slow down.",
                        "retry_after_seconds": ttl if ttl > 0 else period
                    })
                    response.headers["Retry-After"] = str(ttl)
                    return response, 429
                    
            except redis.RedisError as e:
                # Log redis error, but allow the request through to preserve uptime
                print(f"[Redis Error] Rate limiter connection issue: {e}")
                
            return f(*args, **kwargs)
        return wrapped
    return decorator