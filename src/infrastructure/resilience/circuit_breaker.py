"""
Circuit breaker pattern implementation for external services.

This module provides circuit breaker functionality to prevent cascading
failures and improve system resilience.
"""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional

from src.core import get_logger

logger = get_logger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service is recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    failure_threshold: int = 5  # Failures before opening
    recovery_timeout: float = 60.0  # Seconds before trying half-open
    success_threshold: int = 3  # Successes to close from half-open
    timeout: float = 30.0  # Request timeout
    expected_exception: type = Exception  # Exception type to count as failure


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rejected_requests: int = 0
    state_changes: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    current_consecutive_failures: int = 0
    current_consecutive_successes: int = 0


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open."""

    pass


class CircuitBreakerTimeoutException(Exception):
    """Exception raised when request times out."""

    pass


class CircuitBreaker:
    """
    Circuit breaker implementation for resilient external service calls.

    Features:
    - Automatic failure detection
    - Configurable thresholds
    - Recovery mechanism
    - Statistics and monitoring
    - Async/await support
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.

        Args:
            name: Circuit breaker name for identification
            config: Configuration parameters
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
        self._last_failure_time: Optional[float] = None

        logger.info(f"Circuit breaker '{name}' initialized")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenException: When circuit is open
            CircuitBreakerTimeoutException: When request times out
        """
        async with self._lock:
            self.stats.total_requests += 1

            # Check if circuit should be opened
            await self._check_state()

            if self.state == CircuitState.OPEN:
                self.stats.rejected_requests += 1
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.name}' is open"
                )

        # Execute the function
        start_time = time.time()

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self._execute_async(func, *args, **kwargs), timeout=self.config.timeout
            )

            # Record success
            await self._record_success()

            execution_time = time.time() - start_time
            logger.debug(
                f"Circuit breaker '{self.name}' - Success "
                f"(time: {execution_time:.3f}s)"
            )

            return result

        except asyncio.TimeoutError:
            await self._record_failure()
            execution_time = time.time() - start_time

            logger.warning(
                f"Circuit breaker '{self.name}' - Timeout "
                f"(time: {execution_time:.3f}s)"
            )

            raise CircuitBreakerTimeoutException(
                f"Request to '{self.name}' timed out after {self.config.timeout}s"
            )

        except self.config.expected_exception as e:
            await self._record_failure()
            execution_time = time.time() - start_time

            logger.warning(
                f"Circuit breaker '{self.name}' - Failure: {e} "
                f"(time: {execution_time:.3f}s)"
            )

            raise

    async def _execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function, handling both sync and async functions."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            # Run sync function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)

    async def _check_state(self):
        """Check and update circuit breaker state."""
        current_time = time.time()

        if self.state == CircuitState.OPEN:
            # Check if we should try half-open
            if (
                self._last_failure_time
                and current_time - self._last_failure_time
                >= self.config.recovery_timeout
            ):

                self.state = CircuitState.HALF_OPEN
                self.stats.state_changes += 1

                logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN")

        elif self.state == CircuitState.HALF_OPEN:
            # Half-open state is handled in success/failure recording
            pass

    async def _record_success(self):
        """Record successful execution."""
        async with self._lock:
            self.stats.successful_requests += 1
            self.stats.current_consecutive_failures = 0
            self.stats.current_consecutive_successes += 1
            self.stats.last_success_time = datetime.now(UTC)

            if self.state == CircuitState.HALF_OPEN:
                if (
                    self.stats.current_consecutive_successes
                    >= self.config.success_threshold
                ):

                    # Transition to closed
                    self.state = CircuitState.CLOSED
                    self.stats.state_changes += 1
                    self.stats.current_consecutive_successes = 0

                    logger.info(f"Circuit breaker '{self.name}' transitioned to CLOSED")

    async def _record_failure(self):
        """Record failed execution."""
        async with self._lock:
            self.stats.failed_requests += 1
            self.stats.current_consecutive_successes = 0
            self.stats.current_consecutive_failures += 1
            self.stats.last_failure_time = datetime.now(UTC)
            self._last_failure_time = time.time()

            # In HALF_OPEN state, any failure reopens the circuit immediately
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.stats.state_changes += 1
                logger.warning(
                    f"Circuit breaker '{self.name}' reopened from HALF_OPEN after failure"
                )
            # In CLOSED state, check if we reached the failure threshold
            elif (
                self.state == CircuitState.CLOSED
                and self.stats.current_consecutive_failures
                >= self.config.failure_threshold
            ):
                self.state = CircuitState.OPEN
                self.stats.state_changes += 1

                logger.warning(
                    f"Circuit breaker '{self.name}' opened after "
                    f"{self.stats.current_consecutive_failures} consecutive failures"
                )

    def get_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics."""
        success_rate = (
            self.stats.successful_requests / self.stats.total_requests
            if self.stats.total_requests > 0
            else 0
        )

        return {
            "name": self.name,
            "state": self.state.value,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout,
            },
            "stats": {
                "total_requests": self.stats.total_requests,
                "successful_requests": self.stats.successful_requests,
                "failed_requests": self.stats.failed_requests,
                "rejected_requests": self.stats.rejected_requests,
                "success_rate": success_rate,
                "state_changes": self.stats.state_changes,
                "current_consecutive_failures": self.stats.current_consecutive_failures,
                "current_consecutive_successes": self.stats.current_consecutive_successes,
                "last_failure_time": (
                    self.stats.last_failure_time.isoformat()
                    if self.stats.last_failure_time
                    else None
                ),
                "last_success_time": (
                    self.stats.last_success_time.isoformat()
                    if self.stats.last_success_time
                    else None
                ),
            },
        }

    async def reset(self):
        """Reset circuit breaker to closed state."""
        async with self._lock:
            self.state = CircuitState.CLOSED
            self.stats.current_consecutive_failures = 0
            self.stats.current_consecutive_successes = 0
            self._last_failure_time = None

            logger.info(f"Circuit breaker '{self.name}' manually reset")

    async def force_open(self):
        """Force circuit breaker to open state."""
        async with self._lock:
            self.state = CircuitState.OPEN
            self._last_failure_time = time.time()

            logger.warning(f"Circuit breaker '{self.name}' manually opened")


