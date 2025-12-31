"""Tests for rate limiter infrastructure."""

from datetime import datetime, timedelta

import pytest

from src.infrastructure.rate_limiter import (
    RateLimitConfig,
    RateLimiter,
    RateLimitStrategy,
    RateLimitTier,
    rate_limiter,
)


class TestRateLimitConfig:
    """Tests for RateLimitConfig class."""

    def test_tier_limits_exist(self):
        """Test that all tier limits are defined."""
        config = RateLimitConfig()
        assert RateLimitTier.FREE in config.TIER_LIMITS
        assert RateLimitTier.BASIC in config.TIER_LIMITS
        assert RateLimitTier.PRO in config.TIER_LIMITS
        assert RateLimitTier.ENTERPRISE in config.TIER_LIMITS
        assert RateLimitTier.UNLIMITED in config.TIER_LIMITS

    def test_tier_limits_have_required_keys(self):
        """Test that tier limits have all required keys."""
        config = RateLimitConfig()
        required_keys = {"per_second", "per_minute", "per_hour", "per_day", "burst"}

        for tier in RateLimitTier:
            tier_limits = config.TIER_LIMITS[tier]
            for key in required_keys:
                assert key in tier_limits, f"Missing {key} in {tier}"

    def test_endpoint_limits_exist(self):
        """Test that endpoint limits are defined."""
        assert "/api/v1/investigations/analyze" in RateLimitConfig.ENDPOINT_LIMITS
        assert "/api/v1/visualization/*" in RateLimitConfig.ENDPOINT_LIMITS
        assert "/api/v1/geographic/*" in RateLimitConfig.ENDPOINT_LIMITS
        assert "/health" in RateLimitConfig.ENDPOINT_LIMITS

    def test_free_tier_limits(self):
        """Test free tier has reasonable limits."""
        limits = RateLimitConfig.TIER_LIMITS[RateLimitTier.FREE]
        assert limits["per_second"] >= 1
        assert limits["per_minute"] >= 10
        assert limits["per_hour"] >= 100
        assert limits["per_day"] >= 1000


class TestRateLimiter:
    """Tests for RateLimiter class."""

    @pytest.fixture
    def limiter(self):
        """Create rate limiter for testing."""
        return RateLimiter(
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            use_redis=False,  # Use local storage for testing
        )

    def test_initialization(self, limiter):
        """Test rate limiter initialization."""
        assert limiter.strategy == RateLimitStrategy.SLIDING_WINDOW
        assert limiter.use_redis is False

    def test_initialization_with_redis(self):
        """Test rate limiter initialization with Redis."""
        limiter = RateLimiter(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            use_redis=True,
        )
        assert limiter.strategy == RateLimitStrategy.TOKEN_BUCKET
        assert limiter.use_redis is True

    def test_get_window_duration_per_second(self, limiter):
        """Test window duration for per_second."""
        duration = limiter._get_window_duration("per_second")
        assert duration == 1

    def test_get_window_duration_per_minute(self, limiter):
        """Test window duration for per_minute."""
        duration = limiter._get_window_duration("per_minute")
        assert duration == 60

    def test_get_window_duration_per_hour(self, limiter):
        """Test window duration for per_hour."""
        duration = limiter._get_window_duration("per_hour")
        assert duration == 3600

    def test_get_window_duration_per_day(self, limiter):
        """Test window duration for per_day."""
        duration = limiter._get_window_duration("per_day")
        assert duration == 86400

    def test_get_window_duration_unknown(self, limiter):
        """Test window duration for unknown window."""
        duration = limiter._get_window_duration("unknown")
        assert duration == 60  # Default

    def test_match_endpoint_exact(self, limiter):
        """Test endpoint matching - exact match."""
        assert limiter._match_endpoint("/health", "/health") is True
        assert limiter._match_endpoint("/health", "/api") is False

    def test_match_endpoint_wildcard(self, limiter):
        """Test endpoint matching - wildcard."""
        assert (
            limiter._match_endpoint(
                "/api/v1/visualization/chart", "/api/v1/visualization/*"
            )
            is True
        )
        assert (
            limiter._match_endpoint("/api/v1/other/chart", "/api/v1/visualization/*")
            is False
        )

    def test_get_limits_for_tier(self, limiter):
        """Test getting limits for a specific tier."""
        limits = limiter._get_limits(
            endpoint="/api/test",
            tier=RateLimitTier.FREE,
            custom_limits=None,
        )
        assert "per_minute" in limits
        assert "per_hour" in limits

    def test_get_limits_with_endpoint_override(self, limiter):
        """Test getting limits with endpoint-specific override."""
        limits = limiter._get_limits(
            endpoint="/api/v1/visualization/chart",
            tier=RateLimitTier.ENTERPRISE,
            custom_limits=None,
        )
        # Should use the more restrictive endpoint limits
        assert limits["per_minute"] <= 60

    def test_get_limits_with_custom(self, limiter):
        """Test getting limits with custom override."""
        custom = {"per_minute": 5, "per_hour": 50}
        limits = limiter._get_limits(
            endpoint="/api/test",
            tier=RateLimitTier.FREE,
            custom_limits=custom,
        )
        assert limits["per_minute"] == 5
        assert limits["per_hour"] == 50

    def test_get_window_reset_per_second(self, limiter):
        """Test window reset time for per_second."""
        reset = limiter._get_window_reset("per_second")
        assert isinstance(reset, datetime)
        assert reset > datetime.now()

    def test_get_window_reset_per_minute(self, limiter):
        """Test window reset time for per_minute."""
        reset = limiter._get_window_reset("per_minute")
        assert isinstance(reset, datetime)
        assert reset.second == 0

    def test_get_headers(self, limiter):
        """Test rate limit headers generation."""
        results = {
            "per_minute": {
                "allowed": True,
                "limit": 60,
                "remaining": 55,
                "reset": datetime.now() + timedelta(minutes=1),
            },
            "per_hour": {
                "allowed": True,
                "limit": 500,
                "remaining": 450,
                "reset": datetime.now() + timedelta(hours=1),
            },
        }
        headers = limiter.get_headers(results)
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers
        assert "X-RateLimit-Window" in headers

    @pytest.mark.asyncio
    async def test_check_rate_limit_allowed(self, limiter):
        """Test rate limit check - allowed."""
        allowed, results = await limiter.check_rate_limit(
            key="test_user",
            endpoint="/api/test",
            tier=RateLimitTier.UNLIMITED,
        )
        assert allowed is True

    @pytest.mark.asyncio
    async def test_check_fixed_window_local(self, limiter):
        """Test fixed window rate limiting with local storage."""
        limiter.strategy = RateLimitStrategy.FIXED_WINDOW

        # First request should be allowed
        allowed, remaining = await limiter._check_fixed_window(
            key="test_key", window="per_minute", limit=10
        )
        assert allowed is True
        assert remaining == 9

    @pytest.mark.asyncio
    async def test_check_sliding_window_local(self, limiter):
        """Test sliding window rate limiting with local storage."""
        # First request should be allowed
        allowed, remaining = await limiter._check_sliding_window(
            key="test_key_sliding", window="per_minute", limit=10
        )
        assert allowed is True
        assert remaining == 9

    @pytest.mark.asyncio
    async def test_check_token_bucket_local(self, limiter):
        """Test token bucket rate limiting with local storage."""
        # First request should be allowed
        allowed, remaining = await limiter._check_token_bucket(
            key="test_key_token", window="per_minute", limit=10
        )
        assert allowed is True


