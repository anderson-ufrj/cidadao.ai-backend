"""
Tests for Bo Bardi Frontend Designer Agent.

This module contains comprehensive tests for the Lina Bo Bardi agent,
which specializes in frontend integration guidance for Cidadão.AI.
"""

import pytest

from src.agents.bo_bardi import (
    BoBardiAgent,
    FrontendDesignerAgent,
    FrontendTopic,
    LinaBoBardi,
)
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus


class TestFrontendDesignerAgent:
    """Tests for the FrontendDesignerAgent (Bo Bardi)."""

    @pytest.fixture
    def agent(self) -> FrontendDesignerAgent:
        """Create a Bo Bardi agent instance for testing."""
        return FrontendDesignerAgent()

    @pytest.fixture
    def context(self) -> AgentContext:
        """Create an agent context for testing."""
        return AgentContext()

    def test_agent_initialization(self, agent: FrontendDesignerAgent):
        """Test that the agent initializes correctly."""
        assert agent.name == "bo_bardi"
        assert (
            "frontend" in agent.description.lower()
            or "interface" in agent.description.lower()
        )
        assert len(agent.capabilities) >= 5

    def test_agent_capabilities(self, agent: FrontendDesignerAgent):
        """Test that the agent has the expected capabilities."""
        expected_capabilities = [
            "guide_sse_integration",
            "explain_component_structure",
            "teach_api_consumption",
            "advise_accessibility",
            "suggest_styling_patterns",
            "help_error_handling",
        ]
        for capability in expected_capabilities:
            assert capability in agent.capabilities

    def test_frontend_knowledge_loaded(self, agent: FrontendDesignerAgent):
        """Test that frontend knowledge is properly loaded."""
        assert hasattr(agent, "frontend_knowledge")
        assert "sse_integration" in agent.frontend_knowledge
        assert "component_structure" in agent.frontend_knowledge
        assert "api_endpoints" in agent.frontend_knowledge
        assert "agents_available" in agent.frontend_knowledge

    def test_sse_integration_knowledge(self, agent: FrontendDesignerAgent):
        """Test SSE integration knowledge content."""
        sse_info = agent.frontend_knowledge["sse_integration"]
        assert "endpoint" in sse_info
        assert "POST" in sse_info["endpoint"]
        assert "/api/v1/chat/stream" in sse_info["endpoint"]
        assert "events" in sse_info
        assert "chunk" in sse_info["events"]
        assert "complete" in sse_info["events"]

    def test_api_endpoints_knowledge(self, agent: FrontendDesignerAgent):
        """Test API endpoints knowledge content."""
        endpoints = agent.frontend_knowledge["api_endpoints"]
        assert "chat_stream" in endpoints
        assert "agents_list" in endpoints
        assert "health" in endpoints

    def test_agents_available_list(self, agent: FrontendDesignerAgent):
        """Test that available agents list is populated."""
        agents = agent.frontend_knowledge["agents_available"]
        assert len(agents) > 0

        # Check structure of agent entries
        for agent_info in agents:
            assert "id" in agent_info
            assert "name" in agent_info
            assert "emoji" in agent_info
            assert "role" in agent_info

    @pytest.mark.asyncio
    async def test_process_guide_action_sse(
        self, agent: FrontendDesignerAgent, context: AgentContext
    ):
        """Test processing guide action for SSE integration."""
        message = AgentMessage(
            sender="test_user",
            recipient="bo_bardi",
            action="guide",
            payload={"topic": "sse_integration"},
        )

        response = await agent.process(message, context)

        assert response.agent_name == "bo_bardi"
        assert response.status == AgentStatus.COMPLETED
        assert "guide" in response.result
        assert response.metadata.get("frontend") is True
        assert response.metadata.get("topic") == "sse_integration"

    @pytest.mark.asyncio
    async def test_process_guide_action_component_structure(
        self, agent: FrontendDesignerAgent, context: AgentContext
    ):
        """Test processing guide action for component structure."""
        message = AgentMessage(
            sender="test_user",
            recipient="bo_bardi",
            action="guide",
            payload={"topic": "component_structure"},
        )

        response = await agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert "guide" in response.result
        assert response.metadata.get("topic") == "component_structure"

    @pytest.mark.asyncio
    async def test_process_guide_action_api_consumption(
        self, agent: FrontendDesignerAgent, context: AgentContext
    ):
        """Test processing guide action for API consumption."""
        message = AgentMessage(
            sender="test_user",
            recipient="bo_bardi",
            action="guide",
            payload={"topic": "api_consumption"},
        )

        response = await agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert "guide" in response.result
        assert response.metadata.get("topic") == "api_consumption"

    @pytest.mark.asyncio
    async def test_process_code_example_sse_chat(
        self, agent: FrontendDesignerAgent, context: AgentContext
    ):
        """Test processing code example action for SSE chat."""
        message = AgentMessage(
            sender="test_user",
            recipient="bo_bardi",
            action="code_example",
            payload={"feature": "sse_chat"},
        )

        response = await agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert "code" in response.result
        assert "dependencies" in response.result
        assert response.metadata.get("type") == "code_example"

    @pytest.mark.asyncio
    async def test_process_code_example_agent_selector(
        self, agent: FrontendDesignerAgent, context: AgentContext
    ):
        """Test processing code example action for agent selector."""
        message = AgentMessage(
            sender="test_user",
            recipient="bo_bardi",
            action="code_example",
            payload={"feature": "agent_selector"},
        )

        response = await agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert "code" in response.result
        assert "AgentSelector" in response.result["code"]

    @pytest.mark.asyncio
    async def test_process_explain_event(
        self, agent: FrontendDesignerAgent, context: AgentContext
    ):
        """Test processing explain event action."""
        message = AgentMessage(
            sender="test_user",
            recipient="bo_bardi",
            action="explain_event",
            payload={"event_type": "chunk"},
        )

        response = await agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert response.metadata.get("type") == "event_explanation"
        assert "event" in response.result or "error" not in response.result

    @pytest.mark.asyncio
    async def test_process_explain_event_unknown(
        self, agent: FrontendDesignerAgent, context: AgentContext
    ):
        """Test processing explain event action for unknown event."""
        message = AgentMessage(
            sender="test_user",
            recipient="bo_bardi",
            action="explain_event",
            payload={"event_type": "nonexistent_event"},
        )

        response = await agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert "error" in response.result or "available_events" in response.result

    @pytest.mark.asyncio
    async def test_process_unknown_action(
        self, agent: FrontendDesignerAgent, context: AgentContext
    ):
        """Test processing unknown action returns error."""
        message = AgentMessage(
            sender="test_user",
            recipient="bo_bardi",
            action="unknown_action",
            payload={},
        )

        response = await agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert "error" in response.result

    @pytest.mark.asyncio
    async def test_guide_topic_not_found(
        self, agent: FrontendDesignerAgent, context: AgentContext
    ):
        """Test guide action with unknown topic."""
        message = AgentMessage(
            sender="test_user",
            recipient="bo_bardi",
            action="guide",
            payload={"topic": "nonexistent_topic"},
        )

        response = await agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        # Should return guidance about available topics
        assert "guide" in response.result

    @pytest.mark.asyncio
    async def test_code_example_not_found(
        self, agent: FrontendDesignerAgent, context: AgentContext
    ):
        """Test code example action with unknown feature."""
        message = AgentMessage(
            sender="test_user",
            recipient="bo_bardi",
            action="code_example",
            payload={"feature": "nonexistent_feature"},
        )

        response = await agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert "code" in response.result or "explanation" in response.result

    @pytest.mark.asyncio
    async def test_initialize_agent(self, agent: FrontendDesignerAgent):
        """Test agent initialization method."""
        # Should not raise any exceptions
        await agent.initialize()

    @pytest.mark.asyncio
    async def test_shutdown_agent(self, agent: FrontendDesignerAgent):
        """Test agent shutdown method."""
        # Should not raise any exceptions
        await agent.shutdown()


