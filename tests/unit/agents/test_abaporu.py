"""
Unit tests for Abaporu (MasterAgent) - Core orchestration agent.
Tests self-reflection, investigation planning, and agent coordination.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4

from src.agents.abaporu import (
    MasterAgent,
    InvestigationPlan,
    InvestigationResult,
)
from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
)
from src.core.exceptions import AgentExecutionError, InvestigationError


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    with patch("src.agents.abaporu.get_logger") as mock:
        yield mock.return_value


@pytest.fixture
def mock_agent_registry():
    """Mock agent registry with test agents."""
    registry = {
        "investigator": AsyncMock(
            name="investigator",
            capabilities=["anomaly_detection", "data_analysis"],
            process=AsyncMock(return_value={
                "anomalies_found": True,
                "confidence": 0.85,
                "findings": ["Test anomaly 1", "Test anomaly 2"]
            })
        ),
        "analyst": AsyncMock(
            name="analyst",
            capabilities=["pattern_recognition", "correlation_analysis"],
            process=AsyncMock(return_value={
                "patterns": ["Pattern A", "Pattern B"],
                "correlations": {"factor1": 0.75, "factor2": 0.82}
            })
        ),
        "reporter": AsyncMock(
            name="reporter",
            capabilities=["report_generation", "summarization"],
            process=AsyncMock(return_value={
                "report": "Test investigation report",
                "summary": "Key findings summarized"
            })
        ),
    }
    return registry


@pytest.fixture
def agent_context():
    """Test agent context."""
    return AgentContext(
        investigation_id=str(uuid4()),
        user_id="test-user",
        session_id="test-session",
        metadata={"test": True},
        trace_id="test-trace-123"
    )


@pytest.fixture
def master_agent(mock_agent_registry):
    """Create MasterAgent instance for testing."""
    with patch("src.agents.abaporu.MasterAgent._initialize_agents") as mock_init:
        mock_init.return_value = mock_agent_registry
        agent = MasterAgent(
            reflection_threshold=0.8,
            max_reflection_iterations=3
        )
        agent.agent_registry = mock_agent_registry
        return agent


class TestMasterAgent:
    """Test suite for MasterAgent (Abaporu)."""
    
    @pytest.mark.unit
    async def test_initialization(self, master_agent):
        """Test MasterAgent initialization."""
        assert master_agent.name == "Abaporu"
        assert master_agent.reflection_threshold == 0.8
        assert master_agent.max_reflection_iterations == 3
        assert "orchestration" in master_agent.capabilities
        assert "self_reflection" in master_agent.capabilities
        assert len(master_agent.agent_registry) > 0
    
    @pytest.mark.unit
    async def test_create_investigation_plan(self, master_agent, agent_context):
        """Test investigation plan creation."""
        query = "Analyze contract anomalies in Ministry of Education"
        
        plan = await master_agent._create_investigation_plan(query, agent_context)
        
        assert isinstance(plan, InvestigationPlan)
        assert plan.objective == query
        assert len(plan.steps) > 0
        assert len(plan.required_agents) > 0
        assert plan.estimated_time > 0
        assert "accuracy" in plan.quality_criteria
    
    @pytest.mark.unit
    async def test_execute_investigation_step(self, master_agent, agent_context):
        """Test individual investigation step execution."""
        step = {
            "agent": "investigator",
            "action": "detect_anomalies",
            "params": {"data_source": "contracts", "threshold": 0.7}
        }
        
        result = await master_agent._execute_step(step, agent_context)
        
        assert result is not None
        assert "anomalies_found" in result
        assert result["confidence"] == 0.85
    
    @pytest.mark.unit
    async def test_self_reflection(self, master_agent):
        """Test self-reflection mechanism."""
        initial_result = {
            "findings": ["anomaly1", "anomaly2"],
            "confidence": 0.6,  # Below threshold
            "sources": ["contracts"]
        }
        
        improved_result = await master_agent._reflect_on_results(
            initial_result,
            "Find corruption patterns"
        )
        
        assert improved_result is not None
        assert improved_result.get("confidence", 0) >= initial_result["confidence"]
        assert "reflection_applied" in improved_result.get("metadata", {})
    
    @pytest.mark.unit
    async def test_process_investigation_success(self, master_agent, agent_context):
        """Test successful investigation processing."""
        query = "Investigate unusual spending patterns"
        
        result = await master_agent.process_investigation(query, agent_context)
        
        assert isinstance(result, InvestigationResult)
        assert result.query == query
        assert result.investigation_id == agent_context.investigation_id
        assert len(result.findings) > 0
        assert result.confidence_score > 0
        assert result.processing_time_ms is not None
    
    @pytest.mark.unit
    async def test_process_investigation_with_error(self, master_agent, agent_context):
        """Test investigation processing with error handling."""
        # Mock agent to raise error
        master_agent.agent_registry["investigator"].process.side_effect = Exception("Agent failed")
        
        with pytest.raises(InvestigationError) as exc_info:
            await master_agent.process_investigation(
                "Test query with error",
                agent_context
            )
        
        assert "Investigation failed" in str(exc_info.value)
    
    @pytest.mark.unit
    async def test_adaptive_strategy_selection(self, master_agent):
        """Test adaptive strategy selection based on context."""
        contexts = [
            {"data_type": "contracts", "complexity": "high"},
            {"data_type": "expenses", "complexity": "low"},
            {"data_type": "mixed", "urgency": "high"}
        ]
        
        strategies = []
        for ctx in contexts:
            strategy = master_agent._select_strategy(ctx)
            strategies.append(strategy)
        
        assert len(strategies) == len(contexts)
        assert all(s in ["comprehensive", "focused", "rapid"] for s in strategies)
        assert len(set(strategies)) > 1  # Different strategies selected
    
    @pytest.mark.unit
    async def test_agent_coordination(self, master_agent, agent_context):
        """Test coordination between multiple agents."""
        # Create a complex investigation requiring multiple agents
        query = "Analyze contract anomalies and generate detailed report"
        
        result = await master_agent.process_investigation(query, agent_context)
        
        # Verify multiple agents were used
        assert len(result.metadata.get("agents_used", [])) >= 2
        assert "investigator" in result.metadata.get("agents_used", [])
        assert "reporter" in result.metadata.get("agents_used", [])
    
    @pytest.mark.unit
    async def test_quality_assessment(self, master_agent):
        """Test investigation quality assessment."""
        results = {
            "findings": ["anomaly1", "anomaly2", "anomaly3"],
            "confidence": 0.85,
            "sources": ["contracts", "expenses"],
            "evidence_strength": "high"
        }
        
        quality_score = master_agent._assess_quality(results)
        
        assert 0 <= quality_score <= 1
        assert quality_score > 0.7  # High quality expected
    
    @pytest.mark.unit
    async def test_fallback_strategies(self, master_agent, agent_context):
        """Test fallback strategies when primary agents fail."""
        # Make primary agent fail
        master_agent.agent_registry["investigator"].process.side_effect = [
            Exception("First attempt failed"),
            {"findings": ["fallback result"], "confidence": 0.7}
        ]
        
        result = await master_agent.process_investigation(
            "Test with fallback",
            agent_context
        )
        
        assert result is not None
        assert "fallback_used" in result.metadata
        assert result.confidence_score == 0.7
    
    @pytest.mark.unit
    async def test_investigation_caching(self, master_agent, agent_context):
        """Test investigation result caching."""
        query = "Cached investigation test"
        
        # First call
        result1 = await master_agent.process_investigation(query, agent_context)
        
        # Second call (should use cache)
        with patch.object(master_agent, "_execute_plan") as mock_execute:
            result2 = await master_agent.process_investigation(query, agent_context)
            
            # Verify plan wasn't executed again
            mock_execute.assert_not_called()
        
        assert result1.investigation_id == result2.investigation_id
    
    @pytest.mark.unit
    async def test_concurrent_investigations(self, master_agent):
        """Test handling multiple concurrent investigations."""
        contexts = [
            AgentContext(investigation_id=str(uuid4())),
            AgentContext(investigation_id=str(uuid4())),
            AgentContext(investigation_id=str(uuid4()))
        ]
        
        queries = [
            "Investigation 1",
            "Investigation 2", 
            "Investigation 3"
        ]
        
        # Run investigations concurrently
        import asyncio
        results = await asyncio.gather(*[
            master_agent.process_investigation(query, ctx)
            for query, ctx in zip(queries, contexts)
        ])
        
        assert len(results) == 3
        assert all(isinstance(r, InvestigationResult) for r in results)
        assert len(set(r.investigation_id for r in results)) == 3  # All unique
    
    @pytest.mark.unit
    def test_message_formatting(self, master_agent):
        """Test agent message formatting."""
        message = master_agent._format_message(
            recipient="analyst",
            action="analyze_patterns",
            payload={"data": "test_data"},
            context={"priority": "high"}
        )
        
        assert isinstance(message, AgentMessage)
        assert message.sender == "Abaporu"
        assert message.recipient == "analyst"
        assert message.action == "analyze_patterns"
        assert message.payload["data"] == "test_data"
        assert message.context["priority"] == "high"
    
    @pytest.mark.unit
    async def test_status_tracking(self, master_agent, agent_context):
        """Test agent status tracking during investigation."""
        assert master_agent.status == AgentStatus.IDLE
        
        # Start investigation
        investigation_task = asyncio.create_task(
            master_agent.process_investigation("Test status", agent_context)
        )
        
        # Give it a moment to start
        await asyncio.sleep(0.1)
        assert master_agent.status in [AgentStatus.PROCESSING, AgentStatus.BUSY]
        
        # Wait for completion
        await investigation_task
        assert master_agent.status == AgentStatus.IDLE


@pytest.mark.unit
class TestInvestigationPlan:
    """Test InvestigationPlan model."""
    
    def test_plan_creation(self):
        """Test creating investigation plan."""
        plan = InvestigationPlan(
            objective="Test objective",
            steps=[{"agent": "investigator", "action": "analyze"}],
            required_agents=["investigator", "analyst"],
            estimated_time=120,
            quality_criteria={"accuracy": 0.9, "completeness": 0.85}
        )
        
        assert plan.objective == "Test objective"
        assert len(plan.steps) == 1
        assert len(plan.required_agents) == 2
        assert plan.estimated_time == 120
    
    def test_plan_with_fallback_strategies(self):
        """Test plan with fallback strategies."""
        plan = InvestigationPlan(
            objective="Test with fallbacks",
            steps=[],
            required_agents=["primary_agent"],
            estimated_time=60,
            quality_criteria={},
            fallback_strategies=["use_alternative_agent", "reduce_scope"]
        )
        
        assert len(plan.fallback_strategies) == 2
        assert "use_alternative_agent" in plan.fallback_strategies


@pytest.mark.unit 
class TestInvestigationResult:
    """Test InvestigationResult model."""
    
    def test_result_creation(self):
        """Test creating investigation result."""
        result = InvestigationResult(
            investigation_id="test-123",
            query="Test query",
            findings=[{"type": "anomaly", "description": "Test finding"}],
            confidence_score=0.85,
            sources=["contracts", "expenses"],
            explanation="Test explanation"
        )
        
        assert result.investigation_id == "test-123"
        assert result.query == "Test query"
        assert len(result.findings) == 1
        assert result.confidence_score == 0.85
        assert result.timestamp is not None
    
    def test_result_with_metadata(self):
        """Test result with metadata."""
        result = InvestigationResult(
            investigation_id="test-456",
            query="Test",
            findings=[],
            confidence_score=0.9,
            sources=[],
            metadata={
                "agents_used": ["agent1", "agent2"],
                "strategies_applied": ["strategy1"],
                "processing_stages": 3
            },
            processing_time_ms=1234.5
        )
        
        assert result.metadata["agents_used"] == ["agent1", "agent2"]
        assert result.processing_time_ms == 1234.5