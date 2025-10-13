"""Unit tests for rate limiting middleware."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request

from src.api.middleware.rate_limiting import (
    MemoryRateLimitStore,
    RateLimitConfig,
    RateLimitMiddleware,
    RedisRateLimitStore,
    TokenBucket,
    get_client_id,
)


class TestTokenBucket:
    """Test TokenBucket implementation."""

    def test_token_bucket_initialization(self):
        """Test token bucket initializes with full capacity."""
        capacity = 10
        refill_rate = 2.0  # 2 tokens per second

        bucket = TokenBucket(capacity, refill_rate)

        assert bucket.capacity == capacity
        assert bucket.tokens == capacity
        assert bucket.refill_rate == refill_rate

    def test_consume_tokens_success(self):
        """Test consuming tokens when available."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        # Should be able to consume 5 tokens
        assert bucket.consume(5) is True
        assert bucket.tokens == 5

    def test_consume_tokens_insufficient(self):
        """Test consuming tokens when insufficient."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        # Consume all tokens
        bucket.consume(10)

        # Should not be able to consume more
        assert bucket.consume(1) is False
        assert bucket.tokens == 0

    def test_token_refill(self):
        """Test token refill over time."""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens/second

        # Consume all tokens
        bucket.consume(10)
        assert bucket.tokens == 0

        # Wait for refill (0.5 seconds = 5 tokens)
        bucket.last_refill = datetime.utcnow() - timedelta(seconds=0.5)

        # Try to consume, should trigger refill
        assert bucket.consume(5) is True
        assert bucket.tokens == 0  # 5 refilled, 5 consumed

    def test_token_refill_cap(self):
        """Test token refill doesn't exceed capacity."""
        bucket = TokenBucket(capacity=10, refill_rate=100.0)  # Very fast refill

        # Wait a long time
        bucket.last_refill = datetime.utcnow() - timedelta(seconds=10)

        # Refill should cap at capacity
        bucket._refill()
        assert bucket.tokens == 10  # Not more than capacity

    def test_concurrent_token_consumption(self):
        """Test thread-safe token consumption."""
        bucket = TokenBucket(capacity=100, refill_rate=0)  # No refill
        consumed_count = 0

        def consume_tokens():
            nonlocal consumed_count
            if bucket.consume(1):
                consumed_count += 1

        # Simulate concurrent access
        import threading

        threads = []
        for _ in range(150):  # More than capacity
            thread = threading.Thread(target=consume_tokens)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should only consume up to capacity
        assert consumed_count == 100


class TestMemoryRateLimitStore:
    """Test in-memory rate limit store."""

    @pytest.fixture
    def store(self):
        """Create memory store instance."""
        return MemoryRateLimitStore()

    @pytest.mark.asyncio
    async def test_get_bucket_creates_new(self, store):
        """Test getting bucket creates new one if not exists."""
        client_id = "test_client"
        endpoint = "/api/test"
        config = RateLimitConfig(requests_per_minute=60)

        bucket = await store.get_bucket(client_id, endpoint, config)

        assert bucket is not None
        assert bucket.capacity == 60
        assert bucket.refill_rate == 1.0  # 60 per minute = 1 per second

    @pytest.mark.asyncio
    async def test_get_bucket_returns_existing(self, store):
        """Test getting bucket returns existing one."""
        client_id = "test_client"
        endpoint = "/api/test"
        config = RateLimitConfig(requests_per_minute=60)

        # Get bucket twice
        bucket1 = await store.get_bucket(client_id, endpoint, config)
        bucket2 = await store.get_bucket(client_id, endpoint, config)

        # Should be the same instance
        assert bucket1 is bucket2

    @pytest.mark.asyncio
    async def test_different_clients_different_buckets(self, store):
        """Test different clients get different buckets."""
        endpoint = "/api/test"
        config = RateLimitConfig(requests_per_minute=60)

        bucket1 = await store.get_bucket("client1", endpoint, config)
        bucket2 = await store.get_bucket("client2", endpoint, config)

        # Should be different instances
        assert bucket1 is not bucket2

    @pytest.mark.asyncio
    async def test_cleanup_old_buckets(self, store):
        """Test cleanup of old unused buckets."""
        client_id = "old_client"
        endpoint = "/api/test"
        config = RateLimitConfig(requests_per_minute=60)

        # Create bucket and mark it as old
        bucket = await store.get_bucket(client_id, endpoint, config)
        key = f"{client_id}:{endpoint}"

        # Mark as old by setting last refill to past
        bucket.last_refill = datetime.utcnow() - timedelta(hours=2)

        # Run cleanup
        await store.cleanup()

        # Old bucket should be removed
        assert key not in store._buckets