class TestBoBardiFrontendTopic:
    """Tests for the FrontendTopic enum."""

    def test_frontend_topic_values(self):
        """Test that all expected topics exist."""
        assert FrontendTopic.SSE_INTEGRATION.value == "sse_integration"
        assert FrontendTopic.COMPONENT_STRUCTURE.value == "component_structure"
        assert FrontendTopic.STATE_MANAGEMENT.value == "state_management"
        assert FrontendTopic.API_CONSUMPTION.value == "api_consumption"
        assert FrontendTopic.STYLING.value == "styling"
        assert FrontendTopic.ACCESSIBILITY.value == "accessibility"
        assert FrontendTopic.RESPONSIVE_DESIGN.value == "responsive_design"
        assert FrontendTopic.ERROR_HANDLING.value == "error_handling"


class TestBoBardiAliases:
    """Tests for Bo Bardi agent aliases."""

    def test_bo_bardi_agent_alias(self):
        """Test that BoBardiAgent is an alias for FrontendDesignerAgent."""
        assert BoBardiAgent is FrontendDesignerAgent

    def test_lina_bo_bardi_alias(self):
        """Test that LinaBoBardi is an alias for FrontendDesignerAgent."""
        assert LinaBoBardi is FrontendDesignerAgent

    def test_aliases_create_same_agent(self):
        """Test that all aliases create equivalent agents."""
        agent1 = FrontendDesignerAgent()
        agent2 = BoBardiAgent()
        agent3 = LinaBoBardi()

        assert agent1.name == agent2.name == agent3.name
        assert agent1.capabilities == agent2.capabilities == agent3.capabilities


