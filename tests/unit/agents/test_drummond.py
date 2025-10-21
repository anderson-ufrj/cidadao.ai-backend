"""
Unit tests for Drummond Communication Agent - Carlos Drummond de Andrade.

Author: Anderson H. Silva
Date: 2025-10-12
"""

from unittest.mock import Mock, patch

import pytest

from src.agents.deodoro import AgentContext
from src.agents.drummond import CommunicationAgent
from src.services.chat_service import Intent, IntentType


@pytest.fixture
def drummond_agent():
    """Create Drummond agent instance."""
    return CommunicationAgent()


@pytest.fixture
def context():
    """Create agent context."""
    return AgentContext(
        investigation_id="test-inv", session_id="test-session", user_id="test-user"
    )


class TestDrummondAgent:
    """Test suite for Drummond Communication Agent."""

    @pytest.mark.unit
    def test_agent_initialization(self, drummond_agent):
        """Test agent initializes correctly."""
        assert drummond_agent.name == "drummond"
        assert "process_chat" in drummond_agent.capabilities
        assert "send_notification" in drummond_agent.capabilities
        assert drummond_agent.communication_config["max_daily_messages_per_user"] == 10

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_greeting_morning(self, drummond_agent):
        """Test morning greeting generation."""
        with patch("src.agents.drummond.datetime") as mock_dt:
            mock_dt.now.return_value = Mock(hour=9)

            greeting = await drummond_agent.generate_greeting()

            assert "content" in greeting
            assert "metadata" in greeting
            assert len(greeting["content"]) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_smalltalk(self, drummond_agent):
        """Test smalltalk handling."""
        response = await drummond_agent.handle_smalltalk("Como está o tempo?")

        assert "content" in response
        assert "metadata" in response
        assert response["metadata"]["style"] == "poetic_philosophical"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_explain_system(self, drummond_agent):
        """Test system explanation."""
        explanation = await drummond_agent.explain_system()

        assert "content" in explanation
        assert "Cidadão.AI" in explanation["content"]
        assert "metadata" in explanation

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_determine_handoff_investigate(self, drummond_agent):
        """Test handoff determination for investigation."""
        intent = Intent(
            type=IntentType.INVESTIGATE,
            confidence=0.9,
            entities={},
            suggested_agent="zumbi",
        )

        handoff = await drummond_agent.determine_handoff(intent)

        assert handoff == "zumbi"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_chat_greeting(self, drummond_agent):
        """Test processing conversational greeting."""
        from src.memory.conversational import ConversationContext
        from src.services.chat_service import Intent, IntentType

        conv_context = ConversationContext(
            session_id="test-session", user_id="test-user"
        )

        intent = Intent(
            type=IntentType.GREETING,
            confidence=0.95,
            entities={},
            suggested_agent="drummond",
        )

        response = await drummond_agent.process_conversation(
            message="Oi", context=conv_context, intent=intent
        )

        assert "content" in response
        assert len(response["content"]) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_initialize(self, drummond_agent):
        """Test agent initialization."""
        await drummond_agent.initialize()

        # Verify templates are loaded (system loads 7 templates including alert_template)
        assert "alert_template" in drummond_agent.message_templates
        assert (
            len(drummond_agent.message_templates) >= 4
        )  # At least core templates loaded

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_shutdown(self, drummond_agent):
        """Test agent shutdown."""
        await drummond_agent.shutdown()

        assert len(drummond_agent.communication_history) == 0
