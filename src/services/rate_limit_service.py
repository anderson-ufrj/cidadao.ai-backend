"""Distributed rate limiting service using Redis"""

import time
from typing import Optional

import redis.asyncio as redis
from redis.exceptions import RedisError

from src.core import get_logger
from src.core.config import settings

logger = get_logger(__name__)


class DistributedRateLimiter:
    """Distributed rate limiter using Redis with sliding window algorithm"""

    def __init__(
        self,
        redis_url: Optional[str] = None,
        requests_per_minute: int = 60,
        requests_per_hour: int = 600,
        requests_per_day: int = 10000,
        burst_size: int = 10,
    ):
        self.redis_url = redis_url or settings.REDIS_URL
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self.burst_size = burst_size
        self._redis_client = None

    async def get_redis(self) -> redis.Redis:
        """Get Redis client with lazy initialization"""
        if self._redis_client is None:
            self._redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_keepalive=True,
                health_check_interval=30,
            )
        return self._redis_client

    async def is_allowed(
        self, identifier: str, endpoint: Optional[str] = None
    ) -> tuple[bool, dict[str, any]]:
        """
        Check if request is allowed using sliding window algorithm

        Args:
            identifier: Unique identifier (IP address or user ID)
            endpoint: Optional endpoint for per-endpoint limits

        Returns:
            Tuple of (allowed, rate_info)
        """
        try:
            redis_client = await self.get_redis()
            current_time = time.time()

            # Create key prefix
            key_prefix = f"rate_limit:{identifier}"
            if endpoint:
                key_prefix += f":{endpoint}"

            # Keys for different windows
            minute_key = f"{key_prefix}:minute"
            hour_key = f"{key_prefix}:hour"
            day_key = f"{key_prefix}:day"
            burst_key = f"{key_prefix}:burst"

            # Use pipeline for atomic operations
            async with redis_client.pipeline() as pipe:
                # Get current counts
                pipe.zcount(minute_key, current_time - 60, current_time)
                pipe.zcount(hour_key, current_time - 3600, current_time)
                pipe.zcount(day_key, current_time - 86400, current_time)
                pipe.get(burst_key)

                results = await pipe.execute()

                minute_count = results[0]
                hour_count = results[1]
                day_count = results[2]
                burst_tokens = int(results[3] or self.burst_size)

            # Check limits
            if minute_count >= self.requests_per_minute:
                return False, {
                    "reason": "minute_limit_exceeded",
                    "limit": self.requests_per_minute,
                    "count": minute_count,
                    "reset_in": 60 - (current_time % 60),
                }

            if hour_count >= self.requests_per_hour:
                return False, {
                    "reason": "hour_limit_exceeded",
                    "limit": self.requests_per_hour,
                    "count": hour_count,
                    "reset_in": 3600 - (current_time % 3600),
                }

            if day_count >= self.requests_per_day:
                return False, {
                    "reason": "day_limit_exceeded",
                    "limit": self.requests_per_day,
                    "count": day_count,
                    "reset_in": 86400 - (current_time % 86400),
                }

            # Check burst limit
            if burst_tokens <= 0:
                return False, {
                    "reason": "burst_limit_exceeded",
                    "limit": self.burst_size,
                    "count": 0,
                    "reset_in": 1,
                }

            # Request allowed - update counts
            request_id = f"{current_time}:{identifier}"

            async with redis_client.pipeline() as pipe:
                # Add to sliding windows
                pipe.zadd(minute_key, {request_id: current_time})
                pipe.zadd(hour_key, {request_id: current_time})
                pipe.zadd(day_key, {request_id: current_time})

                # Update burst tokens
                pipe.decr(burst_key)

                # Set expiration times
                pipe.expire(minute_key, 120)  # 2 minutes
                pipe.expire(hour_key, 7200)  # 2 hours
                pipe.expire(day_key, 172800)  # 2 days
                pipe.expire(burst_key, 60)  # 1 minute

                # Clean old entries
                pipe.zremrangebyscore(minute_key, 0, current_time - 60)
                pipe.zremrangebyscore(hour_key, 0, current_time - 3600)
                pipe.zremrangebyscore(day_key, 0, current_time - 86400)

                await pipe.execute()

            # Replenish burst tokens over time
            await self._replenish_burst_tokens(burst_key, burst_tokens)

            return True, {
                "allowed": True,
                "minute_count": minute_count + 1,
                "hour_count": hour_count + 1,
                "day_count": day_count + 1,
                "burst_remaining": burst_tokens - 1,
                "limits": {
                    "per_minute": self.requests_per_minute,
                    "per_hour": self.requests_per_hour,
                    "per_day": self.requests_per_day,
                    "burst": self.burst_size,
                },
            }

        except RedisError as e:
            logger.error(f"Redis error in rate limiting: {e}")
            # Fail open - allow request if Redis is down
            return True, {"error": "rate_limit_unavailable"}
        except Exception as e:
            logger.error(f"Unexpected error in rate limiting: {e}")
            return True, {"error": "rate_limit_error"}

    async def _replenish_burst_tokens(self, burst_key: str, current_tokens: int):
        """Replenish burst tokens over time"""
        if current_tokens < self.burst_size:
            try:
                redis_client = await self.get_redis()
                # Replenish 1 token per second up to burst_size
                await redis_client.set(
                    burst_key,
                    min(current_tokens + 1, self.burst_size),
                    ex=60,
                    nx=True,  # Only set if doesn't exist
                )
            except Exception:
                pass

    async def reset_limits(self, identifier: str, endpoint: Optional[str] = None):
        """Reset rate limits for an identifier"""
        try:
            redis_client = await self.get_redis()
            key_prefix = f"rate_limit:{identifier}"
            if endpoint:
                key_prefix += f":{endpoint}"

            keys = [
                f"{key_prefix}:minute",
                f"{key_prefix}:hour",
                f"{key_prefix}:day",
                f"{key_prefix}:burst",
            ]

            if keys:
                await redis_client.delete(*keys)

        except Exception as e:
            logger.error(f"Error resetting limits: {e}")

    async def get_limit_status(
        self, identifier: str, endpoint: Optional[str] = None
    ) -> dict[str, any]:
        """Get current limit status for an identifier"""
        try:
            redis_client = await self.get_redis()
            current_time = time.time()

            key_prefix = f"rate_limit:{identifier}"
            if endpoint:
                key_prefix += f":{endpoint}"

            minute_key = f"{key_prefix}:minute"
            hour_key = f"{key_prefix}:hour"
            day_key = f"{key_prefix}:day"
            burst_key = f"{key_prefix}:burst"

            async with redis_client.pipeline() as pipe:
                pipe.zcount(minute_key, current_time - 60, current_time)
                pipe.zcount(hour_key, current_time - 3600, current_time)
                pipe.zcount(day_key, current_time - 86400, current_time)
                pipe.get(burst_key)

                results = await pipe.execute()

            return {
                "minute": {
                    "used": results[0],
                    "limit": self.requests_per_minute,
                    "remaining": self.requests_per_minute - results[0],
                },
                "hour": {
                    "used": results[1],
                    "limit": self.requests_per_hour,
                    "remaining": self.requests_per_hour - results[1],
                },
                "day": {
                    "used": results[2],
                    "limit": self.requests_per_day,
                    "remaining": self.requests_per_day - results[2],
                },
                "burst": {
                    "remaining": int(results[3] or self.burst_size),
                    "limit": self.burst_size,
                },
            }

        except Exception as e:
            logger.error(f"Error getting limit status: {e}")
            return {}

    async def cleanup_old_entries(self):
        """Clean up old entries from all rate limit keys"""
        try:
            redis_client = await self.get_redis()
            current_time = time.time()

            # Scan for rate limit keys
            cursor = 0
            while True:
                cursor, keys = await redis_client.scan(
                    cursor, match="rate_limit:*", count=100
                )

                for key in keys:
                    if key.endswith(":minute"):
                        await redis_client.zremrangebyscore(key, 0, current_time - 60)
                    elif key.endswith(":hour"):
                        await redis_client.zremrangebyscore(key, 0, current_time - 3600)
                    elif key.endswith(":day"):
                        await redis_client.zremrangebyscore(
                            key, 0, current_time - 86400
                        )

                if cursor == 0:
                    break

        except Exception as e:
            logger.error(f"Error cleaning up old entries: {e}")

    async def close(self):
        """Close Redis connection"""
        if self._redis_client:
            await self._redis_client.close()


# Singleton instance
_rate_limiter = None


def get_rate_limiter() -> DistributedRateLimiter:
    """Get singleton rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = DistributedRateLimiter(
            requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
            requests_per_hour=settings.RATE_LIMIT_PER_HOUR,
            requests_per_day=settings.RATE_LIMIT_PER_DAY,
        )
    return _rate_limiter
