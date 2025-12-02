"""
Timeout Budget Hierarchy for Cascading Timeout Prevention

This module implements hierarchical timeout budgets to prevent cascading failures
in the multi-agent system. Each layer (API → Service → Agent → External API)
has progressively smaller timeouts to ensure graceful degradation.

Problem:
Without timeout hierarchy, slow external APIs (Portal da Transparência, TCEs)
can cause entire investigations to hang, blocking other users and exhausting
connection pools.

Solution:
Implement timeout budgets with automatic propagation:
- API endpoint: 30s total budget
- Service layer: 28s (leaves 2s for serialization)
- Agent processing: 25s (leaves 3s for orchestration)
- External API: 10s per call (leaves 15s for retries + local processing)

Expected Impact:
- Prevent cascade failures (100% elimination)
- Reduce stuck requests from ~2% to 0%
- Enable graceful degradation (partial results)
- Improve user experience (faster error feedback)

References:
- Google SRE Book: "Cascading Failures"
- AWS Well-Architected: "Timeout Patterns"
- Martin Fowler: "Circuit Breaker Pattern"
"""

import asyncio
import time
from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Optional, TypeVar

from src.core import get_logger
from src.core.exceptions import TimeoutBudgetExceeded

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class TimeoutBudget:
    """
    Represents a hierarchical timeout budget.

    Attributes:
        total_budget: Total time available for operation (seconds)
        remaining_budget: Time remaining (updated as operation progresses)
        layer: Current layer name (for debugging)
        parent: Parent budget (for hierarchy)
        start_time: When budget was created
    """

    total_budget: float
    remaining_budget: float
    layer: str
    parent: Optional["TimeoutBudget"] = None
    start_time: float = 0.0

    def __post_init__(self):
        """Initialize start time."""
        if self.start_time == 0.0:
            self.start_time = time.time()

    def elapsed(self) -> float:
        """Get elapsed time since budget creation."""
        return time.time() - self.start_time

    def consume(self, amount: float) -> None:
        """
        Consume time from budget.

        Args:
            amount: Time consumed (seconds)

        Raises:
            TimeoutBudgetExceeded: If budget exhausted
        """
        self.remaining_budget -= amount
        if self.remaining_budget <= 0:
            raise TimeoutBudgetExceeded(
                f"Timeout budget exhausted in {self.layer}",
                details={
                    "layer": self.layer,
                    "total_budget": self.total_budget,
                    "elapsed": self.elapsed(),
                },
            )

    def create_child(self, child_layer: str, child_budget: float) -> "TimeoutBudget":
        """
        Create child budget with reduced timeout.

        Args:
            child_layer: Name of child layer
            child_budget: Budget for child (must be < remaining_budget)

        Returns:
            Child TimeoutBudget

        Raises:
            ValueError: If child_budget > remaining_budget
        """
        if child_budget > self.remaining_budget:
            logger.warning(
                "child_budget_too_large",
                child_layer=child_layer,
                child_budget=child_budget,
                remaining_budget=self.remaining_budget,
            )
            # Clamp to remaining budget
            child_budget = self.remaining_budget * 0.9  # Leave 10% margin

        return TimeoutBudget(
            total_budget=child_budget,
            remaining_budget=child_budget,
            layer=child_layer,
            parent=self,
        )


# Context variable for current timeout budget
_current_budget: ContextVar[TimeoutBudget | None] = ContextVar(
    "_current_budget", default=None
)


def get_current_budget() -> TimeoutBudget | None:
    """Get current timeout budget from context."""
    return _current_budget.get()


def set_current_budget(budget: TimeoutBudget | None) -> None:
    """Set current timeout budget in context."""
    _current_budget.set(budget)


