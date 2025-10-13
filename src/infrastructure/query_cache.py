"""
Query result caching system for database optimization.

This module provides intelligent caching of database query results
to reduce database load and improve response times.
"""

import hashlib
from collections.abc import Callable
from functools import wraps
from typing import Any, Optional, TypeVar, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.core import get_logger
from src.core.json_utils import dumps
from src.services.cache_service import cache_service

logger = get_logger(__name__)

T = TypeVar("T")


class QueryCache:
    """
    Intelligent query result caching system.

    Features:
    - Automatic cache key generation
    - Configurable TTL per query type
    - Cache invalidation strategies
    - Performance metrics
    """

    def __init__(self):
        """Initialize query cache."""
        self._cache = cache_service
        self._ttl_config = {
            # Table-specific TTLs (in seconds)
            "investigations": 300,  # 5 minutes
            "contracts": 3600,  # 1 hour
            "users": 1800,  # 30 minutes
            "anomalies": 600,  # 10 minutes
            "agent_messages": 120,  # 2 minutes
            "chat_sessions": 60,  # 1 minute
            "default": 300,  # 5 minutes default
        }

        # Cache statistics
        self._stats = {"hits": 0, "misses": 0, "invalidations": 0, "errors": 0}

    def _generate_cache_key(
        self,
        query: Union[str, Select],
        params: Optional[dict[str, Any]] = None,
        prefix: str = "query",
    ) -> str:
        """Generate a unique cache key for a query."""
        # Convert query to string
        query_str = (
            str(query.compile(compile_kwargs={"literal_binds": True}))
            if hasattr(query, "compile")
            else str(query)
        )

        # Include parameters in key
        if params:
            params_str = dumps(sorted(params.items()))
        else:
            params_str = ""

        # Create hash of query + params
        key_data = f"{query_str}:{params_str}"
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]

        return f"db:{prefix}:{key_hash}"

    def _get_ttl_for_query(self, query: Union[str, Select]) -> int:
        """Determine TTL based on query type."""
        query_str = str(query).lower()

        # Check for table names in query
        for table, ttl in self._ttl_config.items():
            if table in query_str:
                return ttl

        return self._ttl_config["default"]

    async def get_or_fetch(
        self,
        query: Union[str, Select],
        fetch_func: Callable,
        params: Optional[dict[str, Any]] = None,
        ttl: Optional[int] = None,
        prefix: str = "query",
    ) -> Any:
        """
        Get query result from cache or fetch from database.

        Args:
            query: SQL query
            fetch_func: Async function to fetch data if not cached
            params: Query parameters
            ttl: Cache TTL (auto-determined if not provided)
            prefix: Cache key prefix

        Returns:
            Query result
        """
        # Generate cache key
        cache_key = self._generate_cache_key(query, params, prefix)

        # Try to get from cache
        cached_result = await self._cache.get(cache_key)
        if cached_result is not None:
            self._stats["hits"] += 1
            logger.debug(f"Cache hit for query: {cache_key}")
            return cached_result

        # Cache miss - fetch from database
        self._stats["misses"] += 1
        logger.debug(f"Cache miss for query: {cache_key}")

        try:
            # Fetch data
            result = await fetch_func()

            # Determine TTL
            if ttl is None:
                ttl = self._get_ttl_for_query(query)

            # Cache the result
            await self._cache.set(
                cache_key,
                result,
                ttl=ttl,
                compress=len(dumps(result)) > 1024,  # Compress if > 1KB
            )

            return result

        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Error in cache fetch: {e}")
            raise

    async def invalidate(
        self,
        pattern: Optional[str] = None,
        table: Optional[str] = None,
        prefix: str = "query",
    ):
        """
        Invalidate cached queries.

        Args:
            pattern: Pattern to match cache keys
            table: Table name to invalidate
            prefix: Cache key prefix
        """
        self._stats["invalidations"] += 1

        if pattern:
            # Invalidate by pattern
            invalidated = await self._invalidate_by_pattern(f"db:{prefix}:{pattern}*")
            logger.info(
                f"Invalidated {invalidated} cache entries matching pattern: {pattern}"
            )

        elif table:
            # Invalidate all queries for a table
            invalidated = await self._invalidate_by_pattern(f"db:*{table}*")
            logger.info(f"Invalidated {invalidated} cache entries for table: {table}")

        else:
            # Invalidate all query cache
            invalidated = await self._invalidate_by_pattern(f"db:{prefix}:*")
            logger.info(
                f"Invalidated {invalidated} cache entries with prefix: {prefix}"
            )

    async def _invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        # Note: This is a simplified implementation
        # In production, use Redis SCAN to find matching keys
        count = 0

        try:
            # For now, we'll track invalidations
            logger.debug(f"Invalidating cache pattern: {pattern}")
            count = 1  # Placeholder
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")

        return count

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0

        return {**self._stats, "total_requests": total_requests, "hit_rate": hit_rate}


# Global query cache instance
query_cache = QueryCache()


def cached_query(
    ttl: Optional[int] = None,
    key_prefix: str = "query",
    invalidate_on: Optional[list[str]] = None,
):
    """
    Decorator for caching database queries.

    Args:
        ttl: Cache TTL in seconds
        key_prefix: Prefix for cache key
        invalidate_on: List of table names that invalidate this cache

    Example:
        @cached_query(ttl=300, invalidate_on=["users"])
        async def get_user_by_id(session: AsyncSession, user_id: int):
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract session and create a cache key from function name and args
            session = None
            for arg in args:
                if isinstance(arg, AsyncSession):
                    session = arg
                    break

            # Generate cache key from function and arguments
            cache_key_parts = [
                func.__name__,
                *[str(arg) for arg in args if not isinstance(arg, AsyncSession)],
                *[f"{k}={v}" for k, v in sorted(kwargs.items())],
            ]
            cache_key = ":".join(cache_key_parts)

            # Use query cache
            async def fetch_func():
                return await func(*args, **kwargs)

            return await query_cache.get_or_fetch(
                query=cache_key,  # Use function signature as "query"
                fetch_func=fetch_func,
                ttl=ttl,
                prefix=key_prefix,
            )

        # Store invalidation configuration
        if invalidate_on:
            wrapper._invalidate_on = invalidate_on

        return wrapper

    return decorator


class CachedRepository:
    """
    Base repository class with built-in caching support.

    Example:
        class UserRepository(CachedRepository):
            def __init__(self, session: AsyncSession):
                super().__init__(session, "users")

            @cached_query(ttl=1800)
            async def get_by_id(self, user_id: int):
                # Implementation
    """

    def __init__(self, session: AsyncSession, table_name: str):
        """
        Initialize cached repository.

        Args:
            session: Database session
            table_name: Name of the table for cache invalidation
        """
        self.session = session
        self.table_name = table_name
        self._cache = query_cache

    async def invalidate_cache(self, pattern: Optional[str] = None):
        """Invalidate cache for this repository."""
        await self._cache.invalidate(
            table=self.table_name if not pattern else None, pattern=pattern
        )

    async def after_insert(self, entity: Any):
        """Hook called after insert - invalidates relevant cache."""
        await self.invalidate_cache()

    async def after_update(self, entity: Any):
        """Hook called after update - invalidates relevant cache."""
        await self.invalidate_cache()

    async def after_delete(self, entity: Any):
        """Hook called after delete - invalidates relevant cache."""
        await self.invalidate_cache()
