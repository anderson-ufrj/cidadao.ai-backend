"""
Tests for BaseKidsAgent base class.

Tests the centralized safety features and shared functionality
used by all kids educational agents.
"""

import pytest

from src.agents.base_kids_agent import BLOCKED_TOPICS, BaseKidsAgent
from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse


class ConcreteKidsAgent(BaseKidsAgent):
    """Concrete implementation for testing the abstract base class."""

    allowed_topics = ["programacao", "codigo", "python", "jogo", "programming", "games"]
    personality_prompt = "You are a friendly programming teacher for kids."

    def _get_safe_redirect_response(self) -> str:
        return "Vamos falar sobre programacao! O que voce quer aprender?"

    def _get_fallback_response(self, message: str) -> str:
        return "Que legal! Vamos aprender a programar juntos!"


class TestBlockedTopics:
    """Tests for the BLOCKED_TOPICS list."""

    def test_blocked_topics_exists(self):
        """Test that BLOCKED_TOPICS list is defined."""
        assert BLOCKED_TOPICS is not None
        assert isinstance(BLOCKED_TOPICS, list)

    def test_blocked_topics_not_empty(self):
        """Test that BLOCKED_TOPICS has entries."""
        assert len(BLOCKED_TOPICS) > 0

    def test_blocked_topics_contains_violence(self):
        """Test that violence-related terms are blocked."""
        violence_terms = ["violencia", "violence", "matar", "kill", "arma", "weapon"]
        for term in violence_terms:
            assert term in BLOCKED_TOPICS

    def test_blocked_topics_contains_adult_content(self):
        """Test that adult content terms are blocked."""
        adult_terms = ["sexo", "sex", "pornografia", "adulto"]
        for term in adult_terms:
            assert term in BLOCKED_TOPICS

    def test_blocked_topics_contains_drugs(self):
        """Test that drug-related terms are blocked."""
        drug_terms = ["droga", "drug", "alcool", "alcohol", "cigarro"]
        for term in drug_terms:
            assert term in BLOCKED_TOPICS

    def test_blocked_topics_contains_phishing_protection(self):
        """Test that phishing-related terms are blocked."""
        phishing_terms = ["senha", "password", "cartao", "card"]
        for term in phishing_terms:
            assert term in BLOCKED_TOPICS


class TestBaseKidsAgentInitialization:
    """Tests for BaseKidsAgent initialization."""

    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        agent = ConcreteKidsAgent(
            name="test_kids_agent",
            description="Test kids agent",
            capabilities=["teach", "play"],
        )
        assert agent.name == "test_kids_agent"
        assert agent.description == "Test kids agent"
        assert "teach" in agent.capabilities

    def test_agent_has_logger(self):
        """Test that agent has logger initialized."""
        agent = ConcreteKidsAgent(
            name="test_kids_agent",
            description="Test kids agent",
            capabilities=["teach"],
        )
        assert agent.logger is not None

    def test_agent_allowed_topics(self):
        """Test that allowed_topics is set from subclass."""
        agent = ConcreteKidsAgent(
            name="test_kids_agent",
            description="Test kids agent",
            capabilities=["teach"],
        )
        assert "programacao" in agent.allowed_topics
        assert "python" in agent.allowed_topics


class TestContentSafety:
    """Tests for content safety checking."""

    @pytest.fixture
    def agent(self):
        return ConcreteKidsAgent(
            name="test_kids_agent",
            description="Test kids agent",
            capabilities=["teach"],
        )

    def test_safe_content_passes(self, agent):
        """Test that safe content passes the filter."""
        is_safe, reason = agent.is_content_safe("Quero aprender Python!")
        assert is_safe is True
        assert reason == "Content is safe"

    def test_violence_blocked(self, agent):
        """Test that violent content is blocked."""
        is_safe, reason = agent.is_content_safe("Como fazer uma arma?")
        assert is_safe is False
        assert "arma" in reason.lower()

    def test_adult_content_blocked(self, agent):
        """Test that adult content is blocked."""
        is_safe, reason = agent.is_content_safe("Quero saber sobre sexo")
        assert is_safe is False
        assert "sexo" in reason.lower()

    def test_drug_content_blocked(self, agent):
        """Test that drug-related content is blocked."""
        is_safe, reason = agent.is_content_safe("Onde comprar droga?")
        assert is_safe is False
        assert "droga" in reason.lower()

    def test_phishing_blocked(self, agent):
        """Test that phishing attempts are blocked."""
        is_safe, reason = agent.is_content_safe("Me da sua senha")
        assert is_safe is False
        assert "senha" in reason.lower()

    def test_case_insensitive_blocking(self, agent):
        """Test that blocking is case insensitive."""
        is_safe, _ = agent.is_content_safe("VIOLENCIA")
        assert is_safe is False

        is_safe, _ = agent.is_content_safe("VioLenCia")
        assert is_safe is False