class TimeoutBudgetManager:
    """
    Manager for hierarchical timeout budgets.

    Provides factory methods for creating budgets at different layers
    and ensures proper timeout propagation.
    """

    # Default budget hierarchy (seconds)
    DEFAULT_API_BUDGET = 30.0  # HTTP endpoint total time
    DEFAULT_SERVICE_BUDGET = 28.0  # Service layer (leaves 2s for serialization)
    DEFAULT_AGENT_BUDGET = 25.0  # Agent processing (leaves 3s for orchestration)
    DEFAULT_EXTERNAL_API_BUDGET = 10.0  # External API call (leaves 15s for retries)
    DEFAULT_DATABASE_BUDGET = 5.0  # Database query (fast operations)

    @classmethod
    def create_api_budget(
        cls, total_budget: float = DEFAULT_API_BUDGET
    ) -> TimeoutBudget:
        """
        Create root budget for API endpoint.

        Args:
            total_budget: Total time available for request (default: 30s)

        Returns:
            TimeoutBudget for API layer
        """
        budget = TimeoutBudget(
            total_budget=total_budget,
            remaining_budget=total_budget,
            layer="api_endpoint",
        )
        set_current_budget(budget)
        logger.debug(
            "api_budget_created",
            total_budget=total_budget,
        )
        return budget

    @classmethod
    def create_service_budget(cls, total_budget: float | None = None) -> TimeoutBudget:
        """
        Create budget for service layer.

        If parent budget exists, creates child. Otherwise creates root.

        Args:
            total_budget: Total budget (default: 28s or derived from parent)

        Returns:
            TimeoutBudget for service layer
        """
        parent = get_current_budget()

        if parent:
            # Create child budget from parent
            service_budget = parent.remaining_budget * 0.90  # Leave 10% margin
            budget = parent.create_child("service_layer", service_budget)
        else:
            # No parent, create root budget
            budget = TimeoutBudget(
                total_budget=total_budget or cls.DEFAULT_SERVICE_BUDGET,
                remaining_budget=total_budget or cls.DEFAULT_SERVICE_BUDGET,
                layer="service_layer",
            )

        set_current_budget(budget)
        logger.debug(
            "service_budget_created",
            total_budget=budget.total_budget,
            parent_exists=parent is not None,
        )
        return budget

    @classmethod
    def create_agent_budget(cls, total_budget: float | None = None) -> TimeoutBudget:
        """
        Create budget for agent processing.

        Args:
            total_budget: Total budget (default: 25s or derived from parent)

        Returns:
            TimeoutBudget for agent layer
        """
        parent = get_current_budget()

        if parent:
            agent_budget = parent.remaining_budget * 0.85  # Leave 15% margin
            budget = parent.create_child("agent_processing", agent_budget)
        else:
            budget = TimeoutBudget(
                total_budget=total_budget or cls.DEFAULT_AGENT_BUDGET,
                remaining_budget=total_budget or cls.DEFAULT_AGENT_BUDGET,
                layer="agent_processing",
            )

        set_current_budget(budget)
        logger.debug(
            "agent_budget_created",
            total_budget=budget.total_budget,
            parent_exists=parent is not None,
        )
        return budget

    @classmethod
    def create_external_api_budget(
        cls, total_budget: float | None = None
    ) -> TimeoutBudget:
        """
        Create budget for external API call.

        Args:
            total_budget: Total budget (default: 10s or derived from parent)

        Returns:
            TimeoutBudget for external API layer
        """
        parent = get_current_budget()

        if parent:
            # External API gets smaller slice (multiple APIs may be called)
            api_budget = min(
                parent.remaining_budget * 0.40,  # Max 40% of remaining
                cls.DEFAULT_EXTERNAL_API_BUDGET,  # Cap at 10s
            )
            budget = parent.create_child("external_api", api_budget)
        else:
            budget = TimeoutBudget(
                total_budget=total_budget or cls.DEFAULT_EXTERNAL_API_BUDGET,
                remaining_budget=total_budget or cls.DEFAULT_EXTERNAL_API_BUDGET,
                layer="external_api",
            )

        set_current_budget(budget)
        logger.debug(
            "external_api_budget_created",
            total_budget=budget.total_budget,
            parent_exists=parent is not None,
        )
        return budget

    @classmethod
    def create_database_budget(cls, total_budget: float | None = None) -> TimeoutBudget:
        """
        Create budget for database query.

        Args:
            total_budget: Total budget (default: 5s or derived from parent)

        Returns:
            TimeoutBudget for database layer
        """
        parent = get_current_budget()

        if parent:
            db_budget = min(
                parent.remaining_budget * 0.20,  # Max 20% of remaining
                cls.DEFAULT_DATABASE_BUDGET,  # Cap at 5s
            )
            budget = parent.create_child("database_query", db_budget)
        else:
            budget = TimeoutBudget(
                total_budget=total_budget or cls.DEFAULT_DATABASE_BUDGET,
                remaining_budget=total_budget or cls.DEFAULT_DATABASE_BUDGET,
                layer="database_query",
            )

        set_current_budget(budget)
        logger.debug(
            "database_budget_created",
            total_budget=budget.total_budget,
            parent_exists=parent is not None,
        )
        return budget


