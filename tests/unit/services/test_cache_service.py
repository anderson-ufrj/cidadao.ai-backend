"""Tests for cache service."""

import zlib
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis.exceptions import RedisError

from src.services.cache_service import CacheService, CacheTTL, cache_result, cache_service


class TestCacheTTL:
    """Tests for CacheTTL enum."""

    def test_cache_ttl_values(self):
        """Test cache TTL enum values."""
        assert CacheTTL.SHORT.value == 300
        assert CacheTTL.MEDIUM.value == 1800
        assert CacheTTL.LONG.value == 3600
        assert CacheTTL.VERY_LONG.value == 86400


class TestCacheServiceInitialization:
    """Tests for CacheService initialization."""

    def test_initialization(self):
        """Test cache service initialization."""
        service = CacheService()

        assert service.pool is None
        assert service.redis is None
        assert service._initialized is False
        assert service.TTL_CHAT_RESPONSE == 300
        assert service.TTL_INVESTIGATION == 3600
        assert service.TTL_SESSION == 86400
        assert service.TTL_AGENT_CONTEXT == 1800
        assert service.TTL_SEARCH_RESULTS == 600

    def test_singleton_instance(self):
        """Test singleton cache_service exists."""
        assert cache_service is not None
        assert isinstance(cache_service, CacheService)


class TestGenerateKey:
    """Tests for _generate_key method."""

    @pytest.fixture
    def service(self):
        """Create cache service for testing."""
        return CacheService()

    def test_generate_key_basic(self, service):
        """Test basic key generation."""
        key = service._generate_key("test", "arg1", "arg2")
        assert key == "cidadao:test:arg1:arg2"

    def test_generate_key_single_arg(self, service):
        """Test key generation with single argument."""
        key = service._generate_key("prefix", "value")
        assert key == "cidadao:prefix:value"

    def test_generate_key_long_data_hashed(self, service):
        """Test long key data is hashed."""
        long_arg = "x" * 150  # > 100 chars
        key = service._generate_key("test", long_arg)

        assert key.startswith("cidadao:test:")
        # Should be hashed (32 char md5 hash)
        hash_part = key.split(":")[-1]
        assert len(hash_part) == 32

    def test_generate_key_numeric_args(self, service):
        """Test key generation with numeric arguments."""
        key = service._generate_key("num", 123, 456)
        assert key == "cidadao:num:123:456"


