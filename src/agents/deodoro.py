"""
Module: agents.deodoro
Codinome: Deodoro da Fonseca - Fundador da Arquitetura Multi-Agente
Description: Base agent class for all Cidadão.AI agents
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel
from pydantic import Field as PydanticField

from src.core import AgentStatus, get_logger
from src.core.exceptions import AgentExecutionError
from src.infrastructure.observability.metrics import BusinessMetrics, metrics_manager


@dataclass
class AgentContext:
    """Context shared between agents."""

    investigation_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str | None = None
    session_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    memory_context: dict[str, Any] = field(default_factory=dict)
    parent_agent: str | None = None
    trace_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "investigation_id": self.investigation_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "memory_context": self.memory_context,
            "parent_agent": self.parent_agent,
            "trace_id": self.trace_id,
        }


class AgentMessage(BaseModel):
    """Message passed between agents."""

    sender: str = PydanticField(..., description="Agent that sent the message")
    recipient: str = PydanticField(
        ..., description="Agent that should receive the message"
    )
    action: str = PydanticField(..., description="Action to perform")
    payload: dict[str, Any] = PydanticField(
        default_factory=dict, description="Message payload"
    )
    context: dict[str, Any] = PydanticField(
        default_factory=dict, description="Message context"
    )
    timestamp: datetime = PydanticField(default_factory=datetime.utcnow)
    message_id: str = PydanticField(default_factory=lambda: str(uuid4()))
    requires_response: bool = PydanticField(
        default=True, description="Whether response is expected"
    )


class AgentResponse(BaseModel):
    """Response from an agent."""

    agent_name: str = PydanticField(..., description="Name of the responding agent")
    status: AgentStatus = PydanticField(..., description="Agent status")
    result: Any | None = PydanticField(default=None, description="Result of the action")
    error: str | None = PydanticField(
        default=None, description="Error message if failed"
    )
    metadata: dict[str, Any] = PydanticField(
        default_factory=dict, description="Response metadata"
    )
    timestamp: datetime = PydanticField(default_factory=datetime.utcnow)
    processing_time_ms: float | None = PydanticField(
        default=None, description="Processing time"
    )


class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        description: str,
        capabilities: list[str],
        max_retries: int = 3,
        timeout: int = 60,
    ) -> None:
        """
        Initialize base agent.

        Args:
            name: Agent name
            description: Agent description
            capabilities: List of agent capabilities
            max_retries: Maximum number of retries
            timeout: Timeout in seconds
        """
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.max_retries = max_retries
        self.timeout = timeout
        self.status = AgentStatus.IDLE
        self.logger = get_logger(f"agent.{name}")
        self._message_history: list[AgentMessage] = []
        self._response_history: list[AgentResponse] = []
        self._metadata: dict[str, Any] = {}
        self._start_time = datetime.utcnow()

        self.logger.info(
            "agent_initialized",
            agent_name=self.name,
            capabilities=self.capabilities,
        )

    @abstractmethod
    async def process(
        self,
        message: AgentMessage,
        context: AgentContext,
    ) -> AgentResponse:
        """
        Process a message and return a response.

        Args:
            message: Message to process
            context: Agent context

        Returns:
            Agent response

        Raises:
            AgentExecutionError: If processing fails
        """
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize agent resources."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Cleanup agent resources."""
        pass

    async def execute(
        self,
        action: str,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> AgentResponse:
        """
        Execute an action with retry logic.

        Args:
            action: Action to execute
            payload: Action payload
            context: Agent context

        Returns:
            Agent response
        """
        message = AgentMessage(
            sender=context.parent_agent or "system",
            recipient=self.name,
            action=action,
            payload=payload,
            context=context.to_dict(),
        )

        start_time = datetime.utcnow()
        retries = 0
        last_error = None

        # Increment task counter using metrics manager
        metrics_manager.increment_counter(
            "cidadao_ai_agent_tasks_total",
            labels={
                "agent_name": self.name,
                "task_type": action,
                "status": "started",
            },
        )

        while retries <= self.max_retries:
            try:
                self.status = AgentStatus.THINKING
                self.logger.info(
                    "agent_executing",
                    agent_name=self.name,
                    action=action,
                    retry=retries,
                )

                # Process the message
                response = await self.process(message, context)

                # Calculate processing time
                processing_time = (
                    datetime.utcnow() - start_time
                ).total_seconds() * 1000
                response.processing_time_ms = processing_time

                # Record metrics using centralized metrics manager
                metrics_manager.increment_counter(
                    "cidadao_ai_agent_tasks_total",
                    labels={
                        "agent_name": self.name,
                        "task_type": action,
                        "status": "completed",
                    },
                )

                BusinessMetrics.record_agent_task(
                    agent_name=self.name,
                    task_type=action,
                    duration_seconds=processing_time / 1000.0,
                    status="success",
                )

                # Update status
                self.status = AgentStatus.COMPLETED

                # Store in history
                self._message_history.append(message)
                self._response_history.append(response)

                self.logger.info(
                    "agent_execution_completed",
                    agent_name=self.name,
                    action=action,
                    processing_time_ms=processing_time,
                )

                return response

            except Exception as e:
                last_error = str(e)
                self.logger.error(
                    "agent_execution_failed",
                    agent_name=self.name,
                    action=action,
                    error=last_error,
                    retry=retries,
                )

                # Record retry attempt
                metrics_manager.increment_counter(
                    "cidadao_ai_agent_tasks_total",
                    labels={
                        "agent_name": self.name,
                        "task_type": action,
                        "status": "retry",
                    },
                )

                retries += 1
                if retries <= self.max_retries:
                    # Exponential backoff
                    await self._wait(2**retries)

        # All retries exhausted - record failure
        metrics_manager.increment_counter(
            "cidadao_ai_agent_tasks_total",
            labels={"agent_name": self.name, "task_type": action, "status": "failed"},
        )

        BusinessMetrics.record_agent_task(
            agent_name=self.name,
            task_type=action,
            duration_seconds=(datetime.utcnow() - start_time).total_seconds(),
            status="failed",
        )

        self.status = AgentStatus.ERROR

        error_response = AgentResponse(
            agent_name=self.name,
            status=AgentStatus.ERROR,
            error=f"Failed after {self.max_retries} retries: {last_error}",
            metadata={"action": action, "retries": retries},
        )

        self._response_history.append(error_response)

        raise AgentExecutionError(
            f"Agent {self.name} failed to execute {action}: {last_error}",
            details={"agent": self.name, "action": action, "error": last_error},
        )

    async def _wait(self, seconds: float) -> None:
        """Wait for specified seconds (async-friendly)."""
        import asyncio

        await asyncio.sleep(seconds)

    def can_handle(self, action: str) -> bool:
        """
        Check if agent can handle the given action.

        Args:
            action: Action to check

        Returns:
            True if agent can handle the action
        """
        return action in self.capabilities

    def get_status(self) -> dict[str, Any]:
        """Get agent status information."""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "message_count": len(self._message_history),
            "response_count": len(self._response_history),
        }

    def get_history(self, limit: int | None = None) -> dict[str, list[dict[str, Any]]]:
        """
        Get agent message and response history.

        Args:
            limit: Maximum number of entries to return

        Returns:
            Dictionary with message and response history
        """
        if limit is None:
            messages = self._message_history
            responses = self._response_history
        elif limit == 0:
            messages = []
            responses = []
        else:
            messages = self._message_history[-limit:]
            responses = self._response_history[-limit:]

        return {
            "messages": [msg.model_dump() for msg in messages],
            "responses": [resp.model_dump() for resp in responses],
        }

    def clear_history(self) -> None:
        """Clear agent history."""
        self._message_history.clear()
        self._response_history.clear()
        self.logger.info("agent_history_cleared", agent_name=self.name)

    def has_capability(self, capability: str) -> bool:
        """
        Check if agent has a specific capability.

        Args:
            capability: Capability to check

        Returns:
            True if agent has the capability
        """
        return capability in self.capabilities

    def set_status(self, status: AgentStatus) -> None:
        """
        Set agent status.

        Args:
            status: New agent status
        """
        self.status = status
        self.logger.debug(
            "agent_status_changed", agent_name=self.name, status=status.value
        )

    def set_metadata(self, key: str, value: Any) -> None:  # noqa: ANN401
        """
        Set agent metadata value.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:  # noqa: ANN401
        """
        Get agent metadata value.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self._metadata.get(key, default)

    def update_metadata(self, metadata: dict[str, Any]) -> None:
        """
        Update multiple metadata values.

        Args:
            metadata: Dictionary of metadata to update
        """
        self._metadata.update(metadata)

    def health_check(self) -> dict[str, Any]:
        """
        Get agent health status.

        Returns:
            Dictionary with health information
        """
        uptime = (datetime.utcnow() - self._start_time).total_seconds()
        return {
            "status": "healthy" if self.status != AgentStatus.ERROR else "unhealthy",
            "name": self.name,
            "capabilities": self.capabilities,
            "uptime": uptime,
            "message_count": len(self._message_history),
            "response_count": len(self._response_history),
        }

    async def execute_with_timeout(
        self,
        message: AgentMessage,
        context: AgentContext,
    ) -> AgentResponse:
        """
        Execute message processing with timeout.

        Args:
            message: Message to process
            context: Agent context

        Returns:
            Agent response

        Raises:
            AgentExecutionError: If execution times out or fails
        """
        import asyncio

        try:
            return await asyncio.wait_for(
                self.process(message, context),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError as e:
            self.status = AgentStatus.ERROR
            raise AgentExecutionError(
                f"Agent {self.name} execution timed out after {self.timeout}s",
                details={"agent": self.name, "timeout": self.timeout},
            ) from e

    def __repr__(self) -> str:
        """String representation of agent."""
        return f"<{self.__class__.__name__}(name='{self.name}', status={self.status.value})>"


class ReflectiveAgent(BaseAgent):
    """Base class for agents with reflection capabilities."""

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        description: str,
        capabilities: list[str],
        reflection_threshold: float = 0.7,
        max_reflection_loops: int = 3,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """
        Initialize reflective agent.

        Args:
            name: Agent name
            description: Agent description
            capabilities: List of capabilities
            reflection_threshold: Minimum quality threshold
            max_reflection_loops: Maximum reflection iterations
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__(name, description, capabilities, **kwargs)
        self.reflection_threshold = reflection_threshold
        self.max_reflection_loops = max_reflection_loops
        # Alias for backwards compatibility with tests
        self.max_reflection_iterations = max_reflection_loops

    def _needs_reflection(self, result: dict[str, Any]) -> bool:
        """
        Check if result needs reflection based on quality assessment.

        Args:
            result: Result to assess

        Returns:
            True if result needs reflection
        """
        quality = self._assess_result_quality(result)
        return quality < self.reflection_threshold

    def _assess_result_quality(self, result: dict[str, Any]) -> float:
        """
        Assess the quality of a result.

        Args:
            result: Result to assess

        Returns:
            Quality score between 0 and 1
        """
        # Default implementation returns 1.0 (perfect quality)
        # Subclasses should override this method
        return result.get("quality", 1.0)

    @abstractmethod
    async def reflect(
        self,
        result: Any,  # noqa: ANN401
        context: AgentContext,
    ) -> dict[str, Any]:
        """
        Reflect on the result and provide quality assessment.

        Args:
            result: Result to reflect on
            context: Agent context

        Returns:
            Reflection result with quality score and improvements
        """
        pass

    async def process_with_reflection(
        self,
        message: AgentMessage,
        context: AgentContext,
    ) -> AgentResponse:
        """
        Process message with reflection loop.

        Args:
            message: Message to process
            context: Agent context

        Returns:
            Agent response after reflection
        """
        reflection_count = 0
        current_result = None

        while reflection_count < self.max_reflection_loops:
            # Process the message
            if reflection_count == 0:
                current_result = await self.process(message, context)
            else:
                # Modify message based on reflection feedback
                message_data = message.model_dump()
                message_data["payload"] = {
                    **message.payload,
                    "reflection_feedback": current_result.metadata.get(
                        "reflection", {}
                    ),
                    "reflection_iteration": reflection_count,
                }
                reflected_message = AgentMessage(**message_data)
                current_result = await self.process(reflected_message, context)

            # First check if current quality is already good enough
            if isinstance(current_result.result, dict):
                original_quality = self._assess_result_quality(current_result.result)
            else:
                original_quality = 0.0

            # If quality is already good, return without reflection
            if original_quality >= self.reflection_threshold:
                return current_result

            # Quality is low, perform reflection
            reflection = await self.reflect(current_result, context)
            quality_score = reflection.get("quality_score", 0.0)

            self.logger.info(
                "agent_reflection",
                agent_name=self.name,
                reflection_count=reflection_count,
                quality_score=quality_score,
            )

            # Apply improved result if available
            if "improved_result" in reflection:
                current_result.result = reflection["improved_result"]

            # Check if quality threshold is met after reflection
            if quality_score >= self.reflection_threshold:
                current_result.metadata["reflection"] = reflection
                current_result.metadata["reflection_count"] = reflection_count + 1
                return current_result

            # Store reflection feedback for next iteration
            current_result.metadata["reflection"] = reflection
            reflection_count += 1

        # Max reflections reached
        self.logger.warning(
            "max_reflections_reached",
            agent_name=self.name,
            reflection_count=reflection_count,
        )

        current_result.metadata["max_reflections_reached"] = True
        return current_result
