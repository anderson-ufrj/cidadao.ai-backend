"""
Module: infrastructure.rate_limiter
Description: Advanced rate limiting system with multiple strategies
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import time
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from src.core import get_logger
from src.core.cache import get_redis_client

logger = get_logger(__name__)


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""

    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitTier(str, Enum):
    """Rate limit tiers."""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    UNLIMITED = "unlimited"


class RateLimitConfig:
    """Rate limit configuration."""

    # Default limits by tier
    TIER_LIMITS = {
        RateLimitTier.FREE: {
            "per_second": 1,
            "per_minute": 10,
            "per_hour": 100,
            "per_day": 1000,
            "burst": 5,
        },
        RateLimitTier.BASIC: {
            "per_second": 5,
            "per_minute": 30,
            "per_hour": 500,
            "per_day": 5000,
            "burst": 20,
        },
        RateLimitTier.PRO: {
            "per_second": 10,
            "per_minute": 60,
            "per_hour": 2000,
            "per_day": 20000,
            "burst": 50,
        },
        RateLimitTier.ENTERPRISE: {
            "per_second": 50,
            "per_minute": 300,
            "per_hour": 10000,
            "per_day": 100000,
            "burst": 200,
        },
        RateLimitTier.UNLIMITED: {
            "per_second": 9999,
            "per_minute": 99999,
            "per_hour": 999999,
            "per_day": 9999999,
            "burst": 9999,
        },
    }

    # Endpoint-specific limits (override tier limits)
    ENDPOINT_LIMITS = {
        "/api/v1/investigations/analyze": {
            "per_minute": 5,
            "per_hour": 20,
            "cost": 10,  # Cost units
        },
        "/api/v1/reports/generate": {"per_minute": 2, "per_hour": 10, "cost": 20},
        "/api/v1/chat/message": {"per_minute": 30, "per_hour": 300, "cost": 1},
        "/api/v1/export/*": {"per_minute": 5, "per_hour": 50, "cost": 5},
    }


class RateLimiter:
    """Advanced rate limiter with multiple strategies."""

    def __init__(
        self,
        strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW,
        use_redis: bool = True,
    ):
        """Initialize rate limiter."""
        self.strategy = strategy
        self.use_redis = use_redis
        self._local_storage = defaultdict(dict)
        self._config = RateLimitConfig()

    async def check_rate_limit(
        self,
        key: str,
        endpoint: str,
        tier: RateLimitTier = RateLimitTier.FREE,
        custom_limits: Optional[dict[str, int]] = None,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Check if request is within rate limits.

        Args:
            key: Unique identifier (user_id, api_key, ip)
            endpoint: API endpoint being accessed
            tier: Rate limit tier
            custom_limits: Override limits

        Returns:
            Tuple of (allowed, metadata)
        """
        # Get applicable limits
        limits = self._get_limits(endpoint, tier, custom_limits)

        # Check each time window
        results = {}
        for window, limit in limits.items():
            if window == "burst" or window == "cost":
                continue

            window_key = f"{key}:{endpoint}:{window}"
            allowed, remaining = await self._check_window(window_key, window, limit)

            results[window] = {
                "allowed": allowed,
                "limit": limit,
                "remaining": remaining,
                "reset": self._get_window_reset(window),
            }

            if not allowed:
                logger.warning(
                    "rate_limit_exceeded",
                    key=key,
                    endpoint=endpoint,
                    window=window,
                    limit=limit,
                )
                return False, results

        # All windows passed
        return True, results

    async def _check_window(
        self, key: str, window: str, limit: int
    ) -> tuple[bool, int]:
        """Check specific time window."""
        if self.strategy == RateLimitStrategy.FIXED_WINDOW:
            return await self._check_fixed_window(key, window, limit)
        elif self.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self._check_sliding_window(key, window, limit)
        elif self.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await self._check_token_bucket(key, window, limit)
        else:
            return await self._check_leaky_bucket(key, window, limit)

    async def _check_fixed_window(
        self, key: str, window: str, limit: int
    ) -> tuple[bool, int]:
        """Fixed window rate limiting."""
        if self.use_redis:
            redis = await get_redis_client()

            # Get window duration in seconds
            duration = self._get_window_duration(window)

            # Increment counter
            pipe = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, duration)
            count, _ = await pipe.execute()

            remaining = max(0, limit - count)
            return count <= limit, remaining
        else:
            # Local implementation
            now = time.time()
            duration = self._get_window_duration(window)
            window_start = int(now / duration) * duration

            window_key = f"{key}:{window_start}"
            if window_key not in self._local_storage:
                self._local_storage[window_key] = {
                    "count": 0,
                    "expires": window_start + duration,
                }

            # Clean expired windows
            expired = [k for k, v in self._local_storage.items() if v["expires"] < now]
            for k in expired:
                del self._local_storage[k]

            # Check limit
            self._local_storage[window_key]["count"] += 1
            count = self._local_storage[window_key]["count"]

            remaining = max(0, limit - count)
            return count <= limit, remaining

    async def _check_sliding_window(
        self, key: str, window: str, limit: int
    ) -> tuple[bool, int]:
        """Sliding window rate limiting using sorted sets."""
        if self.use_redis:
            redis = await get_redis_client()

            now = time.time()
            duration = self._get_window_duration(window)
            window_start = now - duration

            # Use sorted set with timestamp as score
            pipe = redis.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)

            # Add current request
            pipe.zadd(key, {str(now): now})

            # Count requests in window
            pipe.zcard(key)

            # Set expiry
            pipe.expire(key, duration)

            results = await pipe.execute()
            count = results[2]  # zcard result

            remaining = max(0, limit - count)
            return count <= limit, remaining
        else:
            # Local sliding window
            now = time.time()
            duration = self._get_window_duration(window)
            window_start = now - duration

            # Initialize if needed
            if key not in self._local_storage:
                self._local_storage[key] = []

            # Remove old entries
            self._local_storage[key] = [
                ts for ts in self._local_storage[key] if ts > window_start
            ]

            # Add current request
            self._local_storage[key].append(now)

            count = len(self._local_storage[key])
            remaining = max(0, limit - count)
            return count <= limit, remaining

    async def _check_token_bucket(
        self, key: str, window: str, limit: int
    ) -> tuple[bool, int]:
        """Token bucket rate limiting."""
        if self.use_redis:
            redis = await get_redis_client()

            # Lua script for atomic token bucket
            script = """
                local key = KEYS[1]
                local capacity = tonumber(ARGV[1])
                local refill_rate = tonumber(ARGV[2])
                local now = tonumber(ARGV[3])

                local bucket = redis.call('HGETALL', key)
                local tokens = capacity
                local last_refill = now

                if #bucket > 0 then
                    for i = 1, #bucket, 2 do
                        if bucket[i] == 'tokens' then
                            tokens = tonumber(bucket[i + 1])
                        elseif bucket[i] == 'last_refill' then
                            last_refill = tonumber(bucket[i + 1])
                        end
                    end
                end

                -- Refill tokens
                local elapsed = now - last_refill
                local new_tokens = math.min(capacity, tokens + (elapsed * refill_rate))

                -- Try to consume a token
                if new_tokens >= 1 then
                    new_tokens = new_tokens - 1
                    redis.call('HSET', key, 'tokens', new_tokens, 'last_refill', now)
                    redis.call('EXPIRE', key, 3600)
                    return {1, math.floor(new_tokens)}
                else
                    redis.call('HSET', key, 'tokens', new_tokens, 'last_refill', now)
                    redis.call('EXPIRE', key, 3600)
                    return {0, 0}
                end
            """

            # Calculate refill rate
            duration = self._get_window_duration(window)
            refill_rate = limit / duration

            result = await redis.eval(
                script, 1, key, limit, refill_rate, time.time()  # capacity
            )

            return result[0] == 1, result[1]
        else:
            # Local token bucket
            now = time.time()
            duration = self._get_window_duration(window)
            refill_rate = limit / duration

            if key not in self._local_storage:
                self._local_storage[key] = {"tokens": limit, "last_refill": now}

            bucket = self._local_storage[key]
            elapsed = now - bucket["last_refill"]

            # Refill tokens
            bucket["tokens"] = min(limit, bucket["tokens"] + (elapsed * refill_rate))
            bucket["last_refill"] = now

            # Try to consume
            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1
                return True, int(bucket["tokens"])

            return False, 0

    async def _check_leaky_bucket(
        self, key: str, window: str, limit: int
    ) -> tuple[bool, int]:
        """Leaky bucket rate limiting."""
        # Similar to token bucket but with constant leak rate
        return await self._check_token_bucket(key, window, limit)

    def _get_limits(
        self,
        endpoint: str,
        tier: RateLimitTier,
        custom_limits: Optional[dict[str, int]],
    ) -> dict[str, int]:
        """Get applicable rate limits."""
        # Start with tier limits
        limits = self._config.TIER_LIMITS.get(tier, {}).copy()

        # Apply endpoint-specific limits
        for pattern, endpoint_limits in self._config.ENDPOINT_LIMITS.items():
            if self._match_endpoint(endpoint, pattern):
                # Endpoint limits override tier limits
                for window, limit in endpoint_limits.items():
                    if window != "cost":
                        limits[window] = min(limits.get(window, float("inf")), limit)

        # Apply custom limits
        if custom_limits:
            limits.update(custom_limits)

        return limits

    def _match_endpoint(self, endpoint: str, pattern: str) -> bool:
        """Check if endpoint matches pattern."""
        if pattern.endswith("*"):
            return endpoint.startswith(pattern[:-1])
        return endpoint == pattern

    def _get_window_duration(self, window: str) -> int:
        """Get window duration in seconds."""
        durations = {
            "per_second": 1,
            "per_minute": 60,
            "per_hour": 3600,
            "per_day": 86400,
        }
        return durations.get(window, 60)

    def _get_window_reset(self, window: str) -> datetime:
        """Get window reset time."""
        duration = self._get_window_duration(window)
        now = datetime.now()

        if window == "per_second":
            return now + timedelta(seconds=1)
        elif window == "per_minute":
            return now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        elif window == "per_hour":
            return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        elif window == "per_day":
            return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(
                days=1
            )

        return now + timedelta(seconds=duration)

    def get_headers(self, results: dict[str, Any]) -> dict[str, str]:
        """Get rate limit headers for response."""
        headers = {}

        # Find the most restrictive window
        most_restrictive = None
        min_remaining = float("inf")

        for window, data in results.items():
            if data["remaining"] < min_remaining:
                min_remaining = data["remaining"]
                most_restrictive = (window, data)

        if most_restrictive:
            window, data = most_restrictive
            headers["X-RateLimit-Limit"] = str(data["limit"])
            headers["X-RateLimit-Remaining"] = str(data["remaining"])
            headers["X-RateLimit-Reset"] = str(int(data["reset"].timestamp()))
            headers["X-RateLimit-Window"] = window

        return headers


# Global rate limiter instance
rate_limiter = RateLimiter()