class TestRedisRateLimitStore:
    """Test Redis-based rate limit store."""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        redis = AsyncMock()
        return redis

    @pytest.fixture
    def store(self, mock_redis):
        """Create Redis store instance."""
        with patch(
            "src.api.middleware.rate_limiting.get_redis_client", return_value=mock_redis
        ):
            return RedisRateLimitStore()

    @pytest.mark.asyncio
    async def test_consume_token_success(self, store, mock_redis):
        """Test consuming token from Redis."""
        client_id = "test_client"
        endpoint = "/api/test"
        config = RateLimitConfig(requests_per_minute=60)

        # Mock Redis responses
        mock_redis.get.return_value = b"50"  # Current tokens
        mock_redis.set.return_value = True

        # Should be able to consume
        result = await store.consume_token(client_id, endpoint, config)

        assert result is True
        assert mock_redis.get.called
        assert mock_redis.set.called

    @pytest.mark.asyncio
    async def test_consume_token_insufficient(self, store, mock_redis):
        """Test consuming token when insufficient in Redis."""
        client_id = "test_client"
        endpoint = "/api/test"
        config = RateLimitConfig(requests_per_minute=60)

        # Mock Redis responses - no tokens left
        mock_redis.get.return_value = b"0"

        # Should not be able to consume
        result = await store.consume_token(client_id, endpoint, config)

        assert result is False

    @pytest.mark.asyncio
    async def test_redis_connection_error_fallback(self, store, mock_redis):
        """Test fallback when Redis is unavailable."""
        client_id = "test_client"
        endpoint = "/api/test"
        config = RateLimitConfig(requests_per_minute=60)

        # Mock Redis connection error
        mock_redis.get.side_effect = Exception("Redis connection error")

        # Should fall back gracefully (allow request)
        result = await store.consume_token(client_id, endpoint, config)

        assert result is True  # Fail open for availability


class TestRateLimitMiddleware:
    """Test rate limiting middleware."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        app = MagicMock()
        config = {
            "/api/v1/investigations": RateLimitConfig(
                requests_per_minute=30, requests_per_hour=500
            ),
            "/api/v1/analysis": RateLimitConfig(
                requests_per_minute=60, requests_per_hour=1000
            ),
        }
        return RateLimitMiddleware(app, config)

    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.100"
        request.headers = {"user-agent": "TestClient/1.0"}
        request.url.path = "/api/v1/investigations"
        request.method = "GET"
        request.state = MagicMock()
        return request

    @pytest.mark.asyncio
    async def test_rate_limit_allows_under_limit(self, middleware, mock_request):
        """Test requests are allowed under rate limit."""
        response = MagicMock()
        call_next = AsyncMock(return_value=response)

        # Should allow request
        result = await middleware.dispatch(mock_request, call_next)

        assert result == response
        assert call_next.called

    @pytest.mark.asyncio
    async def test_rate_limit_blocks_over_limit(self, middleware, mock_request):
        """Test requests are blocked over rate limit."""
        call_next = AsyncMock()

        # Exhaust rate limit
        config = middleware.endpoint_limits["/api/v1/investigations"]
        bucket = await middleware.store.get_bucket(
            "192.168.1.100", "/api/v1/investigations", config
        )
        bucket.tokens = 0  # No tokens left

        # Should block request
        result = await middleware.dispatch(mock_request, call_next)

        assert result.status_code == 429
        assert b"Rate limit exceeded" in result.body
        assert not call_next.called

    @pytest.mark.asyncio
    async def test_rate_limit_headers(self, middleware, mock_request):
        """Test rate limit headers are added to response."""
        response = MagicMock()
        response.headers = {}
        call_next = AsyncMock(return_value=response)

        # Process request
        result = await middleware.dispatch(mock_request, call_next)

        # Check rate limit headers
        assert "X-RateLimit-Limit" in result.headers
        assert "X-RateLimit-Remaining" in result.headers
        assert "X-RateLimit-Reset" in result.headers

    @pytest.mark.asyncio
    async def test_authenticated_user_priority(self, middleware, mock_request):
        """Test authenticated users get different rate limits."""
        # Add authenticated user to request
        mock_request.state.user = MagicMock(id="user123", role="premium")

        response = MagicMock()
        call_next = AsyncMock(return_value=response)

        # Should use user ID for rate limiting
        result = await middleware.dispatch(mock_request, call_next)

        assert result == response
        # Verify different bucket would be used for user

    @pytest.mark.asyncio
    async def test_exempt_endpoints(self, middleware):
        """Test certain endpoints are exempt from rate limiting."""
        # Health check should be exempt
        request = MagicMock()
        request.url.path = "/health"
        request.client.host = "192.168.1.100"

        response = MagicMock()
        call_next = AsyncMock(return_value=response)

        # Should not apply rate limiting
        result = await middleware.dispatch(request, call_next)

        assert result == response
        assert "X-RateLimit-Limit" not in response.headers


class TestGetClientId:
    """Test client ID extraction."""

    def test_get_client_id_from_ip(self):
        """Test getting client ID from IP address."""
        request = MagicMock()
        request.client.host = "192.168.1.100"
        request.state = MagicMock()
        request.state.user = None

        client_id = get_client_id(request)

        assert client_id == "192.168.1.100"

    def test_get_client_id_from_user(self):
        """Test getting client ID from authenticated user."""
        request = MagicMock()
        request.client.host = "192.168.1.100"
        request.state = MagicMock()
        request.state.user = MagicMock(id="user123")

        client_id = get_client_id(request)

        assert client_id == "user:user123"

    def test_get_client_id_from_api_key(self):
        """Test getting client ID from API key."""
        request = MagicMock()
        request.client.host = "192.168.1.100"
        request.headers = {"X-API-Key": "sk_test_abc123"}
        request.state = MagicMock()
        request.state.user = None

        client_id = get_client_id(request)

        assert client_id == "api:sk_test_abc123"

    def test_get_client_id_with_forwarded_ip(self):
        """Test getting client ID from X-Forwarded-For header."""
        request = MagicMock()
        request.client.host = "10.0.0.1"  # Proxy IP
        request.headers = {"X-Forwarded-For": "203.0.113.1, 10.0.0.1"}
        request.state = MagicMock()
        request.state.user = None

        client_id = get_client_id(request)

        assert client_id == "203.0.113.1"  # Original client IP
