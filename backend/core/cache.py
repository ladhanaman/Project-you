# core/cache.py - Redis Cache
"""
Redis caching module with decorator support.
"""
import redis
import json
import logging
from typing import Optional, Any
from functools import wraps

from core.config import settings

logger = logging.getLogger(__name__)

# Redis connection
REDIS_URL = settings.REDIS_URL

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info(f"Redis cache connected: {REDIS_URL}")
except Exception as e:
    logger.warning(f"Redis cache not available: {e}. Caching will be disabled.")
    redis_client = None


def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    if not redis_client:
        return None
    
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Cache get error for key {key}: {e}")
        return None


def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """Set value in cache with TTL (default 1 hour)"""
    if not redis_client:
        return False
    
    try:
        redis_client.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        logger.error(f"Cache set error for key {key}: {e}")
        return False


def cache_delete(key: str) -> bool:
    """Delete key from cache"""
    if not redis_client:
        return False
    
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Cache delete error for key {key}: {e}")
        return False


def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator for caching function results
    
    Usage:
        @cached(ttl=3600, key_prefix="tests")
        def get_tests():
            return expensive_operation()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_value = cache_get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {cache_key}, cached result")
            return result
        
        return wrapper
    return decorator