class TestBoBardiPersonality:
    """Tests for Bo Bardi agent personality prompt."""

    @pytest.fixture
    def agent(self) -> FrontendDesignerAgent:
        """Create agent for testing."""
        return FrontendDesignerAgent()

    def test_personality_prompt_exists(self, agent: FrontendDesignerAgent):
        """Test that personality prompt is set."""
        assert hasattr(agent, "personality_prompt")
        assert len(agent.personality_prompt) > 0

    def test_personality_mentions_lina_bo_bardi(self, agent: FrontendDesignerAgent):
        """Test that personality prompt mentions Lina Bo Bardi."""
        assert "Lina Bo Bardi" in agent.personality_prompt

    def test_personality_mentions_frontend(self, agent: FrontendDesignerAgent):
        """Test that personality prompt mentions frontend expertise."""
        prompt_lower = agent.personality_prompt.lower()
        assert "frontend" in prompt_lower or "interface" in prompt_lower

    def test_personality_mentions_backend_knowledge(self, agent: FrontendDesignerAgent):
        """Test that personality prompt mentions backend knowledge."""
        prompt_lower = agent.personality_prompt.lower()
        assert "backend" in prompt_lower or "api" in prompt_lower


class TestBoBardiFormatting:
    """Tests for Bo Bardi formatting methods."""

    @pytest.fixture
    def agent(self) -> FrontendDesignerAgent:
        """Create agent for testing."""
        return FrontendDesignerAgent()

    def test_format_events_method(self, agent: FrontendDesignerAgent):
        """Test the _format_events private method."""
        events = {"start": "Start event", "chunk": "Data chunk"}
        formatted = agent._format_events(events)

        assert "| Evento | Descrição |" in formatted
        assert "start" in formatted
        assert "chunk" in formatted

    def test_format_events_empty(self, agent: FrontendDesignerAgent):
        """Test formatting empty events dict."""
        formatted = agent._format_events({})
        assert "| Evento | Descrição |" in formatted
