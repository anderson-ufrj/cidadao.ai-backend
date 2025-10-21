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

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_send_bulk_communication(self, drummond_agent):
        """Test bulk communication sending."""
        from src.agents.drummond import MessageType

        await drummond_agent.initialize()

        content = {"title": "Campaign", "body": "Campaign message"}
        target_segments = ["segment-1", "segment-2"]

        result = await drummond_agent.send_bulk_communication(
            message_type=MessageType.NOTIFICATION,
            content=content,
            target_segments=target_segments,
        )

        assert "campaign_id" in result
        assert result["segments"] == target_segments
        assert "scheduled_messages" in result
        assert "optimal_send_time" in result
        assert result["total_targets"] >= 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_report_summary_technical(self, drummond_agent):
        """Test report summary generation for technical audience."""
        report_data = {
            "total_records": 1500,
            "anomalies_found": 12,
            "financial_impact": 250000.50,
            "entities_involved": ["Entity1", "Entity2", "Entity3"],
        }

        summary = await drummond_agent.generate_report_summary(
            report_data=report_data, target_audience="technical"
        )

        assert "executive_summary" in summary
        assert "12" in summary["executive_summary"]
        assert "key_findings" in summary
        assert "action_items" in summary
        assert summary["metadata"]["audience"] == "technical"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_report_summary_citizen(self, drummond_agent):
        """Test report summary generation for citizen audience."""
        report_data = {
            "total_records": 100,
            "anomalies_found": 2,
            "financial_impact": 5000,
            "entities_involved": [],
        }

        summary = await drummond_agent.generate_report_summary(
            report_data=report_data, target_audience="citizen"
        )

        assert summary["metadata"]["complexity"] == "low"
        assert "citizen_impact" in summary
        assert "direito de saber" in summary["citizen_impact"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_translate_content_same_language(self, drummond_agent):
        """Test translation with same source and target language."""
        content = "Este é um teste"
        result = await drummond_agent.translate_content(
            content=content, source_language="pt-BR", target_language="pt-BR"
        )

        assert result == content

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_provide_help_investigation(self, drummond_agent):
        """Test help provision for investigation queries."""
        response = await drummond_agent.provide_help("Como investigar contratos?")

        assert "content" in response
        assert "Zumbi dos Palmares" in response["content"]
        assert response["metadata"]["help_type"] == "contextual"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_thanks(self, drummond_agent):
        """Test handling thank you messages."""
        response = await drummond_agent.handle_thanks()

        assert "content" in response
        assert "metadata" in response
        assert response["metadata"]["type"] == "gratitude_response"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_goodbye(self, drummond_agent):
        """Test handling goodbye messages."""
        response = await drummond_agent.handle_goodbye()

        assert "content" in response
        assert response["metadata"]["type"] == "farewell"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_contextual_response_fallback(self, drummond_agent):
        """Test contextual response fallback without LLM."""
        from src.memory.conversational import ConversationContext

        drummond_agent.llm_client = None
        context = ConversationContext(session_id="test-sess", user_id="test-user")

        response = await drummond_agent.generate_contextual_response(
            message="Teste de fallback", context=context
        )

        assert "content" in response
        assert "metadata" in response
        assert response["metadata"]["fallback"] is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_conversation_help_intent(self, drummond_agent):
        """Test conversation processing with help intent."""
        from src.memory.conversational import ConversationContext
        from src.services.chat_service import Intent, IntentType

        context = ConversationContext(session_id="test-session", user_id="test-user")

        intent = Intent(
            type=IntentType.HELP_REQUEST,
            confidence=0.95,
            entities={},
            suggested_agent="drummond",
        )

        response = await drummond_agent.process_conversation(
            message="Preciso de ajuda", context=context, intent=intent
        )

        assert "content" in response
        assert len(response["content"]) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_determine_handoff_low_confidence(self, drummond_agent):
        """Test handoff determination with low confidence."""
        from src.services.chat_service import Intent, IntentType

        intent = Intent(
            type=IntentType.INVESTIGATE,
            confidence=0.5,
            entities={},
            suggested_agent="zumbi",
        )

        handoff = await drummond_agent.determine_handoff(intent)

        assert handoff is None
