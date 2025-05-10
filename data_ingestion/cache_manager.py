import redis
from typing import Any, Optional
import json

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hour
        
    def get_cached_data(self, key: str) -> Optional[Any]:
        """Retrieve data from cache"""
        data = self.redis_client.get(key)
        return json.loads(data) if data else None
        
    def cache_data(self, key: str, data: Any, ttl: Optional[int] = None):
        """Store data in cache with TTL"""
        ttl = ttl or self.default_ttl
        self.redis_client.setex(key, ttl, json.dumps(data))
        
    def invalidate_cache(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)