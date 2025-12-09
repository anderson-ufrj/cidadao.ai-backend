"""
Redis cache service for chat responses and investigations.

This service provides:
- Caching of frequent chat responses
- Investigation results caching
- Session state persistence
- Distributed cache for scalability
"""

import asyncio
import hashlib
import zlib  # For compression
from datetime import UTC, datetime
from enum import Enum
from functools import wraps
from typing import Any

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import RedisError

from src.core import get_logger, json_utils, settings
from src.core.exceptions import CacheError
from src.core.json_utils import dumps, dumps_bytes, loads
from src.infrastructure.observability.metrics import metrics_manager

logger = get_logger(__name__)

# Prometheus metrics for cache
CACHE_HITS = "cidadao_ai_cache_hits_total"
CACHE_MISSES = "cidadao_ai_cache_misses_total"
CACHE_ERRORS = "cidadao_ai_cache_errors_total"
CACHE_SIZE_BYTES = "cidadao_ai_cache_size_bytes"


class CacheTTL(Enum):
    """Cache Time-To-Live constants."""

    SHORT = 300  # 5 minutes
    MEDIUM = 1800  # 30 minutes
    LONG = 3600  # 1 hour
    VERY_LONG = 86400  # 24 hours


class CacheService:
    """Redis-based caching service for Cidadão.AI."""

    def __init__(self):
        """Initialize Redis connection pool."""
        self.pool: ConnectionPool | None = None
        self.redis: redis.Redis | None = None
        self._initialized = False

        # Cache TTLs (in seconds)
        self.TTL_CHAT_RESPONSE = 300  # 5 minutes for chat responses
        self.TTL_INVESTIGATION = 3600  # 1 hour for investigation results
        self.TTL_SESSION = 86400  # 24 hours for session data
        self.TTL_AGENT_CONTEXT = 1800  # 30 minutes for agent context
        self.TTL_SEARCH_RESULTS = 600  # 10 minutes for search results

        # Stampede protection settings
        self.STAMPEDE_DELTA = 10  # seconds before expiry to refresh
        self.STAMPEDE_BETA = 1.0  # randomization factor

    async def initialize(self):
        """Initialize Redis connection."""
        if self._initialized:
            return

        try:
            # Create connection pool
            self.pool = ConnectionPool.from_url(
                settings.redis_url,
                decode_responses=True,
                max_connections=50,
                socket_keepalive=True,
            )

            # Create Redis client
            self.redis = redis.Redis(connection_pool=self.pool)

            # Test connection
            await self.redis.ping()

            self._initialized = True
            logger.info("Redis cache service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise CacheError(f"Redis initialization failed: {str(e)}")

    async def close(self):
        """Close Redis connections."""
        if self.redis:
            await self.redis.close()
        if self.pool:
            await self.pool.disconnect()
        self._initialized = False

    def _generate_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments."""
        # Create a consistent key from arguments
        key_parts = [str(arg) for arg in args]
        key_data = ":".join(key_parts)

        # Hash long keys to avoid Redis key size limits
        if len(key_data) > 100:
            key_hash = hashlib.md5(key_data.encode()).hexdigest()
            return f"cidadao:{prefix}:{key_hash}"

        return f"cidadao:{prefix}:{key_data}"

    async def get(self, key: str, decompress: bool = False) -> Any | None:
        """Get value from cache with optional decompression."""
        if not self._initialized:
            await self.initialize()

        try:
            value = await self.redis.get(key)
            if value:
                # Record cache hit
                metrics_manager.increment_counter(
                    CACHE_HITS,
                    labels={
                        "key_prefix": key.split(":")[1] if ":" in key else "unknown"
                    },
                )

                # Decompress if needed
                if decompress and isinstance(value, bytes):
                    try:
                        value = zlib.decompress(value)
                    except zlib.error:
                        pass  # Not compressed

                # Try to deserialize JSON
                try:
                    return loads(value)
                except Exception:
                    return value
            else:
                # Record cache miss
                metrics_manager.increment_counter(
                    CACHE_MISSES,
                    labels={
                        "key_prefix": key.split(":")[1] if ":" in key else "unknown"
                    },
                )
            return None
        except RedisError as e:
            logger.error(f"Redis get error: {e}")
            metrics_manager.increment_counter(
                CACHE_ERRORS,
                labels={"operation": "get", "error_type": type(e).__name__},
            )
            return None

    async def set(
        self, key: str, value: Any, ttl: int | None = None, compress: bool = False
    ) -> bool:
        """Set value in cache with optional TTL and compression."""
        if not self._initialized:
            await self.initialize()

        try:
            # Serialize complex objects to JSON
            if isinstance(value, (dict, list)):
                value = dumps_bytes(value)
            elif not isinstance(value, bytes):
                value = str(value).encode("utf-8")

            # Record cache size
            metrics_manager.observe_histogram(
                CACHE_SIZE_BYTES, len(value), labels={"compressed": str(compress)}
            )

            # Compress if requested and value is large enough
            if compress and len(value) > 1024:  # Compress if > 1KB
                value = zlib.compress(value, level=6)

            if ttl:
                await self.redis.setex(key, ttl, value)
            else:
                await self.redis.set(key, value)

            return True
        except RedisError as e:
            logger.error(f"Redis set error: {e}")
            metrics_manager.increment_counter(
                CACHE_ERRORS,
                labels={"operation": "set", "error_type": type(e).__name__},
            )
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.redis.delete(key)
            return result > 0
        except RedisError as e:
            logger.error(f"Redis delete error: {e}")
            return False

    async def get_with_stampede_protection(
        self, key: str, ttl: int, refresh_callback=None, decompress: bool = False
    ) -> Any | None:
        """
        Get value with cache stampede protection using probabilistic early expiration.

        Args:
            key: Cache key
            ttl: Time to live for the cache
            refresh_callback: Async function to refresh cache if needed
            decompress: Whether to decompress the value

        Returns:
            Cached value or None
        """
        # Get value with TTL info
        pipeline = self.redis.pipeline()
        pipeline.get(key)
        pipeline.ttl(key)
        value, remaining_ttl = await pipeline.execute()

        if value is None:
            return None

        # Decompress and deserialize
        if decompress and isinstance(value, bytes):
            try:
                value = zlib.decompress(value)
            except zlib.error:
                pass

        try:
            result = loads(value)
        except Exception:
            result = value

        # Check if we should refresh early to prevent stampede
        if refresh_callback and remaining_ttl > 0:
            import math
            import random

            # XFetch algorithm for cache stampede prevention
            now = datetime.now().timestamp()
            delta = self.STAMPEDE_DELTA * math.log(random.random()) * self.STAMPEDE_BETA

            if remaining_ttl < abs(delta):
                # Refresh cache asynchronously
                asyncio.create_task(self._refresh_cache(key, ttl, refresh_callback))

        return result

    async def _refresh_cache(self, key: str, ttl: int, refresh_callback):
        """Refresh cache value asynchronously."""
        try:
            new_value = await refresh_callback()
            if new_value is not None:
                await self.set(
                    key, new_value, ttl=ttl, compress=len(dumps(new_value)) > 1024
                )
        except Exception as e:
            logger.error(f"Error refreshing cache for key {key}: {e}")

    # Chat-specific methods

    async def cache_chat_response(
        self, message: str, response: dict[str, Any], intent: str | None = None
    ) -> bool:
        """Cache a chat response for a given message."""
        # Generate key from message and optional intent
        key = self._generate_key("chat", message.lower().strip(), intent)

        # Store response with metadata
        cache_data = {
            "response": response,
            "cached_at": datetime.now(UTC).isoformat(),
            "hit_count": 0,
        }

        return await self.set(key, cache_data, self.TTL_CHAT_RESPONSE, compress=True)

    async def get_cached_chat_response(
        self, message: str, intent: str | None = None
    ) -> dict[str, Any] | None:
        """Get cached chat response if available."""
        key = self._generate_key("chat", message.lower().strip(), intent)
        cache_data = await self.get(key, decompress=True)

        if cache_data:
            # Increment hit count
            cache_data["hit_count"] += 1
            await self.set(key, cache_data, self.TTL_CHAT_RESPONSE, compress=True)

            logger.info(f"Cache hit for chat message: {message[:50]}...")
            return cache_data["response"]

        return None

    # Session management

    async def save_session_state(self, session_id: str, state: dict[str, Any]) -> bool:
        """Save session state to cache."""
        key = self._generate_key("session", session_id)
        state["last_updated"] = datetime.now(UTC).isoformat()
        return await self.set(key, state, self.TTL_SESSION, compress=True)

    async def get_session_state(self, session_id: str) -> dict[str, Any] | None:
        """Get session state from cache."""
        key = self._generate_key("session", session_id)
        return await self.get(key)

    async def update_session_field(
        self, session_id: str, field: str, value: Any
    ) -> bool:
        """Update a specific field in session state."""
        state = await self.get_session_state(session_id) or {}
        state[field] = value
        return await self.save_session_state(session_id, state)

    # Investigation caching

    async def cache_investigation_result(
        self, investigation_id: str, result: dict[str, Any]
    ) -> bool:
        """Cache investigation results."""
        key = self._generate_key("investigation", investigation_id)
        return await self.set(key, result, self.TTL_INVESTIGATION, compress=True)

    async def get_cached_investigation(
        self, investigation_id: str
    ) -> dict[str, Any] | None:
        """Get cached investigation results."""
        key = self._generate_key("investigation", investigation_id)
        return await self.get(key)

    # Agent context caching

    async def save_agent_context(
        self, agent_id: str, session_id: str, context: dict[str, Any]
    ) -> bool:
        """Save agent context for a session."""
        key = self._generate_key("agent_context", agent_id, session_id)
        return await self.set(key, context, self.TTL_AGENT_CONTEXT)

    async def get_agent_context(
        self, agent_id: str, session_id: str
    ) -> dict[str, Any] | None:
        """Get agent context for a session."""
        key = self._generate_key("agent_context", agent_id, session_id)
        return await self.get(key)

    # Search results caching

    async def cache_search_results(
        self, query: str, filters: dict[str, Any], results: list[dict[str, Any]]
    ) -> bool:
        """Cache search/query results."""
        # Create deterministic key from query and filters
        filter_str = json_utils.dumps(filters, sort_keys=True)
        key = self._generate_key("search", query, filter_str)

        cache_data = {
            "results": results,
            "count": len(results),
            "cached_at": datetime.now(UTC).isoformat(),
        }

        return await self.set(key, cache_data, self.TTL_SEARCH_RESULTS)

    async def get_cached_search_results(
        self, query: str, filters: dict[str, Any]
    ) -> list[dict[str, Any]] | None:
        """Get cached search results."""
        filter_str = json_utils.dumps(filters, sort_keys=True)
        key = self._generate_key("search", query, filter_str)

        cache_data = await self.get(key)
        if cache_data:
            logger.info(f"Cache hit for search: {query}")
            return cache_data["results"]

        return None

    # Cache statistics

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        if not self._initialized:
            return {"error": "Cache not initialized"}

        try:
            info = await self.redis.info("stats")
            memory = await self.redis.info("memory")

            # Count keys by pattern
            chat_keys = len([k async for k in self.redis.scan_iter("cidadao:chat:*")])
            session_keys = len(
                [k async for k in self.redis.scan_iter("cidadao:session:*")]
            )
            investigation_keys = len(
                [k async for k in self.redis.scan_iter("cidadao:investigation:*")]
            )

            return {
                "connected": True,
                "total_keys": await self.redis.dbsize(),
                "keys_by_type": {
                    "chat": chat_keys,
                    "session": session_keys,
                    "investigation": investigation_keys,
                },
                "memory_used": memory.get("used_memory_human", "N/A"),
                "hit_rate": f"{info.get('keyspace_hit_ratio', 0):.2%}",
                "total_connections": info.get("total_connections_received", 0),
                "commands_processed": info.get("total_commands_processed", 0),
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}


# Cache decorator for functions
def cache_result(prefix: str, ttl: int = 300):
    """Decorator to cache function results.

    Gracefully handles Redis unavailability by executing the function
    without caching when Redis is not available.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip self argument if it's a method
            cache_args = args[1:] if args and hasattr(args[0], "__class__") else args

            # Generate cache key
            cache_service = CacheService()
            key = cache_service._generate_key(
                prefix, func.__name__, *cache_args, **kwargs
            )

            # Try to check cache, but gracefully handle Redis unavailability
            try:
                cached = await cache_service.get(key)
                if cached is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached
            except CacheError:
                # Redis not available, execute function without cache
                logger.debug(
                    f"Cache unavailable for {func.__name__}, executing without cache"
                )
                return await func(*args, **kwargs)

            # Execute function
            result = await func(*args, **kwargs)

            # Try to cache result, ignore errors
            try:
                await cache_service.set(key, result, ttl)
            except CacheError:
                logger.debug(
                    f"Cache unavailable, could not store result for {func.__name__}"
                )

            return result

        return wrapper

    return decorator


# Global cache service instance
cache_service = CacheService()
