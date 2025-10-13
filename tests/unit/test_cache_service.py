"""Unit tests for cache service"""

import zlib
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from src.core.exceptions import CacheError
from src.services.cache_service import CacheService, cache_result


class TestCacheService:
    """Test CacheService functionality"""

    @pytest.fixture
    async def cache_service(self):
        """Create cache service instance"""
        service = CacheService()
        # Mock Redis
        service.redis = AsyncMock()
        service._initialized = True
        yield service

    @pytest.fixture
    async def uninitialized_cache(self):
        """Create uninitialized cache service"""
        service = CacheService()
        yield service

    def test_generate_key_short(self, cache_service):
        """Test key generation for short inputs"""
        key = cache_service._generate_key("test", "arg1", "arg2")
        assert key == "cidadao:test:arg1:arg2"

    def test_generate_key_long(self, cache_service):
        """Test key generation for long inputs (should hash)"""
        long_arg = "a" * 200
        key = cache_service._generate_key("test", long_arg)
        assert key.startswith("cidadao:test:")
        assert len(key) < 100  # Should be hashed

    @pytest.mark.asyncio
    async def test_initialize_success(self):
        """Test successful initialization"""
        service = CacheService()

        with patch("redis.asyncio.ConnectionPool.from_url") as mock_pool:
            with patch("redis.asyncio.Redis") as mock_redis:
                mock_redis_instance = AsyncMock()
                mock_redis_instance.ping = AsyncMock(return_value=True)
                mock_redis.return_value = mock_redis_instance

                await service.initialize()

                assert service._initialized is True
                mock_redis_instance.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_failure(self):
        """Test initialization failure"""
        service = CacheService()

        with patch("redis.asyncio.ConnectionPool.from_url") as mock_pool:
            mock_pool.side_effect = Exception("Connection failed")

            with pytest.raises(CacheError):
                await service.initialize()

    @pytest.mark.asyncio
    async def test_get_success(self, cache_service):
        """Test successful get operation"""
        cache_service.redis.get.return_value = '{"key": "value"}'

        result = await cache_service.get("test_key")
        assert result == {"key": "value"}
        cache_service.redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_compressed(self, cache_service):
        """Test get with decompression"""
        original = '{"key": "value"}'
        compressed = zlib.compress(original.encode())
        cache_service.redis.get.return_value = compressed

        result = await cache_service.get("test_key", decompress=True)
        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_not_found(self, cache_service):
        """Test get when key doesn't exist"""
        cache_service.redis.get.return_value = None

        result = await cache_service.get("test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_redis_error(self, cache_service):
        """Test get with Redis error"""
        cache_service.redis.get.side_effect = Exception("Redis error")

        result = await cache_service.get("test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_success_with_ttl(self, cache_service):
        """Test successful set operation with TTL"""
        cache_service.redis.setex = AsyncMock(return_value=True)

        result = await cache_service.set("test_key", {"data": "value"}, ttl=300)
        assert result is True
        cache_service.redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_success_without_ttl(self, cache_service):
        """Test successful set operation without TTL"""
        cache_service.redis.set = AsyncMock(return_value=True)

        result = await cache_service.set("test_key", {"data": "value"})
        assert result is True
        cache_service.redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_with_compression(self, cache_service):
        """Test set with compression for large values"""
        large_value = {"data": "x" * 2000}  # Large enough to trigger compression
        cache_service.redis.setex = AsyncMock(return_value=True)

        result = await cache_service.set(
            "test_key", large_value, ttl=300, compress=True
        )
        assert result is True

        # Verify compression was applied
        call_args = cache_service.redis.setex.call_args[0]
        compressed_value = call_args[2]
        # Should be compressed (smaller than original JSON)
        assert len(compressed_value) < len(str(large_value))

    @pytest.mark.asyncio
    async def test_delete_success(self, cache_service):
        """Test successful delete operation"""
        cache_service.redis.delete.return_value = 1

        result = await cache_service.delete("test_key")
        assert result is True
        cache_service.redis.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_delete_key_not_found(self, cache_service):
        """Test delete when key doesn't exist"""
        cache_service.redis.delete.return_value = 0

        result = await cache_service.delete("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_cache_chat_response(self, cache_service):
        """Test caching chat response"""
        cache_service.redis.setex = AsyncMock(return_value=True)

        response = {"message": "Test response"}
        result = await cache_service.cache_chat_response("Hello", response, "greeting")

        assert result is True
        cache_service.redis.setex.assert_called_once()

        # Check TTL is correct
        call_args = cache_service.redis.setex.call_args[0]
        assert call_args[1] == 300  # TTL_CHAT_RESPONSE

    @pytest.mark.asyncio
    async def test_get_cached_chat_response(self, cache_service):
        """Test getting cached chat response"""
        cached_data = {
            "response": {"message": "Cached response"},
            "cached_at": datetime.utcnow().isoformat(),
            "hit_count": 5,
        }
        cache_service.redis.get.return_value = str(cached_data)
        cache_service.redis.setex = AsyncMock(return_value=True)

        # Mock loads to return the cached data
        with patch("src.services.cache_service.loads", return_value=cached_data):
            result = await cache_service.get_cached_chat_response("Hello", "greeting")

        assert result == {"message": "Cached response"}
        # Should increment hit count
        assert cache_service.redis.setex.called

    @pytest.mark.asyncio
    async def test_save_session_state(self, cache_service):
        """Test saving session state"""
        cache_service.redis.setex = AsyncMock(return_value=True)

        state = {"user_id": "123", "context": "test"}
        result = await cache_service.save_session_state("session_123", state)

        assert result is True
        cache_service.redis.setex.assert_called_once()

        # Check TTL
        call_args = cache_service.redis.setex.call_args[0]
        assert call_args[1] == 86400  # TTL_SESSION

    @pytest.mark.asyncio
    async def test_get_session_state(self, cache_service):
        """Test getting session state"""
        state = {"user_id": "123", "context": "test"}
        cache_service.redis.get.return_value = str(state)

        with patch("src.services.cache_service.loads", return_value=state):
            result = await cache_service.get_session_state("session_123")

        assert result == state

    @pytest.mark.asyncio
    async def test_update_session_field(self, cache_service):
        """Test updating session field"""
        existing_state = {"user_id": "123", "context": "test"}
        cache_service.redis.get.return_value = str(existing_state)
        cache_service.redis.setex = AsyncMock(return_value=True)

        with patch("src.services.cache_service.loads", return_value=existing_state):
            result = await cache_service.update_session_field(
                "session_123", "new_field", "value"
            )

        assert result is True
        # Verify the updated state was saved
        cache_service.redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_investigation_result(self, cache_service):
        """Test caching investigation result"""
        cache_service.redis.setex = AsyncMock(return_value=True)

        result_data = {"findings": ["anomaly1", "anomaly2"]}
        result = await cache_service.cache_investigation_result("inv_123", result_data)

        assert result is True
        call_args = cache_service.redis.setex.call_args[0]
        assert call_args[1] == 3600  # TTL_INVESTIGATION

    @pytest.mark.asyncio
    async def test_get_cache_stats(self, cache_service):
        """Test getting cache statistics"""
        cache_service.redis.info = AsyncMock()
        cache_service.redis.info.side_effect = [
            {"keyspace_hit_ratio": 0.85, "total_connections_received": 100},
            {"used_memory_human": "10M"},
        ]
        cache_service.redis.dbsize = AsyncMock(return_value=1000)
        cache_service.redis.scan_iter = AsyncMock()
        cache_service.redis.scan_iter.return_value.__aiter__.return_value = iter(
            ["key1", "key2"]
        )

        stats = await cache_service.get_cache_stats()

        assert stats["connected"] is True
        assert stats["total_keys"] == 1000
        assert stats["memory_used"] == "10M"
        assert "hit_rate" in stats

    @pytest.mark.asyncio
    async def test_cache_stampede_protection(self, cache_service):
        """Test cache stampede protection mechanism"""
        # Mock pipeline
        pipeline = AsyncMock()
        pipeline.execute.return_value = ['{"value": "test"}', 5]  # value, TTL
        cache_service.redis.pipeline.return_value = pipeline

        refresh_called = False

        async def refresh_callback():
            nonlocal refresh_called
            refresh_called = True
            return {"value": "refreshed"}

        with patch("src.services.cache_service.loads", return_value={"value": "test"}):
            result = await cache_service.get_with_stampede_protection(
                "test_key", 300, refresh_callback
            )

        assert result == {"value": "test"}
        # Refresh might be called based on random factor

    @pytest.mark.asyncio
    async def test_auto_initialization(self, uninitialized_cache):
        """Test automatic initialization on first operation"""
        with patch.object(uninitialized_cache, "initialize") as mock_init:
            mock_init.return_value = None
            uninitialized_cache._initialized = True
            uninitialized_cache.redis = AsyncMock()
            uninitialized_cache.redis.get.return_value = None

            await uninitialized_cache.get("test_key")
            mock_init.assert_called_once()


class TestCacheDecorator:
    """Test cache_result decorator"""

    @pytest.mark.asyncio
    async def test_cache_decorator_hit(self):
        """Test cache decorator with cache hit"""
        mock_cache = AsyncMock()
        mock_cache._generate_key.return_value = "test_key"
        mock_cache.get.return_value = {"cached": "result"}

        with patch("src.services.cache_service.CacheService", return_value=mock_cache):

            @cache_result("test", ttl=60)
            async def test_function(arg1, arg2):
                return {"result": f"{arg1}-{arg2}"}

            result = await test_function("a", "b")

        assert result == {"cached": "result"}
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_cache_decorator_miss(self):
        """Test cache decorator with cache miss"""
        mock_cache = AsyncMock()
        mock_cache._generate_key.return_value = "test_key"
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True

        with patch("src.services.cache_service.CacheService", return_value=mock_cache):

            @cache_result("test", ttl=60)
            async def test_function(arg1, arg2):
                return {"result": f"{arg1}-{arg2}"}

            result = await test_function("a", "b")

        assert result == {"result": "a-b"}
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once_with("test_key", {"result": "a-b"}, 60)
