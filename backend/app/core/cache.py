"""
Redis Cache Module

Provides Redis-based caching functionality for the waste optimization system.
Implements connection pooling, serialization, and cache management utilities.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Union
from urllib.parse import urlparse

import redis
from redis import RedisError
from redis.connection import ConnectionPool

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager with connection pooling and serialization.
    
    Provides a centralized cache interface with automatic JSON serialization,
    connection pooling for performance, and error handling.
    
    Attributes:
        _pool: Redis connection pool
        _default_ttl: Default time-to-live for cache entries in seconds
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True,
        max_connections: int = 50,
    ):
        """Initialize Redis cache manager.
        
        Args:
            host: Redis host address (defaults to settings)
            port: Redis port number (defaults to settings)
            db: Redis database number
            password: Redis password (optional)
            decode_responses: Whether to decode responses as strings
            max_connections: Maximum number of connections in pool
        """
        self._host = host or settings.REDIS_HOST
        self._port = port or settings.REDIS_PORT
        self._db = db
        self._password = password or settings.REDIS_PASSWORD
        self._decode_responses = decode_responses
        self._max_connections = max_connections
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._default_ttl = settings.CACHE_DEFAULT_TTL
        self._initialized = False
    
    @property
    def is_connected(self) -> bool:
        """Check if cache manager is connected."""
        return self._initialized and self._client is not None
    
    def connect(self) -> bool:
        """Establish connection to Redis server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._pool = ConnectionPool(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password if self._password else None,
                decode_responses=self._decode_responses,
                max_connections=self._max_connections,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            
            self._client = redis.Redis(connection_pool=self._pool)
            # Test connection with ping
            self._client.ping()
            self._initialized = True
            logger.info(
                f"Redis cache connected: {self._host}:{self._port}/{self._db}"
            )
            return True
            
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._initialized = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
            self._initialized = False
            return False
    
    def disconnect(self) -> None:
        """Close Redis connection and cleanup resources."""
        if self._pool:
            self._pool.disconnect()
            self._pool = None
        if self._client:
            self._client = None
        self._initialized = False
        logger.info("Redis cache disconnected")
    
    def _serialize(self, value: Any) -> str:
        """Serialize value to JSON string for storage.
        
        Args:
            value: Value to serialize (must be JSON serializable)
            
        Returns:
            JSON string representation
        """
        if isinstance(value, (datetime, timedelta)):
            value = str(value)
        return json.dumps(value, default=str, ensure_ascii=False)
    
    def _deserialize(self, value: Optional[str]) -> Any:
        """Deserialize JSON string from storage.
        
        Args:
            value: JSON string to deserialize
            
        Returns:
            Deserialized Python object
        """
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            logger.warning(f"Failed to deserialize cache value: {value[:100]}")
            return value
    
    def get(self, key: str) -> Any:
        """Retrieve value from cache by key.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Cached value or None if not found
        """
        if not self.is_connected:
            logger.warning("Cache not connected, cannot get value")
            return None
        
        try:
            value = self._client.get(key)
            return self._deserialize(value)
        except RedisError as e:
            logger.error(f"Redis get error for key '{key}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting cache key '{key}': {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Store value in cache with optional expiration.
        
        Args:
            key: Cache key
            value: Value to store (must be JSON serializable)
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            logger.warning("Cache not connected, cannot set value")
            return False
        
        try:
            serialized = self._serialize(value)
            expire_time = ttl if ttl is not None else self._default_ttl
            
            if expire_time > 0:
                self._client.setex(key, expire_time, serialized)
            else:
                self._client.set(key, serialized)
            
            return True
        except RedisError as e:
            logger.error(f"Redis set error for key '{key}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting cache key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted, False otherwise
        """
        if not self.is_connected:
            logger.warning("Cache not connected, cannot delete value")
            return False
        
        try:
            result = self._client.delete(key)
            return result > 0
        except RedisError as e:
            logger.error(f"Redis delete error for key '{key}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting cache key '{key}': {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache.
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            return self._client.exists(key) > 0
        except RedisError as e:
            logger.error(f"Redis exists error for key '{key}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking cache key '{key}': {e}")
            return False
    
    def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Retrieve multiple values from cache.
        
        Args:
            keys: List of cache keys to retrieve
            
        Returns:
            Dictionary mapping keys to values (missing keys excluded)
        """
        if not self.is_connected:
            return {}
        
        try:
            values = self._client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = self._deserialize(value)
            return result
        except RedisError as e:
            logger.error(f"Redis mget error: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error getting multiple cache keys: {e}")
            return {}
    
    def set_many(
        self,
        mapping: dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """Store multiple key-value pairs in cache.
        
        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time-to-live in seconds for all entries
            
        Returns:
            True if all operations successful, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            pipeline = self._client.pipeline()
            expire_time = ttl if ttl is not None else self._default_ttl
            
            for key, value in mapping.items():
                serialized = self._serialize(value)
                if expire_time > 0:
                    pipeline.setex(key, expire_time, serialized)
                else:
                    pipeline.set(key, serialized)
            
            pipeline.execute()
            return True
        except RedisError as e:
            logger.error(f"Redis mset error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting multiple cache keys: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value in cache.
        
        Args:
            key: Cache key to increment
            amount: Amount to increment by
            
        Returns:
            New value after increment, or None on error
        """
        if not self.is_connected:
            return None
        
        try:
            return self._client.incrby(key, amount)
        except RedisError as e:
            logger.error(f"Redis increment error for key '{key}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error incrementing cache key '{key}': {e}")
            return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement numeric value in cache.
        
        Args:
            key: Cache key to decrement
            amount: Amount to decrement by
            
        Returns:
            New value after decrement, or None on error
        """
        if not self.is_connected:
            return None
        
        try:
            return self._client.decrby(key, amount)
        except RedisError as e:
            logger.error(f"Redis decrement error for key '{key}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error decrementing cache key '{key}': {e}")
            return None
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a cache key.
        
        Args:
            key: Cache key to set expiration for
            ttl: Time-to-live in seconds
            
        Returns:
            True if expiration was set, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            return self._client.expire(key, ttl)
        except RedisError as e:
            logger.error(f"Redis expire error for key '{key}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting expiration for key '{key}': {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """Get remaining time-to-live for a key.
        
        Args:
            key: Cache key to check
            
        Returns:
            TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        if not self.is_connected:
            return -2
        
        try:
            return self._client.ttl(key)
        except RedisError as e:
            logger.error(f"Redis ttl error for key '{key}': {e}")
            return -2
        except Exception as e:
            logger.error(f"Unexpected error getting TTL for key '{key}': {e}")
            return -2
    
    def keys(self, pattern: str = "*") -> list[str]:
        """Get all keys matching pattern.
        
        Args:
            pattern: Glob pattern for key matching
            
        Returns:
            List of matching keys
        """
        if not self.is_connected:
            return []
        
        try:
            return self._client.keys(pattern)
        except RedisError as e:
            logger.error(f"Redis keys error with pattern '{pattern}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting keys with pattern '{pattern}': {e}")
            return []
    
    def flush_db(self) -> bool:
        """Flush all keys in current database.
        
        WARNING: This operation is destructive and cannot be undone.
        
        Returns:
            True if flush successful, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            self._client.flushdb()
            logger.warning("Redis database flushed")
            return True
        except RedisError as e:
            logger.error(f"Redis flushdb error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error flushing database: {e}")
            return False
    
    def health_check(self) -> dict[str, Any]:
        """Perform health check on Redis connection.
        
        Returns:
            Dictionary with health status information
        """
        result = {
            "status": "unhealthy",
            "connected": False,
            "response_time_ms": None,
            "error": None,
        }
        
        if not self.is_connected:
            result["error"] = "Not connected to Redis"
            return result
        
        try:
            import time
            start = time.time()
            self._client.ping()
            elapsed = (time.time() - start) * 1000
            
            result["status"] = "healthy"
            result["connected"] = True
            result["response_time_ms"] = round(elapsed, 2)
            
        except RedisError as e:
            result["error"] = str(e)
        except Exception as e:
            result["error"] = str(e)
        
        return result


# Global cache manager instance
cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance.
    
    Returns:
        CacheManager instance
    """
    global cache_manager
    if cache_manager is None:
        cache_manager = CacheManager()
    return cache_manager


def init_cache() -> bool:
    """Initialize cache connection on application startup.
    
    Returns:
        True if initialization successful, False otherwise
    """
    global cache_manager
    cache_manager = CacheManager()
    return cache_manager.connect()


def close_cache() -> None:
    """Close cache connection on application shutdown."""
    global cache_manager
    if cache_manager:
        cache_manager.disconnect()
        cache_manager = None