class CircuitBreakerManager:
    """
    Manager for multiple circuit breakers.

    Provides centralized management and monitoring of circuit breakers.
    """

    def __init__(self):
        """Initialize circuit breaker manager."""
        self._breakers: dict[str, CircuitBreaker] = {}
        self._default_configs: dict[str, CircuitBreakerConfig] = {}

    def register_default_config(self, service_name: str, config: CircuitBreakerConfig):
        """
        Register default configuration for a service.

        Args:
            service_name: Service name
            config: Default configuration
        """
        self._default_configs[service_name] = config
        logger.info(f"Registered default config for service '{service_name}'")

    def get_circuit_breaker(
        self, service_name: str, config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """
        Get or create circuit breaker for service.

        Args:
            service_name: Service name
            config: Configuration (uses default if not provided)

        Returns:
            Circuit breaker instance
        """
        if service_name not in self._breakers:
            # Use provided config or default
            breaker_config = (
                config
                or self._default_configs.get(service_name)
                or CircuitBreakerConfig()
            )

            self._breakers[service_name] = CircuitBreaker(service_name, breaker_config)

        return self._breakers[service_name]

    async def call_service(
        self,
        service_name: str,
        func: Callable,
        *args,
        config: Optional[CircuitBreakerConfig] = None,
        **kwargs,
    ) -> Any:
        """
        Call service through circuit breaker.

        Args:
            service_name: Service name
            func: Function to call
            *args: Function arguments
            config: Optional configuration
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        breaker = self.get_circuit_breaker(service_name, config)
        return await breaker.call(func, *args, **kwargs)

    def get_all_stats(self) -> dict[str, Any]:
        """Get statistics for all circuit breakers."""
        return {name: breaker.get_stats() for name, breaker in self._breakers.items()}

    async def reset_all(self):
        """Reset all circuit breakers."""
        for breaker in self._breakers.values():
            await breaker.reset()

        logger.info("All circuit breakers reset")

    def get_health_status(self) -> dict[str, Any]:
        """Get health status of all services."""
        healthy_services = []
        degraded_services = []
        failed_services = []

        for name, breaker in self._breakers.items():
            if breaker.state == CircuitState.CLOSED:
                healthy_services.append(name)
            elif breaker.state == CircuitState.HALF_OPEN:
                degraded_services.append(name)
            else:  # OPEN
                failed_services.append(name)

        total_services = len(self._breakers)
        healthy_count = len(healthy_services)

        overall_health = "healthy"
        if len(failed_services) > 0:
            if healthy_count == 0:
                overall_health = "critical"
            else:
                overall_health = "degraded"
        elif len(degraded_services) > 0:
            overall_health = "degraded"

        return {
            "overall_health": overall_health,
            "total_services": total_services,
            "healthy_services": healthy_services,
            "degraded_services": degraded_services,
            "failed_services": failed_services,
            "health_score": (
                healthy_count / total_services if total_services > 0 else 1.0
            ),
        }


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()


# Pre-configured circuit breakers for common services
def setup_default_circuit_breakers():
    """Setup default circuit breaker configurations."""

    # Portal da Transparência API
    circuit_breaker_manager.register_default_config(
        "transparency_api",
        CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0,
            success_threshold=2,
            timeout=15.0,
        ),
    )

    # LLM Services (Groq, etc)
    circuit_breaker_manager.register_default_config(
        "llm_service",
        CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60.0,
            success_threshold=3,
            timeout=30.0,
        ),
    )

    # Database connections
    circuit_breaker_manager.register_default_config(
        "database",
        CircuitBreakerConfig(
            failure_threshold=2, recovery_timeout=10.0, success_threshold=1, timeout=5.0
        ),
    )

    # Redis connections
    circuit_breaker_manager.register_default_config(
        "redis",
        CircuitBreakerConfig(
            failure_threshold=3, recovery_timeout=20.0, success_threshold=2, timeout=3.0
        ),
    )


# Initialize default configurations
setup_default_circuit_breakers()


# Convenience decorators
def circuit_breaker(service_name: str, config: Optional[CircuitBreakerConfig] = None):
    """
    Decorator to protect functions with circuit breaker.

    Args:
        service_name: Service name for circuit breaker
        config: Optional configuration
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await circuit_breaker_manager.call_service(
                service_name, func, *args, config=config, **kwargs
            )

        return wrapper

    return decorator


# Example usage functions
async def protected_api_call(url: str) -> dict:
    """Example of API call protected by circuit breaker."""
    import httpx

    async def make_request():
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    return await circuit_breaker_manager.call_service("external_api", make_request)