class TestRateLimiterSingleton:
    """Tests for rate limiter singleton."""

    def test_singleton_exists(self):
        """Test singleton instance exists."""
        assert rate_limiter is not None
        assert isinstance(rate_limiter, RateLimiter)

    def test_singleton_default_strategy(self):
        """Test singleton has default strategy."""
        # Default is SLIDING_WINDOW
        assert rate_limiter.strategy == RateLimitStrategy.SLIDING_WINDOW


class TestRateLimitStrategies:
    """Tests for different rate limit strategies."""

    @pytest.mark.asyncio
    async def test_fixed_window_strategy(self):
        """Test fixed window strategy."""
        limiter = RateLimiter(
            strategy=RateLimitStrategy.FIXED_WINDOW,
            use_redis=False,
        )
        allowed, _ = await limiter.check_rate_limit(
            key="fixed_test",
            endpoint="/test",
            tier=RateLimitTier.FREE,
        )
        assert allowed is True

    @pytest.mark.asyncio
    async def test_sliding_window_strategy(self):
        """Test sliding window strategy."""
        limiter = RateLimiter(
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            use_redis=False,
        )
        allowed, _ = await limiter.check_rate_limit(
            key="sliding_test",
            endpoint="/test",
            tier=RateLimitTier.FREE,
        )
        assert allowed is True

    @pytest.mark.asyncio
    async def test_token_bucket_strategy(self):
        """Test token bucket strategy."""
        limiter = RateLimiter(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            use_redis=False,
        )
        allowed, _ = await limiter.check_rate_limit(
            key="token_test",
            endpoint="/test",
            tier=RateLimitTier.FREE,
        )
        assert allowed is True

    @pytest.mark.asyncio
    async def test_leaky_bucket_strategy(self):
        """Test leaky bucket strategy."""
        limiter = RateLimiter(
            strategy=RateLimitStrategy.LEAKY_BUCKET,
            use_redis=False,
        )
        allowed, _ = await limiter.check_rate_limit(
            key="leaky_test",
            endpoint="/test",
            tier=RateLimitTier.FREE,
        )
        assert allowed is True
