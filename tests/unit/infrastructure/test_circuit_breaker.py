"""
Unit tests for circuit breaker implementation.
Tests failure detection, state transitions, and recovery mechanisms.
"""

import asyncio

import pytest

from src.infrastructure.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerManager,
    CircuitBreakerOpenException,
    CircuitBreakerTimeoutException,
    CircuitState,
    circuit_breaker,
    circuit_breaker_manager,
)


class MockExceptionError(Exception):
    """Mock exception for testing."""

    pass


async def async_success_function(value: int = 42) -> int:
    """Async function that always succeeds."""
    await asyncio.sleep(0.01)
    return value


async def async_failure_function():
    """Async function that always fails."""
    await asyncio.sleep(0.01)
    raise MockExceptionError("Intentional failure")


def sync_success_function(value: int = 42) -> int:
    """Sync function that always succeeds."""
    return value


def sync_failure_function():
    """Sync function that always fails."""
    raise MockExceptionError("Intentional failure")


async def async_slow_function(delay: float = 2.0) -> str:
    """Async function that is slow."""
    await asyncio.sleep(delay)
    return "completed"


@pytest.fixture
def circuit_config():
    """Create test circuit breaker config."""
    return CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=1.0,  # Short for tests
        success_threshold=2,
        timeout=0.5,  # Short timeout for tests
        expected_exception=MockExceptionError,
    )


@pytest.fixture
def circuit(circuit_config):
    """Create test circuit breaker."""
    return CircuitBreaker("test_service", circuit_config)


class TestCircuitBreakerConfig:
    """Test CircuitBreakerConfig class."""

    @pytest.mark.unit
    def test_default_config(self):
        """Test default configuration values."""
        config = CircuitBreakerConfig()

        assert config.failure_threshold == 5
        assert config.recovery_timeout == 60.0
        assert config.success_threshold == 3
        assert config.timeout == 30.0
        assert config.expected_exception == Exception

    @pytest.mark.unit
    def test_custom_config(self):
        """Test custom configuration values."""
        config = CircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=120.0,
            success_threshold=5,
            timeout=60.0,
            expected_exception=ValueError,
        )

        assert config.failure_threshold == 10
        assert config.recovery_timeout == 120.0
        assert config.success_threshold == 5
        assert config.timeout == 60.0
        assert config.expected_exception == ValueError


