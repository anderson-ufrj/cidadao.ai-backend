"""
Unit tests for Monteiro Lobato Agent - Kids programming educator.
Tests content safety, educational responses, and proper content filtering.
"""

import pytest

from src.agents.base_kids_agent import BLOCKED_TOPICS
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus
from src.agents.monteiro_lobato import (
    ALLOWED_TOPICS_PROGRAMMING,
    KidsProgrammingAgent,
    LobatoAgent,
    MonteiroLobatoAgent,
)


@pytest.fixture
def agent_context():
    """Test agent context for kids sessions."""
    return AgentContext(
        investigation_id="kids-session-001",
        user_id="kid-001",
        session_id="learning-session",
        metadata={
            "target_audience": "kids_6_12",
            "mode": "educational",
        },
        trace_id="trace-lobato-001",
    )


@pytest.fixture
def lobato_agent():
    """Create Monteiro Lobato agent."""
    return KidsProgrammingAgent()


class TestMonteiroLobatoAgent:
    """Test suite for Monteiro Lobato (Kids Programming Agent)."""

    @pytest.mark.unit
    def test_agent_initialization(self, lobato_agent):
        """Test Monteiro Lobato agent initialization."""
        assert lobato_agent.name == "monteiro_lobato"
        assert "teach_programming_basics" in lobato_agent.capabilities
        assert "explain_algorithms" in lobato_agent.capabilities
        assert "tell_code_stories" in lobato_agent.capabilities
        assert "answer_kids_questions" in lobato_agent.capabilities
        assert "make_learning_fun" in lobato_agent.capabilities
        assert len(lobato_agent.capabilities) == 5

    @pytest.mark.unit
    def test_blocked_topics_exist(self):
        """Test that blocked topics are properly defined."""
        assert len(BLOCKED_TOPICS) > 50  # Ensure comprehensive blocking
        assert "violencia" in BLOCKED_TOPICS
        assert "sexo" in BLOCKED_TOPICS
        assert "droga" in BLOCKED_TOPICS
        assert "hack" in BLOCKED_TOPICS
        assert "terror" in BLOCKED_TOPICS

    @pytest.mark.unit
    def test_allowed_topics_exist(self):
        """Test that allowed topics are properly defined."""
        assert (
            len(ALLOWED_TOPICS_PROGRAMMING) > 100
        )  # Ensure comprehensive allowed list
        assert "programacao" in ALLOWED_TOPICS_PROGRAMMING
        assert "variavel" in ALLOWED_TOPICS_PROGRAMMING
        assert "loop" in ALLOWED_TOPICS_PROGRAMMING
        assert "emilia" in ALLOWED_TOPICS_PROGRAMMING
        assert "aprender" in ALLOWED_TOPICS_PROGRAMMING


class TestContentSafety:
    """Test content safety filters."""

    @pytest.fixture
    def agent(self):
        return KidsProgrammingAgent()

    @pytest.mark.unit
    def test_safe_content_detected(self, agent):
        """Test that safe content is properly detected."""
        safe_texts = [
            "o que e uma variavel?",
            "como funciona um loop?",
            "quero aprender programacao",
            "a emilia e legal",
            "me ensina a fazer um jogo",
        ]
        for text in safe_texts:
            is_safe, _ = agent.is_content_safe(text)
            assert is_safe, f"'{text}' should be safe"

    @pytest.mark.unit
    def test_unsafe_content_blocked(self, agent):
        """Test that unsafe content is properly blocked."""
        unsafe_texts = [
            "como hackear um computador",
            "quero ver violencia",
            "fala sobre sexo",
            "como usar drogas",
            "quero matar alguem",
        ]
        for text in unsafe_texts:
            is_safe, _ = agent.is_content_safe(text)
            assert not is_safe, f"'{text}' should NOT be safe"

    @pytest.mark.unit
    def test_topic_allowed_programming(self, agent):
        """Test that programming topics are allowed."""
        programming_topics = [
            "o que e variavel",
            "como fazer um loop",
            "funcao em programacao",
            "logica de programacao",
            "como criar um jogo",
        ]
        for topic in programming_topics:
            assert agent.is_topic_allowed(topic), f"'{topic}' should be allowed"

    @pytest.mark.unit
    def test_topic_allowed_sitio_references(self, agent):
        """Test that Sitio do Picapau Amarelo references are allowed."""
        sitio_refs = [
            "emilia e muito legal",
            "pedrinho e aventureiro",
            "narizinho quer aprender",
            "visconde explica bem",
        ]
        for ref in sitio_refs:
            assert agent.is_topic_allowed(ref), f"'{ref}' should be allowed"


