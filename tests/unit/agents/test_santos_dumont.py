"""
Unit tests for Santos-Dumont Agent - System educator specialist.
Tests educational content generation, learning path suggestions, and onboarding guidance.
"""

import pytest

from src.agents.deodoro import AgentContext, AgentMessage
from src.agents.santos_dumont import DifficultyLevel, EducatorAgent, LearningTopic
from src.core import AgentStatus


@pytest.fixture
def agent_context():
    """Test agent context for educational sessions."""
    return AgentContext(
        investigation_id="education-session-001",
        user_id="intern-001",
        session_id="learning-session",
        metadata={
            "track": "backend",
            "level": "beginner",
            "focus": "system_overview",
        },
        trace_id="trace-santos-dumont-789",
    )


@pytest.fixture
def santos_dumont_agent():
    """Create Santos-Dumont agent."""
    return EducatorAgent()


class TestSantosDumontAgent:
    """Test suite for Santos-Dumont (Educator Agent)."""

    @pytest.mark.unit
    def test_agent_initialization(self, santos_dumont_agent):
        """Test Santos-Dumont agent initialization."""
        assert santos_dumont_agent.name == "santos_dumont"
        assert "teach_system_overview" in santos_dumont_agent.capabilities
        assert "explain_agent_architecture" in santos_dumont_agent.capabilities
        assert "guide_first_contribution" in santos_dumont_agent.capabilities
        assert "explain_specific_agent" in santos_dumont_agent.capabilities
        assert "troubleshoot_issues" in santos_dumont_agent.capabilities
        assert "suggest_learning_path" in santos_dumont_agent.capabilities
        assert "answer_technical_questions" in santos_dumont_agent.capabilities
        assert len(santos_dumont_agent.capabilities) == 7

    @pytest.mark.unit
    def test_system_knowledge_loaded(self, santos_dumont_agent):
        """Test that system knowledge is properly loaded."""
        assert "overview" in santos_dumont_agent.system_knowledge
        assert "agents" in santos_dumont_agent.system_knowledge
        assert "architecture" in santos_dumont_agent.system_knowledge
        assert "contribution" in santos_dumont_agent.system_knowledge
        assert "commands" in santos_dumont_agent.system_knowledge

    @pytest.mark.unit
    def test_agents_knowledge_complete(self, santos_dumont_agent):
        """Test that all 17 agents are documented in knowledge base."""
        agents = santos_dumont_agent.system_knowledge["agents"]
        expected_agents = [
            "deodoro",
            "zumbi",
            "anita",
            "tiradentes",
            "drummond",
            "ayrton_senna",
            "bonifacio",
            "maria_quiteria",
            "machado",
            "oxossi",
            "lampiao",
            "oscar_niemeyer",
            "abaporu",
            "nana",
            "ceuci",
            "obaluaie",
            "dandara",
        ]
        for agent in expected_agents:
            assert agent in agents, f"Agent {agent} not found in knowledge base"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_teach_system_overview(self, santos_dumont_agent, agent_context):
        """Test teaching system overview."""
        message = AgentMessage(
            action="teach",
            recipient="santos_dumont",
            payload={
                "topic": "system_overview",
                "level": "beginner",
            },
            sender="intern",
            metadata={},
        )

        response = await santos_dumont_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "lesson" in response.result
        assert "suggested_next" in response.result
        assert "related_agents" in response.result
        assert "Cidadao.AI" in response.result["lesson"]
        assert "17 agentes" in response.result["lesson"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_teach_agent_architecture(self, santos_dumont_agent, agent_context):
        """Test teaching agent architecture."""
        message = AgentMessage(
            action="teach",
            recipient="santos_dumont",
            payload={
                "topic": "agent_architecture",
                "level": "intermediate",
            },
            sender="intern",
            metadata={},
        )

        response = await santos_dumont_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "lesson" in response.result
        assert (
            "BaseAgent" in response.result["lesson"]
            or "ReflectiveAgent" in response.result["lesson"]
        )
        assert (
            "lazy loading" in response.result["lesson"].lower()
            or "Lazy Loading" in response.result["lesson"]
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_explain_specific_agent_zumbi(
        self, santos_dumont_agent, agent_context
    ):
        """Test explaining a specific agent (Zumbi)."""
        message = AgentMessage(
            action="explain_agent",
            recipient="santos_dumont",
            payload={
                "agent_name": "zumbi",
            },
            sender="intern",
            metadata={},
        )

        response = await santos_dumont_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "explanation" in response.result
        assert "agent_info" in response.result
        assert (
            "Zumbi" in response.result["explanation"]
            or "zumbi" in response.result["explanation"]
        )
        assert response.result["agent_info"]["type"] == "Investigator"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_explain_unknown_agent(self, santos_dumont_agent, agent_context):
        """Test explaining an unknown agent returns helpful error."""
        message = AgentMessage(
            action="explain_agent",
            recipient="santos_dumont",
            payload={
                "agent_name": "unknown_agent",
            },
            sender="intern",
            metadata={},
        )

        response = await santos_dumont_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "explanation" in response.result
        assert "nao encontrei" in response.result["explanation"].lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_first_steps_guide(self, santos_dumont_agent, agent_context):
        """Test first steps onboarding guide."""
        message = AgentMessage(
            action="first_steps",
            recipient="santos_dumont",
            payload={},
            sender="intern",
            metadata={},
        )

        response = await santos_dumont_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "guide" in response.result
        assert "checklist" in response.result
        assert len(response.result["checklist"]) >= 5
        assert (
            "Clone" in response.result["checklist"][0]
            or "repositorio" in response.result["checklist"][0].lower()
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_teach_contribution_guide(self, santos_dumont_agent, agent_context):
        """Test teaching contribution guide."""
        message = AgentMessage(
            action="teach",
            recipient="santos_dumont",
            payload={
                "topic": "contribution_guide",
                "level": "beginner",
            },
            sender="intern",
            metadata={},
        )

        response = await santos_dumont_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "lesson" in response.result
        lesson = response.result["lesson"]
        assert "commit" in lesson.lower()
        assert "test" in lesson.lower() or "teste" in lesson.lower()
        assert "JWT_SECRET_KEY" in lesson

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_teach_testing_patterns(self, santos_dumont_agent, agent_context):
        """Test teaching testing patterns."""
        message = AgentMessage(
            action="teach",
            recipient="santos_dumont",
            payload={
                "topic": "testing_patterns",
                "level": "beginner",
            },
            sender="intern",
            metadata={},
        )

        response = await santos_dumont_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "lesson" in response.result
        assert "pytest" in response.result["lesson"].lower()
        assert "80%" in response.result["lesson"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_suggest_learning_path(self, santos_dumont_agent, agent_context):
        """Test suggesting a learning path."""
        message = AgentMessage(
            action="suggest_learning_path",
            recipient="santos_dumont",
            payload={
                "track": "backend",
                "level": "beginner",
                "interests": ["agents", "testing"],
            },
            sender="intern",
            metadata={},
        )

        response = await santos_dumont_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "learning_path" in response.result
        path = response.result["learning_path"]
        assert len(path) >= 4
        assert path[0]["step"] == 1
        assert "system_overview" in path[0]["topic"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_answer_question_agents_count(
        self, santos_dumont_agent, agent_context
    ):
        """Test answering question about number of agents."""
        message = AgentMessage(
            action="answer_question",
            recipient="santos_dumont",
            payload={
                "question": "Quantos agentes existem no sistema?",
            },
            sender="intern",
            metadata={},
        )

        response = await santos_dumont_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "answer" in response.result
        assert "17" in response.result["answer"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_answer_question_about_zumbi(
        self, santos_dumont_agent, agent_context
    ):
        """Test answering question about Zumbi agent."""
        message = AgentMessage(
            action="answer_question",
            recipient="santos_dumont",
            payload={
                "question": "Como funciona o Zumbi?",
            },
            sender="intern",
            metadata={},
        )

        response = await santos_dumont_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "answer" in response.result
        assert (
            "Zumbi" in response.result["answer"] or "zumbi" in response.result["answer"]
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_teach_api_structure(self, santos_dumont_agent, agent_context):
        """Test teaching API structure."""
        message = AgentMessage(
            action="teach",
            recipient="santos_dumont",
            payload={
                "topic": "api_structure",
                "level": "intermediate",
            },
            sender="intern",
            metadata={},
        )

        response = await santos_dumont_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "lesson" in response.result
        assert "src/api/app.py" in response.result["lesson"]
        assert "middleware" in response.result["lesson"].lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_teach_troubleshooting(self, santos_dumont_agent, agent_context):
        """Test teaching troubleshooting guide."""
        message = AgentMessage(
            action="teach",
            recipient="santos_dumont",
            payload={
                "topic": "troubleshooting",
            },
            sender="intern",
            metadata={},
        )

        response = await santos_dumont_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "lesson" in response.result
        assert "JWT_SECRET_KEY" in response.result["lesson"]
        assert (
            "erro" in response.result["lesson"].lower()
            or "problem" in response.result["lesson"].lower()
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unknown_action(self, santos_dumont_agent, agent_context):
        """Test handling unknown action."""
        message = AgentMessage(
            action="unknown_action",
            recipient="santos_dumont",
            payload={},
            sender="intern",
            metadata={},
        )

        response = await santos_dumont_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "error" in response.result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_initialize_and_shutdown(self, santos_dumont_agent):
        """Test agent initialization and shutdown lifecycle."""
        await santos_dumont_agent.initialize()
        await santos_dumont_agent.shutdown()
        # No exceptions means success

    @pytest.mark.unit
    def test_personality_prompt_exists(self, santos_dumont_agent):
        """Test that personality prompt is defined."""
        assert hasattr(santos_dumont_agent, "personality_prompt")
        assert "Santos-Dumont" in santos_dumont_agent.personality_prompt
        assert "inventor" in santos_dumont_agent.personality_prompt.lower()


class TestLearningTopicEnum:
    """Test suite for LearningTopic enum."""

    @pytest.mark.unit
    def test_learning_topics(self):
        """Test all learning topics are defined."""
        assert LearningTopic.SYSTEM_OVERVIEW.value == "system_overview"
        assert LearningTopic.AGENT_ARCHITECTURE.value == "agent_architecture"
        assert LearningTopic.SPECIFIC_AGENT.value == "specific_agent"
        assert LearningTopic.API_STRUCTURE.value == "api_structure"
        assert LearningTopic.CONTRIBUTION_GUIDE.value == "contribution_guide"
        assert LearningTopic.TESTING_PATTERNS.value == "testing_patterns"
        assert LearningTopic.CODE_PATTERNS.value == "code_patterns"
        assert LearningTopic.FIRST_MISSION.value == "first_mission"
        assert LearningTopic.TROUBLESHOOTING.value == "troubleshooting"


class TestDifficultyLevelEnum:
    """Test suite for DifficultyLevel enum."""

    @pytest.mark.unit
    def test_difficulty_levels(self):
        """Test all difficulty levels are defined."""
        assert DifficultyLevel.BEGINNER.value == "beginner"
        assert DifficultyLevel.INTERMEDIATE.value == "intermediate"
        assert DifficultyLevel.ADVANCED.value == "advanced"


class TestAgentAliasImport:
    """Test that agent can be imported via alias."""

    @pytest.mark.unit
    def test_import_via_alias(self):
        """Test importing EducatorAgent via SantosDumontAgent alias."""
        from src.agents.santos_dumont import SantosDumontAgent

        agent = SantosDumontAgent()
        assert agent.name == "santos_dumont"

    @pytest.mark.unit
    def test_import_via_lazy_loading(self):
        """Test importing via lazy loading system."""
        from src.agents import get_agent

        agent = get_agent("santos_dumont")
        assert agent is not None
        assert agent.name == "santos_dumont"

    @pytest.mark.unit
    def test_import_educator_agent(self):
        """Test importing EducatorAgent directly."""
        from src.agents import EducatorAgent

        agent = EducatorAgent()
        assert agent.name == "santos_dumont"
