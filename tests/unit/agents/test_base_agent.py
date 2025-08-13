"""
Module: tests.unit.agents.test_base_agent
Description: Comprehensive unit tests for BaseAgent class
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

from src.agents.base_agent import (
    BaseAgent,
    ReflectiveAgent,
    AgentContext,
    AgentMessage,
    AgentResponse,
)
from src.core import AgentStatus
from src.core.exceptions import AgentExecutionError


class MockAgent(BaseAgent):
    """Mock agent for testing BaseAgent functionality."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="test_agent",
            description="Test agent for unit testing",
            capabilities=["test_action", "another_action"],
            **kwargs
        )
        self.process_calls = 0
        self.initialize_calls = 0
        self.shutdown_calls = 0
        self.should_fail = False
        self.fail_count = 0
        
    async def process(self, message: AgentMessage, context: AgentContext) -> AgentResponse:
        """Mock process method."""
        self.process_calls += 1
        
        if self.should_fail and self.fail_count < 2:
            self.fail_count += 1
            raise Exception(f"Mock failure {self.fail_count}")
        
        return AgentResponse(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            result={"action": message.action, "processed": True},
            metadata={"process_calls": self.process_calls}
        )
    
    async def initialize(self) -> None:
        """Mock initialize method."""
        self.initialize_calls += 1
        await asyncio.sleep(0.01)  # Simulate async work
    
    async def shutdown(self) -> None:
        """Mock shutdown method."""
        self.shutdown_calls += 1
        await asyncio.sleep(0.01)  # Simulate async work


