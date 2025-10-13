"""
Retry logic with exponential backoff for federal API clients.

Provides decorators and utilities for automatic retry of failed requests.

Author: Anderson Henrique da Silva
Created: 2025-10-12
License: Proprietary - All rights reserved
"""

import asyncio
import random
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any, Optional

from src.core import get_logger

from .exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)

logger = get_logger(__name__)


# Exceptions that should trigger a retry
RETRYABLE_EXCEPTIONS: tuple[type[Exception], ...] = (
    NetworkError,
    TimeoutError,
    ServerError,
    ConnectionError,
    asyncio.TimeoutError,
)

# Exceptions that should NOT be retried (client errors)
NON_RETRYABLE_EXCEPTIONS: tuple[type[Exception], ...] = (
    AuthenticationError,
    NotFoundError,
    ValidationError,
)


def calculate_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
) -> float:
    """
    Calculate exponential backoff delay with optional jitter.

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation (usually 2.0)
        jitter: Whether to add random jitter

    Returns:
        Delay in seconds

    Examples:
        >>> calculate_backoff(0, jitter=False)  # 1.0s
        >>> calculate_backoff(1, jitter=False)  # 2.0s
        >>> calculate_backoff(2, jitter=False)  # 4.0s
        >>> calculate_backoff(3, jitter=False)  # 8.0s
    """
    delay = min(base_delay * (exponential_base**attempt), max_delay)

    if jitter:
        # Add random jitter between 0% and 25% of delay
        jitter_amount = delay * random.uniform(0, 0.25)
        delay += jitter_amount

    return delay


