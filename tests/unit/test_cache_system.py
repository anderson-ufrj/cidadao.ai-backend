"""Unit tests for cache system."""
import pytest
import asyncio
import json
import time
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
import pickle

from src.infrastructure.cache_system import (
    CacheSystem,
    CacheLevel,
    CacheEntry,
    CacheStats,
    MemoryCache,
    RedisCache,
    PersistentCache,
    CacheKey,
    CacheSerializer
)


class TestCacheEntry:
    """Test cache entry data structure."""
    
    def test_cache_entry_creation(self):
        """Test creating cache entry."""
        entry = CacheEntry(
            key="test_key",
            value={"data": "test"},
            ttl=3600,
            level=CacheLevel.L1_MEMORY
        )
        
        assert entry.key == "test_key"
        assert entry.value == {"data": "test"}
        assert entry.ttl == 3600
        assert entry.level == CacheLevel.L1_MEMORY
        assert entry.created_at is not None
        assert entry.hits == 0
    
    def test_cache_entry_expiration(self):
        """Test cache entry expiration check."""
        # Create entry with 1 second TTL
        entry = CacheEntry(
            key="expire_test",
            value="data",
            ttl=1
        )
        
        # Should not be expired immediately
        assert entry.is_expired() is False
        
        # Wait and check expiration
        time.sleep(1.1)
        assert entry.is_expired() is True
    
    def test_cache_entry_hit_tracking(self):
        """Test hit count tracking."""
        entry = CacheEntry(key="hit_test", value="data")
        
        # Track hits
        entry.record_hit()
        entry.record_hit()
        entry.record_hit()
        
        assert entry.hits == 3
        assert entry.last_accessed is not None


class TestCacheSerializer:
    """Test cache serialization."""
    
    def test_json_serialization(self):
        """Test JSON serialization."""
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        
        serialized = CacheSerializer.serialize(data, format="json")
        deserialized = CacheSerializer.deserialize(serialized, format="json")
        
        assert isinstance(serialized, bytes)
        assert deserialized == data
    
    def test_pickle_serialization(self):
        """Test pickle serialization for complex objects."""
        # Complex object with datetime
        data = {
            "timestamp": datetime.now(),
            "function": lambda x: x * 2,
            "nested": {"deep": {"value": 123}}
        }
        
        serialized = CacheSerializer.serialize(data, format="pickle")
        deserialized = CacheSerializer.deserialize(serialized, format="pickle")
        
        assert isinstance(serialized, bytes)
        assert deserialized["nested"]["deep"]["value"] == 123
    
    def test_compression(self):
        """Test data compression."""
        # Large data that benefits from compression
        large_data = {"key": "x" * 10000}
        
        uncompressed = CacheSerializer.serialize(large_data, compress=False)
        compressed = CacheSerializer.serialize(large_data, compress=True)
        
        # Compressed should be smaller
        assert len(compressed) < len(uncompressed)
        
        # Should decompress correctly
        decompressed = CacheSerializer.deserialize(compressed, compress=True)
        assert decompressed == large_data


class TestMemoryCache:
    """Test in-memory cache implementation."""
    
    @pytest.fixture
    def memory_cache(self):
        """Create memory cache instance."""
        return MemoryCache(max_size_mb=10)
    
    @pytest.mark.asyncio
    async def test_memory_cache_get_set(self, memory_cache):
        """Test basic get/set operations."""
        key = "test_key"
        value = {"data": "test_value"}
        
        # Set value
        await memory_cache.set(key, value, ttl=60)
        
        # Get value
        retrieved = await memory_cache.get(key)
        assert retrieved == value
    
    @pytest.mark.asyncio
    async def test_memory_cache_ttl(self, memory_cache):
        """Test TTL expiration."""
        key = "ttl_test"
        value = "expires_soon"
        
        # Set with 1 second TTL
        await memory_cache.set(key, value, ttl=1)
        
        # Should exist immediately
        assert await memory_cache.get(key) == value
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Should be expired
        assert await memory_cache.get(key) is None
    
    @pytest.mark.asyncio
    async def test_memory_cache_eviction(self, memory_cache):
        """Test LRU eviction when cache is full."""
        # Fill cache with data
        memory_cache.max_size_mb = 0.001  # Very small for testing
        
        # Add items until eviction happens
        for i in range(100):
            await memory_cache.set(f"key_{i}", f"value_{i}" * 1000)
        
        # Early items should be evicted
        assert await memory_cache.get("key_0") is None
        
        # Recent items should still exist
        assert await memory_cache.get("key_99") is not None
    
    @pytest.mark.asyncio
    async def test_memory_cache_clear(self, memory_cache):
        """Test clearing cache."""
        # Add multiple items
        for i in range(10):
            await memory_cache.set(f"key_{i}", f"value_{i}")
        
        # Clear cache
        await memory_cache.clear()
        
        # All items should be gone
        for i in range(10):
            assert await memory_cache.get(f"key_{i}") is None
    
    @pytest.mark.asyncio
    async def test_memory_cache_stats(self, memory_cache):
        """Test cache statistics."""
        # Perform operations
        await memory_cache.set("key1", "value1")
        await memory_cache.get("key1")  # Hit
        await memory_cache.get("key1")  # Hit
        await memory_cache.get("missing")  # Miss
        
        stats = await memory_cache.get_stats()
        
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 2/3
        assert stats["size"] == 1