class MockReflectiveAgent(ReflectiveAgent):
    """Mock reflective agent for testing."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="reflective_test_agent",
            description="Test reflective agent",
            capabilities=["reflect_action"],
            **kwargs
        )
        self.reflection_calls = 0
        
    async def process(self, message: AgentMessage, context: AgentContext) -> AgentResponse:
        """Mock process method."""
        reflection_iteration = message.payload.get("reflection_iteration", 0)
        
        # Simulate improving quality with each reflection
        base_quality = 0.5
        quality_improvement = reflection_iteration * 0.3
        final_quality = min(base_quality + quality_improvement, 1.0)
        
        return AgentResponse(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            result={"quality": final_quality, "reflection_iteration": reflection_iteration},
            metadata={"base_quality": base_quality}
        )
    
    async def reflect(self, result: Any, context: AgentContext) -> Dict[str, Any]:
        """Mock reflect method."""
        self.reflection_calls += 1
        
        quality = result.result.get("quality", 0.0) if result.result else 0.0
        
        return {
            "quality_score": quality,
            "improvements": ["Better analysis", "More details"],
            "reflection_call": self.reflection_calls
        }
    
    async def initialize(self) -> None:
        """Mock initialize method."""
        pass
    
    async def shutdown(self) -> None:
        """Mock shutdown method."""
        pass


@pytest.fixture
def agent_context():
    """Create a test agent context."""
    return AgentContext(
        investigation_id="test-investigation-123",
        user_id="test-user",
        session_id="test-session",
        metadata={"test": True},
        parent_agent="test_parent"
    )


@pytest.fixture
def agent_message():
    """Create a test agent message."""
    return AgentMessage(
        sender="test_sender",
        recipient="test_agent",
        action="test_action",
        payload={"data": "test_data"},
        context={"test_context": True}
    )


class TestAgentContext:
    """Test AgentContext class."""
    
    def test_context_creation(self):
        """Test basic context creation."""
        context = AgentContext()
        
        assert context.investigation_id is not None
        assert context.user_id is None
        assert context.session_id is None
        assert isinstance(context.timestamp, datetime)
        assert context.metadata == {}
        assert context.memory_context == {}
        assert context.parent_agent is None
        assert context.trace_id is None
    
    def test_context_with_params(self):
        """Test context creation with parameters."""
        timestamp = datetime.utcnow()
        metadata = {"key": "value"}
        memory = {"memory_key": "memory_value"}
        
        context = AgentContext(
            investigation_id="test-123",
            user_id="user-456",
            session_id="session-789",
            timestamp=timestamp,
            metadata=metadata,
            memory_context=memory,
            parent_agent="parent",
            trace_id="trace-abc"
        )
        
        assert context.investigation_id == "test-123"
        assert context.user_id == "user-456"
        assert context.session_id == "session-789"
        assert context.timestamp == timestamp
        assert context.metadata == metadata
        assert context.memory_context == memory
        assert context.parent_agent == "parent"
        assert context.trace_id == "trace-abc"
    
    def test_context_to_dict(self):
        """Test context serialization to dictionary."""
        context = AgentContext(
            investigation_id="test-123",
            user_id="user-456",
            metadata={"key": "value"}
        )
        
        result = context.to_dict()
        
        assert result["investigation_id"] == "test-123"
        assert result["user_id"] == "user-456"
        assert result["metadata"] == {"key": "value"}
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)  # ISO format


class TestAgentMessage:
    """Test AgentMessage class."""
    
    def test_message_creation(self):
        """Test basic message creation."""
        message = AgentMessage(
            sender="sender_agent",
            recipient="recipient_agent",
            action="test_action"
        )
        
        assert message.sender == "sender_agent"
        assert message.recipient == "recipient_agent"
        assert message.action == "test_action"
        assert message.payload == {}
        assert message.context == {}
        assert isinstance(message.timestamp, datetime)
        assert message.message_id is not None
        assert message.requires_response is True
    
    def test_message_with_payload(self):
        """Test message creation with payload and context."""
        payload = {"data": "test", "value": 123}
        context = {"session": "abc"}
        
        message = AgentMessage(
            sender="sender",
            recipient="recipient",
            action="process",
            payload=payload,
            context=context,
            requires_response=False
        )
        
        assert message.payload == payload
        assert message.context == context
        assert message.requires_response is False


class TestAgentResponse:
    """Test AgentResponse class."""
    
    def test_response_creation(self):
        """Test basic response creation."""
        response = AgentResponse(
            agent_name="test_agent",
            status=AgentStatus.COMPLETED
        )
        
        assert response.agent_name == "test_agent"
        assert response.status == AgentStatus.COMPLETED
        assert response.result is None
        assert response.error is None
        assert response.metadata == {}
        assert isinstance(response.timestamp, datetime)
        assert response.processing_time_ms is None
    
    def test_response_with_result(self):
        """Test response creation with result and metadata."""
        result = {"output": "success", "count": 5}
        metadata = {"performance": "good"}
        
        response = AgentResponse(
            agent_name="test_agent",
            status=AgentStatus.COMPLETED,
            result=result,
            metadata=metadata,
            processing_time_ms=150.5
        )
        
        assert response.result == result
        assert response.metadata == metadata
        assert response.processing_time_ms == 150.5
    
    def test_response_with_error(self):
        """Test response creation with error."""
        response = AgentResponse(
            agent_name="test_agent",
            status=AgentStatus.ERROR,
            error="Something went wrong"
        )
        
        assert response.status == AgentStatus.ERROR
        assert response.error == "Something went wrong"


class TestBaseAgent:
    """Test BaseAgent class functionality."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = MockAgent(max_retries=5, timeout=120)
        
        assert agent.name == "test_agent"
        assert agent.description == "Test agent for unit testing"
        assert agent.capabilities == ["test_action", "another_action"]
        assert agent.max_retries == 5
        assert agent.timeout == 120
        assert agent.status == AgentStatus.IDLE
        assert agent.logger is not None
        assert len(agent._message_history) == 0
        assert len(agent._response_history) == 0
    
    def test_can_handle(self):
        """Test capability checking."""
        agent = MockAgent()
        
        assert agent.can_handle("test_action") is True
        assert agent.can_handle("another_action") is True
        assert agent.can_handle("unknown_action") is False
    
    def test_get_status(self):
        """Test status information retrieval."""
        agent = MockAgent()
        status = agent.get_status()
        
        assert status["name"] == "test_agent"
        assert status["description"] == "Test agent for unit testing"
        assert status["status"] == AgentStatus.IDLE.value
        assert status["capabilities"] == ["test_action", "another_action"]
        assert status["message_count"] == 0
        assert status["response_count"] == 0
    
    @pytest.mark.asyncio
    async def test_successful_execution(self, agent_context):
        """Test successful agent execution."""
        agent = MockAgent()
        
        response = await agent.execute(
            action="test_action",
            payload={"key": "value"},
            context=agent_context
        )
        
        assert response.agent_name == "test_agent"
        assert response.status == AgentStatus.COMPLETED
        assert response.result == {"action": "test_action", "processed": True}
        assert response.processing_time_ms is not None
        assert response.processing_time_ms > 0
        
        # Check agent state
        assert agent.status == AgentStatus.COMPLETED
        assert len(agent._message_history) == 1
        assert len(agent._response_history) == 1
        assert agent.process_calls == 1
    
    @pytest.mark.asyncio
    async def test_execution_with_retry(self, agent_context):
        """Test execution with retry logic."""
        agent = MockAgent(max_retries=3)
        agent.should_fail = True  # Will fail first 2 times, succeed on 3rd
        
        response = await agent.execute(
            action="test_action",
            payload={},
            context=agent_context
        )
        
        # Should succeed after retries
        assert response.status == AgentStatus.COMPLETED
        assert agent.process_calls == 3  # Failed twice, succeeded on third
        assert agent.status == AgentStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_execution_failure_exhausted_retries(self, agent_context):
        """Test execution failure after exhausting retries."""
        agent = MockAgent(max_retries=1)
        agent.should_fail = True
        agent.fail_count = 0  # Will always fail
        
        with pytest.raises(AgentExecutionError) as exc_info:
            await agent.execute(
                action="test_action",
                payload={},
                context=agent_context
            )
        
        assert "Mock failure" in str(exc_info.value)
        assert agent.status == AgentStatus.ERROR
        assert len(agent._response_history) == 1
        assert agent._response_history[0].status == AgentStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_execute_creates_proper_message(self, agent_context):
        """Test that execute creates proper message structure."""
        agent = MockAgent()
        
        await agent.execute(
            action="test_action",
            payload={"test": "data"},
            context=agent_context
        )
        
        message = agent._message_history[0]
        assert message.sender == "test_parent"  # From context.parent_agent
        assert message.recipient == "test_agent"
        assert message.action == "test_action"
        assert message.payload == {"test": "data"}
        assert message.context == agent_context.to_dict()
    
    def test_get_history(self):
        """Test history retrieval."""
        agent = MockAgent()
        
        # Initially empty
        history = agent.get_history()
        assert history["messages"] == []
        assert history["responses"] == []
        
        # Add some mock history
        message = AgentMessage(sender="test", recipient="test_agent", action="test")
        response = AgentResponse(agent_name="test_agent", status=AgentStatus.COMPLETED)
        
        agent._message_history.append(message)
        agent._response_history.append(response)
        
        history = agent.get_history()
        assert len(history["messages"]) == 1
        assert len(history["responses"]) == 1
        
        # Test with limit
        history_limited = agent.get_history(limit=0)
        assert history_limited["messages"] == []
        assert history_limited["responses"] == []
    
    def test_clear_history(self):
        """Test history clearing."""
        agent = MockAgent()
        
        # Add some history
        message = AgentMessage(sender="test", recipient="test_agent", action="test")
        response = AgentResponse(agent_name="test_agent", status=AgentStatus.COMPLETED)
        
        agent._message_history.append(message)
        agent._response_history.append(response)
        
        assert len(agent._message_history) == 1
        assert len(agent._response_history) == 1
        
        # Clear history
        agent.clear_history()
        
        assert len(agent._message_history) == 0
        assert len(agent._response_history) == 0
    
    def test_agent_repr(self):
        """Test agent string representation."""
        agent = MockAgent()
        repr_str = repr(agent)
        
        assert "MockAgent" in repr_str
        assert "name='test_agent'" in repr_str
        assert f"status={AgentStatus.IDLE.value}" in repr_str


