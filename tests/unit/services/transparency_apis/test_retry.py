"""
Unit tests for retry logic with exponential backoff.

Tests the retry decorators, backoff calculation, and retry context manager.

Author: Anderson Henrique da Silva
Created: 2025-10-12 15:53:52 -03
License: Proprietary - All rights reserved
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from src.services.transparency_apis.federal_apis.exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)
from src.services.transparency_apis.federal_apis.retry import (
    NON_RETRYABLE_EXCEPTIONS,
    RETRYABLE_EXCEPTIONS,
    RetryContext,
    aggressive_retry,
    calculate_backoff,
    retry_on_network_error,
    retry_on_server_error,
    retry_with_backoff,
    should_retry_exception,
)


class TestBackoffCalculation:
    """Test exponential backoff calculation."""

    def test_backoff_without_jitter(self):
        """Test exponential backoff calculation without jitter."""
        # Base delay = 1.0, exponential_base = 2.0
        assert calculate_backoff(0, base_delay=1.0, jitter=False) == 1.0
        assert calculate_backoff(1, base_delay=1.0, jitter=False) == 2.0
        assert calculate_backoff(2, base_delay=1.0, jitter=False) == 4.0
        assert calculate_backoff(3, base_delay=1.0, jitter=False) == 8.0
        assert calculate_backoff(4, base_delay=1.0, jitter=False) == 16.0

    def test_backoff_respects_max_delay(self):
        """Test that backoff doesn't exceed max_delay."""
        # Even with high attempt number, should cap at max_delay
        delay = calculate_backoff(10, base_delay=1.0, max_delay=30.0, jitter=False)
        assert delay == 30.0

    def test_backoff_with_custom_base(self):
        """Test backoff with custom exponential base."""
        # exponential_base = 1.5 instead of 2.0
        delay1 = calculate_backoff(
            1, base_delay=2.0, exponential_base=1.5, jitter=False
        )
        assert delay1 == 3.0  # 2.0 * 1.5^1

        delay2 = calculate_backoff(
            2, base_delay=2.0, exponential_base=1.5, jitter=False
        )
        assert delay2 == 4.5  # 2.0 * 1.5^2

    def test_backoff_with_jitter(self):
        """Test that jitter adds randomness to delay."""
        delays = [calculate_backoff(1, base_delay=1.0, jitter=True) for _ in range(10)]

        # All delays should be different due to jitter
        assert len(set(delays)) > 1

        # All delays should be between base and base * 1.25 (0-25% jitter)
        for delay in delays:
            assert 2.0 <= delay <= 2.5  # base=1.0, attempt=1 → 2.0s, +25% jitter max

    def test_backoff_first_attempt_is_base_delay(self):
        """Test that first retry uses base delay."""
        delay = calculate_backoff(0, base_delay=5.0, jitter=False)
        assert delay == 5.0


class TestRetryableExceptions:
    """Test exception classification for retry logic."""

    def test_network_error_is_retryable(self):
        """Test NetworkError is retryable."""
        error = NetworkError("Connection failed", api_name="Test")
        assert should_retry_exception(error) is True

    def test_timeout_error_is_retryable(self):
        """Test TimeoutError is retryable."""
        error = TimeoutError("Timeout", api_name="Test", timeout_seconds=30)
        assert should_retry_exception(error) is True

    def test_server_error_is_retryable(self):
        """Test ServerError is retryable."""
        error = ServerError("Server error", api_name="Test", status_code=503)
        assert should_retry_exception(error) is True

    def test_connection_error_is_retryable(self):
        """Test ConnectionError is retryable."""
        error = ConnectionError("Connection refused")
        assert should_retry_exception(error) is True

    def test_asyncio_timeout_is_retryable(self):
        """Test asyncio.TimeoutError is retryable."""
        error = asyncio.TimeoutError()
        assert should_retry_exception(error) is True

    def test_authentication_error_not_retryable(self):
        """Test AuthenticationError is not retryable."""
        error = AuthenticationError("Unauthorized", api_name="Test", status_code=401)
        assert should_retry_exception(error) is False

    def test_not_found_error_not_retryable(self):
        """Test NotFoundError is not retryable."""
        error = NotFoundError("Not found", api_name="Test")
        assert should_retry_exception(error) is False

    def test_validation_error_not_retryable(self):
        """Test ValidationError is not retryable."""
        error = ValidationError("Invalid data", api_name="Test", status_code=400)
        assert should_retry_exception(error) is False

    def test_rate_limit_error_is_retryable(self):
        """Test RateLimitError is retryable (special case)."""
        error = RateLimitError("Rate limit", api_name="Test", retry_after=60)
        assert should_retry_exception(error) is True

    def test_unknown_exception_not_retryable(self):
        """Test unknown exceptions are not retryable by default."""
        error = ValueError("Some error")
        assert should_retry_exception(error) is False