class TestCacheServiceOperations:
    """Tests for cache get/set/delete operations."""

    @pytest.fixture
    def service(self):
        """Create cache service for testing."""
        service = CacheService()
        service._initialized = True
        service.redis = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_cache_hit(self, service):
        """Test getting cached value."""
        service.redis.get = AsyncMock(return_value='{"key": "value"}')

        with patch(
            "src.services.cache_service.metrics_manager.increment_counter"
        ) as mock_metric:
            result = await service.get("cidadao:test:key")

            assert result == {"key": "value"}
            mock_metric.assert_called()

    @pytest.mark.asyncio
    async def test_get_cache_miss(self, service):
        """Test cache miss returns None."""
        service.redis.get = AsyncMock(return_value=None)

        with patch(
            "src.services.cache_service.metrics_manager.increment_counter"
        ):
            result = await service.get("cidadao:test:nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_with_decompress(self, service):
        """Test getting compressed value."""
        original = b'{"data": "test"}'
        compressed = zlib.compress(original)
        service.redis.get = AsyncMock(return_value=compressed)

        with patch(
            "src.services.cache_service.metrics_manager.increment_counter"
        ):
            result = await service.get("cidadao:test:key", decompress=True)

            assert result == {"data": "test"}

    @pytest.mark.asyncio
    async def test_get_redis_error(self, service):
        """Test Redis error handling in get."""
        service.redis.get = AsyncMock(side_effect=RedisError("Connection failed"))

        with patch(
            "src.services.cache_service.metrics_manager.increment_counter"
        ):
            result = await service.get("cidadao:test:key")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_initializes_if_needed(self):
        """Test get initializes Redis if not initialized."""
        service = CacheService()
        service._initialized = False

        with patch.object(service, "initialize") as mock_init:
            mock_init.return_value = None
            service.redis = AsyncMock()
            service.redis.get = AsyncMock(return_value=None)

            await service.get("test:key")

            mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_dict_value(self, service):
        """Test setting dict value."""
        service.redis.setex = AsyncMock()

        with patch(
            "src.services.cache_service.metrics_manager.observe_histogram"
        ):
            result = await service.set(
                "cidadao:test:key", {"data": "value"}, ttl=300
            )

            assert result is True
            service.redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_with_compression(self, service):
        """Test setting with compression."""
        service.redis.setex = AsyncMock()
        large_value = {"data": "x" * 2000}

        with patch(
            "src.services.cache_service.metrics_manager.observe_histogram"
        ):
            result = await service.set(
                "cidadao:test:key", large_value, ttl=300, compress=True
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_set_without_ttl(self, service):
        """Test setting without TTL."""
        service.redis.set = AsyncMock()

        with patch(
            "src.services.cache_service.metrics_manager.observe_histogram"
        ):
            result = await service.set("cidadao:test:key", "value")

            assert result is True
            service.redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_redis_error(self, service):
        """Test Redis error handling in set."""
        service.redis.setex = AsyncMock(side_effect=RedisError("Write failed"))

        with patch(
            "src.services.cache_service.metrics_manager.observe_histogram"
        ), patch(
            "src.services.cache_service.metrics_manager.increment_counter"
        ):
            result = await service.set("cidadao:test:key", "value", ttl=300)

            assert result is False

    @pytest.mark.asyncio
    async def test_delete_success(self, service):
        """Test deleting key."""
        service.redis.delete = AsyncMock(return_value=1)

        result = await service.delete("cidadao:test:key")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_key_not_found(self, service):
        """Test deleting non-existent key."""
        service.redis.delete = AsyncMock(return_value=0)

        result = await service.delete("cidadao:test:nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_redis_error(self, service):
        """Test Redis error handling in delete."""
        service.redis.delete = AsyncMock(side_effect=RedisError("Delete failed"))

        result = await service.delete("cidadao:test:key")

        assert result is False


class TestChatCaching:
    """Tests for chat-specific caching methods."""

    @pytest.fixture
    def service(self):
        """Create cache service for testing."""
        service = CacheService()
        service._initialized = True
        service.redis = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_cache_chat_response(self, service):
        """Test caching chat response."""
        with patch.object(service, "set") as mock_set:
            mock_set.return_value = True

            result = await service.cache_chat_response(
                message="Hello",
                response={"text": "Hi there"},
                intent="greeting",
            )

            assert result is True
            mock_set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cached_chat_response_hit(self, service):
        """Test getting cached chat response."""
        cached_data = {
            "response": {"text": "cached response"},
            "cached_at": datetime.now(UTC).isoformat(),
            "hit_count": 5,
        }

        with patch.object(service, "get") as mock_get, patch.object(
            service, "set"
        ) as mock_set:
            mock_get.return_value = cached_data
            mock_set.return_value = True

            result = await service.get_cached_chat_response("Hello", "greeting")

            assert result == {"text": "cached response"}
            # Hit count should be incremented and saved
            mock_set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cached_chat_response_miss(self, service):
        """Test cache miss for chat response."""
        with patch.object(service, "get") as mock_get:
            mock_get.return_value = None

            result = await service.get_cached_chat_response("New message")

            assert result is None


class TestSessionCaching:
    """Tests for session state caching methods."""

    @pytest.fixture
    def service(self):
        """Create cache service for testing."""
        service = CacheService()
        service._initialized = True
        service.redis = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_save_session_state(self, service):
        """Test saving session state."""
        with patch.object(service, "set") as mock_set:
            mock_set.return_value = True

            result = await service.save_session_state(
                "session-123", {"user": "test", "data": "value"}
            )

            assert result is True
            call_args = mock_set.call_args
            # Verify last_updated was added
            assert "last_updated" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_get_session_state(self, service):
        """Test getting session state."""
        with patch.object(service, "get") as mock_get:
            mock_get.return_value = {"user": "test"}

            result = await service.get_session_state("session-123")

            assert result == {"user": "test"}

    @pytest.mark.asyncio
    async def test_update_session_field_existing(self, service):
        """Test updating field in existing session."""
        with patch.object(service, "get_session_state") as mock_get, patch.object(
            service, "save_session_state"
        ) as mock_save:
            mock_get.return_value = {"existing": "data"}
            mock_save.return_value = True

            result = await service.update_session_field(
                "session-123", "new_field", "new_value"
            )

            assert result is True
            call_args = mock_save.call_args[0][1]
            assert call_args["existing"] == "data"
            assert call_args["new_field"] == "new_value"

    @pytest.mark.asyncio
    async def test_update_session_field_new_session(self, service):
        """Test updating field in new session."""
        with patch.object(service, "get_session_state") as mock_get, patch.object(
            service, "save_session_state"
        ) as mock_save:
            mock_get.return_value = None
            mock_save.return_value = True

            result = await service.update_session_field(
                "session-new", "field", "value"
            )

            assert result is True


class TestInvestigationCaching:
    """Tests for investigation caching methods."""

    @pytest.fixture
    def service(self):
        """Create cache service for testing."""
        service = CacheService()
        service._initialized = True
        service.redis = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_cache_investigation_result(self, service):
        """Test caching investigation result."""
        with patch.object(service, "set") as mock_set:
            mock_set.return_value = True

            result = await service.cache_investigation_result(
                "inv-123", {"findings": [1, 2, 3]}
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_get_cached_investigation(self, service):
        """Test getting cached investigation."""
        with patch.object(service, "get") as mock_get:
            mock_get.return_value = {"findings": [1, 2, 3]}

            result = await service.get_cached_investigation("inv-123")

            assert result == {"findings": [1, 2, 3]}


class TestAgentContextCaching:
    """Tests for agent context caching methods."""

    @pytest.fixture
    def service(self):
        """Create cache service for testing."""
        service = CacheService()
        service._initialized = True
        service.redis = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_save_agent_context(self, service):
        """Test saving agent context."""
        with patch.object(service, "set") as mock_set:
            mock_set.return_value = True

            result = await service.save_agent_context(
                "agent-1", "session-123", {"memory": "data"}
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_get_agent_context(self, service):
        """Test getting agent context."""
        with patch.object(service, "get") as mock_get:
            mock_get.return_value = {"memory": "data"}

            result = await service.get_agent_context("agent-1", "session-123")

            assert result == {"memory": "data"}


class TestSearchCaching:
    """Tests for search results caching methods."""

    @pytest.fixture
    def service(self):
        """Create cache service for testing."""
        service = CacheService()
        service._initialized = True
        service.redis = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_cache_search_results(self, service):
        """Test caching search results."""
        with patch.object(service, "set") as mock_set:
            mock_set.return_value = True

            result = await service.cache_search_results(
                "query text",
                {"ano": 2024},
                [{"id": 1}, {"id": 2}],
            )

            assert result is True
            call_args = mock_set.call_args[0][1]
            assert call_args["results"] == [{"id": 1}, {"id": 2}]
            assert call_args["count"] == 2

    @pytest.mark.asyncio
    async def test_get_cached_search_results_hit(self, service):
        """Test getting cached search results."""
        with patch.object(service, "get") as mock_get:
            mock_get.return_value = {
                "results": [{"id": 1}, {"id": 2}],
                "count": 2,
                "cached_at": datetime.now(UTC).isoformat(),
            }

            result = await service.get_cached_search_results("query", {"ano": 2024})

            assert result == [{"id": 1}, {"id": 2}]

    @pytest.mark.asyncio
    async def test_get_cached_search_results_miss(self, service):
        """Test cache miss for search results."""
        with patch.object(service, "get") as mock_get:
            mock_get.return_value = None

            result = await service.get_cached_search_results("new query", {})

            assert result is None


class TestCacheStats:
    """Tests for get_cache_stats method."""

    @pytest.fixture
    def service(self):
        """Create cache service for testing."""
        service = CacheService()
        service._initialized = True
        service.redis = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_cache_stats_not_initialized(self):
        """Test stats when not initialized."""
        service = CacheService()
        service._initialized = False

        result = await service.get_cache_stats()

        assert result == {"error": "Cache not initialized"}

    @pytest.mark.asyncio
    async def test_get_cache_stats_success(self, service):
        """Test getting cache statistics."""
        service.redis.info = AsyncMock(
            side_effect=[
                {"keyspace_hit_ratio": 0.75, "total_connections_received": 100},
                {"used_memory_human": "1.5M"},
            ]
        )
        service.redis.dbsize = AsyncMock(return_value=500)

        # Mock scan_iter to return async iterator
        async def mock_scan_iter(pattern):
            for i in range(3):
                yield f"key{i}"

        service.redis.scan_iter = mock_scan_iter

        result = await service.get_cache_stats()

        assert result["connected"] is True
        assert result["total_keys"] == 500
        assert result["memory_used"] == "1.5M"

    @pytest.mark.asyncio
    async def test_get_cache_stats_error(self, service):
        """Test error handling in stats."""
        service.redis.info = AsyncMock(side_effect=Exception("Stats error"))

        result = await service.get_cache_stats()

        assert "error" in result


class TestStampedeProtection:
    """Tests for cache stampede protection."""

    @pytest.fixture
    def service(self):
        """Create cache service for testing."""
        service = CacheService()
        service._initialized = True
        service.redis = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_with_stampede_protection_miss(self, service):
        """Test stampede protection with cache miss."""
        mock_pipeline = AsyncMock()
        mock_pipeline.get = MagicMock()
        mock_pipeline.ttl = MagicMock()
        mock_pipeline.execute = AsyncMock(return_value=[None, -2])
        service.redis.pipeline = MagicMock(return_value=mock_pipeline)

        result = await service.get_with_stampede_protection(
            "cidadao:test:key", ttl=300
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_with_stampede_protection_hit(self, service):
        """Test stampede protection with cache hit."""
        mock_pipeline = AsyncMock()
        mock_pipeline.get = MagicMock()
        mock_pipeline.ttl = MagicMock()
        mock_pipeline.execute = AsyncMock(
            return_value=['{"data": "value"}', 250]
        )
        service.redis.pipeline = MagicMock(return_value=mock_pipeline)

        result = await service.get_with_stampede_protection(
            "cidadao:test:key", ttl=300
        )

        assert result == {"data": "value"}


class TestCacheDecorator:
    """Tests for cache_result decorator."""

    @pytest.mark.asyncio
    async def test_cache_decorator_hit(self):
        """Test decorator returns cached value."""

        @cache_result(prefix="test", ttl=300)
        async def expensive_function(x):
            return x * 2

        with patch.object(CacheService, "get") as mock_get, patch.object(
            CacheService, "set"
        ):
            mock_get.return_value = 10

            result = await expensive_function(5)

            assert result == 10

    @pytest.mark.asyncio
    async def test_cache_decorator_miss(self):
        """Test decorator executes function on miss."""

        @cache_result(prefix="test", ttl=300)
        async def expensive_function(x):
            return x * 2

        with patch.object(CacheService, "get") as mock_get, patch.object(
            CacheService, "set"
        ) as mock_set:
            mock_get.return_value = None
            mock_set.return_value = True

            result = await expensive_function(5)

            assert result == 10
            mock_set.assert_called_once()


class TestCacheServiceLifecycle:
    """Tests for initialize and close methods."""

    @pytest.mark.asyncio
    async def test_initialize_success(self):
        """Test successful initialization."""
        service = CacheService()

        with patch(
            "src.services.cache_service.ConnectionPool.from_url"
        ) as mock_pool, patch("src.services.cache_service.redis.Redis") as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping = AsyncMock()
            mock_redis.return_value = mock_redis_instance

            await service.initialize()

            assert service._initialized is True
            mock_pool.assert_called_once()
            mock_redis_instance.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self):
        """Test initialize returns early if already initialized."""
        service = CacheService()
        service._initialized = True

        with patch(
            "src.services.cache_service.ConnectionPool.from_url"
        ) as mock_pool:
            await service.initialize()

            mock_pool.assert_not_called()

    @pytest.mark.asyncio
    async def test_initialize_failure(self):
        """Test initialization failure."""
        service = CacheService()

        with patch(
            "src.services.cache_service.ConnectionPool.from_url"
        ) as mock_pool:
            mock_pool.side_effect = Exception("Connection failed")

            with pytest.raises(Exception):
                await service.initialize()

    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing connections."""
        service = CacheService()
        service.redis = AsyncMock()
        service.pool = AsyncMock()
        service._initialized = True

        await service.close()

        service.redis.close.assert_called_once()
        service.pool.disconnect.assert_called_once()
        assert service._initialized is False

    @pytest.mark.asyncio
    async def test_close_no_connections(self):
        """Test closing when no connections exist."""
        service = CacheService()
        service.redis = None
        service.pool = None

        # Should not raise
        await service.close()
        assert service._initialized is False
