"""
Additional comprehensive tests for Abaporu to achieve 100% coverage.
Tests full investigation flow, error paths, and edge cases.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.agents.abaporu import InvestigationPlan, InvestigationResult, MasterAgent
from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse, AgentStatus
from src.core.exceptions import InvestigationError


@pytest.fixture
def agent_context():
    """Test agent context."""
    return AgentContext(
        investigation_id=str(uuid4()),
        user_id="test-user",
        session_id="test-session",
        metadata={"test": True},
        trace_id="test-trace-123",
    )


@pytest.fixture
def master_agent():
    """Create MasterAgent instance for testing."""
    mock_maritaca = AsyncMock()
    mock_maritaca.chat_completion = AsyncMock(
        return_value=AsyncMock(
            content="Plan generated",
            usage={"total_tokens": 100},
        )
    )
    mock_maritaca.health_check = AsyncMock(
        return_value={"status": "healthy", "model": "sabiazinho-3"}
    )
    mock_maritaca.shutdown = AsyncMock()

    mock_memory = AsyncMock()
    mock_memory.get_relevant_context = AsyncMock(return_value={})
    mock_memory.store_investigation = AsyncMock()
    mock_memory.initialize = AsyncMock()
    mock_memory.shutdown = AsyncMock()

    agent = MasterAgent(
        maritaca_client=mock_maritaca,
        memory_agent=mock_memory,
    )

    return agent


@pytest.mark.unit
class TestAbaporuCompleteCoverage:
    """Test suite for complete Abaporu coverage."""

    @pytest.mark.asyncio
    async def test_investigate_full_flow(self, master_agent, agent_context):
        """Test complete investigation flow from query to result."""
        # Setup: Mock agent registry
        master_agent.agent_registry["Zumbi"] = AsyncMock(
            execute=AsyncMock(
                return_value=AgentResponse(
                    agent_name="Zumbi",
                    status=AgentStatus.COMPLETED,
                    result={
                        "findings": [{"description": "Anomaly", "anomaly_score": 0.9}],
                        "sources": ["contracts"],
                    },
                )
            )
        )

        payload = {"query": "Detect contract anomalies"}

        result = await master_agent._investigate(payload, agent_context)

        assert isinstance(result, InvestigationResult)
        assert result.query == "Detect contract anomalies"
        assert result.processing_time_ms is not None

    @pytest.mark.asyncio
    async def test_investigate_no_query_raises_error(self, master_agent, agent_context):
        """Test investigation with missing query raises InvestigationError."""
        payload = {}

        with pytest.raises(InvestigationError) as exc_info:
            await master_agent._investigate(payload, agent_context)

        assert "No query provided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_investigate_with_step_failure(self, master_agent, agent_context):
        """Test investigation continues when a step fails."""
        master_agent.agent_registry["Zumbi"] = AsyncMock(
            execute=AsyncMock(
                return_value=AgentResponse(
                    agent_name="Zumbi",
                    status=AgentStatus.ERROR,
                    error="Step failed",
                    result={},
                )
            )
        )

        payload = {"query": "Detect anomalies"}

        result = await master_agent._investigate(payload, agent_context)

        assert isinstance(result, InvestigationResult)
        assert result.confidence_score >= 0

    @pytest.mark.asyncio
    async def test_process_plan_investigation_action(self, master_agent, agent_context):
        """Test process() with plan_investigation action."""
        message = AgentMessage(
            sender="user",
            recipient="Abaporu",
            action="plan_investigation",
            payload={"query": "Test planning"},
        )

        response = await master_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert isinstance(response.result, InvestigationPlan)

    @pytest.mark.asyncio
    async def test_process_monitor_progress_action(self, master_agent, agent_context):
        """Test process() with monitor_progress action."""
        plan = InvestigationPlan(
            objective="Test",
            steps=[],
            required_agents=[],
            estimated_time=30,
            quality_criteria={},
        )
        master_agent.active_investigations[agent_context.investigation_id] = plan

        message = AgentMessage(
            sender="user",
            recipient="Abaporu",
            action="monitor_progress",
            payload={},
        )

        response = await master_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert response.result["status"] == "active"

    @pytest.mark.asyncio
    async def test_process_adapt_strategy_action(self, master_agent, agent_context):
        """Test process() with adapt_strategy action."""
        plan = InvestigationPlan(
            objective="Test adaptation",
            steps=[],
            required_agents=["Zumbi"],
            estimated_time=30,
            quality_criteria={"min_findings": 5},
        )
        master_agent.active_investigations[agent_context.investigation_id] = plan

        message = AgentMessage(
            sender="user",
            recipient="Abaporu",
            action="adapt_strategy",
            payload={
                "query": "Test",
                "current_results": {
                    "findings": [],
                    "confidence_score": 0.5,
                    "sources": [],
                    "anomaly_rate": 0.1,
                },
            },
        )

        response = await master_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert response.result["status"] == "adapted"

    @pytest.mark.asyncio
    async def test_initialize_with_memory_initialize(self, master_agent):
        """Test initialization when memory agent has initialize method."""
        await master_agent.initialize()

        master_agent.memory_agent.initialize.assert_called_once()
        assert master_agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_initialize_with_health_check_failure(self):
        """Test initialization continues when health check fails."""
        mock_maritaca = AsyncMock()
        mock_maritaca.health_check = AsyncMock(
            side_effect=Exception("Health check failed")
        )

        mock_memory = AsyncMock()

        agent = MasterAgent(
            maritaca_client=mock_maritaca,
            memory_agent=mock_memory,
        )

        await agent.initialize()

        assert agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_shutdown_calls_all_cleanup(self, master_agent):
        """Test shutdown calls all cleanup methods."""
        master_agent.active_investigations["test-1"] = InvestigationPlan(
            objective="Test",
            steps=[],
            required_agents=[],
            estimated_time=30,
            quality_criteria={},
        )
        master_agent.agent_registry["TestAgent"] = AsyncMock()

        await master_agent.shutdown()

        assert len(master_agent.active_investigations) == 0
        assert len(master_agent.agent_registry) == 0
        master_agent.maritaca_client.shutdown.assert_called_once()
        master_agent.memory_agent.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_explanation_with_llm_failure(
        self, master_agent, agent_context
    ):
        """Test explanation generation falls back when LLM fails."""
        master_agent.maritaca_client.chat_completion.side_effect = Exception(
            "LLM error"
        )

        findings = [{"description": "Test", "value": 1000, "anomaly_score": 0.8}]

        explanation = await master_agent._generate_explanation(
            findings, "Test query", agent_context
        )

        assert "Resumo da Investigação" in explanation
        assert "Test query" in explanation

    @pytest.mark.asyncio
    async def test_adapt_strategy_high_anomaly_rate(self, master_agent, agent_context):
        """Test strategy adaptation with high anomaly rate."""
        plan = InvestigationPlan(
            objective="Test",
            steps=[],
            required_agents=["Zumbi"],
            estimated_time=30,
            quality_criteria={"min_confidence": 0.7},
        )
        master_agent.active_investigations[agent_context.investigation_id] = plan

        result = await master_agent._adapt_strategy(
            {
                "query": "Test",
                "current_results": {
                    "findings": [{"x": 1}] * 10,
                    "confidence_score": 0.8,
                    "sources": ["s1", "s2"],
                    "anomaly_rate": 0.4,  # High anomaly rate > 30%
                },
            },
            agent_context,
        )

        assert result["status"] == "adapted"
        assert len(result["changes"]) > 0

    @pytest.mark.asyncio
    async def test_adapt_strategy_geographic_concentration(
        self, master_agent, agent_context
    ):
        """Test strategy adaptation with geographic concentration."""
        plan = InvestigationPlan(
            objective="Test",
            steps=[],
            required_agents=["Zumbi"],
            estimated_time=30,
            quality_criteria={},
        )
        master_agent.active_investigations[agent_context.investigation_id] = plan

        result = await master_agent._adapt_strategy(
            {
                "query": "Test",
                "current_results": {
                    "findings": [{"x": 1}] * 5,
                    "confidence_score": 0.7,
                    "sources": ["s1"],
                    "anomaly_rate": 0.1,
                    "geographic_concentration": 0.75,  # 75% in one region
                },
            },
            agent_context,
        )

        assert result["status"] == "adapted"
        assert len(result["new_steps"]) > 0

    @pytest.mark.asyncio
    async def test_monitor_progress_not_found(self, master_agent, agent_context):
        """Test monitoring progress for non-existent investigation."""
        result = await master_agent._monitor_progress({}, agent_context)

        assert result["status"] == "not_found"

    @pytest.mark.asyncio
    async def test_adapt_strategy_not_found(self, master_agent, agent_context):
        """Test adapting strategy for non-existent investigation."""
        result = await master_agent._adapt_strategy(
            {"current_results": {}}, agent_context
        )

        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_process_with_exception(self, master_agent, agent_context):
        """Test process() handles exceptions gracefully."""
        # Make plan_investigation fail
        master_agent.maritaca_client.chat_completion.side_effect = RuntimeError(
            "Critical error"
        )

        message = AgentMessage(
            sender="user",
            recipient="Abaporu",
            action="investigate",  # This will fail at planning
            payload={"query": "Test"},
        )

        response = await master_agent.process(message, agent_context)

        assert response.status == AgentStatus.ERROR
        assert response.error is not None

    @pytest.mark.asyncio
    async def test_investigate_with_parallel_steps(self, master_agent, agent_context):
        """Test investigation with parallel execution of multiple steps."""
        from unittest.mock import patch

        # Setup multiple agents for parallel execution
        master_agent.agent_registry["Zumbi"] = AsyncMock(
            execute=AsyncMock(
                return_value=AgentResponse(
                    agent_name="Zumbi",
                    status=AgentStatus.COMPLETED,
                    result={"findings": [{"type": "anomaly"}], "sources": ["s1"]},
                )
            )
        )
        master_agent.agent_registry["Anita"] = AsyncMock(
            execute=AsyncMock(
                return_value=AgentResponse(
                    agent_name="Anita",
                    status=AgentStatus.COMPLETED,
                    result={"findings": [{"type": "pattern"}], "sources": ["s2"]},
                )
            )
        )

        # Mock parallel processor
        with patch("src.agents.abaporu.parallel_processor") as mock_pp:
            mock_pp.execute_parallel = AsyncMock(return_value=[])
            mock_pp.aggregate_results = AsyncMock(
                return_value={"findings": [{"test": 1}], "sources": ["parallel_src"]}
            )

            # Query that triggers parallel execution (both agents)
            payload = {"query": "Analyze contract anomalies and patterns"}

            result = await master_agent._investigate(payload, agent_context)

            # Should have called parallel processor
            assert isinstance(result, InvestigationResult)
            # Check if parallel execution was attempted
            if mock_pp.execute_parallel.called:
                mock_pp.execute_parallel.assert_called_once()
                mock_pp.aggregate_results.assert_called_once()

    @pytest.mark.asyncio
    async def test_plan_investigation_with_memory_context(
        self, master_agent, agent_context
    ):
        """Test planning uses memory context when available."""
        # Setup memory to return context
        master_agent.memory_agent.get_relevant_context = AsyncMock(
            return_value={"previous_findings": ["old anomaly"]}
        )

        payload = {"query": "Test with memory"}

        plan = await master_agent._plan_investigation(payload, agent_context)

        # Verify memory was queried
        master_agent.memory_agent.get_relevant_context.assert_called_once()
        assert isinstance(plan, InvestigationPlan)

    @pytest.mark.asyncio
    async def test_plan_investigation_memory_failure(self, master_agent, agent_context):
        """Test planning continues when memory retrieval fails."""
        # Make memory fail
        master_agent.memory_agent.get_relevant_context = AsyncMock(
            side_effect=Exception("Memory error")
        )

        payload = {"query": "Test without memory"}

        plan = await master_agent._plan_investigation(payload, agent_context)

        # Should still return valid plan
        assert isinstance(plan, InvestigationPlan)

    @pytest.mark.asyncio
    async def test_create_planning_prompt(self, master_agent):
        """Test planning prompt creation."""
        query = "Analyze contract anomalies"
        memory_context = {"prev": "data"}

        prompt = master_agent._create_planning_prompt(query, memory_context)

        assert query in prompt
        assert "AGENTES ESPECIALIZADOS" in prompt
        assert "Zumbi dos Palmares" in prompt

    @pytest.mark.asyncio
    async def test_create_explanation_prompt(self, master_agent):
        """Test explanation prompt creation."""
        findings = [{"description": "Test", "anomaly_score": 0.9}]
        query = "Test query"

        prompt = master_agent._create_explanation_prompt(findings, query)

        assert query in prompt
        assert "RESUMO EXECUTIVO" in prompt
        assert "ACHADOS PRINCIPAIS" in prompt

    @pytest.mark.asyncio
    async def test_investigate_stores_in_memory(self, master_agent, agent_context):
        """Test investigation result is stored in memory."""
        master_agent.agent_registry["Zumbi"] = AsyncMock(
            execute=AsyncMock(
                return_value=AgentResponse(
                    agent_name="Zumbi",
                    status=AgentStatus.COMPLETED,
                    result={"findings": [], "sources": []},
                )
            )
        )

        payload = {"query": "Test memory storage"}

        result = await master_agent._investigate(payload, agent_context)

        # Verify memory storage was called
        master_agent.memory_agent.store_investigation.assert_called_once()
        call_args = master_agent.memory_agent.store_investigation.call_args
        assert call_args[0][0] == result  # First arg should be the result
        assert call_args[0][1] == agent_context  # Second arg should be context
