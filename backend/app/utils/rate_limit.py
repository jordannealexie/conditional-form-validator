import time
from redis import Redis
from fastapi import HTTPException, Request
from app.core.config import settings
from typing import Optional

class SimpleRateLimiter:
    """
    Very simple Redis-based rate limiter
    """
    def __init__(self):
        redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        try:
            self.redis = Redis.from_url(redis_url)
        except:
            self.redis = None

    async def check(self, key: str, limit: int, window_seconds: int):
        """
        Check if the key is within the rate limit.
        Simple window approach (not sliding).
        """
        if not self.redis:
            return # Skip if Redis is down
            
        try:
            full_key = f"rate_limit:{key}"
            current = self.redis.get(full_key)
            
            if current and int(current) >= limit:
                ttl = self.redis.ttl(full_key)
                raise HTTPException(
                    status_code=429, 
                    detail=f"Too many requests. Try again in {ttl} seconds."
                )
            
            pipe = self.redis.pipeline()
            pipe.incr(full_key)
            if not current:
                pipe.expire(full_key, window_seconds)
            pipe.execute()
        except HTTPException:
            raise
        except Exception as e:
            print(f"Rate limiter error: {e}")
            return # Fail open if Redis has issues

rate_limiter = SimpleRateLimiter()
