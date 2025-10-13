"""Multi-agent coordination tests."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.abaporu import MasterAgent
from src.agents.ayrton_senna import SemanticRouterAgent
from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
    BaseAgent,
    ReflectiveAgent,
)
from src.infrastructure.agent_pool import AgentPool
from src.infrastructure.orchestrator import AgentOrchestrator


class TestAgentMessage:
    """Test agent message system."""

    def test_create_agent_message(self):
        """Test creating agent message."""
        message = AgentMessage(
            sender="agent1",
            recipient="agent2",
            action="analyze",
            payload={"data": "test"},
            context={"investigation_id": "inv-123"},
        )

        assert message.sender == "agent1"
        assert message.recipient == "agent2"
        assert message.action == "analyze"
        assert message.payload["data"] == "test"
        assert message.requires_response is True  # Default
        assert message.message_id is not None

    def test_message_serialization(self):
        """Test message serialization."""
        message = AgentMessage(
            sender="test_agent",
            recipient="target_agent",
            action="process",
            payload={"value": 100},
        )

        # Serialize to dict
        message_dict = message.to_dict()

        assert isinstance(message_dict, dict)
        assert message_dict["sender"] == "test_agent"
        assert "timestamp" in message_dict

        # Deserialize back
        restored = AgentMessage.from_dict(message_dict)
        assert restored.sender == message.sender
        assert restored.action == message.action


class TestAgentContext:
    """Test agent context management."""

    def test_agent_context_creation(self):
        """Test creating agent context."""
        context = AgentContext(
            investigation_id="inv-456",
            user_id="user-789",
            parameters={"threshold": 0.8},
        )

        assert context.investigation_id == "inv-456"
        assert context.user_id == "user-789"
        assert context.parameters["threshold"] == 0.8
        assert context.shared_data == {}  # Empty initially

    def test_context_data_sharing(self):
        """Test data sharing through context."""
        context = AgentContext(investigation_id="inv-123")

        # Agent 1 adds data
        context.add_data("anomalies", [{"type": "price", "score": 0.9}])

        # Agent 2 can access it
        anomalies = context.get_data("anomalies")
        assert len(anomalies) == 1
        assert anomalies[0]["type"] == "price"

    def test_context_history_tracking(self):
        """Test context tracks agent history."""
        context = AgentContext(investigation_id="inv-123")

        # Track agent executions
        context.add_history("agent1", "Started analysis")
        context.add_history("agent2", "Found 3 anomalies")

        history = context.get_history()
        assert len(history) == 2
        assert history[0]["agent"] == "agent1"
        assert history[1]["message"] == "Found 3 anomalies"


class TestBaseAgent:
    """Test base agent functionality."""

    @pytest.fixture
    def test_agent(self):
        """Create test agent."""

        class TestAgent(BaseAgent):
            def __init__(self):
                super().__init__(
                    agent_id="test_agent",
                    name="Test Agent",
                    description="Agent for testing",
                )

            async def process(self, message: AgentMessage) -> AgentResponse:
                return AgentResponse(
                    agent_id=self.agent_id,
                    status=AgentStatus.COMPLETED,
                    result={"processed": True},
                )

        return TestAgent()

    @pytest.mark.asyncio
    async def test_agent_initialization(self, test_agent):
        """Test agent initialization."""
        assert test_agent.agent_id == "test_agent"
        assert test_agent.name == "Test Agent"
        assert test_agent.status == AgentStatus.IDLE
        assert test_agent.metrics is not None

    @pytest.mark.asyncio
    async def test_agent_execute(self, test_agent):
        """Test agent execution."""
        message = AgentMessage(
            sender="orchestrator",
            recipient="test_agent",
            action="test",
            payload={"data": "test"},
        )

        response = await test_agent.execute(message)

        assert response.status == AgentStatus.COMPLETED
        assert response.result["processed"] is True
        assert test_agent.metrics["executions"] == 1

    @pytest.mark.asyncio
    async def test_agent_retry_on_failure(self, test_agent):
        """Test agent retry mechanism."""
        # Mock process to fail first time, succeed second
        call_count = 0

        async def mock_process(message):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary failure")
            return AgentResponse(
                agent_id="test_agent",
                status=AgentStatus.COMPLETED,
                result={"success": True},
            )

        test_agent.process = mock_process

        message = AgentMessage(
            sender="test", recipient="test_agent", action="retry_test"
        )

        response = await test_agent.execute(message)

        assert response.status == AgentStatus.COMPLETED
        assert call_count == 2  # Failed once, succeeded on retry


class TestReflectiveAgent:
    """Test reflective agent capabilities."""

    @pytest.fixture
    def reflective_agent(self):
        """Create reflective test agent."""

        class TestReflectiveAgent(ReflectiveAgent):
            def __init__(self):
                super().__init__(
                    agent_id="reflective_test",
                    name="Reflective Test Agent",
                    description="Agent with reflection",
                )

            async def process(self, message: AgentMessage) -> AgentResponse:
                # Simulate processing with quality score
                return AgentResponse(
                    agent_id=self.agent_id,
                    status=AgentStatus.COMPLETED,
                    result={
                        "analysis": "Basic analysis",
                        "quality_score": 0.6,  # Below threshold
                    },
                )

            async def reflect(self, result: dict, context: dict) -> dict:
                # Improve based on reflection
                return {
                    "analysis": "Improved analysis with more detail",
                    "quality_score": 0.9,
                }

        return TestReflectiveAgent()

    @pytest.mark.asyncio
    async def test_reflection_improves_quality(self, reflective_agent):
        """Test reflection improves result quality."""
        message = AgentMessage(
            sender="test", recipient="reflective_test", action="analyze_with_reflection"
        )

        response = await reflective_agent.execute(message)

        # Should have improved through reflection
        assert response.result["quality_score"] > 0.8
        assert "Improved analysis" in response.result["analysis"]
        assert reflective_agent.metrics["reflections"] > 0

    @pytest.mark.asyncio
    async def test_reflection_loop_limit(self, reflective_agent):
        """Test reflection loop has maximum iterations."""

        # Mock reflect to never improve quality
        async def mock_reflect(result, context):
            return {"quality_score": 0.5}  # Always below threshold

        reflective_agent.reflect = mock_reflect
        reflective_agent.max_reflection_loops = 3

        message = AgentMessage(
            sender="test", recipient="reflective_test", action="test"
        )

        response = await reflective_agent.execute(message)

        # Should stop after max loops
        assert reflective_agent.metrics["reflections"] == 3


class TestMasterAgentOrchestration:
    """Test master agent orchestration."""

    @pytest.fixture
    def master_agent(self):
        """Create master agent."""
        return MasterAgent()

    @pytest.fixture
    def mock_agents(self):
        """Create mock agents."""
        investigator = AsyncMock()
        investigator.agent_id = "zumbi"
        investigator.execute.return_value = AgentResponse(
            agent_id="zumbi",
            status=AgentStatus.COMPLETED,
            result={"anomalies": [{"type": "price", "score": 0.8}]},
        )

        analyst = AsyncMock()
        analyst.agent_id = "anita"
        analyst.execute.return_value = AgentResponse(
            agent_id="anita",
            status=AgentStatus.COMPLETED,
            result={"patterns": [{"type": "temporal", "confidence": 0.7}]},
        )

        return {"zumbi": investigator, "anita": analyst}

    @pytest.mark.asyncio
    async def test_master_agent_coordination(self, master_agent, mock_agents):
        """Test master agent coordinating multiple agents."""
        # Patch agent registry
        with patch.object(master_agent, "_agent_registry", mock_agents):
            message = AgentMessage(
                sender="user",
                recipient="abaporu",
                action="investigate",
                payload={
                    "query": "Analyze Ministry of Health contracts",
                    "parameters": {"year": 2024},
                },
            )

            response = await master_agent.execute(message)

            assert response.status == AgentStatus.COMPLETED
            assert "anomalies" in response.result
            assert "patterns" in response.result

            # Verify agents were called
            mock_agents["zumbi"].execute.assert_called_once()
            mock_agents["anita"].execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_master_agent_error_handling(self, master_agent, mock_agents):
        """Test master agent handles agent failures."""
        # Make one agent fail
        mock_agents["zumbi"].execute.side_effect = Exception("Agent error")

        with patch.object(master_agent, "_agent_registry", mock_agents):
            message = AgentMessage(
                sender="user",
                recipient="abaporu",
                action="investigate",
                payload={"query": "Test investigation"},
            )

            response = await master_agent.execute(message)

            # Should still complete with partial results
            assert response.status == AgentStatus.COMPLETED
            assert "patterns" in response.result  # From analyst
            assert response.result.get("errors") is not None


class TestSemanticRouter:
    """Test semantic router agent."""

    @pytest.fixture
    def router(self):
        """Create semantic router."""
        return SemanticRouterAgent()

    @pytest.mark.asyncio
    async def test_rule_based_routing(self, router):
        """Test rule-based routing."""
        # Query about anomalies should route to Zumbi
        message = AgentMessage(
            sender="user",
            recipient="ayrton_senna",
            action="route",
            payload={"query": "Find anomalies in contracts"},
        )

        response = await router.execute(message)

        assert response.status == AgentStatus.COMPLETED
        assert response.result["target_agent"] == "zumbi"
        assert response.result["confidence"] > 0.8

    @pytest.mark.asyncio
    async def test_semantic_routing_fallback(self, router):
        """Test semantic routing for complex queries."""
        # Complex query requiring semantic understanding
        message = AgentMessage(
            sender="user",
            recipient="ayrton_senna",
            action="route",
            payload={"query": "I need a comprehensive analysis of spending patterns"},
        )

        with patch.object(router, "_semantic_route") as mock_semantic:
            mock_semantic.return_value = ("anita", 0.85)

            response = await router.execute(message)

            assert response.result["target_agent"] == "anita"
            assert response.result["routing_method"] == "semantic"


class TestAgentOrchestrator:
    """Test agent orchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator."""
        return AgentOrchestrator()

    @pytest.mark.asyncio
    async def test_orchestrate_investigation(self, orchestrator):
        """Test orchestrating full investigation."""
        # Create investigation context
        context = AgentContext(
            investigation_id="orch-test-123",
            parameters={"entity": "Ministry of Health", "year": 2024},
        )

        # Mock agent pool
        mock_pool = MagicMock()
        orchestrator.agent_pool = mock_pool

        # Mock agent responses
        async def mock_get_agent(agent_type):
            if agent_type == "investigator":
                agent = AsyncMock()
                agent.execute.return_value = AgentResponse(
                    agent_id="zumbi",
                    status=AgentStatus.COMPLETED,
                    result={"anomalies": [{"type": "price"}]},
                )
                return agent
            elif agent_type == "analyst":
                agent = AsyncMock()
                agent.execute.return_value = AgentResponse(
                    agent_id="anita",
                    status=AgentStatus.COMPLETED,
                    result={"patterns": [{"type": "seasonal"}]},
                )
                return agent

        mock_pool.get_agent = mock_get_agent

        # Execute orchestration
        result = await orchestrator.orchestrate_investigation(context)

        assert result["status"] == "completed"
        assert "anomalies" in result
        assert "patterns" in result
        assert len(result["execution_timeline"]) > 0

    @pytest.mark.asyncio
    async def test_parallel_agent_execution(self, orchestrator):
        """Test parallel execution of independent agents."""
        agents = []
        execution_order = []

        # Create mock agents that track execution order
        for i in range(3):
            agent = AsyncMock()
            agent.agent_id = f"agent_{i}"

            async def execute_with_delay(msg, agent_id=i):
                execution_order.append(f"start_{agent_id}")
                await asyncio.sleep(0.1)  # Simulate work
                execution_order.append(f"end_{agent_id}")
                return AgentResponse(
                    agent_id=f"agent_{agent_id}",
                    status=AgentStatus.COMPLETED,
                    result={"data": f"result_{agent_id}"},
                )

            agent.execute = execute_with_delay
            agents.append(agent)

        # Execute in parallel
        messages = [
            AgentMessage(sender="orch", recipient=f"agent_{i}", action="test")
            for i in range(3)
        ]

        results = await orchestrator.execute_parallel(agents, messages)

        # All should complete
        assert len(results) == 3
        assert all(r.status == AgentStatus.COMPLETED for r in results)

        # Verify parallel execution (starts should be close together)
        start_indices = [execution_order.index(f"start_{i}") for i in range(3)]
        assert max(start_indices) - min(start_indices) < 3


class TestAgentPool:
    """Test agent pool management."""

    @pytest.fixture
    def agent_pool(self):
        """Create agent pool."""
        return AgentPool(min_agents=2, max_agents=10)

    @pytest.mark.asyncio
    async def test_agent_pool_initialization(self, agent_pool):
        """Test agent pool initializes with minimum agents."""
        await agent_pool.initialize()

        # Should have minimum agents of each type
        assert len(agent_pool._agents["investigator"]) >= 2
        assert len(agent_pool._agents["analyst"]) >= 2
        assert len(agent_pool._agents["reporter"]) >= 2

    @pytest.mark.asyncio
    async def test_agent_pool_scaling(self, agent_pool):
        """Test agent pool scales with demand."""
        await agent_pool.initialize()

        # Request many agents to trigger scaling
        agents = []
        for _ in range(5):
            agent = await agent_pool.get_agent("investigator")
            agents.append(agent)

        # Pool should have scaled up
        assert len(agent_pool._agents["investigator"]) > 2

        # Return agents
        for agent in agents:
            await agent_pool.return_agent(agent)

    @pytest.mark.asyncio
    async def test_agent_health_monitoring(self, agent_pool):
        """Test agent health monitoring and recovery."""
        await agent_pool.initialize()

        # Get an agent and simulate failure
        agent = await agent_pool.get_agent("investigator")
        agent.status = AgentStatus.ERROR
        agent.metrics["errors"] = 5

        # Return unhealthy agent
        await agent_pool.return_agent(agent)

        # Pool should detect and replace unhealthy agent
        await agent_pool.health_check()

        # Verify unhealthy agent was replaced
        all_healthy = all(
            a.status != AgentStatus.ERROR for a in agent_pool._agents["investigator"]
        )
        assert all_healthy


class TestMultiAgentScenarios:
    """Test complex multi-agent scenarios."""

    @pytest.mark.asyncio
    async def test_end_to_end_investigation(self):
        """Test complete investigation flow."""
        # Create orchestrator with real agents
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()

        # Create investigation context
        context = AgentContext(
            investigation_id="e2e-test",
            parameters={
                "query": "Analyze health ministry contracts for anomalies",
                "entity": "26000",  # Health ministry code
                "year": 2024,
                "threshold": 100000,
            },
        )

        # Mock external API calls
        with patch(
            "src.tools.transparency_api.TransparencyAPIClient.get_contracts"
        ) as mock_api:
            mock_api.return_value = {
                "data": [
                    {
                        "id": "contract-1",
                        "valor": 500000,
                        "fornecedor": "Company A",
                        "data_assinatura": "2024-01-15",
                    },
                    {
                        "id": "contract-2",
                        "valor": 2000000,  # Anomaly
                        "fornecedor": "Company B",
                        "data_assinatura": "2024-01-16",
                    },
                ]
            }

            # Run investigation
            result = await orchestrator.run_investigation(context)

            assert result["status"] == "completed"
            assert len(result["anomalies"]) > 0
            assert result["summary"] is not None
            assert result["confidence_score"] > 0.5

    @pytest.mark.asyncio
    async def test_agent_failure_recovery(self):
        """Test system recovery from agent failures."""
        orchestrator = AgentOrchestrator()

        # Inject failing agent
        class FailingAgent(BaseAgent):
            async def process(self, message):
                raise Exception("Simulated failure")

        failing_agent = FailingAgent(agent_id="failing_agent", name="Failing Agent")

        # Replace one agent with failing version
        orchestrator._agent_registry["investigator"] = failing_agent

        context = AgentContext(investigation_id="failure-test")

        # Should handle failure gracefully
        result = await orchestrator.orchestrate_investigation(context)

        assert result["status"] in ["partial", "completed"]
        assert "errors" in result
        assert len(result["errors"]) > 0