def should_retry_exception(exc: Exception) -> bool:
    """
    Determine if an exception should trigger a retry.

    Args:
        exc: Exception to check

    Returns:
        True if should retry, False otherwise
    """
    # Check if it's a non-retryable exception
    if isinstance(exc, NON_RETRYABLE_EXCEPTIONS):
        return False

    # Check if it's a retryable exception
    if isinstance(exc, RETRYABLE_EXCEPTIONS):
        return True

    # Special case: Rate limit errors might be retryable with proper delay
    if isinstance(exc, RateLimitError):
        return True

    # Default: don't retry unknown exceptions
    return False


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    on_retry: Optional[Callable[[int, Exception], None]] = None,
    retryable_exceptions: Optional[tuple[type[Exception], ...]] = None,
):
    """
    Decorator for automatic retry with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including initial)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Whether to add random jitter
        on_retry: Optional callback called on each retry (attempt, exception)
        retryable_exceptions: Custom tuple of retryable exceptions

    Usage:
        @retry_with_backoff(max_attempts=3, base_delay=1.0)
        async def fetch_data():
            # Your async function here
            pass

    Examples:
        # Basic retry with defaults
        @retry_with_backoff()
        async def my_function():
            pass

        # Custom retry configuration
        @retry_with_backoff(
            max_attempts=5,
            base_delay=2.0,
            max_delay=120.0
        )
        async def my_function():
            pass

        # With custom callback
        def log_retry(attempt, exc):
            print(f"Retry {attempt}: {exc}")

        @retry_with_backoff(on_retry=log_retry)
        async def my_function():
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            func_name = func.__name__

            for attempt in range(max_attempts):
                try:
                    # Try to execute the function
                    result = await func(*args, **kwargs)

                    # Success! Log if this was a retry
                    if attempt > 0:
                        logger.info(
                            "Retry successful",
                            function=func_name,
                            attempt=attempt + 1,
                            max_attempts=max_attempts,
                        )

                    return result

                except Exception as exc:
                    last_exception = exc
                    is_last_attempt = attempt == max_attempts - 1

                    # Determine if we should retry
                    should_retry = (
                        (retryable_exceptions and isinstance(exc, retryable_exceptions))
                        if retryable_exceptions
                        else should_retry_exception(exc)
                    )

                    if not should_retry or is_last_attempt:
                        # Don't retry, raise the exception
                        logger.error(
                            "Request failed, not retrying",
                            function=func_name,
                            attempt=attempt + 1,
                            max_attempts=max_attempts,
                            exception=str(exc),
                            exception_type=type(exc).__name__,
                            should_retry=should_retry,
                            is_last_attempt=is_last_attempt,
                        )
                        raise

                    # Calculate delay for rate limit errors
                    if isinstance(exc, RateLimitError) and exc.retry_after:
                        delay = exc.retry_after
                        logger.warning(
                            "Rate limit hit, using retry_after from response",
                            function=func_name,
                            retry_after=delay,
                            attempt=attempt + 1,
                        )
                    else:
                        delay = calculate_backoff(
                            attempt,
                            base_delay=base_delay,
                            max_delay=max_delay,
                            exponential_base=exponential_base,
                            jitter=jitter,
                        )

                    # Log retry attempt
                    logger.warning(
                        f"Request failed, retrying after {delay:.2f}s",
                        function=func_name,
                        attempt=attempt + 1,
                        max_attempts=max_attempts,
                        delay_seconds=delay,
                        exception=str(exc),
                        exception_type=type(exc).__name__,
                    )

                    # Call on_retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt + 1, exc)
                        except Exception as callback_exc:
                            logger.error(
                                "Error in on_retry callback",
                                callback_exception=str(callback_exc),
                            )

                    # Wait before retrying
                    await asyncio.sleep(delay)

            # If we get here, all attempts failed
            logger.error(
                "All retry attempts exhausted",
                function=func_name,
                max_attempts=max_attempts,
                last_exception=str(last_exception),
            )
            raise last_exception

        return wrapper

    return decorator


class RetryContext:
    """Context manager for tracking retry attempts."""

    def __init__(self, operation_name: str, max_attempts: int = 3):
        self.operation_name = operation_name
        self.max_attempts = max_attempts
        self.current_attempt = 0
        self.start_time: Optional[datetime] = None
        self.total_delay = 0.0

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            if exc_type is None:
                logger.info(
                    "Operation completed successfully",
                    operation=self.operation_name,
                    attempts=self.current_attempt + 1,
                    duration_seconds=duration,
                    total_delay_seconds=self.total_delay,
                )
            else:
                logger.error(
                    "Operation failed after all attempts",
                    operation=self.operation_name,
                    attempts=self.current_attempt + 1,
                    duration_seconds=duration,
                    total_delay_seconds=self.total_delay,
                    exception_type=exc_type.__name__ if exc_type else None,
                )

    async def wait_before_retry(self, attempt: int, base_delay: float = 1.0):
        """Wait with exponential backoff before retry."""
        delay = calculate_backoff(attempt, base_delay=base_delay)
        self.total_delay += delay
        logger.info(
            "Waiting before retry",
            operation=self.operation_name,
            attempt=attempt + 1,
            delay_seconds=delay,
        )
        await asyncio.sleep(delay)
        self.current_attempt = attempt


# Convenience decorators for common scenarios


def retry_on_network_error(max_attempts: int = 3, base_delay: float = 1.0):
    """Retry only on network errors."""
    return retry_with_backoff(
        max_attempts=max_attempts,
        base_delay=base_delay,
        retryable_exceptions=(
            NetworkError,
            TimeoutError,
            ConnectionError,
            asyncio.TimeoutError,
        ),
    )


def retry_on_server_error(max_attempts: int = 3, base_delay: float = 2.0):
    """Retry only on server errors (5xx)."""
    return retry_with_backoff(
        max_attempts=max_attempts,
        base_delay=base_delay,
        retryable_exceptions=(ServerError,),
    )


def aggressive_retry(
    max_attempts: int = 5, base_delay: float = 0.5, max_delay: float = 30.0
):
    """Aggressive retry strategy for critical operations."""
    return retry_with_backoff(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=1.5,  # Less aggressive exponential growth
    )
