"""
Redis configuration and client management
"""

import redis.asyncio as redis
import json
from typing import Any, Optional
import structlog

from app.core.config import get_redis_url, settings

logger = structlog.get_logger(__name__)

# Create Redis client
redis_client = redis.from_url(
    get_redis_url(),
    encoding="utf-8",
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
)


class CacheManager:
    """Redis cache manager with JSON serialization"""
    
    def __init__(self, client: redis.Redis):
        self.client = client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error("Cache get error", key=key, error=str(e))
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or settings.CACHE_DEFAULT_TTL
            serialized_value = json.dumps(value, default=str)
            await self.client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error("Cache delete error", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(await self.client.exists(key))
        except Exception as e:
            logger.error("Cache exists error", key=key, error=str(e))
            return False
    
    async def flush_all(self) -> bool:
        """Flush all cache (use with caution)"""
        try:
            await self.client.flushall()
            logger.warning("Cache flushed - all keys deleted")
            return True
        except Exception as e:
            logger.error("Cache flush error", error=str(e))
            return False


# Create cache manager instance
cache = CacheManager(redis_client)


async def get_cache_key(prefix: str, *args) -> str:
    """Generate cache key with prefix"""
    key_parts = [prefix] + [str(arg) for arg in args]
    return ":".join(key_parts)


async def cache_treasury_data(entity_id: str, data: dict, ttl: int = 300) -> bool:
    """Cache treasury data for specific entity"""
    key = await get_cache_key("treasury", entity_id)
    return await cache.set(key, data, ttl)


async def get_cached_treasury_data(entity_id: str) -> Optional[dict]:
    """Get cached treasury data for specific entity"""
    key = await get_cache_key("treasury", entity_id)
    return await cache.get(key)