class TestRetryDecorator:
    """Test retry_with_backoff decorator."""

    @pytest.mark.asyncio
    async def test_successful_function_no_retry(self):
        """Test successful function doesn't trigger retry."""
        mock_func = AsyncMock(return_value="success")

        @retry_with_backoff(max_attempts=3, base_delay=0.01)
        async def test_func():
            return await mock_func()

        result = await test_func()

        assert result == "success"
        assert mock_func.call_count == 1  # Only called once

    @pytest.mark.asyncio
    async def test_retry_on_network_error(self):
        """Test retry happens on NetworkError."""
        mock_func = AsyncMock(
            side_effect=[
                NetworkError("Error 1", api_name="Test"),
                NetworkError("Error 2", api_name="Test"),
                "success",
            ]
        )

        @retry_with_backoff(max_attempts=3, base_delay=0.01)
        async def test_func():
            return await mock_func()

        result = await test_func()

        assert result == "success"
        assert mock_func.call_count == 3  # Retried 2 times

    @pytest.mark.asyncio
    async def test_no_retry_on_authentication_error(self):
        """Test no retry on AuthenticationError."""
        mock_func = AsyncMock(
            side_effect=AuthenticationError("Unauthorized", api_name="Test")
        )

        @retry_with_backoff(max_attempts=3, base_delay=0.01)
        async def test_func():
            return await mock_func()

        with pytest.raises(AuthenticationError):
            await test_func()

        assert mock_func.call_count == 1  # No retry

    @pytest.mark.asyncio
    async def test_max_attempts_exhausted(self):
        """Test all attempts exhausted raises last exception."""
        mock_func = AsyncMock(
            side_effect=NetworkError("Persistent error", api_name="Test")
        )

        @retry_with_backoff(max_attempts=3, base_delay=0.01)
        async def test_func():
            return await mock_func()

        with pytest.raises(NetworkError) as exc_info:
            await test_func()

        assert "Persistent error" in str(exc_info.value)
        assert mock_func.call_count == 3  # All attempts used

    @pytest.mark.asyncio
    async def test_retry_with_rate_limit(self):
        """Test retry respects rate limit retry_after."""
        mock_func = AsyncMock(
            side_effect=[
                RateLimitError("Rate limit", api_name="Test", retry_after=0.05),
                "success",
            ]
        )

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:

            @retry_with_backoff(max_attempts=3, base_delay=0.01)
            async def test_func():
                return await mock_func()

            result = await test_func()

            assert result == "success"
            # Should use retry_after from exception, not exponential backoff
            mock_sleep.assert_called_once_with(0.05)

    @pytest.mark.asyncio
    async def test_on_retry_callback(self):
        """Test on_retry callback is called."""
        callback_calls = []

        def on_retry_callback(attempt, exception):
            callback_calls.append((attempt, str(exception)))

        mock_func = AsyncMock(
            side_effect=[NetworkError("Error", api_name="Test"), "success"]
        )

        @retry_with_backoff(max_attempts=3, base_delay=0.01, on_retry=on_retry_callback)
        async def test_func():
            return await mock_func()

        await test_func()

        assert len(callback_calls) == 1
        assert callback_calls[0][0] == 1  # First retry
        assert "Error" in callback_calls[0][1]

    @pytest.mark.asyncio
    async def test_custom_retryable_exceptions(self):
        """Test custom retryable exceptions parameter."""
        mock_func = AsyncMock(side_effect=[ValueError("Error"), "success"])

        @retry_with_backoff(
            max_attempts=3, base_delay=0.01, retryable_exceptions=(ValueError,)
        )
        async def test_func():
            return await mock_func()

        result = await test_func()

        assert result == "success"
        assert mock_func.call_count == 2  # Retried once

    @pytest.mark.asyncio
    async def test_preserves_function_metadata(self):
        """Test decorator preserves function metadata."""

        @retry_with_backoff(max_attempts=3)
        async def test_func():
            """Test function docstring."""
            pass

        assert test_func.__name__ == "test_func"
        assert test_func.__doc__ == "Test function docstring."