class TestRedisCache:
    """Test Redis cache implementation."""
    
    @pytest.fixture
    def redis_cache(self):
        """Create Redis cache instance."""
        with patch("src.infrastructure.cache_system.get_redis_client"):
            return RedisCache()
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        redis = AsyncMock()
        return redis
    
    @pytest.mark.asyncio
    async def test_redis_cache_get_set(self, redis_cache, mock_redis):
        """Test Redis get/set operations."""
        redis_cache._redis = mock_redis
        
        key = "redis_key"
        value = {"data": "redis_value"}
        
        # Mock Redis responses
        mock_redis.setex.return_value = True
        mock_redis.get.return_value = json.dumps(value).encode()
        
        # Set value
        await redis_cache.set(key, value, ttl=300)
        
        # Verify setex called correctly
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == f"cache:{key}"
        assert args[1] == 300
        
        # Get value
        retrieved = await redis_cache.get(key)
        assert retrieved == value
    
    @pytest.mark.asyncio
    async def test_redis_cache_batch_operations(self, redis_cache, mock_redis):
        """Test batch get/set operations."""
        redis_cache._redis = mock_redis
        
        # Batch set
        items = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        
        await redis_cache.set_many(items, ttl=300)
        
        # Verify pipeline used
        assert mock_redis.pipeline.called
        
        # Batch get
        mock_redis.mget.return_value = [
            json.dumps("value1").encode(),
            None,
            json.dumps("value3").encode()
        ]
        
        results = await redis_cache.get_many(["key1", "key2", "key3"])
        
        assert results["key1"] == "value1"
        assert results["key2"] is None
        assert results["key3"] == "value3"
    
    @pytest.mark.asyncio
    async def test_redis_cache_delete(self, redis_cache, mock_redis):
        """Test cache deletion."""
        redis_cache._redis = mock_redis
        
        # Delete single key
        await redis_cache.delete("key1")
        mock_redis.delete.assert_called_with("cache:key1")
        
        # Delete pattern
        mock_redis.keys.return_value = [b"cache:pattern:1", b"cache:pattern:2"]
        await redis_cache.delete_pattern("pattern:*")
        
        assert mock_redis.keys.called
        assert mock_redis.delete.call_count == 3  # 1 single + 2 pattern
    
    @pytest.mark.asyncio
    async def test_redis_connection_failure(self, redis_cache, mock_redis):
        """Test handling Redis connection failures."""
        redis_cache._redis = mock_redis
        
        # Simulate connection error
        mock_redis.get.side_effect = Exception("Redis connection failed")
        
        # Should return None on error (fail open)
        result = await redis_cache.get("key")
        assert result is None
        
        # Should log error (verify in real implementation)


class TestPersistentCache:
    """Test persistent file-based cache."""
    
    @pytest.fixture
    def persistent_cache(self, tmp_path):
        """Create persistent cache instance."""
        return PersistentCache(cache_dir=str(tmp_path))
    
    @pytest.mark.asyncio
    async def test_persistent_cache_get_set(self, persistent_cache):
        """Test file-based cache operations."""
        key = "persistent_key"
        value = {"persistent": "data", "number": 42}
        
        # Set value
        await persistent_cache.set(key, value, ttl=3600)
        
        # Get value
        retrieved = await persistent_cache.get(key)
        assert retrieved == value
        
        # Verify file exists
        cache_file = persistent_cache._get_cache_path(key)
        assert cache_file.exists()
    
    @pytest.mark.asyncio
    async def test_persistent_cache_expiration(self, persistent_cache):
        """Test persistent cache expiration."""
        key = "expire_key"
        value = "expires"
        
        # Set with past expiration
        await persistent_cache.set(key, value, ttl=-1)
        
        # Should return None for expired
        result = await persistent_cache.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_persistent_cache_cleanup(self, persistent_cache):
        """Test cleanup of expired entries."""
        # Create multiple entries
        for i in range(5):
            await persistent_cache.set(f"key_{i}", f"value_{i}", ttl=1)
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Run cleanup
        await persistent_cache.cleanup()
        
        # All files should be removed
        cache_files = list(persistent_cache.cache_dir.glob("*.cache"))
        assert len(cache_files) == 0


