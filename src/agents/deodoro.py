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
from typing import Any, Dict, List, Optional, Type
from uuid import uuid4

from pydantic import BaseModel, Field as PydanticField

from src.core import AgentStatus, get_logger
from src.core.exceptions import AgentError, AgentExecutionError
from src.core.monitoring import AGENT_TASK_COUNT, AGENT_TASK_DURATION
import time


@dataclass
class AgentContext:
    """Context shared between agents."""
    
    investigation_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    memory_context: Dict[str, Any] = field(default_factory=dict)
    parent_agent: Optional[str] = None
    trace_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
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
    recipient: str = PydanticField(..., description="Agent that should receive the message")
    action: str = PydanticField(..., description="Action to perform")
    payload: Dict[str, Any] = PydanticField(default_factory=dict, description="Message payload")
    context: Dict[str, Any] = PydanticField(default_factory=dict, description="Message context")
    timestamp: datetime = PydanticField(default_factory=datetime.utcnow)
    message_id: str = PydanticField(default_factory=lambda: str(uuid4()))
    requires_response: bool = PydanticField(default=True, description="Whether response is expected")


class AgentResponse(BaseModel):
    """Response from an agent."""
    
    agent_name: str = PydanticField(..., description="Name of the responding agent")
    status: AgentStatus = PydanticField(..., description="Agent status")
    result: Optional[Any] = PydanticField(default=None, description="Result of the action")
    error: Optional[str] = PydanticField(default=None, description="Error message if failed")
    metadata: Dict[str, Any] = PydanticField(default_factory=dict, description="Response metadata")
    timestamp: datetime = PydanticField(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = PydanticField(default=None, description="Processing time")


class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""
    
    def __init__(
        self,
        name: str,
        description: str,
        capabilities: List[str],
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
        self._message_history: List[AgentMessage] = []
        self._response_history: List[AgentResponse] = []
        
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
        payload: Dict[str, Any],
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
        perf_start_time = time.time()
        retries = 0
        last_error = None
        
        # Increment task counter
        AGENT_TASK_COUNT.labels(
            agent_type=self.name,
            task_type=action,
            status="started"
        ).inc()
        
        while retries <= self.max_retries:
            try:
                self.status = AgentStatus.THINKING
                self.logger.info(
                    "agent_executing",
                    agent_name=self.name,
                    action=action,
                    retry=retries,
                )
                
                # Process the message with timing
                with AGENT_TASK_DURATION.labels(
                    agent_type=self.name,
                    task_type=action
                ).time():
                    response = await self.process(message, context)
                
                # Calculate processing time
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                response.processing_time_ms = processing_time
                
                # Record successful execution
                AGENT_TASK_COUNT.labels(
                    agent_type=self.name,
                    task_type=action,
                    status="completed"
                ).inc()
                
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
                AGENT_TASK_COUNT.labels(
                    agent_type=self.name,
                    task_type=action,
                    status="retry"
                ).inc()
                
                retries += 1
                if retries <= self.max_retries:
                    # Exponential backoff
                    await self._wait(2 ** retries)
        
        # All retries exhausted - record failure
        AGENT_TASK_COUNT.labels(
            agent_type=self.name,
            task_type=action,
            status="failed"
        ).inc()
        
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
            details={"agent": self.name, "action": action, "error": last_error}
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
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "message_count": len(self._message_history),
            "response_count": len(self._response_history),
        }
    
    def get_history(
        self,
        limit: Optional[int] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
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
    
    def __repr__(self) -> str:
        """String representation of agent."""
        return f"<{self.__class__.__name__}(name='{self.name}', status={self.status.value})>"


class ReflectiveAgent(BaseAgent):
    """Base class for agents with reflection capabilities."""
    
    def __init__(
        self,
        name: str,
        description: str,
        capabilities: List[str],
        reflection_threshold: float = 0.7,
        max_reflection_loops: int = 3,
        **kwargs: Any
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
    
    @abstractmethod
    async def reflect(
        self,
        result: Any,
        context: AgentContext,
    ) -> Dict[str, Any]:
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
                    "reflection_feedback": current_result.metadata.get("reflection", {}),
                    "reflection_iteration": reflection_count,
                }
                reflected_message = AgentMessage(**message_data)
                current_result = await self.process(reflected_message, context)
            
            # Reflect on the result
            reflection = await self.reflect(current_result, context)
            quality_score = reflection.get("quality_score", 0.0)
            
            self.logger.info(
                "agent_reflection",
                agent_name=self.name,
                reflection_count=reflection_count,
                quality_score=quality_score,
            )
            
            # Check if quality threshold is met
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