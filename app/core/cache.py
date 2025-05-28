import json
import redis
from typing import Any, Optional

from app.core.config import settings


class RedisCache:
    """
    Utility class for Redis caching operations
    """
    _instance = None
    _redis_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
            cls._redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                decode_responses=True
            )
        return cls._instance

    def set(self, key: str, value: Any, expire_time: int = 300) -> None:
        """
        Set a value in the cache with expiration time

        Args:
            key: Cache key
            value: Value to cache
            expire_time: Seconds until expiration (default: 300 seconds)
        """
        serialized_value = json.dumps(value)
        self._redis_client.set(key, serialized_value, ex=expire_time)

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache

        Args:
            key: Cache key

        Returns:
            Any: Cached value if exists, None otherwise
        """
        value = self._redis_client.get(key)
        if value:
            return json.loads(value)
        return None

    def delete(self, key: str) -> None:
        """
        Delete a value from the cache

        Args:
            key: Cache key to delete
        """
        self._redis_client.delete(key)

    def clear_user_cache(self, user_id: int) -> None:
        """
        Clear all cache entries for a specific user

        Args:
            user_id: User ID to clear cache for
        """
        pattern = f"user:{user_id}:*"
        keys = self._redis_client.keys(pattern)
        if keys:
            self._redis_client.delete(*keys)
