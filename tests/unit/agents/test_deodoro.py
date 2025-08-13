"""
Unit tests for Deodoro (BaseAgent) - Foundation of the multi-agent system.
Tests core agent functionality, messaging, and context management.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from src.agents.deodoro import (
    BaseAgent,
    ReflectiveAgent,
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
)
from src.core.exceptions import AgentError, AgentExecutionError


class TestAgentContext:
    """Test suite for AgentContext."""
    
    @pytest.mark.unit
    def test_context_creation_with_defaults(self):
        """Test creating context with default values."""
        context = AgentContext()
        
        assert context.investigation_id is not None
        assert context.user_id is None
        assert context.session_id is None
        assert isinstance(context.timestamp, datetime)
        assert isinstance(context.metadata, dict)
        assert isinstance(context.memory_context, dict)
        assert context.parent_agent is None
        assert context.trace_id is None
    
    @pytest.mark.unit
    def test_context_creation_with_values(self):
        """Test creating context with specific values."""
        context = AgentContext(
            investigation_id="inv-123",
            user_id="user-456",
            session_id="session-789",
            metadata={"test": True},
            memory_context={"previous_action": "analyze"},
            parent_agent="master",
            trace_id="trace-abc"
        )
        
        assert context.investigation_id == "inv-123"
        assert context.user_id == "user-456"
        assert context.session_id == "session-789"
        assert context.metadata["test"] is True
        assert context.memory_context["previous_action"] == "analyze"
        assert context.parent_agent == "master"
        assert context.trace_id == "trace-abc"
    
    @pytest.mark.unit
    def test_context_to_dict(self):
        """Test converting context to dictionary."""
        context = AgentContext(
            investigation_id="test-123",
            user_id="user-test",
            metadata={"key": "value"}
        )
        
        context_dict = context.to_dict()
        
        assert isinstance(context_dict, dict)
        assert context_dict["investigation_id"] == "test-123"
        assert context_dict["user_id"] == "user-test"
        assert context_dict["metadata"]["key"] == "value"
        assert "timestamp" in context_dict
        assert isinstance(context_dict["timestamp"], str)


class TestAgentMessage:
    """Test suite for AgentMessage."""
    
    @pytest.mark.unit
    def test_message_creation(self):
        """Test creating agent message."""
        message = AgentMessage(
            sender="agent_a",
            recipient="agent_b",
            action="process_data",
            payload={"data": "test_data"},
            context={"priority": "high"},
            requires_response=True
        )
        
        assert message.sender == "agent_a"
        assert message.recipient == "agent_b"
        assert message.action == "process_data"
        assert message.payload["data"] == "test_data"
        assert message.context["priority"] == "high"
        assert message.requires_response is True
        assert isinstance(message.timestamp, datetime)
        assert message.message_id is not None
    
    @pytest.mark.unit
    def test_message_defaults(self):
        """Test message creation with defaults."""
        message = AgentMessage(
            sender="sender",
            recipient="recipient",
            action="test_action"
        )
        
        assert isinstance(message.payload, dict)
        assert isinstance(message.context, dict)
        assert message.requires_response is True
        assert len(message.payload) == 0
        assert len(message.context) == 0


class TestAgentResponse:
    """Test suite for AgentResponse."""
    
    @pytest.mark.unit
    def test_response_creation(self):
        """Test creating agent response."""
        response = AgentResponse(
            agent_name="test_agent",
            status=AgentStatus.COMPLETED,
            result={"findings": ["finding1", "finding2"]},
            metadata={"processing_time": 1.5},
            processing_time_ms=1500.0
        )
        
        assert response.agent_name == "test_agent"
        assert response.status == AgentStatus.COMPLETED
        assert response.result["findings"] == ["finding1", "finding2"]
        assert response.metadata["processing_time"] == 1.5
        assert response.processing_time_ms == 1500.0
        assert response.error is None
        assert isinstance(response.timestamp, datetime)
    
    @pytest.mark.unit
    def test_response_with_error(self):
        """Test creating response with error."""
        response = AgentResponse(
            agent_name="error_agent",
            status=AgentStatus.ERROR,
            error="Processing failed",
            result=None
        )
        
        assert response.status == AgentStatus.ERROR
        assert response.error == "Processing failed"
        assert response.result is None


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""
    
    async def process(self, message: AgentMessage, context: AgentContext) -> AgentResponse:
        """Simple process implementation for testing."""
        await asyncio.sleep(0.01)  # Simulate processing
        
        return AgentResponse(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            result={"processed": message.payload},
            processing_time_ms=10.0
        )
    
    def validate_input(self, message: AgentMessage) -> bool:
        """Simple validation for testing."""
        return message.action in ["test", "process", "analyze"]


class TestBaseAgent:
    """Test suite for BaseAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create test agent instance."""
        return ConcreteAgent(
            name="test_agent",
            description="Agent for testing",
            capabilities=["testing", "processing"],
            max_retries=2,
            timeout=30
        )
    
    @pytest.fixture
    def agent_context(self):
        """Create test context."""
        return AgentContext(investigation_id="test-inv")
    
    @pytest.mark.unit
    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "test_agent"
        assert agent.description == "Agent for testing"
        assert "testing" in agent.capabilities
        assert "processing" in agent.capabilities
        assert agent.max_retries == 2
        assert agent.timeout == 30
        assert agent.status == AgentStatus.IDLE
        assert agent.logger is not None
    
    @pytest.mark.unit
    async def test_agent_process_success(self, agent, agent_context):
        """Test successful agent processing."""
        message = AgentMessage(
            sender="test_sender",
            recipient=agent.name,
            action="test",
            payload={"data": "test_data"}
        )
        
        response = await agent.process(message, agent_context)
        
        assert isinstance(response, AgentResponse)
        assert response.agent_name == agent.name
        assert response.status == AgentStatus.COMPLETED
        assert response.result["processed"]["data"] == "test_data"
        assert response.processing_time_ms > 0
    
    @pytest.mark.unit
    def test_agent_capabilities_check(self, agent):
        """Test checking agent capabilities."""
        assert agent.has_capability("testing")
        assert agent.has_capability("processing")
        assert not agent.has_capability("non_existent")
    
    @pytest.mark.unit
    def test_agent_status_transitions(self, agent):
        """Test agent status transitions."""
        assert agent.status == AgentStatus.IDLE
        
        agent.set_status(AgentStatus.PROCESSING)
        assert agent.status == AgentStatus.PROCESSING
        
        agent.set_status(AgentStatus.COMPLETED)
        assert agent.status == AgentStatus.COMPLETED
        
        agent.set_status(AgentStatus.ERROR)
        assert agent.status == AgentStatus.ERROR
    
    @pytest.mark.unit
    def test_agent_validation(self, agent):
        """Test input validation."""
        valid_message = AgentMessage(
            sender="sender",
            recipient=agent.name,
            action="test"
        )
        
        invalid_message = AgentMessage(
            sender="sender",
            recipient=agent.name,
            action="invalid_action"
        )
        
        assert agent.validate_input(valid_message) is True
        assert agent.validate_input(invalid_message) is False
    
    @pytest.mark.unit
    async def test_agent_timeout_handling(self, agent, agent_context):
        """Test agent timeout handling."""
        # Create agent with very short timeout
        timeout_agent = ConcreteAgent(
            name="timeout_agent",
            description="Agent that times out",
            capabilities=["testing"],
            timeout=0.001  # 1ms timeout
        )
        
        # Override process to take longer than timeout
        async def slow_process(message, context):
            await asyncio.sleep(0.01)  # 10ms - longer than timeout
            return AgentResponse(
                agent_name=timeout_agent.name,
                status=AgentStatus.COMPLETED
            )
        
        timeout_agent.process = slow_process
        
        message = AgentMessage(
            sender="sender",
            recipient=timeout_agent.name,
            action="test"
        )
        
        with pytest.raises(AgentExecutionError) as exc_info:
            await timeout_agent.execute_with_timeout(message, agent_context)
        
        assert "timeout" in str(exc_info.value).lower()
    
    @pytest.mark.unit
    def test_agent_metadata_management(self, agent):
        """Test agent metadata management."""
        assert agent.get_metadata("non_existent") is None
        
        agent.set_metadata("test_key", "test_value")
        assert agent.get_metadata("test_key") == "test_value"
        
        agent.update_metadata({"key1": "value1", "key2": "value2"})
        assert agent.get_metadata("key1") == "value1"
        assert agent.get_metadata("key2") == "value2"
    
    @pytest.mark.unit
    def test_agent_health_check(self, agent):
        """Test agent health check."""
        health = agent.health_check()
        
        assert isinstance(health, dict)
        assert "status" in health
        assert "name" in health
        assert "capabilities" in health
        assert "uptime" in health
        assert health["status"] == "healthy"
        assert health["name"] == agent.name


class ConcreteReflectiveAgent(ReflectiveAgent):
    """Concrete implementation of ReflectiveAgent for testing."""
    
    async def process(self, message: AgentMessage, context: AgentContext) -> AgentResponse:
        """Process with reflection capability."""
        result = {"processed": message.payload}
        
        # Simulate low-quality result that needs reflection
        if message.payload.get("force_reflection"):
            result["confidence"] = 0.5  # Low confidence
        else:
            result["confidence"] = 0.9  # High confidence
        
        return AgentResponse(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            result=result
        )
    
    async def _reflect_on_result(self, result: dict, original_message: AgentMessage) -> dict:
        """Improve result through reflection."""
        improved_result = result.copy()
        improved_result["confidence"] = min(result.get("confidence", 0) + 0.2, 1.0)
        improved_result["reflection_applied"] = True
        return improved_result
    
    def _assess_result_quality(self, result: dict) -> float:
        """Assess quality of result."""
        return result.get("confidence", 0.0)


class TestReflectiveAgent:
    """Test suite for ReflectiveAgent."""
    
    @pytest.fixture
    def reflective_agent(self):
        """Create reflective agent for testing."""
        return ConcreteReflectiveAgent(
            name="reflective_agent",
            description="Agent with reflection",
            capabilities=["reflection", "processing"],
            reflection_threshold=0.7,
            max_reflection_iterations=2
        )
    
    @pytest.fixture
    def agent_context(self):
        """Create test context."""
        return AgentContext(investigation_id="reflection-test")
    
    @pytest.mark.unit
    def test_reflective_agent_initialization(self, reflective_agent):
        """Test reflective agent initialization."""
        assert reflective_agent.reflection_threshold == 0.7
        assert reflective_agent.max_reflection_iterations == 2
        assert "reflection" in reflective_agent.capabilities
    
    @pytest.mark.unit
    async def test_process_without_reflection(self, reflective_agent, agent_context):
        """Test processing that doesn't require reflection."""
        message = AgentMessage(
            sender="sender",
            recipient=reflective_agent.name,
            action="process",
            payload={"data": "good_quality"}
        )
        
        response = await reflective_agent.process_with_reflection(message, agent_context)
        
        assert response.result["confidence"] == 0.9
        assert "reflection_applied" not in response.result
    
    @pytest.mark.unit
    async def test_process_with_reflection(self, reflective_agent, agent_context):
        """Test processing that triggers reflection."""
        message = AgentMessage(
            sender="sender",
            recipient=reflective_agent.name,
            action="process",
            payload={"force_reflection": True}
        )
        
        response = await reflective_agent.process_with_reflection(message, agent_context)
        
        assert response.result["confidence"] > 0.5  # Improved through reflection
        assert response.result["reflection_applied"] is True
    
    @pytest.mark.unit
    async def test_reflection_iteration_limit(self, reflective_agent, agent_context):
        """Test reflection iteration limit."""
        # Create agent that always reflects
        always_reflect_agent = ConcreteReflectiveAgent(
            name="always_reflect",
            description="Always reflects",
            capabilities=["reflection"],
            reflection_threshold=1.0,  # Always reflect
            max_reflection_iterations=3
        )
        
        # Override to always return low quality
        async def always_low_quality(result, message):
            return {"confidence": 0.1, "iterations": result.get("iterations", 0) + 1}
        
        def always_assess_low(result):
            return 0.1  # Always low quality
        
        always_reflect_agent._reflect_on_result = always_low_quality
        always_reflect_agent._assess_result_quality = always_assess_low
        
        message = AgentMessage(
            sender="sender",
            recipient=always_reflect_agent.name,
            action="process"
        )
        
        response = await always_reflect_agent.process_with_reflection(message, agent_context)
        
        # Should stop after max iterations
        assert response.result["iterations"] <= 3
    
    @pytest.mark.unit
    def test_quality_assessment_thresholds(self, reflective_agent):
        """Test quality assessment with different thresholds."""
        high_quality_result = {"confidence": 0.95}
        medium_quality_result = {"confidence": 0.65}
        low_quality_result = {"confidence": 0.4}
        
        assert reflective_agent._assess_result_quality(high_quality_result) == 0.95
        assert reflective_agent._assess_result_quality(medium_quality_result) == 0.65
        assert reflective_agent._assess_result_quality(low_quality_result) == 0.4
        
        # Test reflection needed
        assert not reflective_agent._needs_reflection(high_quality_result)
        assert not reflective_agent._needs_reflection(medium_quality_result)
        assert reflective_agent._needs_reflection(low_quality_result)


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for agent system."""
    
    @pytest.mark.integration
    async def test_agent_communication(self):
        """Test communication between agents."""
        agent_a = ConcreteAgent(
            name="agent_a",
            description="First agent",
            capabilities=["sending"]
        )
        
        agent_b = ConcreteAgent(
            name="agent_b", 
            description="Second agent",
            capabilities=["receiving"]
        )
        
        context = AgentContext(investigation_id="integration-test")
        
        # Agent A sends message to Agent B
        message = AgentMessage(
            sender=agent_a.name,
            recipient=agent_b.name,
            action="process",
            payload={"forwarded_data": "test"}
        )
        
        response = await agent_b.process(message, context)
        
        assert response.agent_name == agent_b.name
        assert response.result["processed"]["forwarded_data"] == "test"
    
    @pytest.mark.integration
    async def test_agent_chain_processing(self):
        """Test chain of agent processing."""
        agents = [
            ConcreteAgent(f"agent_{i}", f"Agent {i}", ["chain_processing"])
            for i in range(3)
        ]
        
        context = AgentContext(investigation_id="chain-test")
        initial_data = {"value": 1}
        
        # Process through chain
        current_data = initial_data
        for i, agent in enumerate(agents):
            message = AgentMessage(
                sender=f"agent_{i-1}" if i > 0 else "client",
                recipient=agent.name,
                action="process",
                payload=current_data
            )
            
            response = await agent.process(message, context)
            current_data = response.result["processed"]
        
        assert current_data["value"] == 1  # Data preserved through chain
        assert "processed" not in current_data  # Final result unwrapped