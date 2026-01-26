"""
Template Caching Layer for Performance Optimization
Prevents N+1 queries and reduces RDS load
"""
from typing import Optional, Dict, Any
from functools import lru_cache
import json
import hashlib
from datetime import datetime, timedelta

class TemplateCache:
    """
    In-memory cache for form templates
    
    Use Redis in production for distributed caching:
    - redis.Redis(host='localhost', port=6379, db=0)
    - Set TTL for cache entries
    - Invalidate on template updates
    """
    
    def __init__(self, ttl_seconds: int = 3600):
        """Initialize cache with TTL (default 1 hour)"""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, datetime] = {}
        self.ttl = timedelta(seconds=ttl_seconds)
    
    def _generate_key(self, template_id: int) -> str:
        """Generate cache key for template"""
        return f"template:{template_id}"
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self._timestamps:
            return True
        return datetime.now() - self._timestamps[key] > self.ttl
    
    def get(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        Get template from cache
        
        Returns:
            Template dict or None if not cached/expired
        """
        key = self._generate_key(template_id)
        
        if key not in self._cache or self._is_expired(key):
            return None
        
        return self._cache[key]
    
    def set(self, template_id: int, template_data: Dict[str, Any]) -> None:
        """
        Store template in cache
        
        Args:
            template_id: Template ID
            template_data: Full template data including schema
        """
        key = self._generate_key(template_id)
        self._cache[key] = template_data
        self._timestamps[key] = datetime.now()
    
    def invalidate(self, template_id: int) -> None:
        """
        Invalidate cache for specific template
        
        Call this on template create/update/delete
        """
        key = self._generate_key(template_id)
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def invalidate_all(self) -> None:
        """Clear entire cache"""
        self._cache.clear()
        self._timestamps.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "entries": len(self._cache),
            "ttl_seconds": self.ttl.total_seconds(),
            "oldest_entry": min(self._timestamps.values()) if self._timestamps else None,
            "newest_entry": max(self._timestamps.values()) if self._timestamps else None
        }


# Global cache instance
template_cache = TemplateCache(ttl_seconds=3600)  # 1 hour TTL


# Redis implementation (for production)
"""
import redis
from typing import Optional, Dict, Any
import json

class RedisTemplateCache:
    def __init__(self, redis_url: str = "redis://localhost:6379/0", ttl_seconds: int = 3600):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.ttl = ttl_seconds
    
    def _generate_key(self, template_id: int) -> str:
        return f"template:{template_id}"
    
    def get(self, template_id: int) -> Optional[Dict[str, Any]]:
        key = self._generate_key(template_id)
        data = self.redis_client.get(key)
        return json.loads(data) if data else None
    
    def set(self, template_id: int, template_data: Dict[str, Any]) -> None:
        key = self._generate_key(template_id)
        self.redis_client.setex(key, self.ttl, json.dumps(template_data))
    
    def invalidate(self, template_id: int) -> None:
        key = self._generate_key(template_id)
        self.redis_client.delete(key)
    
    def invalidate_all(self) -> None:
        keys = self.redis_client.keys("template:*")
        if keys:
            self.redis_client.delete(*keys)
"""
