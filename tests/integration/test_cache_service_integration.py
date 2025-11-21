"""Integration tests for cache service with real Redis"""

import asyncio
import os
from datetime import UTC, datetime

import pytest

from src.services.cache_service import CacheService, cache_result

# Skip these tests if Redis is not available
redis_available = os.getenv("REDIS_URL") is not None


@pytest.mark.skipif(not redis_available, reason="Redis not available")
class TestCacheServiceIntegration:
    """Integration tests with real Redis instance"""

    @pytest.fixture
    async def cache_service(self):
        """Create real cache service instance"""
        service = CacheService()
        await service.initialize()
        yield service
        # Cleanup
        await service.redis.flushdb()
        await service.close()

    @pytest.mark.asyncio
    async def test_basic_operations(self, cache_service):
        """Test basic get/set/delete operations"""
        # Set value
        assert await cache_service.set("test_key", {"data": "value"}, ttl=10)

        # Get value
        result = await cache_service.get("test_key")
        assert result == {"data": "value"}

        # Delete value
        assert await cache_service.delete("test_key")

        # Verify deleted
        result = await cache_service.get("test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_ttl_expiration(self, cache_service):
        """Test TTL expiration"""
        # Set with 1 second TTL
        await cache_service.set("expire_key", "value", ttl=1)

        # Should exist immediately
        assert await cache_service.get("expire_key") == "value"

        # Wait for expiration
        await asyncio.sleep(1.5)

        # Should be expired
        assert await cache_service.get("expire_key") is None

    @pytest.mark.asyncio
    async def test_compression(self, cache_service):
        """Test compression for large values"""
        large_data = {"data": "x" * 10000}  # ~10KB

        # Set with compression
        await cache_service.set("compressed_key", large_data, compress=True)

        # Get with decompression
        result = await cache_service.get("compressed_key", decompress=True)
        assert result == large_data

    @pytest.mark.asyncio
    async def test_chat_response_caching(self, cache_service):
        """Test chat response caching workflow"""
        response = {
            "message": "This is a test response",
            "confidence": 0.95,
            "agent": "test_agent",
        }

        # Cache response
        assert await cache_service.cache_chat_response(
            "Hello world", response, "greeting"
        )

        # Get cached response
        cached = await cache_service.get_cached_chat_response("Hello world", "greeting")
        assert cached == response

        # Case insensitive and trimmed
        cached2 = await cache_service.get_cached_chat_response(
            "  hello WORLD  ", "greeting"
        )
        assert cached2 == response

    @pytest.mark.asyncio
    async def test_session_management(self, cache_service):
        """Test session state management"""
        session_id = "test_session_123"
        initial_state = {
            "user_id": "user_456",
            "started_at": datetime.now(UTC).isoformat(),
            "context": {"intent": "help"},
        }

        # Save session
        assert await cache_service.save_session_state(session_id, initial_state)

        # Get session
        state = await cache_service.get_session_state(session_id)
        assert state["user_id"] == "user_456"
        assert state["context"]["intent"] == "help"
        assert "last_updated" in state

        # Update field
        assert await cache_service.update_session_field(session_id, "messages_count", 5)

        # Verify update
        state = await cache_service.get_session_state(session_id)
        assert state["messages_count"] == 5
        assert state["user_id"] == "user_456"  # Original fields preserved

    @pytest.mark.asyncio
    async def test_investigation_caching(self, cache_service):
        """Test investigation result caching"""
        investigation_id = "inv_789"
        results = {
            "anomalies_found": 3,
            "contracts_analyzed": 150,
            "findings": [
                {"type": "price_anomaly", "severity": "high"},
                {"type": "vendor_concentration", "severity": "medium"},
            ],
        }

        # Cache investigation
        assert await cache_service.cache_investigation_result(investigation_id, results)

        # Retrieve investigation
        cached = await cache_service.get_cached_investigation(investigation_id)
        assert cached == results

    @pytest.mark.asyncio
    async def test_search_results_caching(self, cache_service):
        """Test search results caching with filters"""
        query = "contratos suspeitos"
        filters = {"year": 2024, "min_value": 100000, "status": "active"}
        results = [
            {"id": "1", "title": "Contrato A", "value": 150000},
            {"id": "2", "title": "Contrato B", "value": 200000},
        ]

        # Cache search results
        assert await cache_service.cache_search_results(query, filters, results)

        # Get cached results
        cached = await cache_service.get_cached_search_results(query, filters)
        assert cached == results

        # Different filters should not hit cache
        different_filters = {"year": 2023, "min_value": 100000, "status": "active"}
        cached2 = await cache_service.get_cached_search_results(
            query, different_filters
        )
        assert cached2 is None

    @pytest.mark.asyncio
    async def test_agent_context_management(self, cache_service):
        """Test agent context storage"""
        agent_id = "zumbi"
        session_id = "session_123"
        context = {
            "investigation_id": "inv_456",
            "findings": ["anomaly1", "anomaly2"],
            "confidence": 0.85,
        }

        # Save context
        assert await cache_service.save_agent_context(agent_id, session_id, context)

        # Get context
        retrieved = await cache_service.get_agent_context(agent_id, session_id)
        assert retrieved == context

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, cache_service):
        """Test concurrent cache operations"""

        async def set_value(key, value):
            await cache_service.set(key, value)

        async def get_value(key):
            return await cache_service.get(key)

        # Create many concurrent operations
        tasks = []
        for i in range(50):
            tasks.append(set_value(f"concurrent_{i}", f"value_{i}"))

        await asyncio.gather(*tasks)

        # Verify all values
        get_tasks = []
        for i in range(50):
            get_tasks.append(get_value(f"concurrent_{i}"))

        results = await asyncio.gather(*get_tasks)

        for i, result in enumerate(results):
            assert result == f"value_{i}"

    @pytest.mark.asyncio
    async def test_cache_stats(self, cache_service):
        """Test cache statistics"""
        # Add some data
        await cache_service.cache_chat_response("test1", {"msg": "response1"})
        await cache_service.save_session_state("session1", {"data": "test"})
        await cache_service.cache_investigation_result("inv1", {"results": "data"})

        # Get stats
        stats = await cache_service.get_cache_stats()

        assert stats["connected"] is True
        assert stats["total_keys"] >= 3
        assert "memory_used" in stats
        assert "hit_rate" in stats
        assert stats["keys_by_type"]["chat"] >= 1
        assert stats["keys_by_type"]["session"] >= 1
        assert stats["keys_by_type"]["investigation"] >= 1

    @pytest.mark.asyncio
    async def test_stampede_protection(self, cache_service):
        """Test cache stampede protection"""
        refresh_count = 0

        async def slow_refresh():
            nonlocal refresh_count
            refresh_count += 1
            await asyncio.sleep(0.1)
            return {"refreshed": refresh_count}

        # Set initial value with short TTL
        await cache_service.set("stampede_key", {"initial": "value"}, ttl=2)

        # Multiple concurrent requests near expiration
        await asyncio.sleep(1.5)  # Close to expiration

        tasks = []
        for _ in range(10):
            tasks.append(
                cache_service.get_with_stampede_protection(
                    "stampede_key", 10, slow_refresh
                )
            )

        results = await asyncio.gather(*tasks)

        # All should get same value
        assert all(r == results[0] for r in results)

        # Refresh should be called only once or twice (not 10 times)
        assert refresh_count <= 2


@pytest.mark.skipif(not redis_available, reason="Redis not available")
class TestCacheDecoratorIntegration:
    """Integration tests for cache decorator"""

    @pytest.fixture
    async def cleanup_redis(self):
        """Clean Redis after tests"""
        yield
        service = CacheService()
        await service.initialize()
        await service.redis.flushdb()
        await service.close()

    @pytest.mark.asyncio
    async def test_decorator_caching(self, cleanup_redis):
        """Test function caching with decorator"""
        call_count = 0

        @cache_result("expensive", ttl=5)
        async def expensive_function(param1, param2):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate expensive operation
            return {"result": f"{param1}-{param2}", "count": call_count}

        # First call - should execute
        result1 = await expensive_function("test", "123")
        assert result1["count"] == 1

        # Second call - should use cache
        result2 = await expensive_function("test", "123")
        assert result2["count"] == 1  # Same count, not executed again

        # Different parameters - should execute
        result3 = await expensive_function("test", "456")
        assert result3["count"] == 2

        # Original parameters again - should use cache
        result4 = await expensive_function("test", "123")
        assert result4["count"] == 1