class TestConvenienceDecorators:
    """Test convenience decorator functions."""

    @pytest.mark.asyncio
    async def test_retry_on_network_error_decorator(self):
        """Test retry_on_network_error only retries network errors."""
        network_calls = []

        @retry_on_network_error(max_attempts=3, base_delay=0.01)
        async def test_func():
            network_calls.append(1)
            if len(network_calls) < 2:
                raise NetworkError("Network error", api_name="Test")
            return "success"

        result = await test_func()
        assert result == "success"
        assert len(network_calls) == 2

    @pytest.mark.asyncio
    async def test_retry_on_server_error_decorator(self):
        """Test retry_on_server_error only retries server errors."""
        server_calls = []

        @retry_on_server_error(max_attempts=3, base_delay=0.01)
        async def test_func():
            server_calls.append(1)
            if len(server_calls) < 2:
                raise ServerError("Server error", api_name="Test", status_code=503)
            return "success"

        result = await test_func()
        assert result == "success"
        assert len(server_calls) == 2

    @pytest.mark.asyncio
    async def test_aggressive_retry_decorator(self):
        """Test aggressive_retry uses 5 attempts and lower base delay."""
        aggressive_calls = []

        @aggressive_retry(max_attempts=5, base_delay=0.01)
        async def test_func():
            aggressive_calls.append(1)
            if len(aggressive_calls) < 4:
                raise NetworkError("Error", api_name="Test")
            return "success"

        result = await test_func()
        assert result == "success"
        assert len(aggressive_calls) == 4  # Succeeded on 4th attempt


class TestRetryContext:
    """Test RetryContext manager."""

    def test_retry_context_tracks_attempts(self):
        """Test RetryContext tracks number of attempts."""
        with RetryContext("test_operation", max_attempts=5) as ctx:
            assert ctx.operation_name == "test_operation"
            assert ctx.max_attempts == 5
            assert ctx.current_attempt == 0

    @pytest.mark.asyncio
    async def test_retry_context_wait_before_retry(self):
        """Test RetryContext wait_before_retry calculates delay."""
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            with RetryContext("test_operation") as ctx:
                await ctx.wait_before_retry(attempt=1, base_delay=0.01)

                # Should have called asyncio.sleep with calculated backoff
                assert mock_sleep.called
                assert ctx.total_delay > 0

    def test_retry_context_completion(self):
        """Test RetryContext records completion."""
        ctx = RetryContext("test_operation")
        with ctx:
            pass
        # Context completed successfully (no exception)


class TestConstantsAndConfiguration:
    """Test retry constants and configuration."""

    def test_retryable_exceptions_tuple(self):
        """Test RETRYABLE_EXCEPTIONS contains expected types."""
        assert NetworkError in RETRYABLE_EXCEPTIONS
        assert TimeoutError in RETRYABLE_EXCEPTIONS
        assert ServerError in RETRYABLE_EXCEPTIONS
        assert ConnectionError in RETRYABLE_EXCEPTIONS
        assert asyncio.TimeoutError in RETRYABLE_EXCEPTIONS

    def test_non_retryable_exceptions_tuple(self):
        """Test NON_RETRYABLE_EXCEPTIONS contains expected types."""
        assert AuthenticationError in NON_RETRYABLE_EXCEPTIONS
        assert NotFoundError in NON_RETRYABLE_EXCEPTIONS
        assert ValidationError in NON_RETRYABLE_EXCEPTIONS

    def test_exception_tuples_are_disjoint(self):
        """Test retryable and non-retryable exceptions don't overlap."""
        retryable_set = set(RETRYABLE_EXCEPTIONS)
        non_retryable_set = set(NON_RETRYABLE_EXCEPTIONS)

        # Should have no intersection
        assert len(retryable_set & non_retryable_set) == 0
