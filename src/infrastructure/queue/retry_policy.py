"""
Module: infrastructure.queue.retry_policy
Description: Retry policies and mechanisms for batch processing
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import asyncio
import random
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from src.core import get_logger

logger = get_logger(__name__)


class RetryStrategy(str, Enum):
    """Retry strategy types."""

    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    RANDOM_JITTER = "random_jitter"
    FIBONACCI = "fibonacci"


@dataclass
class RetryPolicy:
    """Retry policy configuration."""

    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 300.0  # 5 minutes
    multiplier: float = 2.0  # for exponential backoff
    jitter: bool = True  # add randomness to prevent thundering herd
    retry_on: Optional[list[type]] = None  # specific exceptions to retry
    dont_retry_on: Optional[list[type]] = None  # exceptions to not retry
    on_retry: Optional[Callable] = None  # callback on retry
    on_failure: Optional[Callable] = None  # callback on final failure


class RetryHandler:
    """Handles retry logic for failed operations."""

    def __init__(self, policy: RetryPolicy):
        """Initialize retry handler with policy."""
        self.policy = policy
        self._fibonacci_cache = {0: 0, 1: 1}

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if operation should be retried.

        Args:
            exception: The exception that occurred
            attempt: Current attempt number (1-based)

        Returns:
            True if should retry
        """
        # Check max attempts
        if attempt >= self.policy.max_attempts:
            logger.warning(
                "max_retry_attempts_exceeded",
                attempt=attempt,
                max_attempts=self.policy.max_attempts,
            )
            return False

        # Check exception type
        exc_type = type(exception)

        # Check dont_retry_on list first
        if self.policy.dont_retry_on:
            if any(isinstance(exception, t) for t in self.policy.dont_retry_on):
                logger.info(
                    "retry_skipped_exception_blacklist",
                    exception_type=exc_type.__name__,
                )
                return False

        # Check retry_on list
        if self.policy.retry_on:
            should_retry = any(isinstance(exception, t) for t in self.policy.retry_on)
            if not should_retry:
                logger.info(
                    "retry_skipped_exception_not_whitelisted",
                    exception_type=exc_type.__name__,
                )
            return should_retry

        # Default: retry on any exception
        return True

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay before next retry.

        Args:
            attempt: Current attempt number (1-based)

        Returns:
            Delay in seconds
        """
        base_delay = self._calculate_base_delay(attempt)

        # Apply max delay cap
        delay = min(base_delay, self.policy.max_delay)

        # Apply jitter if enabled
        if self.policy.jitter:
            # Add random jitter of ±25%
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)

        # Ensure minimum delay
        delay = max(delay, 0.1)

        logger.debug(
            "retry_delay_calculated",
            attempt=attempt,
            delay=delay,
            strategy=self.policy.strategy.value,
        )

        return delay

    def _calculate_base_delay(self, attempt: int) -> float:
        """Calculate base delay based on strategy."""
        if self.policy.strategy == RetryStrategy.FIXED_DELAY:
            return self.policy.initial_delay

        elif self.policy.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return self.policy.initial_delay * (self.policy.multiplier ** (attempt - 1))

        elif self.policy.strategy == RetryStrategy.LINEAR_BACKOFF:
            return self.policy.initial_delay * attempt

        elif self.policy.strategy == RetryStrategy.RANDOM_JITTER:
            # Random delay between initial and max
            return random.uniform(
                self.policy.initial_delay,
                min(self.policy.initial_delay * 10, self.policy.max_delay),
            )

        elif self.policy.strategy == RetryStrategy.FIBONACCI:
            return self.policy.initial_delay * self._fibonacci(attempt)

        else:
            return self.policy.initial_delay

    def _fibonacci(self, n: int) -> int:
        """Calculate fibonacci number with memoization."""
        if n in self._fibonacci_cache:
            return self._fibonacci_cache[n]

        # Calculate and cache
        self._fibonacci_cache[n] = self._fibonacci(n - 1) + self._fibonacci(n - 2)
        return self._fibonacci_cache[n]

    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        last_exception = None

        for attempt in range(1, self.policy.max_attempts + 1):
            try:
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Success - return result
                if attempt > 1:
                    logger.info(
                        "retry_succeeded", attempt=attempt, function=func.__name__
                    )

                return result

            except Exception as e:
                last_exception = e

                # Check if should retry
                if not self.should_retry(e, attempt):
                    if self.policy.on_failure:
                        await self._call_callback(self.policy.on_failure, e, attempt)
                    raise

                # Calculate delay
                delay = self.calculate_delay(attempt)

                logger.warning(
                    "operation_failed_retrying",
                    attempt=attempt,
                    max_attempts=self.policy.max_attempts,
                    delay=delay,
                    error=str(e),
                    function=func.__name__,
                )

                # Call retry callback if provided
                if self.policy.on_retry:
                    await self._call_callback(self.policy.on_retry, e, attempt, delay)

                # Wait before retry
                await asyncio.sleep(delay)

        # All retries exhausted
        if self.policy.on_failure:
            await self._call_callback(
                self.policy.on_failure, last_exception, self.policy.max_attempts
            )

        raise last_exception

    async def _call_callback(
        self,
        callback: Callable,
        exception: Exception,
        attempt: int,
        delay: Optional[float] = None,
    ):
        """Call callback function safely."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(exception, attempt, delay)
            else:
                callback(exception, attempt, delay)
        except Exception as e:
            logger.error(
                "retry_callback_failed", callback=callback.__name__, error=str(e)
            )