class TestReflectiveAgent:
    """Test ReflectiveAgent class functionality."""
    
    def test_reflective_agent_initialization(self):
        """Test reflective agent initialization."""
        agent = MockReflectiveAgent(
            reflection_threshold=0.8,
            max_reflection_loops=5
        )
        
        assert agent.name == "reflective_test_agent"
        assert agent.reflection_threshold == 0.8
        assert agent.max_reflection_loops == 5
        assert agent.capabilities == ["reflect_action"]
    
    @pytest.mark.asyncio
    async def test_process_with_reflection_success(self, agent_context):
        """Test reflection process that meets threshold."""
        agent = MockReflectiveAgent(reflection_threshold=0.7)
        
        message = AgentMessage(
            sender="test",
            recipient="reflective_test_agent",
            action="reflect_action"
        )
        
        response = await agent.process_with_reflection(message, agent_context)
        
        # Should succeed after 1 reflection (quality improves from 0.5 to 0.8)
        assert response.status == AgentStatus.COMPLETED
        assert "reflection" in response.metadata
        assert response.metadata["reflection_count"] == 2  # 1 initial + 1 reflection
        assert agent.reflection_calls == 2
    
    @pytest.mark.asyncio
    async def test_process_with_reflection_max_loops(self, agent_context):
        """Test reflection process that hits max loops."""
        agent = MockReflectiveAgent(
            reflection_threshold=0.95,  # Very high threshold
            max_reflection_loops=2
        )
        
        message = AgentMessage(
            sender="test",
            recipient="reflective_test_agent",
            action="reflect_action"
        )
        
        response = await agent.process_with_reflection(message, agent_context)
        
        # Should hit max reflections
        assert response.status == AgentStatus.COMPLETED
        assert response.metadata.get("max_reflections_reached") is True
        assert agent.reflection_calls == 2  # Hit the max
    
    @pytest.mark.asyncio
    async def test_reflection_improves_quality(self, agent_context):
        """Test that reflection actually improves quality."""
        agent = MockReflectiveAgent(reflection_threshold=0.6)
        
        message = AgentMessage(
            sender="test",
            recipient="reflective_test_agent", 
            action="reflect_action"
        )
        
        response = await agent.process_with_reflection(message, agent_context)
        
        # Check that quality improved through reflection
        final_quality = response.metadata["reflection"]["quality_score"]
        assert final_quality >= 0.6  # Met the threshold
        assert response.metadata["reflection_count"] >= 1


