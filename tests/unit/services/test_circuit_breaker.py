"""Tests for circuit breaker resilience pattern."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.orchestration.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitBreakerRegistry,
    CircuitState,
)


class TestCircuitState:
    """Tests for CircuitState enum."""

    def test_circuit_states_exist(self):
        """Test all circuit states are defined."""
        assert CircuitState.CLOSED == "closed"
        assert CircuitState.OPEN == "open"
        assert CircuitState.HALF_OPEN == "half_open"

    def test_circuit_state_values(self):
        """Test circuit state string values."""
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"


class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""

    @pytest.fixture
    def breaker(self):
        """Create circuit breaker for testing."""
        return CircuitBreaker(
            name="test_service",
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=5,
            half_open_max_calls=2,
        )

    def test_initialization(self, breaker):
        """Test circuit breaker initialization."""
        assert breaker.name == "test_service"
        assert breaker.failure_threshold == 3
        assert breaker.success_threshold == 2
        assert breaker.timeout_seconds == 5
        assert breaker.half_open_max_calls == 2
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0

    def test_default_initialization(self):
        """Test circuit breaker with default values."""
        breaker = CircuitBreaker(name="default_test")
        assert breaker.failure_threshold == 5
        assert breaker.success_threshold == 2
        assert breaker.timeout_seconds == 60
        assert breaker.half_open_max_calls == 3

    @pytest.mark.asyncio
    async def test_call_success_sync_function(self, breaker):
        """Test successful call with sync function."""

        def sync_func(x):
            return x * 2

        result = await breaker.call(sync_func, 5)
        assert result == 10
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_call_success_async_function(self, breaker):
        """Test successful call with async function."""

        async def async_func(x):
            return x * 3

        result = await breaker.call(async_func, 5)
        assert result == 15
        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_call_failure_increments_count(self, breaker):
        """Test that failures increment failure count."""

        async def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await breaker.call(failing_func)

        assert breaker.failure_count == 1
        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self, breaker):
        """Test circuit opens after failure threshold reached."""

        async def failing_func():
            raise ValueError("Test error")

        # Cause failures up to threshold
        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.call(failing_func)

        assert breaker.state == CircuitState.OPEN
        assert breaker.opened_at is not None

    @pytest.mark.asyncio
    async def test_open_circuit_blocks_calls(self, breaker):
        """Test that open circuit blocks calls."""

        async def failing_func():
            raise ValueError("Test error")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.call(failing_func)

        # Next call should be blocked
        async def should_not_run():
            return "success"

        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            await breaker.call(should_not_run)

        assert "test_service" in str(exc_info.value)
        assert "open" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_success_resets_failure_count(self, breaker):
        """Test that success resets failure count in closed state."""

        async def failing_func():
            raise ValueError("Test error")

        async def success_func():
            return "ok"

        # Cause some failures (but not enough to open)
        for _ in range(2):
            with pytest.raises(ValueError):
                await breaker.call(failing_func)

        assert breaker.failure_count == 2

        # Success should reset count
        await breaker.call(success_func)
        assert breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_half_open_after_timeout(self, breaker):
        """Test circuit transitions to half-open after timeout."""

        async def failing_func():
            raise ValueError("Test error")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.call(failing_func)

        assert breaker.state == CircuitState.OPEN

        # Simulate timeout passing
        breaker.opened_at = time.time() - 10  # 10 seconds ago

        # Next call should be allowed (half-open)
        async def success_func():
            return "recovered"

        result = await breaker.call(success_func)
        assert result == "recovered"
        assert breaker.state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_half_open_closes_after_successes(self, breaker):
        """Test circuit closes after enough successes in half-open."""

        async def failing_func():
            raise ValueError("Test error")

        async def success_func():
            return "ok"

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.call(failing_func)

        # Transition to half-open
        breaker.opened_at = time.time() - 10
        await breaker.call(success_func)
        assert breaker.state == CircuitState.HALF_OPEN

        # Another success should close it (success_threshold=2)
        await breaker.call(success_func)
        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_half_open_reopens_on_failure(self, breaker):
        """Test circuit reopens if failure in half-open state."""

        async def failing_func():
            raise ValueError("Test error")

        async def success_func():
            return "ok"

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.call(failing_func)

        # Transition to half-open
        breaker.opened_at = time.time() - 10
        await breaker.call(success_func)
        assert breaker.state == CircuitState.HALF_OPEN

        # Failure in half-open should reopen
        with pytest.raises(ValueError):
            await breaker.call(failing_func)

        assert breaker.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_half_open_limits_calls(self, breaker):
        """Test half-open state limits number of test calls."""
        breaker.half_open_max_calls = 2

        async def failing_func():
            raise ValueError("Test error")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.call(failing_func)

        # Transition to half-open manually
        breaker.state = CircuitState.HALF_OPEN
        breaker.half_open_calls = 0

        async def success_func():
            return "ok"

        # First two calls allowed
        await breaker.call(success_func)
        assert breaker.half_open_calls == 1

        await breaker.call(success_func)
        # After 2 successes, should be closed
        assert breaker.state == CircuitState.CLOSED

    def test_get_status(self, breaker):
        """Test getting circuit breaker status."""
        status = breaker.get_status()

        assert status["name"] == "test_service"
        assert status["state"] == "closed"
        assert status["failure_count"] == 0
        assert status["success_count"] == 0
        assert status["last_failure_time"] is None
        assert status["opened_at"] is None
        assert status["time_in_open"] is None

    def test_get_status_when_open(self, breaker):
        """Test status when circuit is open."""
        breaker.state = CircuitState.OPEN
        breaker.opened_at = time.time() - 30
        breaker.failure_count = 5

        status = breaker.get_status()

        assert status["state"] == "open"
        assert status["failure_count"] == 5
        assert status["opened_at"] is not None
        assert status["time_in_open"] is not None
        assert status["time_in_open"] >= 30

    @pytest.mark.asyncio
    async def test_manual_reset(self, breaker):
        """Test manually resetting circuit breaker."""
        # Put in open state
        breaker.state = CircuitState.OPEN
        breaker.failure_count = 5
        breaker.opened_at = time.time()

        await breaker.reset()

        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0
        assert breaker.opened_at is None


class TestCircuitBreakerOpenError:
    """Tests for CircuitBreakerOpenError exception."""

    def test_exception_creation(self):
        """Test creating circuit breaker error."""
        error = CircuitBreakerOpenError("Service unavailable")
        assert str(error) == "Service unavailable"

    def test_exception_inheritance(self):
        """Test that error inherits from Exception."""
        error = CircuitBreakerOpenError("test")
        assert isinstance(error, Exception)


class TestCircuitBreakerRegistry:
    """Tests for CircuitBreakerRegistry class."""

    @pytest.fixture
    def registry(self):
        """Create registry for testing."""
        return CircuitBreakerRegistry()

    @pytest.mark.asyncio
    async def test_get_breaker_creates_new(self, registry):
        """Test getting a new circuit breaker."""
        breaker = await registry.get_breaker("api_1")

        assert breaker.name == "api_1"
        assert isinstance(breaker, CircuitBreaker)

    @pytest.mark.asyncio
    async def test_get_breaker_returns_existing(self, registry):
        """Test getting existing circuit breaker."""
        breaker1 = await registry.get_breaker("api_1")
        breaker2 = await registry.get_breaker("api_1")

        assert breaker1 is breaker2

    @pytest.mark.asyncio
    async def test_get_breaker_with_custom_params(self, registry):
        """Test creating breaker with custom parameters."""
        breaker = await registry.get_breaker(
            "custom_api", failure_threshold=10, timeout_seconds=120
        )

        assert breaker.failure_threshold == 10
        assert breaker.timeout_seconds == 120

    @pytest.mark.asyncio
    async def test_get_all_status(self, registry):
        """Test getting status of all circuit breakers."""
        await registry.get_breaker("api_1")
        await registry.get_breaker("api_2")

        status = registry.get_all_status()

        assert "api_1" in status
        assert "api_2" in status
        assert status["api_1"]["state"] == "closed"
        assert status["api_2"]["state"] == "closed"

    @pytest.mark.asyncio
    async def test_reset_all(self, registry):
        """Test resetting all circuit breakers."""
        breaker1 = await registry.get_breaker("api_1")
        breaker2 = await registry.get_breaker("api_2")

        # Put both in open state
        breaker1.state = CircuitState.OPEN
        breaker1.failure_count = 5
        breaker2.state = CircuitState.OPEN
        breaker2.failure_count = 3

        await registry.reset_all()

        assert breaker1.state == CircuitState.CLOSED
        assert breaker2.state == CircuitState.CLOSED
        assert breaker1.failure_count == 0
        assert breaker2.failure_count == 0

    @pytest.mark.asyncio
    async def test_multiple_services_independent(self, registry):
        """Test that different services have independent breakers."""

        async def failing_func():
            raise ValueError("error")

        async def success_func():
            return "ok"

        breaker1 = await registry.get_breaker("api_1", failure_threshold=2)
        breaker2 = await registry.get_breaker("api_2", failure_threshold=2)

        # Fail api_1
        for _ in range(2):
            with pytest.raises(ValueError):
                await breaker1.call(failing_func)

        assert breaker1.state == CircuitState.OPEN
        assert breaker2.state == CircuitState.CLOSED

        # api_2 should still work
        result = await breaker2.call(success_func)
        assert result == "ok"
