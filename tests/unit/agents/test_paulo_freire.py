"""
Unit tests for Paulo Freire Agent - System educator specialist.
Tests educational content generation, learning path suggestions, and onboarding guidance.
"""

import pytest

from src.agents.deodoro import AgentContext, AgentMessage
from src.agents.paulo_freire import DifficultyLevel, EducatorAgent, LearningTopic
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
        trace_id="trace-freire-789",
    )


@pytest.fixture
def paulo_freire_agent():
    """Create Paulo Freire agent."""
    return EducatorAgent()


class TestPauloFreireAgent:
    """Test suite for Paulo Freire (Educator Agent)."""

    @pytest.mark.unit
    def test_agent_initialization(self, paulo_freire_agent):
        """Test Paulo Freire agent initialization."""
        assert paulo_freire_agent.name == "paulo_freire"
        assert "teach_system_overview" in paulo_freire_agent.capabilities
        assert "explain_agent_architecture" in paulo_freire_agent.capabilities
        assert "guide_first_contribution" in paulo_freire_agent.capabilities
        assert "explain_specific_agent" in paulo_freire_agent.capabilities
        assert "troubleshoot_issues" in paulo_freire_agent.capabilities
        assert "suggest_learning_path" in paulo_freire_agent.capabilities
        assert "answer_technical_questions" in paulo_freire_agent.capabilities
        assert len(paulo_freire_agent.capabilities) == 7

    @pytest.mark.unit
    def test_system_knowledge_loaded(self, paulo_freire_agent):
        """Test that system knowledge is properly loaded."""
        assert "overview" in paulo_freire_agent.system_knowledge
        assert "agents" in paulo_freire_agent.system_knowledge
        assert "architecture" in paulo_freire_agent.system_knowledge
        assert "contribution" in paulo_freire_agent.system_knowledge
        assert "commands" in paulo_freire_agent.system_knowledge

    @pytest.mark.unit
    def test_agents_knowledge_complete(self, paulo_freire_agent):
        """Test that all 17 agents are documented in knowledge base."""
        agents = paulo_freire_agent.system_knowledge["agents"]
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
    async def test_teach_system_overview(self, paulo_freire_agent, agent_context):
        """Test teaching system overview."""
        message = AgentMessage(
            action="teach",
            recipient="paulo_freire",
            payload={
                "topic": "system_overview",
                "level": "beginner",
            },
            sender="intern",
            metadata={},
        )

        response = await paulo_freire_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "lesson" in response.result
        assert "suggested_next" in response.result
        assert "related_agents" in response.result
        assert "Cidadao.AI" in response.result["lesson"]
        assert "17 agentes" in response.result["lesson"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_teach_agent_architecture(self, paulo_freire_agent, agent_context):
        """Test teaching agent architecture."""
        message = AgentMessage(
            action="teach",
            recipient="paulo_freire",
            payload={
                "topic": "agent_architecture",
                "level": "intermediate",
            },
            sender="intern",
            metadata={},
        )

        response = await paulo_freire_agent.process(message, agent_context)

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
        self, paulo_freire_agent, agent_context
    ):
        """Test explaining a specific agent (Zumbi)."""
        message = AgentMessage(
            action="explain_agent",
            recipient="paulo_freire",
            payload={
                "agent_name": "zumbi",
            },
            sender="intern",
            metadata={},
        )

        response = await paulo_freire_agent.process(message, agent_context)

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
    async def test_explain_unknown_agent(self, paulo_freire_agent, agent_context):
        """Test explaining an unknown agent returns helpful error."""
        message = AgentMessage(
            action="explain_agent",
            recipient="paulo_freire",
            payload={
                "agent_name": "unknown_agent",
            },
            sender="intern",
            metadata={},
        )

        response = await paulo_freire_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "explanation" in response.result
        assert "nao encontrei" in response.result["explanation"].lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_first_steps_guide(self, paulo_freire_agent, agent_context):
        """Test first steps onboarding guide."""
        message = AgentMessage(
            action="first_steps",
            recipient="paulo_freire",
            payload={},
            sender="intern",
            metadata={},
        )

        response = await paulo_freire_agent.process(message, agent_context)

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
    async def test_teach_contribution_guide(self, paulo_freire_agent, agent_context):
        """Test teaching contribution guide."""
        message = AgentMessage(
            action="teach",
            recipient="paulo_freire",
            payload={
                "topic": "contribution_guide",
                "level": "beginner",
            },
            sender="intern",
            metadata={},
        )

        response = await paulo_freire_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "lesson" in response.result
        lesson = response.result["lesson"]
        assert "commit" in lesson.lower()
        assert "test" in lesson.lower() or "teste" in lesson.lower()
        assert "JWT_SECRET_KEY" in lesson

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_teach_testing_patterns(self, paulo_freire_agent, agent_context):
        """Test teaching testing patterns."""
        message = AgentMessage(
            action="teach",
            recipient="paulo_freire",
            payload={
                "topic": "testing_patterns",
                "level": "beginner",
            },
            sender="intern",
            metadata={},
        )

        response = await paulo_freire_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "lesson" in response.result
        assert "pytest" in response.result["lesson"].lower()
        assert "80%" in response.result["lesson"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_suggest_learning_path(self, paulo_freire_agent, agent_context):
        """Test suggesting a learning path."""
        message = AgentMessage(
            action="suggest_learning_path",
            recipient="paulo_freire",
            payload={
                "track": "backend",
                "level": "beginner",
                "interests": ["agents", "testing"],
            },
            sender="intern",
            metadata={},
        )

        response = await paulo_freire_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "learning_path" in response.result
        path = response.result["learning_path"]
        assert len(path) >= 4
        assert path[0]["step"] == 1
        assert "system_overview" in path[0]["topic"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_answer_question_agents_count(
        self, paulo_freire_agent, agent_context
    ):
        """Test answering question about number of agents."""
        message = AgentMessage(
            action="answer_question",
            recipient="paulo_freire",
            payload={
                "question": "Quantos agentes existem no sistema?",
            },
            sender="intern",
            metadata={},
        )

        response = await paulo_freire_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "answer" in response.result
        assert "17" in response.result["answer"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_answer_question_about_zumbi(self, paulo_freire_agent, agent_context):
        """Test answering question about Zumbi agent."""
        message = AgentMessage(
            action="answer_question",
            recipient="paulo_freire",
            payload={
                "question": "Como funciona o Zumbi?",
            },
            sender="intern",
            metadata={},
        )

        response = await paulo_freire_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "answer" in response.result
        assert (
            "Zumbi" in response.result["answer"] or "zumbi" in response.result["answer"]
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_teach_api_structure(self, paulo_freire_agent, agent_context):
        """Test teaching API structure."""
        message = AgentMessage(
            action="teach",
            recipient="paulo_freire",
            payload={
                "topic": "api_structure",
                "level": "intermediate",
            },
            sender="intern",
            metadata={},
        )

        response = await paulo_freire_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "lesson" in response.result
        assert "src/api/app.py" in response.result["lesson"]
        assert "middleware" in response.result["lesson"].lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_teach_troubleshooting(self, paulo_freire_agent, agent_context):
        """Test teaching troubleshooting guide."""
        message = AgentMessage(
            action="teach",
            recipient="paulo_freire",
            payload={
                "topic": "troubleshooting",
            },
            sender="intern",
            metadata={},
        )

        response = await paulo_freire_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "lesson" in response.result
        assert "JWT_SECRET_KEY" in response.result["lesson"]
        assert (
            "erro" in response.result["lesson"].lower()
            or "problem" in response.result["lesson"].lower()
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unknown_action(self, paulo_freire_agent, agent_context):
        """Test handling unknown action."""
        message = AgentMessage(
            action="unknown_action",
            recipient="paulo_freire",
            payload={},
            sender="intern",
            metadata={},
        )

        response = await paulo_freire_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "error" in response.result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_initialize_and_shutdown(self, paulo_freire_agent):
        """Test agent initialization and shutdown lifecycle."""
        await paulo_freire_agent.initialize()
        await paulo_freire_agent.shutdown()
        # No exceptions means success

    @pytest.mark.unit
    def test_personality_prompt_exists(self, paulo_freire_agent):
        """Test that personality prompt is defined."""
        assert hasattr(paulo_freire_agent, "personality_prompt")
        assert "Paulo Freire" in paulo_freire_agent.personality_prompt
        assert "educador" in paulo_freire_agent.personality_prompt.lower()


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
        """Test importing EducatorAgent via PauloFreireAgent alias."""
        from src.agents.paulo_freire import PauloFreireAgent

        agent = PauloFreireAgent()
        assert agent.name == "paulo_freire"

    @pytest.mark.unit
    def test_import_via_lazy_loading(self):
        """Test importing via lazy loading system."""
        from src.agents import get_agent

        agent = get_agent("paulo_freire")
        assert agent is not None
        assert agent.name == "paulo_freire"

    @pytest.mark.unit
    def test_import_educator_agent(self):
        """Test importing EducatorAgent directly."""
        from src.agents import EducatorAgent

        agent = EducatorAgent()
        assert agent.name == "paulo_freire"
