"""
Redis-based Caching Layer for Performance Optimization
Prevents N+1 queries and reduces database load
Supports distributed caching for horizontal scaling
"""
from typing import Optional, Dict, Any, List
import json
import logging
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis-based cache with support for:
    - Form templates
    - Enum/reference data
    - User sessions
    - Compiled validators
    """
    
    def __init__(self, redis_url: str = None, default_ttl: int = 3600):
        """
        Initialize Redis cache
        
        Args:
            redis_url: Redis connection URL (defaults to settings.REDIS_URL)
            default_ttl: Default TTL in seconds (1 hour)
        """
        self.redis_url = redis_url or settings.REDIS_URL
        self.default_ttl = default_ttl
        self._client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Establish Redis connection"""
        try:
            self._client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Test connection
            await self._client.ping()
            self._connected = True
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Operating without cache.")
            self._connected = False
    
    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self._client:
            await self._client.close()
            self._connected = False
            logger.info("Redis cache disconnected")
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._connected
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/error
        """
        if not self._connected or not self._client:
            return None
        
        try:
            data = await self._client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (defaults to default_ttl)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connected or not self._client:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            await self._client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connected or not self._client:
            return False
        
        try:
            await self._client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern
        
        Args:
            pattern: Redis key pattern (e.g., 'template:*')
            
        Returns:
            Number of keys deleted
        """
        if not self._connected or not self._client:
            return 0
        
        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self._client.delete(*keys)
                return len(keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    async def add_to_set(self, key: str, value: str, ttl: int = None) -> bool:
        """Add a value to a Redis set and optionally set TTL."""
        if not self._connected or not self._client:
            return False

        try:
            await self._client.sadd(key, value)
            if ttl:
                await self._client.expire(key, ttl)
            return True
        except Exception as e:
            logger.warning(f"Cache add_to_set error for key {key}: {e}")
            return False

    async def remove_from_set(self, key: str, value: str) -> bool:
        """Remove a value from a Redis set."""
        if not self._connected or not self._client:
            return False

        try:
            await self._client.srem(key, value)
            return True
        except Exception as e:
            logger.warning(f"Cache remove_from_set error for key {key}: {e}")
            return False

    async def get_set_members(self, key: str) -> List[str]:
        """Get all members of a Redis set."""
        if not self._connected or not self._client:
            return []

        try:
            members = await self._client.smembers(key)
            return list(members) if members else []
        except Exception as e:
            logger.warning(f"Cache get_set_members error for key {key}: {e}")
            return []

    async def invalidate(self, template_id: int) -> None:
        """Invalidate all cache entries related to a template.

        This keeps the interface compatible with the older cache layer
        that exposed an `invalidate(template_id)` method.
        """
        if not self._connected or not self._client:
            return

        try:
            # Single-template cache entry
            await self.delete(CacheKeys.template(template_id))

            # Associated validator caches
            await self.delete(CacheKeys.validator(template_id))
            await self.delete_pattern(f"validator:{template_id}:v*")

            # Template list caches (all/bank-specific)
            await self.delete_pattern("templates:*")
        except Exception as e:
            logger.warning(f"Cache invalidate error for template {template_id}: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self._connected or not self._client:
            return {"connected": False}
        
        try:
            info = await self._client.info("stats")
            memory = await self._client.info("memory")
            return {
                "connected": True,
                "total_connections": info.get("total_connections_received", 0),
                "total_commands": info.get("total_commands_processed", 0),
                "used_memory_human": memory.get("used_memory_human", "unknown"),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            logger.warning(f"Cache stats error: {e}")
            return {"connected": True, "error": str(e)}


class CacheKeys:
    """Cache key patterns for consistent naming"""
    
    @staticmethod
    def template(template_id: int) -> str:
        return f"template:{template_id}"
    
    @staticmethod
    def template_list(bank_id: int = None) -> str:
        if bank_id:
            return f"templates:bank:{bank_id}"
        return "templates:all"
    
    @staticmethod
    def validator(template_id: int, version: int = None) -> str:
        if version:
            return f"validator:{template_id}:v{version}"
        return f"validator:{template_id}"
    
    @staticmethod
    def enum_data(enum_type: str) -> str:
        return f"enum:{enum_type}"
    
    @staticmethod
    def bank(bank_id: int) -> str:
        return f"bank:{bank_id}"
    
    @staticmethod
    def banks_list() -> str:
        return "banks:all"
    
    @staticmethod
    def field_types() -> str:
        return "field_types:all"
    
    @staticmethod
    def user_permissions(user_id: int) -> str:
        return f"permissions:user:{user_id}"


# Global cache instance
cache = RedisCache(default_ttl=3600)  # 1 hour default TTL

# Backward compatibility alias
template_cache = cache