class CircuitBreaker:
    """
    Circuit breaker pattern for preventing cascading failures.

    States:
    - CLOSED: Normal operation
    - OPEN: Failing, reject all requests
    - HALF_OPEN: Testing if service recovered
    """

    class State(str, Enum):
        CLOSED = "closed"
        OPEN = "open"
        HALF_OPEN = "half_open"

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Optional[type] = None,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds before attempting recovery
            expected_exception: Exception type that triggers the breaker
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.state = self.State.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.success_count = 0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker.

        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == self.State.OPEN:
            if self._should_attempt_reset():
                self.state = self.State.HALF_OPEN
                logger.info("circuit_breaker_half_open")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure(e)
            raise

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Async version of call."""
        if self.state == self.State.OPEN:
            if self._should_attempt_reset():
                self.state = self.State.HALF_OPEN
                logger.info("circuit_breaker_half_open")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure(e)
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if should attempt to reset circuit."""
        return (
            self.last_failure_time
            and datetime.now() - self.last_failure_time
            > timedelta(seconds=self.recovery_timeout)
        )

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0

        if self.state == self.State.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:  # Require 3 successes
                self.state = self.State.CLOSED
                self.success_count = 0
                logger.info("circuit_breaker_closed")

    def _on_failure(self, exception: Exception):
        """Handle failed call."""
        # Check if exception should trigger breaker
        if self.expected_exception and not isinstance(
            exception, self.expected_exception
        ):
            return

        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == self.State.HALF_OPEN:
            self.state = self.State.OPEN
            logger.warning("circuit_breaker_opened_from_half_open")

        elif self.failure_count >= self.failure_threshold:
            self.state = self.State.OPEN
            logger.warning(
                "circuit_breaker_opened",
                failures=self.failure_count,
                threshold=self.failure_threshold,
            )


# Default retry policies
DEFAULT_RETRY_POLICY = RetryPolicy(
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
    max_attempts=3,
    initial_delay=1.0,
    max_delay=60.0,
    multiplier=2.0,
    jitter=True,
)

AGGRESSIVE_RETRY_POLICY = RetryPolicy(
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
    max_attempts=5,
    initial_delay=0.5,
    max_delay=120.0,
    multiplier=1.5,
    jitter=True,
)

GENTLE_RETRY_POLICY = RetryPolicy(
    strategy=RetryStrategy.LINEAR_BACKOFF,
    max_attempts=2,
    initial_delay=5.0,
    max_delay=30.0,
    jitter=False,
)
