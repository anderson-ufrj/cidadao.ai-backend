"""
Module: tests.test_infrastructure.test_retry_policy
Description: Tests for retry policies and circuit breaker
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import asyncio

import pytest

from src.infrastructure.queue.retry_policy import (
    AGGRESSIVE_RETRY_POLICY,
    DEFAULT_RETRY_POLICY,
    GENTLE_RETRY_POLICY,
    CircuitBreaker,
    RetryHandler,
    RetryPolicy,
    RetryStrategy,
)


class TestRetryPolicy:
    """Test suite for retry policies."""

    def test_default_policy(self):
        """Test default retry policy settings."""
        assert DEFAULT_RETRY_POLICY.strategy == RetryStrategy.EXPONENTIAL_BACKOFF
        assert DEFAULT_RETRY_POLICY.max_attempts == 3
        assert DEFAULT_RETRY_POLICY.initial_delay == 1.0
        assert DEFAULT_RETRY_POLICY.jitter is True

    def test_aggressive_policy(self):
        """Test aggressive retry policy."""
        assert AGGRESSIVE_RETRY_POLICY.max_attempts == 5
        assert AGGRESSIVE_RETRY_POLICY.initial_delay == 0.5
        assert AGGRESSIVE_RETRY_POLICY.multiplier == 1.5

    def test_gentle_policy(self):
        """Test gentle retry policy."""
        assert GENTLE_RETRY_POLICY.strategy == RetryStrategy.LINEAR_BACKOFF
        assert GENTLE_RETRY_POLICY.max_attempts == 2
        assert GENTLE_RETRY_POLICY.jitter is False


class TestRetryHandler:
    """Test suite for retry handler."""

    def test_should_retry_max_attempts(self):
        """Test retry decision based on max attempts."""
        policy = RetryPolicy(max_attempts=3)
        handler = RetryHandler(policy)

        exception = ValueError("Test error")

        assert handler.should_retry(exception, 1) is True
        assert handler.should_retry(exception, 2) is True
        assert handler.should_retry(exception, 3) is False  # Max reached

    def test_should_retry_exception_whitelist(self):
        """Test retry with specific exception types."""
        policy = RetryPolicy(retry_on=[ValueError, TypeError])
        handler = RetryHandler(policy)

        assert handler.should_retry(ValueError("test"), 1) is True
        assert handler.should_retry(TypeError("test"), 1) is True
        assert handler.should_retry(RuntimeError("test"), 1) is False

    def test_should_retry_exception_blacklist(self):
        """Test retry with exception blacklist."""
        policy = RetryPolicy(dont_retry_on=[RuntimeError, KeyError])
        handler = RetryHandler(policy)

        assert handler.should_retry(ValueError("test"), 1) is True
        assert handler.should_retry(RuntimeError("test"), 1) is False
        assert handler.should_retry(KeyError("test"), 1) is False

    def test_calculate_delay_fixed(self):
        """Test fixed delay calculation."""
        policy = RetryPolicy(
            strategy=RetryStrategy.FIXED_DELAY, initial_delay=2.0, jitter=False
        )
        handler = RetryHandler(policy)

        assert handler.calculate_delay(1) == 2.0
        assert handler.calculate_delay(2) == 2.0
        assert handler.calculate_delay(3) == 2.0

    def test_calculate_delay_exponential(self):
        """Test exponential backoff calculation."""
        policy = RetryPolicy(
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            initial_delay=1.0,
            multiplier=2.0,
            jitter=False,
        )
        handler = RetryHandler(policy)

        assert handler.calculate_delay(1) == 1.0
        assert handler.calculate_delay(2) == 2.0
        assert handler.calculate_delay(3) == 4.0
        assert handler.calculate_delay(4) == 8.0

    def test_calculate_delay_linear(self):
        """Test linear backoff calculation."""
        policy = RetryPolicy(
            strategy=RetryStrategy.LINEAR_BACKOFF, initial_delay=2.0, jitter=False
        )
        handler = RetryHandler(policy)

        assert handler.calculate_delay(1) == 2.0
        assert handler.calculate_delay(2) == 4.0
        assert handler.calculate_delay(3) == 6.0

    def test_calculate_delay_fibonacci(self):
        """Test fibonacci backoff calculation."""
        policy = RetryPolicy(
            strategy=RetryStrategy.FIBONACCI, initial_delay=1.0, jitter=False
        )
        handler = RetryHandler(policy)

        assert handler.calculate_delay(1) == 1.0  # fib(1) = 1
        assert handler.calculate_delay(2) == 1.0  # fib(2) = 1
        assert handler.calculate_delay(3) == 2.0  # fib(3) = 2
        assert handler.calculate_delay(4) == 3.0  # fib(4) = 3
        assert handler.calculate_delay(5) == 5.0  # fib(5) = 5

    def test_calculate_delay_with_jitter(self):
        """Test delay calculation with jitter."""
        policy = RetryPolicy(
            strategy=RetryStrategy.FIXED_DELAY, initial_delay=10.0, jitter=True
        )
        handler = RetryHandler(policy)

        # With jitter, delay should be within ±25% of base
        delays = [handler.calculate_delay(1) for _ in range(10)]
        assert all(7.5 <= d <= 12.5 for d in delays)
        # Should have some variation
        assert len(set(delays)) > 1

    def test_calculate_delay_max_cap(self):
        """Test delay is capped at max_delay."""
        policy = RetryPolicy(
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            initial_delay=10.0,
            multiplier=10.0,
            max_delay=50.0,
            jitter=False,
        )
        handler = RetryHandler(policy)

        assert handler.calculate_delay(1) == 10.0
        assert handler.calculate_delay(2) == 50.0  # Would be 100 but capped
        assert handler.calculate_delay(3) == 50.0  # Would be 1000 but capped

    @pytest.mark.asyncio
    async def test_execute_with_retry_success(self):
        """Test successful execution without retry."""
        policy = RetryPolicy()
        handler = RetryHandler(policy)

        async def successful_func(value):
            return value * 2

        result = await handler.execute_with_retry(successful_func, 5)
        assert result == 10

    @pytest.mark.asyncio
    async def test_execute_with_retry_eventual_success(self):
        """Test execution that succeeds after retries."""
        policy = RetryPolicy(initial_delay=0.1, jitter=False)
        handler = RetryHandler(policy)

        attempt_count = 0

        async def flaky_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = await handler.execute_with_retry(flaky_func)
        assert result == "success"
        assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_execute_with_retry_max_attempts_exceeded(self):
        """Test execution that fails after max attempts."""
        policy = RetryPolicy(max_attempts=2, initial_delay=0.1, jitter=False)
        handler = RetryHandler(policy)

        async def always_failing_func():
            raise ValueError("Always fails")

        with pytest.raises(ValueError) as exc_info:
            await handler.execute_with_retry(always_failing_func)

        assert str(exc_info.value) == "Always fails"

    @pytest.mark.asyncio
    async def test_execute_with_retry_callbacks(self):
        """Test retry callbacks."""
        retry_calls = []
        failure_calls = []

        def on_retry(exc, attempt, delay):
            retry_calls.append((str(exc), attempt, delay))

        def on_failure(exc, attempt, delay):
            failure_calls.append((str(exc), attempt))

        policy = RetryPolicy(
            max_attempts=2,
            initial_delay=0.1,
            jitter=False,
            on_retry=on_retry,
            on_failure=on_failure,
        )
        handler = RetryHandler(policy)

        async def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await handler.execute_with_retry(failing_func)

        # Should have one retry callback
        assert len(retry_calls) == 1
        assert retry_calls[0][0] == "Test error"
        assert retry_calls[0][1] == 1

        # Should have one failure callback
        assert len(failure_calls) == 1
        assert failure_calls[0][0] == "Test error"
        assert failure_calls[0][1] == 2

    def test_execute_with_retry_sync_function(self):
        """Test retry with synchronous function."""
        policy = RetryPolicy(initial_delay=0.1)
        handler = RetryHandler(policy)

        attempt_count = 0

        def sync_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError("Temporary")
            return "success"

        # Run in async context
        result = asyncio.run(handler.execute_with_retry(sync_func))
        assert result == "success"
        assert attempt_count == 2


class TestCircuitBreaker:
    """Test suite for circuit breaker."""

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initialization."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)

        assert breaker.state == CircuitBreaker.State.CLOSED
        assert breaker.failure_count == 0
        assert breaker.failure_threshold == 3
        assert breaker.recovery_timeout == 30.0

    def test_circuit_breaker_success(self):
        """Test circuit breaker with successful calls."""
        breaker = CircuitBreaker()

        def successful_func():
            return "success"

        # Multiple successful calls
        for _ in range(10):
            result = breaker.call(successful_func)
            assert result == "success"

        assert breaker.state == CircuitBreaker.State.CLOSED
        assert breaker.failure_count == 0

    def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after threshold."""
        breaker = CircuitBreaker(failure_threshold=3)

        def failing_func():
            raise ValueError("Always fails")

        # First failures
        for i in range(3):
            with pytest.raises(ValueError):
                breaker.call(failing_func)

        # Circuit should be open
        assert breaker.state == CircuitBreaker.State.OPEN
        assert breaker.failure_count == 3

        # Next call should fail immediately
        with pytest.raises(Exception) as exc_info:
            breaker.call(failing_func)
        assert "Circuit breaker is OPEN" in str(exc_info.value)

    def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker recovery through half-open state."""
        breaker = CircuitBreaker(
            failure_threshold=2, recovery_timeout=0.1  # Short timeout for testing
        )

        # Open the circuit
        def failing_func():
            raise ValueError("Fails")

        for _ in range(2):
            with pytest.raises(ValueError):
                breaker.call(failing_func)

        assert breaker.state == CircuitBreaker.State.OPEN

        # Wait for recovery timeout
        import time

        time.sleep(0.2)

        # Next call should transition to half-open
        def successful_func():
            return "success"

        # First success in half-open
        result = breaker.call(successful_func)
        assert result == "success"
        assert breaker.state == CircuitBreaker.State.HALF_OPEN

        # Need more successes to fully close
        for _ in range(2):
            breaker.call(successful_func)

        assert breaker.state == CircuitBreaker.State.CLOSED

    def test_circuit_breaker_half_open_failure(self):
        """Test circuit breaker returns to open on half-open failure."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

        # Open the circuit
        def failing_func():
            raise ValueError("Fails")

        for _ in range(2):
            with pytest.raises(ValueError):
                breaker.call(failing_func)

        # Wait for recovery
        import time

        time.sleep(0.2)

        # Fail in half-open state
        with pytest.raises(ValueError):
            breaker.call(failing_func)

        # Should return to open
        assert breaker.state == CircuitBreaker.State.OPEN

    @pytest.mark.asyncio
    async def test_circuit_breaker_async(self):
        """Test circuit breaker with async functions."""
        breaker = CircuitBreaker(failure_threshold=2)

        async def async_failing():
            raise ValueError("Async fail")

        # Open circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                await breaker.call_async(async_failing)

        assert breaker.state == CircuitBreaker.State.OPEN

        # Next call should fail immediately
        with pytest.raises(Exception) as exc_info:
            await breaker.call_async(async_failing)
        assert "Circuit breaker is OPEN" in str(exc_info.value)

    def test_circuit_breaker_expected_exception(self):
        """Test circuit breaker only triggers on expected exceptions."""
        breaker = CircuitBreaker(failure_threshold=2, expected_exception=ValueError)

        def func_with_different_error():
            raise TypeError("Different error")

        # These shouldn't trigger the breaker
        for _ in range(5):
            with pytest.raises(TypeError):
                breaker.call(func_with_different_error)

        assert breaker.state == CircuitBreaker.State.CLOSED
        assert breaker.failure_count == 0

        # But ValueError should
        def func_with_expected_error():
            raise ValueError("Expected error")

        for _ in range(2):
            with pytest.raises(ValueError):
                breaker.call(func_with_expected_error)

        assert breaker.state == CircuitBreaker.State.OPEN
