"""
Advanced caching system with Redis, memory cache, and intelligent cache strategies.
Provides multi-level caching, cache warming, and performance optimization.
"""

from __future__ import annotations

import asyncio
import hashlib
import pickle
import time
import zlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from src.core import get_logger, json_utils
from src.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class CacheConfig:
    """Cache configuration for different data types."""

    ttl: int  # Time to live in seconds
    compress: bool = False
    serialize_method: str = "json"  # json, pickle
    max_memory_items: int = 1000
    cache_warming: bool = False
    invalidation_tags: list[str] = None


# Cache configurations for different data types
CACHE_CONFIGS = {
    "transparency_contracts": CacheConfig(
        ttl=3600,  # 1 hour
        compress=True,
        serialize_method="json",
        max_memory_items=500,
        cache_warming=True,
        invalidation_tags=["transparency", "contracts"],
    ),
    "transparency_expenses": CacheConfig(
        ttl=3600,  # 1 hour
        compress=True,
        serialize_method="json",
        max_memory_items=500,
        cache_warming=True,
        invalidation_tags=["transparency", "expenses"],
    ),
    "analysis_results": CacheConfig(
        ttl=86400,  # 24 hours
        compress=True,
        serialize_method="pickle",
        max_memory_items=200,
        invalidation_tags=["analysis"],
    ),
    "agent_responses": CacheConfig(
        ttl=7200,  # 2 hours
        compress=True,
        serialize_method="pickle",
        max_memory_items=300,
        invalidation_tags=["agents"],
    ),
    "user_sessions": CacheConfig(
        ttl=3600,  # 1 hour
        serialize_method="json",
        max_memory_items=1000,
        invalidation_tags=["sessions"],
    ),
    "api_responses": CacheConfig(
        ttl=300,  # 5 minutes
        compress=False,
        serialize_method="json",
        max_memory_items=2000,
        invalidation_tags=["api"],
    ),
    "ml_embeddings": CacheConfig(
        ttl=604800,  # 1 week
        compress=True,
        serialize_method="pickle",
        max_memory_items=100,
        invalidation_tags=["ml", "embeddings"],
    ),
}


