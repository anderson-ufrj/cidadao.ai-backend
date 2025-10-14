"""
Circuit Breaker Pattern

Prevents cascading failures by monitoring API health and blocking calls to failing services.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

import asyncio
import time
from collections.abc import Callable
from enum import Enum
from typing import Any

from src.core import get_logger

logger = get_logger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation, requests pass through
    OPEN = "open"  # Circuit is open, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker for API calls.

    States:
    - CLOSED: Normal operation, all requests pass through
    - OPEN: Too many failures, requests blocked immediately
    - HALF_OPEN: Testing recovery, limited requests allowed

    Transitions:
    - CLOSED → OPEN: When failure threshold exceeded
    - OPEN → HALF_OPEN: After timeout period
    - HALF_OPEN → CLOSED: When success threshold met
    - HALF_OPEN → OPEN: When test request fails
    """

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: int = 60,
        half_open_max_calls: int = 3,
    ) -> None:
        """
        Initialize circuit breaker.

        Args:
            name: Name of the service/API
            failure_threshold: Number of failures before opening circuit
            success_threshold: Successes needed in half-open to close
            timeout_seconds: Time to wait before trying half-open
            half_open_max_calls: Max calls allowed in half-open state
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_max_calls = half_open_max_calls

        # State management
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.last_failure_time: float | None = None
        self.opened_at: float | None = None

        # Thread safety
        self._lock = asyncio.Lock()

        self.logger = get_logger(__name__)

    async def call(
        self, func: Callable, *args: Any, **kwargs: Any  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        """
        Execute function through circuit breaker.

        Args:
            func: Function to execute (can be async or sync)
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: When circuit is open
        """
        async with self._lock:
            # Check if we should allow this call
            if not await self._can_execute():
                self.logger.warning(
                    f"Circuit breaker {self.name} is OPEN, blocking call"
                )
                raise CircuitBreakerOpenError(
                    f"Circuit breaker {self.name} is open, service unavailable"
                )

        # Execute the call
        try:
            # Handle both async and sync functions
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Record success
            await self._on_success()
            return result

        except Exception as e:
            # Record failure
            await self._on_failure()
            raise e

    async def _can_execute(self) -> bool:
        """Check if call should be allowed."""

        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if (
                self.opened_at
                and (time.time() - self.opened_at) >= self.timeout_seconds
            ):
                self.logger.info(
                    f"Circuit breaker {self.name} timeout passed, "
                    f"transitioning to HALF_OPEN"
                )
                await self._transition_to_half_open()
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            # Allow limited number of test calls
            if self.half_open_calls < self.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False

        return False

    async def _on_success(self) -> None:
        """Handle successful call."""
        async with self._lock:
            if self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0

            elif self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                self.logger.debug(
                    f"Circuit breaker {self.name} success in HALF_OPEN: "
                    f"{self.success_count}/{self.success_threshold}"
                )

                # Check if we can close the circuit
                if self.success_count >= self.success_threshold:
                    await self._transition_to_closed()

    async def _on_failure(self) -> None:
        """Handle failed call."""
        async with self._lock:
            self.last_failure_time = time.time()

            if self.state == CircuitState.CLOSED:
                self.failure_count += 1
                self.logger.warning(
                    f"Circuit breaker {self.name} failure: "
                    f"{self.failure_count}/{self.failure_threshold}"
                )

                # Check if we should open the circuit
                if self.failure_count >= self.failure_threshold:
                    await self._transition_to_open()

            elif self.state == CircuitState.HALF_OPEN:
                # Failed during recovery test, reopen circuit
                self.logger.warning(
                    f"Circuit breaker {self.name} failed in HALF_OPEN, "
                    f"reopening circuit"
                )
                await self._transition_to_open()

    async def _transition_to_open(self) -> None:
        """Transition to OPEN state."""
        self.state = CircuitState.OPEN
        self.opened_at = time.time()
        self.logger.error(
            f"Circuit breaker {self.name} OPENED after "
            f"{self.failure_count} failures"
        )

    async def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        self.state = CircuitState.HALF_OPEN
        self.half_open_calls = 0
        self.success_count = 0
        self.logger.info(
            f"Circuit breaker {self.name} entering HALF_OPEN state for recovery test"
        )

    async def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.opened_at = None
        self.logger.info(f"Circuit breaker {self.name} CLOSED, service recovered")

    def get_status(self) -> dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "opened_at": self.opened_at,
            "time_in_open": (time.time() - self.opened_at if self.opened_at else None),
        }

    async def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state."""
        async with self._lock:
            await self._transition_to_closed()
            self.logger.info(f"Circuit breaker {self.name} manually reset")


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.

    Maintains one circuit breaker per API/service.
    """

    def __init__(self) -> None:
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()
        self.logger = get_logger(__name__)

    async def get_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
    ) -> CircuitBreaker:
        """
        Get or create circuit breaker for a service.

        Args:
            name: Service/API name
            failure_threshold: Failures before opening
            timeout_seconds: Time before trying recovery

        Returns:
            CircuitBreaker instance
        """
        async with self._lock:
            if name not in self._breakers:
                breaker = CircuitBreaker(
                    name=name,
                    failure_threshold=failure_threshold,
                    timeout_seconds=timeout_seconds,
                )
                self._breakers[name] = breaker
                self.logger.info(f"Created circuit breaker for {name}")

            return self._breakers[name]

    def get_all_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all circuit breakers."""
        return {name: breaker.get_status() for name, breaker in self._breakers.items()}

    async def reset_all(self) -> None:
        """Reset all circuit breakers."""
        for breaker in self._breakers.values():
            await breaker.reset()
        self.logger.info("All circuit breakers reset")