class TestCircuitBreaker:
    """Test CircuitBreaker class."""

    @pytest.mark.unit
    def test_initialization(self, circuit_config):
        """Test circuit breaker initialization."""
        breaker = CircuitBreaker("test_service", circuit_config)

        assert breaker.name == "test_service"
        assert breaker.config == circuit_config
        assert breaker.state == CircuitState.CLOSED
        assert breaker.stats.total_requests == 0
        assert breaker.stats.successful_requests == 0
        assert breaker.stats.failed_requests == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_successful_async_call(self, circuit):
        """Test successful async function call."""
        result = await circuit.call(async_success_function, 100)

        assert result == 100
        assert circuit.state == CircuitState.CLOSED
        assert circuit.stats.total_requests == 1
        assert circuit.stats.successful_requests == 1
        assert circuit.stats.failed_requests == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_successful_sync_call(self, circuit):
        """Test successful sync function call."""
        result = await circuit.call(sync_success_function, 100)

        assert result == 100
        assert circuit.state == CircuitState.CLOSED
        assert circuit.stats.total_requests == 1
        assert circuit.stats.successful_requests == 1
        assert circuit.stats.failed_requests == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_failed_call(self, circuit):
        """Test failed function call."""
        with pytest.raises(MockExceptionError):
            await circuit.call(async_failure_function)

        assert circuit.state == CircuitState.CLOSED  # Not open yet
        assert circuit.stats.total_requests == 1
        assert circuit.stats.successful_requests == 0
        assert circuit.stats.failed_requests == 1
        assert circuit.stats.current_consecutive_failures == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self, circuit):
        """Test circuit opens after failure threshold."""
        # Fail 3 times to reach threshold
        for _ in range(3):
            with pytest.raises(MockExceptionError):
                await circuit.call(async_failure_function)

        assert circuit.state == CircuitState.OPEN
        assert circuit.stats.failed_requests == 3
        assert circuit.stats.current_consecutive_failures == 3
        assert circuit.stats.state_changes == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_open_circuit_rejects_calls(self, circuit):
        """Test open circuit rejects calls."""
        # Open the circuit
        for _ in range(3):
            with pytest.raises(MockExceptionError):
                await circuit.call(async_failure_function)

        assert circuit.state == CircuitState.OPEN

        # Try another call - should be rejected
        with pytest.raises(CircuitBreakerOpenException) as exc_info:
            await circuit.call(async_success_function)

        assert "Circuit breaker 'test_service' is open" in str(exc_info.value)
        assert circuit.stats.rejected_requests == 1
        assert circuit.stats.total_requests == 4  # 3 failures + 1 rejected

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_half_open_transition(self, circuit):
        """Test transition to half-open state."""
        # Open the circuit
        for _ in range(3):
            with pytest.raises(MockExceptionError):
                await circuit.call(async_failure_function)

        assert circuit.state == CircuitState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(1.1)  # Recovery timeout is 1.0

        # Next call should go through (half-open)
        result = await circuit.call(async_success_function)

        assert result == 42
        assert circuit.state == CircuitState.HALF_OPEN
        assert circuit.stats.current_consecutive_successes == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_half_open_to_closed(self, circuit):
        """Test successful recovery from half-open to closed."""
        # Open the circuit
        for _ in range(3):
            with pytest.raises(MockExceptionError):
                await circuit.call(async_failure_function)

        # Wait for recovery
        await asyncio.sleep(1.1)

        # Two successful calls to close circuit (success_threshold=2)
        await circuit.call(async_success_function)
        assert circuit.state == CircuitState.HALF_OPEN

        await circuit.call(async_success_function)
        assert circuit.state == CircuitState.CLOSED
        assert circuit.stats.state_changes == 3  # CLOSED->OPEN->HALF_OPEN->CLOSED

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_half_open_to_open(self, circuit):
        """Test failure in half-open state reopens circuit."""
        # Open the circuit
        for _ in range(3):
            with pytest.raises(MockExceptionError):
                await circuit.call(async_failure_function)

        # Wait for recovery
        await asyncio.sleep(1.1)

        # Successful call puts in half-open
        await circuit.call(async_success_function)
        assert circuit.state == CircuitState.HALF_OPEN

        # Failed call reopens circuit
        with pytest.raises(MockExceptionError):
            await circuit.call(async_failure_function)

        assert circuit.state == CircuitState.OPEN

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_timeout_handling(self, circuit):
        """Test request timeout handling."""
        with pytest.raises(CircuitBreakerTimeoutException) as exc_info:
            await circuit.call(async_slow_function, 2.0)  # 2s delay, 0.5s timeout

        assert "timed out after 0.5s" in str(exc_info.value)
        assert circuit.stats.failed_requests == 1
        assert circuit.state == CircuitState.CLOSED  # One failure, not at threshold

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unexpected_exception_passthrough(self, circuit):
        """Test unexpected exceptions pass through."""

        async def unexpected_error():
            raise ValueError("Unexpected error")

        # ValueError is not the expected exception type
        with pytest.raises(ValueError):
            await circuit.call(unexpected_error)

        # Should not count as circuit breaker failure
        assert circuit.stats.failed_requests == 0
        assert circuit.stats.total_requests == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reset_circuit(self, circuit):
        """Test manual circuit reset."""
        # Open the circuit
        for _ in range(3):
            with pytest.raises(MockExceptionError):
                await circuit.call(async_failure_function)

        assert circuit.state == CircuitState.OPEN

        # Reset circuit
        await circuit.reset()

        assert circuit.state == CircuitState.CLOSED
        assert circuit.stats.current_consecutive_failures == 0
        assert circuit.stats.current_consecutive_successes == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_force_open(self, circuit):
        """Test forcing circuit to open state."""
        await circuit.force_open()

        assert circuit.state == CircuitState.OPEN

        # Should reject calls
        with pytest.raises(CircuitBreakerOpenException):
            await circuit.call(async_success_function)

    @pytest.mark.unit
    def test_get_stats(self, circuit):
        """Test getting circuit breaker statistics."""
        stats = circuit.get_stats()

        assert stats["name"] == "test_service"
        assert stats["state"] == "closed"
        assert stats["config"]["failure_threshold"] == 3
        assert stats["stats"]["total_requests"] == 0
        assert stats["stats"]["success_rate"] == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_concurrent_calls(self, circuit):
        """Test concurrent calls through circuit breaker."""
        # Run multiple concurrent successful calls
        results = await asyncio.gather(
            circuit.call(async_success_function, 1),
            circuit.call(async_success_function, 2),
            circuit.call(async_success_function, 3),
        )

        assert results == [1, 2, 3]
        assert circuit.stats.total_requests == 3
        assert circuit.stats.successful_requests == 3
        assert circuit.state == CircuitState.CLOSED