class TestAgentResponses:
    """Test agent response generation."""

    @pytest.fixture
    def agent(self):
        return KidsProgrammingAgent()

    @pytest.fixture
    def context(self):
        return AgentContext(
            investigation_id="test-001",
            user_id="kid-test",
            session_id="test-session",
        )

    @pytest.mark.unit
    def test_safe_redirect_response_exists(self, agent):
        """Test that safe redirect response is available."""
        response = agent._get_safe_redirect_response()
        assert len(response) > 100
        assert "programacao" in response.lower() or "sitio" in response.lower()

    @pytest.mark.unit
    def test_fallback_response_variable(self, agent):
        """Test fallback response for variable topic."""
        response = agent._get_fallback_response("o que e uma variavel?")
        assert "variavel" in response.lower() or "caixinha" in response.lower()
        assert "emilia" in response.lower()

    @pytest.mark.unit
    def test_fallback_response_loop(self, agent):
        """Test fallback response for loop topic."""
        response = agent._get_fallback_response("o que e um loop?")
        assert "loop" in response.lower() or "repet" in response.lower()
        assert "saci" in response.lower()

    @pytest.mark.unit
    def test_fallback_response_function(self, agent):
        """Test fallback response for function topic."""
        response = agent._get_fallback_response("o que e uma funcao?")
        assert "funcao" in response.lower() or "receita" in response.lower()
        assert "nastacia" in response.lower()

    @pytest.mark.unit
    def test_fallback_response_conditional(self, agent):
        """Test fallback response for conditional topic."""
        response = agent._get_fallback_response("o que e um if?")
        assert "se" in response.lower() or "senao" in response.lower()
        assert "pedrinho" in response.lower()

    @pytest.mark.unit
    def test_fallback_response_greeting(self, agent):
        """Test fallback response for greeting."""
        response = agent._get_fallback_response("ola!")
        assert "sitio" in response.lower() or "bem-vindo" in response.lower()

    @pytest.mark.unit
    def test_fallback_response_game(self, agent):
        """Test fallback response for game topic."""
        response = agent._get_fallback_response("quero fazer um jogo")
        assert "jogo" in response.lower()


class TestAgentProcess:
    """Test agent process method."""

    @pytest.fixture
    def agent(self):
        return KidsProgrammingAgent()

    @pytest.fixture
    def context(self):
        return AgentContext(
            investigation_id="process-test-001",
            user_id="kid-process-test",
            session_id="process-test-session",
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_safe_message(self, agent, context):
        """Test processing a safe message."""
        message = AgentMessage(
            action="chat",
            recipient="monteiro_lobato",
            payload={"message": "o que e uma variavel?"},
            sender="kid",
            metadata={},
        )

        response = await agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert response.agent_name == "monteiro_lobato"
        assert "response" in response.result
        assert response.result.get("safe_content") is True
        assert response.metadata.get("content_filtered") is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_unsafe_message_redirects(self, agent, context):
        """Test that unsafe messages are redirected to safe topics."""
        message = AgentMessage(
            action="chat",
            recipient="monteiro_lobato",
            payload={"message": "como hackear um computador"},
            sender="kid",
            metadata={},
        )

        response = await agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert response.result.get("safe_content") is True
        # Response should redirect to programming topics
        assert (
            "programacao" in response.result["response"].lower()
            or "sitio" in response.result["response"].lower()
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_empty_message(self, agent, context):
        """Test processing an empty message defaults to greeting."""
        message = AgentMessage(
            action="chat",
            recipient="monteiro_lobato",
            payload={"message": ""},
            sender="kid",
            metadata={},
        )

        response = await agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert "response" in response.result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_string_payload(self, agent, context):
        """Test processing with string payload instead of dict."""
        message = AgentMessage(
            action="chat",
            recipient="monteiro_lobato",
            payload="ola, quero aprender!",
            sender="kid",
            metadata={},
        )

        response = await agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert response.result is not None


class TestAgentAliases:
    """Test agent class aliases."""

    @pytest.mark.unit
    def test_monteiro_lobato_alias(self):
        """Test MonteiroLobatoAgent alias exists."""
        agent = MonteiroLobatoAgent()
        assert agent.name == "monteiro_lobato"

    @pytest.mark.unit
    def test_lobato_alias(self):
        """Test LobatoAgent alias exists."""
        agent = LobatoAgent()
        assert agent.name == "monteiro_lobato"


class TestAgentLifecycle:
    """Test agent lifecycle methods."""

    @pytest.fixture
    def agent(self):
        return KidsProgrammingAgent()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_initialize(self, agent):
        """Test agent initialization."""
        # Should not raise
        await agent.initialize()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_shutdown(self, agent):
        """Test agent shutdown."""
        # Should not raise
        await agent.shutdown()


class TestPersonalityPrompt:
    """Test personality prompt configuration."""

    @pytest.fixture
    def agent(self):
        return KidsProgrammingAgent()

    @pytest.mark.unit
    def test_personality_prompt_exists(self, agent):
        """Test that personality prompt is configured."""
        assert hasattr(agent, "personality_prompt")
        assert len(agent.personality_prompt) > 500  # Should be substantial

    @pytest.mark.unit
    def test_personality_prompt_has_rules(self, agent):
        """Test that personality prompt contains safety rules."""
        prompt = agent.personality_prompt.lower()
        assert "regras" in prompt or "nunca" in prompt
        assert "crianca" in prompt or "criancas" in prompt

    @pytest.mark.unit
    def test_personality_prompt_has_characters(self, agent):
        """Test that personality prompt mentions Sitio characters."""
        prompt = agent.personality_prompt.lower()
        assert "emilia" in prompt
        assert "pedrinho" in prompt
        assert "narizinho" in prompt