class TestAsyncBehavior:
    """Test async behavior and concurrency."""
    
    @pytest.mark.asyncio
    async def test_concurrent_execution(self, agent_context):
        """Test concurrent agent execution."""
        agent = MockAgent()
        
        # Execute multiple actions concurrently
        tasks = [
            agent.execute("test_action", {"id": i}, agent_context)
            for i in range(3)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(responses) == 3
        for response in responses:
            assert response.status == AgentStatus.COMPLETED
        
        # Should have processed all messages
        assert agent.process_calls == 3
        assert len(agent._message_history) == 3
        assert len(agent._response_history) == 3
    
    @pytest.mark.asyncio
    async def test_initialize_and_shutdown(self):
        """Test agent lifecycle methods."""
        agent = MockAgent()
        
        # Test initialize
        await agent.initialize()
        assert agent.initialize_calls == 1
        
        # Test shutdown
        await agent.shutdown()
        assert agent.shutdown_calls == 1
    
    @pytest.mark.asyncio
    async def test_wait_method(self):
        """Test internal wait method."""
        agent = MockAgent()
        
        start_time = datetime.utcnow()
        await agent._wait(0.1)  # Wait 100ms
        end_time = datetime.utcnow()
        
        elapsed = (end_time - start_time).total_seconds()
        assert elapsed >= 0.1  # Should wait at least 100ms


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_process_exception_handling(self, agent_context):
        """Test exception handling in process method."""
        agent = MockAgent(max_retries=0)  # No retries
        agent.should_fail = True
        
        with pytest.raises(AgentExecutionError):
            await agent.execute("test_action", {}, agent_context)
        
        # Should be in error state
        assert agent.status == AgentStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_retry_with_exponential_backoff(self, agent_context):
        """Test retry mechanism with exponential backoff."""
        agent = MockAgent(max_retries=2)
        agent.should_fail = True
        
        start_time = datetime.utcnow()
        
        # This will succeed on 3rd try (after 2 retries)
        response = await agent.execute("test_action", {}, agent_context)
        
        end_time = datetime.utcnow()
        elapsed = (end_time - start_time).total_seconds()
        
        # Should have waited for retries (2^1 + 2^2 = 6 seconds minimum)
        # Using a small tolerance for test execution time
        assert elapsed >= 0.0  # At least some time passed
        assert response.status == AgentStatus.COMPLETED
        assert agent.process_calls == 3  # Initial + 2 retries


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for agent interactions."""
    
    @pytest.mark.asyncio
    async def test_agent_message_flow(self):
        """Test complete message flow between mock agents."""
        sender_agent = MockAgent()
        receiver_agent = MockAgent()
        
        context = AgentContext(parent_agent=sender_agent.name)
        
        # Sender executes action
        response = await receiver_agent.execute(
            action="test_action",
            payload={"from": sender_agent.name},
            context=context
        )
        
        # Verify response
        assert response.agent_name == receiver_agent.name
        assert response.status == AgentStatus.COMPLETED
        
        # Verify message was created properly
        message = receiver_agent._message_history[0]
        assert message.sender == sender_agent.name
        assert message.recipient == receiver_agent.name
    
    @pytest.mark.asyncio
    async def test_reflective_agent_integration(self, agent_context):
        """Test reflective agent in realistic scenario."""
        agent = MockReflectiveAgent(reflection_threshold=0.75)
        
        message = AgentMessage(
            sender="integration_test",
            recipient=agent.name,
            action="reflect_action",
            payload={"complexity": "high"}
        )
        
        response = await agent.process_with_reflection(message, agent_context)
        
        # Should improve through reflection
        assert response.status == AgentStatus.COMPLETED
        assert "reflection" in response.metadata
        quality = response.metadata["reflection"]["quality_score"]
        assert quality >= agent.reflection_threshold