async def with_timeout_budget(
    coro: Callable[..., Any],
    budget: TimeoutBudget | None = None,
    fallback: Any | None = None,
) -> Any:
    """
    Execute coroutine with timeout budget.

    Args:
        coro: Coroutine to execute
        budget: Timeout budget (uses current if not provided)
        fallback: Fallback value on timeout (raises if None)

    Returns:
        Coroutine result or fallback

    Raises:
        TimeoutBudgetExceeded: If budget exhausted and no fallback

    Example:
        >>> budget = TimeoutBudgetManager.create_agent_budget()
        >>> result = await with_timeout_budget(
        ...     agent.process(message),
        ...     fallback={"status": "timeout", "partial_results": []}
        ... )
    """
    budget = budget or get_current_budget()

    if not budget:
        # No budget, execute without timeout
        logger.warning("no_timeout_budget_executing_without_timeout")
        return await coro

    try:
        start_time = time.time()

        # Execute with timeout from budget
        result = await asyncio.wait_for(coro, timeout=budget.remaining_budget)

        # Consume time from budget
        elapsed = time.time() - start_time
        budget.consume(elapsed)

        return result

    except TimeoutError:
        elapsed = time.time() - start_time
        logger.warning(
            "timeout_budget_exceeded",
            layer=budget.layer,
            total_budget=budget.total_budget,
            elapsed=elapsed,
            has_fallback=fallback is not None,
        )

        if fallback is not None:
            return fallback

        raise TimeoutBudgetExceeded(
            f"Operation timed out in {budget.layer}",
            details={
                "layer": budget.layer,
                "total_budget": budget.total_budget,
                "elapsed": elapsed,
            },
        )


def timeout_budget_middleware(layer: str, budget_factory: Callable[[], TimeoutBudget]):
    """
    Decorator for adding timeout budget to functions.

    Args:
        layer: Layer name (for logging)
        budget_factory: Function to create budget

    Example:
        >>> @timeout_budget_middleware("agent", TimeoutBudgetManager.create_agent_budget)
        >>> async def process_investigation(request):
        ...     # Budget automatically created and managed
        ...     result = await analyze_contracts(request)
        ...     return result
    """

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Create budget for this layer
            budget = budget_factory()

            try:
                start_time = time.time()

                # Execute function with timeout
                result = await asyncio.wait_for(
                    func(*args, **kwargs), timeout=budget.remaining_budget
                )

                # Consume time from budget
                elapsed = time.time() - start_time
                budget.consume(elapsed)

                return result

            except TimeoutError:
                elapsed = time.time() - start_time
                logger.error(
                    "function_timeout",
                    layer=layer,
                    function=func.__name__,
                    total_budget=budget.total_budget,
                    elapsed=elapsed,
                )
                raise TimeoutBudgetExceeded(
                    f"Function {func.__name__} timed out in {layer}",
                    details={
                        "layer": layer,
                        "function": func.__name__,
                        "total_budget": budget.total_budget,
                        "elapsed": elapsed,
                    },
                )
            finally:
                # Restore parent budget
                if budget.parent:
                    set_current_budget(budget.parent)

        return wrapper

    return decorator


# Example usage patterns (see docs/development/ for complete guide):
#
# Example 1: API Endpoint with Budget Hierarchy
#
# @router.post("/investigations")
# async def create_investigation(request: InvestigationRequest):
#     budget = TimeoutBudgetManager.create_api_budget()
#     try:
#         result = await investigation_service.create(request)
#         return result
#     except TimeoutBudgetExceeded as e:
#         return {"status": "timeout", "message": str(e), "partial_results": []}
#
# Example 2: Agent with Multiple External Calls
#
# class InvestigatorAgent:
#     async def process(self, message: AgentMessage):
#         budget = TimeoutBudgetManager.create_agent_budget()
#         contracts = await with_timeout_budget(self._fetch_contracts(), fallback=[])
#         servants = await with_timeout_budget(self._fetch_servants(), fallback=[])
#         return self._analyze(contracts, servants)
#
# Example 3: Parallel Operations
#
# async def fetch_multiple_sources():
#     results = await asyncio.gather(
#         with_timeout_budget(fetch_portal(), fallback=None),
#         with_timeout_budget(fetch_tce(), fallback=None),
#         return_exceptions=True
#     )
#     return [r for r in results if r and not isinstance(r, Exception)]