class MemoryCache:
    """High-performance in-memory cache with LRU eviction."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
        self.access_times = {}
        self.expiry_times = {}

    def get(self, key: str) -> Any | None:
        """Get item from memory cache."""
        if key not in self.cache:
            return None

        # Check expiry
        if key in self.expiry_times:
            if datetime.utcnow() > self.expiry_times[key]:
                self.delete(key)
                return None

        # Update access time
        self.access_times[key] = time.time()
        return self.cache[key]

    def set(self, key: str, value: Any, ttl: int | None = None):
        """Set item in memory cache."""
        # Evict old items if necessary
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_lru()

        self.cache[key] = value
        self.access_times[key] = time.time()

        if ttl:
            self.expiry_times[key] = datetime.utcnow() + timedelta(seconds=ttl)

    def delete(self, key: str):
        """Delete item from memory cache."""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.expiry_times.pop(key, None)

    def clear(self):
        """Clear all items from memory cache."""
        self.cache.clear()
        self.access_times.clear()
        self.expiry_times.clear()

    def _evict_lru(self):
        """Evict least recently used item."""
        if not self.access_times:
            return

        # Find LRU item
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.delete(lru_key)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "utilization": len(self.cache) / self.max_size if self.max_size > 0 else 0,
        }


class RedisCache:
    """Redis-based distributed cache."""

    def __init__(self):
        self.redis_client: Redis | None = None
        self._connection_pool = None

    async def get_redis_client(self) -> Redis:
        """Get Redis client with optimized connection pooling.

        Pool sizing calculation (Hikari formula):
        connections = (core_count * 2) + effective_spindle_count
        For cloud: core_count=4, spindles=1 → 9 connections base
        Safety margin: 5× → 45-50 connections recommended for 1000 rps @ 5ms latency
        """
        if not self.redis_client:
            self._connection_pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                max_connections=50,  # Increased from 20 for higher concurrency
                retry_on_timeout=True,
                socket_keepalive=True,  # Prevent connection drops
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE (seconds)
                    2: 1,  # TCP_KEEPINTVL (seconds)
                    3: 3,  # TCP_KEEPCNT (retries)
                },
                health_check_interval=30,  # Regular health checks
                socket_connect_timeout=5,  # Connection timeout
                socket_timeout=5,  # Socket operation timeout
            )
            self.redis_client = Redis(
                connection_pool=self._connection_pool,
                decode_responses=False,  # Handle encoding manually for compression
            )

        return self.redis_client

    async def get(self, key: str) -> Any | None:
        """Get item from Redis cache."""
        try:
            client = await self.get_redis_client()
            data = await client.get(key)

            if data is None:
                return None

            # Try to deserialize
            try:
                # Check if compressed
                if data.startswith(b"\x78\x9c"):  # zlib magic number
                    data = zlib.decompress(data)

                return pickle.loads(data)
            except:
                # Fallback to JSON
                return json_utils.loads(data.decode("utf-8"))

        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int,
        compress: bool = False,
        serialize_method: str = "json",
    ):
        """Set item in Redis cache."""
        try:
            client = await self.get_redis_client()

            # Serialize data
            if serialize_method == "pickle":
                data = pickle.dumps(value)
            else:
                data = json_utils.dumps(value).encode("utf-8")

            # Compress if requested
            if compress and len(data) > 1024:  # Only compress larger items
                data = zlib.compress(data)

            await client.setex(key, ttl, data)

        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")

    async def delete(self, key: str):
        """Delete item from Redis cache."""
        try:
            client = await self.get_redis_client()
            await client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")

    async def delete_pattern(self, pattern: str):
        """Delete multiple keys matching pattern."""
        try:
            client = await self.get_redis_client()
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis delete pattern error for {pattern}: {e}")

    async def invalidate_tags(self, tags: list[str]):
        """Invalidate cache items by tags."""
        for tag in tags:
            await self.delete_pattern(f"*:{tag}:*")

    async def get_stats(self) -> dict[str, Any]:
        """Get Redis cache statistics."""
        try:
            client = await self.get_redis_client()
            info = await client.info()

            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": info.get("keyspace_hits", 0)
                / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1),
            }
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {}


class MultiLevelCache:
    """Multi-level cache combining memory and Redis."""

    def __init__(self):
        self.memory_cache = MemoryCache()
        self.redis_cache = RedisCache()
        self.cache_stats = {"hits": 0, "misses": 0, "memory_hits": 0, "redis_hits": 0}

    def _get_cache_key(self, namespace: str, key: str) -> str:
        """Generate cache key with namespace."""
        return f"cidadao_ai:{namespace}:{key}"

    async def get(self, namespace: str, key: str) -> Any | None:
        """Get item from multi-level cache."""
        cache_key = self._get_cache_key(namespace, key)

        # Try memory cache first
        value = self.memory_cache.get(cache_key)
        if value is not None:
            self.cache_stats["hits"] += 1
            self.cache_stats["memory_hits"] += 1
            return value

        # Try Redis cache
        value = await self.redis_cache.get(cache_key)
        if value is not None:
            # Store in memory cache for faster access
            config = CACHE_CONFIGS.get(namespace, CacheConfig(ttl=300))
            self.memory_cache.set(
                cache_key, value, min(config.ttl, 300)
            )  # Max 5 min in memory

            self.cache_stats["hits"] += 1
            self.cache_stats["redis_hits"] += 1
            return value

        self.cache_stats["misses"] += 1
        return None

    async def set(self, namespace: str, key: str, value: Any):
        """Set item in multi-level cache."""
        config = CACHE_CONFIGS.get(namespace, CacheConfig(ttl=300))
        cache_key = self._get_cache_key(namespace, key)

        # Store in Redis
        await self.redis_cache.set(
            cache_key, value, config.ttl, config.compress, config.serialize_method
        )

        # Store in memory cache if configured
        if config.max_memory_items > 0:
            self.memory_cache.set(cache_key, value, min(config.ttl, 300))

    async def delete(self, namespace: str, key: str):
        """Delete item from multi-level cache."""
        cache_key = self._get_cache_key(namespace, key)

        self.memory_cache.delete(cache_key)
        await self.redis_cache.delete(cache_key)

    async def invalidate_namespace(self, namespace: str):
        """Invalidate all items in namespace."""
        pattern = f"cidadao_ai:{namespace}:*"
        await self.redis_cache.delete_pattern(pattern)

        # Clear memory cache items for this namespace
        to_delete = [
            k
            for k in self.memory_cache.cache.keys()
            if k.startswith(f"cidadao_ai:{namespace}:")
        ]
        for key in to_delete:
            self.memory_cache.delete(key)

    async def invalidate_tags(self, tags: list[str]):
        """Invalidate cache items by tags."""
        await self.redis_cache.invalidate_tags(tags)

    def get_hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self.cache_stats["hits"] + self.cache_stats["misses"]
        return self.cache_stats["hits"] / max(total, 1)

    async def get_comprehensive_stats(self) -> dict[str, Any]:
        """Get comprehensive cache statistics."""
        redis_stats = await self.redis_cache.get_stats()
        memory_stats = self.memory_cache.get_stats()

        return {
            "hit_rate": self.get_hit_rate(),
            "total_hits": self.cache_stats["hits"],
            "total_misses": self.cache_stats["misses"],
            "memory_hits": self.cache_stats["memory_hits"],
            "redis_hits": self.cache_stats["redis_hits"],
            "memory_cache": memory_stats,
            "redis_cache": redis_stats,
        }


# Global cache instance
cache = MultiLevelCache()


def cache_key_generator(*args, **kwargs) -> str:
    """Generate consistent cache key from arguments."""
    key_data = {"args": args, "kwargs": sorted(kwargs.items())}
    key_string = json_utils.dumps(key_data)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(
    namespace: str, ttl: int | None = None, key_generator: Callable | None = None
):
    """Decorator for caching function results."""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                cache_key = cache_key_generator(func.__name__, *args, **kwargs)

            # Try to get from cache
            result = await cache.get(namespace, cache_key)
            if result is not None:
                return result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(namespace, cache_key, result)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we need to handle async cache operations
            cache_key = cache_key_generator(func.__name__, *args, **kwargs)

            # This is a simplified version - in practice, you might want
            # to use a thread pool or make the function async
            result = func(*args, **kwargs)

            # Cache result asynchronously
            asyncio.create_task(cache.set(namespace, cache_key, result))

            return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


class CacheWarming:
    """Cache warming system for preloading frequently accessed data."""

    def __init__(self, cache_instance: MultiLevelCache):
        self.cache = cache_instance
        self.warming_tasks = []

    async def warm_transparency_data(self):
        """Warm cache with frequently accessed transparency data."""
        try:
            from src.services.transparency_service import TransparencyService

            transparency_service = TransparencyService()

            # Warm popular contract searches
            popular_queries = [
                {"orgao": "26000", "ano": 2024},  # Education Ministry
                {"orgao": "36000", "ano": 2024},  # Health Ministry
                {"valor_min": 1000000, "ano": 2024},  # High-value contracts
            ]

            for query in popular_queries:
                try:
                    contracts = await transparency_service.get_contracts(**query)
                    cache_key = cache_key_generator("contracts", **query)
                    await self.cache.set("transparency_contracts", cache_key, contracts)
                except Exception as e:
                    logger.error(f"Cache warming error for contracts {query}: {e}")

            # Warm popular expense searches
            expense_queries = [
                {"orgao": "20000", "ano": 2024},  # Presidency
                {"funcao": "10", "ano": 2024},  # Health function
            ]

            for query in expense_queries:
                try:
                    expenses = await transparency_service.get_expenses(**query)
                    cache_key = cache_key_generator("expenses", **query)
                    await self.cache.set("transparency_expenses", cache_key, expenses)
                except Exception as e:
                    logger.error(f"Cache warming error for expenses {query}: {e}")

            logger.info("Cache warming completed for transparency data")

        except Exception as e:
            logger.error(f"Cache warming failed: {e}")

    async def start_warming_schedule(self):
        """Start scheduled cache warming."""

        async def warming_task():
            while True:
                try:
                    await self.warm_transparency_data()
                    await asyncio.sleep(3600)  # Warm every hour
                except Exception as e:
                    logger.error(f"Scheduled cache warming error: {e}")
                    await asyncio.sleep(300)  # Retry in 5 minutes on error

        task = asyncio.create_task(warming_task())
        self.warming_tasks.append(task)
        return task

    def stop_warming(self):
        """Stop all warming tasks."""
        for task in self.warming_tasks:
            if not task.done():
                task.cancel()
        self.warming_tasks.clear()


# Global cache warming instance
cache_warmer = CacheWarming(cache)


class FallbackRedisClient:
    """
    In-memory Redis client fallback for development/testing.

    Implements a subset of Redis operations using in-memory storage
    when Redis is not available.
    """

    def __init__(self):
        self._data: dict[str, tuple[Any, float | None]] = {}
        self._hash_data: dict[str, dict[str, Any]] = {}

    async def get(self, key: str) -> bytes | None:
        """Get value by key."""
        if key in self._data:
            value, expiry = self._data[key]
            if expiry is None or time.time() < expiry:
                return value
            del self._data[key]
        return None

    async def set(self, key: str, value: bytes, ex: int | None = None) -> bool:
        """Set value with optional expiry."""
        expiry = None if ex is None else time.time() + ex
        self._data[key] = (value, expiry)
        return True

    async def setex(self, key: str, time_seconds: int, value: bytes) -> bool:
        """Set value with expiry (alias for set with ex)."""
        return await self.set(key, value, ex=time_seconds)

    async def delete(self, *keys: str) -> int:
        """Delete one or more keys."""
        count = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                count += 1
            if key in self._hash_data:
                del self._hash_data[key]
                count += 1
        return count

    async def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        count = 0
        for key in keys:
            if key in self._data or key in self._hash_data:
                count += 1
        return count

    async def expire(self, key: str, time_seconds: int) -> bool:
        """Set expiry on key."""
        if key in self._data:
            value, _ = self._data[key]
            self._data[key] = (value, time.time() + time_seconds)
            return True
        return False

    async def hset(self, name: str, key: str, value: Any) -> int:
        """Set hash field."""
        if name not in self._hash_data:
            self._hash_data[name] = {}
            created = 1
        else:
            created = 0
        self._hash_data[name][key] = value
        return created

    async def hget(self, name: str, key: str) -> Any | None:
        """Get hash field."""
        if name in self._hash_data:
            return self._hash_data[name].get(key)
        return None

    async def hgetall(self, name: str) -> dict[str, Any]:
        """Get all hash fields."""
        return self._hash_data.get(name, {})

    async def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields."""
        if name not in self._hash_data:
            return 0
        count = 0
        for key in keys:
            if key in self._hash_data[name]:
                del self._hash_data[name][key]
                count += 1
        return count

    async def keys(self, pattern: str) -> list[str]:
        """Get keys matching pattern (simple implementation)."""
        import fnmatch

        all_keys = list(self._data.keys()) + list(self._hash_data.keys())
        return [key for key in all_keys if fnmatch.fnmatch(key, pattern)]

    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment integer value."""
        current = await self.get(key)
        if current is None:
            value = amount
        else:
            value = (
                int(current.decode()) + amount
                if isinstance(current, bytes)
                else current + amount
            )

        await self.set(key, str(value).encode())
        return value

    async def decr(self, key: str, amount: int = 1) -> int:
        """Decrement integer value."""
        return await self.incr(key, -amount)

    async def sadd(self, key: str, *values: str) -> int:
        """Add members to set."""
        if key not in self._hash_data:
            self._hash_data[key] = set()
        elif not isinstance(self._hash_data[key], set):
            self._hash_data[key] = set()

        initial_size = len(self._hash_data[key])
        self._hash_data[key].update(values)
        return len(self._hash_data[key]) - initial_size

    async def smembers(self, key: str) -> set[str]:
        """Get all members of set."""
        if key in self._hash_data and isinstance(self._hash_data[key], set):
            return self._hash_data[key]
        return set()

    async def srem(self, key: str, *values: str) -> int:
        """Remove members from set."""
        if key not in self._hash_data or not isinstance(self._hash_data[key], set):
            return 0

        count = 0
        for value in values:
            if value in self._hash_data[key]:
                self._hash_data[key].discard(value)
                count += 1
        return count

    async def ping(self) -> bool:
        """Ping (always returns True for fallback)."""
        return True

    async def close(self):
        """Close connection (no-op for in-memory)."""
        pass

    def pipeline(self):
        """Return a pipeline-like object for batch operations."""
        return FallbackPipeline(self)


class FallbackPipeline:
    """In-memory pipeline simulation for rate limiting compatibility."""

    def __init__(self, client: FallbackRedisClient):
        """Initialize pipeline with client reference."""
        self.client = client
        self.commands: list[tuple] = []

    def zadd(self, key: str, mapping: dict[str, float]):
        """Queue sorted set add operation."""
        self.commands.append(("zadd", key, mapping))
        return self

    def zremrangebyscore(self, key: str, min_score: float, max_score: float):
        """Queue sorted set removal by score operation."""
        self.commands.append(("zremrangebyscore", key, min_score, max_score))
        return self

    def zcard(self, key: str):
        """Queue sorted set cardinality operation."""
        self.commands.append(("zcard", key))
        return self

    def expire(self, key: str, seconds: int):
        """Queue expiration operation."""
        self.commands.append(("expire", key, seconds))
        return self

    async def execute(self) -> list:
        """Execute all queued commands and return results."""
        results = []
        for cmd in self.commands:
            operation = cmd[0]
            if operation == "zadd":
                # Simulate zadd: returns number of elements added
                results.append(len(cmd[2]))
            elif operation == "zremrangebyscore":
                # Simulate zremrangebyscore: returns number of elements removed
                results.append(0)
            elif operation == "zcard":
                # Simulate zcard: returns sorted set size
                # For rate limiting, this is critical - estimate based on cache
                key = cmd[1]
                # Check if key exists in sorted sets cache
                if (
                    hasattr(self.client, "_sorted_sets")
                    and key in self.client._sorted_sets
                ):
                    results.append(len(self.client._sorted_sets[key]))
                else:
                    results.append(0)
            elif operation == "expire":
                # Simulate expire: always succeeds
                results.append(True)
        return results


async def get_redis_client() -> Redis | FallbackRedisClient:
    """
    Get Redis client with automatic fallback to in-memory client.

    Returns:
        Real Redis client if available, FallbackRedisClient otherwise
    """
    try:
        client = await cache.redis_cache.get_redis_client()
        # Test connection
        await client.ping()
        return client
    except Exception as e:
        logger.warning(
            f"Redis not available, using in-memory fallback: {e}",
            exc_info=False,
        )
        return FallbackRedisClient()


# Cache management functions
async def clear_all_cache():
    """Clear all cache data."""
    cache.memory_cache.clear()
    client = await get_redis_client()
    await client.flushdb()


async def get_cache_stats() -> dict[str, Any]:
    """Get comprehensive cache statistics."""
    return await cache.get_comprehensive_stats()


# Preload cache configurations
def initialize_cache_system():
    """Initialize the cache system."""
    logger.info("Initializing cache system...")

    # Start cache warming if in production
    if settings.environment == "production":
        asyncio.create_task(cache_warmer.start_warming_schedule())

    logger.info("Cache system initialized successfully")