class TestCircuitBreakerManager:
    """Test CircuitBreakerManager class."""

    @pytest.mark.unit
    def test_manager_initialization(self):
        """Test circuit breaker manager initialization."""
        manager = CircuitBreakerManager()

        assert len(manager._breakers) == 0
        assert len(manager._default_configs) == 0

    @pytest.mark.unit
    def test_register_default_config(self):
        """Test registering default configuration."""
        manager = CircuitBreakerManager()
        config = CircuitBreakerConfig(failure_threshold=10)

        manager.register_default_config("test_service", config)

        assert "test_service" in manager._default_configs
        assert manager._default_configs["test_service"] == config

    @pytest.mark.unit
    def test_get_circuit_breaker(self):
        """Test getting circuit breaker."""
        manager = CircuitBreakerManager()

        breaker1 = manager.get_circuit_breaker("service1")
        breaker2 = manager.get_circuit_breaker("service1")
        breaker3 = manager.get_circuit_breaker("service2")

        assert breaker1 is breaker2  # Same instance
        assert breaker1 is not breaker3  # Different services
        assert len(manager._breakers) == 2

    @pytest.mark.unit
    def test_get_circuit_breaker_with_default_config(self):
        """Test getting circuit breaker with default config."""
        manager = CircuitBreakerManager()
        config = CircuitBreakerConfig(failure_threshold=10)

        manager.register_default_config("test_service", config)
        breaker = manager.get_circuit_breaker("test_service")

        assert breaker.config.failure_threshold == 10

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_call_service(self):
        """Test calling service through manager."""
        manager = CircuitBreakerManager()

        result = await manager.call_service("test_service", async_success_function, 100)

        assert result == 100
        assert "test_service" in manager._breakers

    @pytest.mark.unit
    def test_get_all_stats(self):
        """Test getting all circuit breaker stats."""
        manager = CircuitBreakerManager()

        manager.get_circuit_breaker("service1")
        manager.get_circuit_breaker("service2")

        stats = manager.get_all_stats()

        assert len(stats) == 2
        assert "service1" in stats
        assert "service2" in stats
        assert stats["service1"]["name"] == "service1"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reset_all(self):
        """Test resetting all circuit breakers."""
        manager = CircuitBreakerManager()

        # Create and open multiple breakers
        for service in ["service1", "service2"]:
            breaker = manager.get_circuit_breaker(service)
            await breaker.force_open()

        # Reset all
        await manager.reset_all()

        # Check all are closed
        for breaker in manager._breakers.values():
            assert breaker.state == CircuitState.CLOSED

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_health_status(self):
        """Test getting health status of all services."""
        manager = CircuitBreakerManager()

        # Create breakers in different states
        _ = manager.get_circuit_breaker("healthy_service")

        breaker2 = manager.get_circuit_breaker("degraded_service")
        breaker2.state = CircuitState.HALF_OPEN

        breaker3 = manager.get_circuit_breaker("failed_service")
        await breaker3.force_open()

        health = manager.get_health_status()

        assert health["overall_health"] == "degraded"
        assert health["total_services"] == 3
        assert "healthy_service" in health["healthy_services"]
        assert "degraded_service" in health["degraded_services"]
        assert "failed_service" in health["failed_services"]
        assert health["health_score"] == pytest.approx(1 / 3)


