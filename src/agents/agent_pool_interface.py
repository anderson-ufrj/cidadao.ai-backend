"""
Agent Pool Interface

Defines the common interface for agent pool implementations.
This allows different pooling strategies while maintaining a consistent API.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class AgentPoolInterface(ABC):
    """
    Abstract base class for agent pool implementations.

    This interface defines the minimal contract that all agent pool
    implementations must fulfill, allowing for different pooling
    strategies while maintaining API consistency.

    Implementations:
    - SimpleAgentPool: Direct agent instance management with acquire/release
    - DistributedAgentPool: Task-based execution with queue management
    """

    @abstractmethod
    async def start(self) -> None:
        """
        Start the pool and initialize resources.

        This should set up any background tasks, connections,
        or resources needed for the pool to operate.

        Raises:
            RuntimeError: If pool is already started
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        Stop the pool and cleanup resources.

        This should gracefully shutdown all background tasks,
        release agents, and cleanup resources.
        """
        pass

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """
        Get pool statistics and metrics.

        Returns:
            Dictionary containing pool statistics such as:
            - Number of active agents
            - Number of idle agents
            - Task counts
            - Performance metrics
        """
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check on the pool.

        Returns:
            Dictionary containing health status:
            - healthy: bool
            - message: Optional[str]
            - details: dict[str, Any]
        """
        pass


class SimplePoolInterface(AgentPoolInterface):
    """
    Interface for simple agent pool implementations.

    This extends the base interface with direct agent acquisition
    and release methods for simple pooling strategies.
    """

    @abstractmethod
    async def acquire(self, agent_type: type, context: Any) -> Any:
        """
        Acquire an agent instance from the pool.

        Args:
            agent_type: Type of agent to acquire
            context: Agent context for initialization

        Returns:
            Agent instance

        Raises:
            PoolExhaustedError: If no agents available and max size reached
        """
        pass

    @abstractmethod
    async def prewarm(self, agent_types: list[type]) -> None:
        """
        Pre-create agent instances for faster acquisition.

        Args:
            agent_types: List of agent types to pre-create
        """
        pass


class DistributedPoolInterface(AgentPoolInterface):
    """
    Interface for distributed agent pool implementations.

    This extends the base interface with task submission
    and result retrieval for distributed execution.
    """

    @abstractmethod
    async def submit_task(
        self,
        agent_type: str,
        method: str,
        *args,
        priority: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Submit a task for execution.

        Args:
            agent_type: Type of agent to execute task
            method: Method name to call on agent
            *args: Positional arguments for method
            priority: Task priority (high, normal, low)
            **kwargs: Keyword arguments for method

        Returns:
            Task ID for result retrieval
        """
        pass

    @abstractmethod
    async def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        Get the result of a submitted task.

        Args:
            task_id: Task identifier from submit_task
            timeout: Optional timeout in seconds

        Returns:
            Task result

        Raises:
            TaskNotFoundError: If task ID is invalid
            TaskTimeoutError: If timeout is reached
        """
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the distributed pool.

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """
        Shutdown the distributed pool.

        Alias for stop() in distributed implementations.
        """
        pass