class TestCacheSystem:
    """Test multi-level cache system."""
    
    @pytest.fixture
    def cache_system(self, tmp_path):
        """Create cache system instance."""
        with patch("src.infrastructure.cache_system.get_redis_client"):
            return CacheSystem(
                enable_l1=True,
                enable_l2=True,
                enable_l3=True,
                l3_cache_dir=str(tmp_path)
            )
    
    @pytest.mark.asyncio
    async def test_cache_system_waterfall(self, cache_system):
        """Test cache waterfall (L1 -> L2 -> L3)."""
        key = "waterfall_key"
        value = {"test": "waterfall"}
        
        # Set in L3 only
        await cache_system.l3_cache.set(key, value)
        
        # Get should promote to L2 and L1
        result = await cache_system.get(key)
        assert result == value
        
        # Verify promoted to higher levels
        assert await cache_system.l1_cache.get(key) == value
        assert await cache_system.l2_cache.get(key) == value
    
    @pytest.mark.asyncio
    async def test_cache_system_write_through(self, cache_system):
        """Test write-through to all cache levels."""
        key = "write_through_key"
        value = {"write": "through"}
        
        # Set value
        await cache_system.set(key, value, ttl=300)
        
        # Should be in all levels
        assert await cache_system.l1_cache.get(key) == value
        assert await cache_system.l2_cache.get(key) == value
        assert await cache_system.l3_cache.get(key) == value
    
    @pytest.mark.asyncio
    async def test_cache_system_invalidation(self, cache_system):
        """Test cache invalidation across levels."""
        key = "invalidate_key"
        value = {"invalidate": "me"}
        
        # Set in all levels
        await cache_system.set(key, value)
        
        # Invalidate
        await cache_system.invalidate(key)
        
        # Should be removed from all levels
        assert await cache_system.l1_cache.get(key) is None
        assert await cache_system.l2_cache.get(key) is None
        assert await cache_system.l3_cache.get(key) is None
    
    @pytest.mark.asyncio
    async def test_cache_system_stats_aggregation(self, cache_system):
        """Test aggregated statistics."""
        # Perform operations
        await cache_system.set("key1", "value1")
        await cache_system.get("key1")  # L1 hit
        await cache_system.get("key2")  # Miss all levels
        
        stats = await cache_system.get_stats()
        
        assert "l1" in stats
        assert "l2" in stats
        assert "l3" in stats
        assert "total_hits" in stats
        assert "total_misses" in stats
    
    @pytest.mark.asyncio
    async def test_cache_warming(self, cache_system):
        """Test cache warming functionality."""
        # Define warm-up data
        warm_data = {
            "config:app": {"name": "cidadao.ai", "version": "1.0"},
            "config:features": {"ml_enabled": True, "cache_ttl": 300}
        }
        
        # Warm cache
        await cache_system.warm_cache(warm_data)
        
        # All data should be in L1
        for key, value in warm_data.items():
            assert await cache_system.l1_cache.get(key) == value
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """Test cache key generation."""
        # Simple key
        simple_key = CacheKey.generate("user", "123")
        assert simple_key == "user:123"
        
        # Complex key with params
        complex_key = CacheKey.generate(
            "investigation",
            "abc-123",
            params={"year": 2024, "entity": "26000"}
        )
        assert "investigation:abc-123" in complex_key
        assert "2024" in complex_key
        assert "26000" in complex_key
        
        # Hash-based key for long inputs
        long_data = {"data": "x" * 1000}
        hash_key = CacheKey.generate_hash("long", long_data)
        assert len(hash_key) < 100  # Reasonable length


class TestCacheDecorator:
    """Test cache decorator functionality."""
    
    @pytest.mark.asyncio
    async def test_cache_decorator_basic(self, cache_system):
        """Test basic cache decorator."""
        call_count = 0
        
        @cache_system.cache(ttl=60)
        async def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate expensive operation
            return x + y
        
        # First call - should execute function
        result1 = await expensive_function(2, 3)
        assert result1 == 5
        assert call_count == 1
        
        # Second call - should use cache
        result2 = await expensive_function(2, 3)
        assert result2 == 5
        assert call_count == 1  # No additional call
        
        # Different arguments - should execute again
        result3 = await expensive_function(3, 4)
        assert result3 == 7
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_cache_decorator_key_func(self, cache_system):
        """Test cache decorator with custom key function."""
        @cache_system.cache(
            ttl=60,
            key_func=lambda user_id, _: f"user:{user_id}"
        )
        async def get_user_data(user_id, include_details=False):
            return {"id": user_id, "details": include_details}
        
        # Both calls should use same cache key
        result1 = await get_user_data("123", include_details=True)
        result2 = await get_user_data("123", include_details=False)
        
        # Should return cached result (ignoring include_details)
        assert result1 == result2