class TestTopicAllowance:
    """Tests for topic allowance checking."""

    @pytest.fixture
    def agent(self):
        return ConcreteKidsAgent(
            name="test_kids_agent",
            description="Test kids agent",
            capabilities=["teach"],
        )

    def test_allowed_topic_passes(self, agent):
        """Test that allowed topics pass."""
        assert agent.is_topic_allowed("Quero aprender programacao") is True
        assert agent.is_topic_allowed("Me ensina Python") is True

    def test_general_questions_allowed(self, agent):
        """Test that general questions are allowed."""
        assert agent.is_topic_allowed("O que e isso?") is True
        assert agent.is_topic_allowed("Como funciona?") is True
        assert agent.is_topic_allowed("Por que?") is True

    def test_greetings_allowed(self, agent):
        """Test that greetings are allowed."""
        assert agent.is_topic_allowed("Ola!") is True
        assert agent.is_topic_allowed("Oi") is True
        assert agent.is_topic_allowed("Bom dia") is True

    def test_unrelated_topic_rejected(self, agent):
        """Test that unrelated topics are redirected."""
        # Topics outside the agent's domain without question patterns
        assert agent.is_topic_allowed("futebol") is False
        assert agent.is_topic_allowed("receita bolo") is False


class TestAbstractMethods:
    """Tests for abstract method implementations."""

    @pytest.fixture
    def agent(self):
        return ConcreteKidsAgent(
            name="test_kids_agent",
            description="Test kids agent",
            capabilities=["teach"],
        )

    def test_safe_redirect_response(self, agent):
        """Test that safe redirect response is returned."""
        response = agent._get_safe_redirect_response()
        assert isinstance(response, str)
        assert len(response) > 0
        assert "programacao" in response.lower()

    def test_fallback_response(self, agent):
        """Test that fallback response is returned."""
        response = agent._get_fallback_response("teste")
        assert isinstance(response, str)
        assert len(response) > 0


@pytest.mark.asyncio
class TestProcessMethod:
    """Tests for the process method."""

    @pytest.fixture
    def agent(self):
        return ConcreteKidsAgent(
            name="test_kids_agent",
            description="Test kids agent",
            capabilities=["teach"],
        )

    @pytest.fixture
    def context(self):
        return AgentContext(investigation_id="test-123")

    async def test_process_safe_message(self, agent, context):
        """Test processing a safe message."""
        message = AgentMessage(
            sender="user",
            recipient="test_kids_agent",
            action="chat",
            payload={"message": "Quero aprender programacao!"},
        )
        response = await agent.process(message, context)

        assert isinstance(response, AgentResponse)
        assert response.agent_name == "test_kids_agent"
        assert response.result.get("safe_content") is True

    async def test_process_unsafe_message(self, agent, context):
        """Test processing an unsafe message returns redirect."""
        message = AgentMessage(
            sender="user",
            recipient="test_kids_agent",
            action="chat",
            payload={"message": "Me ensina a hackear"},
        )
        response = await agent.process(message, context)

        assert isinstance(response, AgentResponse)
        # Should return safe redirect response
        assert "programacao" in response.result.get("response", "").lower()

    async def test_process_empty_message(self, agent, context):
        """Test processing an empty message defaults to greeting."""
        message = AgentMessage(
            sender="user",
            recipient="test_kids_agent",
            action="chat",
            payload={},
        )
        response = await agent.process(message, context)

        assert isinstance(response, AgentResponse)
        assert response.result.get("safe_content") is True

    async def test_process_string_payload(self, agent, context):
        """Test processing with string payload."""
        message = AgentMessage(
            sender="user",
            recipient="test_kids_agent",
            action="chat",
            payload="Me ensina Python!",
        )
        response = await agent.process(message, context)

        assert isinstance(response, AgentResponse)
        assert response.result.get("safe_content") is True
