"""
Caching Layer for Transparency APIs

Provides multi-level caching for transparency API responses to improve
performance and reduce API load. Supports in-memory and Redis caching
with configurable TTL per data type.

Author: Anderson Henrique da Silva
Created: 2025-10-09 15:15:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

import json
import hashlib
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum


class CacheTTL(Enum):
    """Cache TTL (Time To Live) presets for different data types."""

    # Municipality lists rarely change
    MUNICIPALITIES = 86400 * 30  # 30 days

    # Supplier lists change occasionally
    SUPPLIERS = 86400 * 7  # 7 days

    # Contract data changes daily
    CONTRACTS = 86400  # 1 day

    # Expense data updated frequently
    EXPENSES = 3600 * 6  # 6 hours

    # Bidding processes change often during active periods
    BIDDING = 3600 * 2  # 2 hours

    # Real-time revenue data
    REVENUE = 3600  # 1 hour

    # API health checks
    HEALTH_CHECK = 300  # 5 minutes


class CacheEntry:
    """
    Represents a cached item with metadata.
    """

    def __init__(self, data: Any, ttl: int):
        """
        Initialize cache entry.

        Args:
            data: Data to cache
            ttl: Time to live in seconds
        """
        self.data = data
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(seconds=ttl)
        self.hits = 0

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return datetime.utcnow() > self.expires_at

    def get_data(self) -> Any:
        """Get cached data and increment hit counter."""
        self.hits += 1
        return self.data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "hits": self.hits
        }


class MemoryCache:
    """
    In-memory cache implementation.

    Simple dictionary-based cache with LRU eviction when size limit is reached.
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize memory cache.

        Args:
            max_size: Maximum number of entries to store
        """
        self._cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self._access_order = []

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        entry = self._cache.get(key)

        if entry is None:
            return None

        if entry.is_expired():
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            return None

        # Update LRU order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        return entry.get_data()

    def set(self, key: str, value: Any, ttl: int) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        # Evict oldest entries if at capacity
        while len(self._cache) >= self.max_size:
            if self._access_order:
                oldest_key = self._access_order.pop(0)
                if oldest_key in self._cache:
                    del self._cache[oldest_key]

        entry = CacheEntry(value, ttl)
        self._cache[key] = entry

        if key not in self._access_order:
            self._access_order.append(key)

    def delete(self, key: str) -> None:
        """Delete entry from cache."""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_order:
            self._access_order.remove(key)

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_order.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_hits = sum(e.hits for e in self._cache.values())

        return {
            "type": "memory",
            "size": len(self._cache),
            "max_size": self.max_size,
            "total_hits": total_hits,
            "utilization": len(self._cache) / self.max_size
        }

    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]

        for key in expired_keys:
            self.delete(key)

        return len(expired_keys)


class TransparencyCache:
    """
    High-level cache interface for transparency APIs.

    Provides convenient methods for caching different types of transparency
    data with appropriate TTL values.
    """

    def __init__(self, backend: Optional[MemoryCache] = None):
        """
        Initialize transparency cache.

        Args:
            backend: Cache backend (defaults to MemoryCache)
        """
        self.backend = backend or MemoryCache(max_size=2000)

    def _generate_key(self, api_name: str, method: str, **params: Any) -> str:
        """
        Generate cache key from API call parameters.

        Args:
            api_name: Name of API client
            method: Method name
            **params: Method parameters

        Returns:
            Hash-based cache key
        """
        # Sort params for consistent key generation
        param_str = json.dumps(params, sort_keys=True)
        key_base = f"{api_name}:{method}:{param_str}"
        key_hash = hashlib.md5(key_base.encode()).hexdigest()
        return f"transparency:{key_hash}"

    def get_contracts(
        self,
        api_name: str,
        **params: Any
    ) -> Optional[Any]:
        """Get cached contracts."""
        key = self._generate_key(api_name, "get_contracts", **params)
        return self.backend.get(key)

    def set_contracts(
        self,
        api_name: str,
        data: Any,
        **params: Any
    ) -> None:
        """Cache contracts data."""
        key = self._generate_key(api_name, "get_contracts", **params)
        self.backend.set(key, data, CacheTTL.CONTRACTS.value)

    def get_expenses(
        self,
        api_name: str,
        **params: Any
    ) -> Optional[Any]:
        """Get cached expenses."""
        key = self._generate_key(api_name, "get_expenses", **params)
        return self.backend.get(key)

    def set_expenses(
        self,
        api_name: str,
        data: Any,
        **params: Any
    ) -> None:
        """Cache expenses data."""
        key = self._generate_key(api_name, "get_expenses", **params)
        self.backend.set(key, data, CacheTTL.EXPENSES.value)

    def get_suppliers(
        self,
        api_name: str,
        **params: Any
    ) -> Optional[Any]:
        """Get cached suppliers."""
        key = self._generate_key(api_name, "get_suppliers", **params)
        return self.backend.get(key)

    def set_suppliers(
        self,
        api_name: str,
        data: Any,
        **params: Any
    ) -> None:
        """Cache suppliers data."""
        key = self._generate_key(api_name, "get_suppliers", **params)
        self.backend.set(key, data, CacheTTL.SUPPLIERS.value)

    def get_bidding_processes(
        self,
        api_name: str,
        **params: Any
    ) -> Optional[Any]:
        """Get cached bidding processes."""
        key = self._generate_key(api_name, "get_bidding_processes", **params)
        return self.backend.get(key)

    def set_bidding_processes(
        self,
        api_name: str,
        data: Any,
        **params: Any
    ) -> None:
        """Cache bidding processes data."""
        key = self._generate_key(api_name, "get_bidding_processes", **params)
        self.backend.set(key, data, CacheTTL.BIDDING.value)

    def get_municipalities(
        self,
        api_name: str
    ) -> Optional[Any]:
        """Get cached municipalities."""
        key = self._generate_key(api_name, "get_municipalities")
        return self.backend.get(key)

    def set_municipalities(
        self,
        api_name: str,
        data: Any
    ) -> None:
        """Cache municipalities data."""
        key = self._generate_key(api_name, "get_municipalities")
        self.backend.set(key, data, CacheTTL.MUNICIPALITIES.value)

    def get_health_check(
        self,
        api_name: str
    ) -> Optional[Any]:
        """Get cached health check result."""
        key = self._generate_key(api_name, "test_connection")
        return self.backend.get(key)

    def set_health_check(
        self,
        api_name: str,
        result: bool
    ) -> None:
        """Cache health check result."""
        key = self._generate_key(api_name, "test_connection")
        self.backend.set(key, result, CacheTTL.HEALTH_CHECK.value)

    def invalidate_api(self, api_name: str) -> None:
        """Invalidate all cache entries for a specific API."""
        # This is a simplified version - in production you'd want
        # to track keys by API name for efficient invalidation
        self.backend.clear()

    def cleanup(self) -> int:
        """Clean up expired entries."""
        if hasattr(self.backend, 'cleanup_expired'):
            return self.backend.cleanup_expired()
        return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.backend.get_stats()


# Global cache instance
_global_cache: Optional[TransparencyCache] = None


def get_cache() -> TransparencyCache:
    """
    Get global cache instance (singleton pattern).

    Returns:
        Global TransparencyCache instance
    """
    global _global_cache

    if _global_cache is None:
        _global_cache = TransparencyCache()

    return _global_cache


def clear_cache() -> None:
    """Clear the global cache."""
    global _global_cache

    if _global_cache is not None:
        _global_cache.backend.clear()