class TestCircuitBreakerDecorator:
    """Test circuit breaker decorator."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_decorator_basic(self):
        """Test basic decorator usage."""

        @circuit_breaker("decorated_service")
        async def decorated_function(value: int) -> int:
            return value * 2

        result = await decorated_function(5)

        assert result == 10

        # Check breaker was created
        stats = circuit_breaker_manager.get_all_stats()
        assert "decorated_service" in stats

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_decorator_with_config(self):
        """Test decorator with custom config."""
        config = CircuitBreakerConfig(failure_threshold=2)

        @circuit_breaker("custom_service", config)
        async def failing_function():
            raise MockExceptionError("Fail")

        # Fail twice to open circuit
        for _ in range(2):
            with pytest.raises(MockExceptionError):
                await failing_function()

        # Check circuit is open
        breaker = circuit_breaker_manager.get_circuit_breaker("custom_service")
        assert breaker.state == CircuitState.OPEN


class TestGlobalCircuitBreakerManager:
    """Test global circuit breaker manager instance."""

    @pytest.mark.unit
    def test_default_configurations(self):
        """Test default configurations are registered."""
        # Check some default services are configured
        assert "transparency_api" in circuit_breaker_manager._default_configs
        assert "llm_service" in circuit_breaker_manager._default_configs
        assert "database" in circuit_breaker_manager._default_configs
        assert "redis" in circuit_breaker_manager._default_configs

        # Check configuration values
        transparency_config = circuit_breaker_manager._default_configs[
            "transparency_api"
        ]
        assert transparency_config.failure_threshold == 3
        assert transparency_config.timeout == 15.0


class TestCircuitBreakerEdgeCases:
    """Test edge cases and error scenarios."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_multiple_concurrent_failures(self, circuit):
        """Test handling multiple concurrent failures."""
        # Create concurrent failing calls
        tasks = []
        for _ in range(5):
            tasks.append(circuit.call(async_failure_function))

        # All should fail
        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert all(isinstance(r, MockExceptionError) for r in results)
        assert circuit.state == CircuitState.OPEN
        assert circuit.stats.failed_requests >= 3  # At least threshold

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_race_condition_state_change(self, circuit):
        """Test race condition during state change."""
        # Bring circuit to edge of opening (2 failures, threshold is 3)
        for _ in range(2):
            with pytest.raises(MockExceptionError):
                await circuit.call(async_failure_function)

        # Concurrent calls - one fails, one succeeds
        _ = await asyncio.gather(
            circuit.call(async_failure_function),
            circuit.call(async_success_function),
            return_exceptions=True,
        )

        # Circuit state should be consistent
        assert circuit.state in [CircuitState.CLOSED, CircuitState.OPEN]
        assert circuit.stats.total_requests == 4

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_very_short_recovery_timeout(self):
        """Test very short recovery timeout."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout=0.01,  # Very short
            success_threshold=1,
        )
        breaker = CircuitBreaker("fast_recovery", config)

        # Open circuit
        with pytest.raises(MockExceptionError):
            await breaker.call(async_failure_function)

        assert breaker.state == CircuitState.OPEN

        # Wait for recovery
        await asyncio.sleep(0.02)

        # Should be able to try again
        result = await breaker.call(async_success_function)
        assert result == 42
