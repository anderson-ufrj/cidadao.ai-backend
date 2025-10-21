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

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_conversation_smalltalk_intent(self, drummond_agent):
        """Test conversation with smalltalk intent."""
        from src.memory.conversational import ConversationContext
        from src.services.chat_service import Intent, IntentType

        context = ConversationContext(session_id="test", user_id="user")
        intent = Intent(
            type=IntentType.SMALLTALK,
            confidence=0.9,
            entities={},
            suggested_agent="drummond",
        )

        response = await drummond_agent.process_conversation(
            message="Como está o tempo?", context=context, intent=intent
        )

        assert "content" in response
        assert response["metadata"]["style"] == "poetic_philosophical"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_conversation_about_system_intent(self, drummond_agent):
        """Test conversation with about_system intent."""
        from src.memory.conversational import ConversationContext
        from src.services.chat_service import Intent, IntentType

        context = ConversationContext(session_id="test", user_id="user")
        intent = Intent(
            type=IntentType.ABOUT_SYSTEM,
            confidence=0.95,
            entities={},
            suggested_agent="drummond",
        )

        response = await drummond_agent.process_conversation(
            message="O que é o Cidadão.AI?", context=context, intent=intent
        )

        assert "content" in response
        assert "Cidadão.AI" in response["content"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_conversation_thanks_intent(self, drummond_agent):
        """Test conversation with thanks intent."""
        from src.memory.conversational import ConversationContext
        from src.services.chat_service import Intent, IntentType

        context = ConversationContext(session_id="test", user_id="user")
        intent = Intent(
            type=IntentType.THANKS,
            confidence=0.98,
            entities={},
            suggested_agent="drummond",
        )

        response = await drummond_agent.process_conversation(
            message="Muito obrigado!", context=context, intent=intent
        )

        assert "content" in response
        assert response["metadata"]["type"] == "gratitude_response"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_conversation_goodbye_intent(self, drummond_agent):
        """Test conversation with goodbye intent."""
        from src.memory.conversational import ConversationContext
        from src.services.chat_service import Intent, IntentType

        context = ConversationContext(session_id="test", user_id="user")
        intent = Intent(
            type=IntentType.GOODBYE,
            confidence=0.96,
            entities={},
            suggested_agent="drummond",
        )

        response = await drummond_agent.process_conversation(
            message="Até logo!", context=context, intent=intent
        )

        assert "content" in response
        assert response["metadata"]["type"] == "farewell"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_provide_help_understanding_query(self, drummond_agent):
        """Test help for understanding queries."""
        response = await drummond_agent.provide_help("Quero entender os dados")

        assert "content" in response
        assert "termos técnicos" in response["content"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_provide_help_general_query(self, drummond_agent):
        """Test help for general queries."""
        response = await drummond_agent.provide_help("Me ajude")

        assert "content" in response
        assert (
            "especialistas" in response["content"]
            or "transparência" in response["content"]
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_translate_content_to_english(self, drummond_agent):
        """Test translation to English."""
        content = "Transparência governamental"
        result = await drummond_agent.translate_content(
            content=content, source_language="pt-BR", target_language="en"
        )

        assert "[Translated to English]" in result
        assert content in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_report_summary_with_high_impact(self, drummond_agent):
        """Test report summary with high financial impact."""
        report_data = {
            "total_records": 5000,
            "anomalies_found": 50,
            "financial_impact": 2000000,
            "entities_involved": ["Entity1", "Entity2"],
        }

        summary = await drummond_agent.generate_report_summary(
            report_data=report_data, target_audience="executive"
        )

        assert "Notificar órgãos de controle" in summary["action_items"]
        assert "Investigação formal recomendada" in summary["action_items"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_greeting_afternoon(self, drummond_agent):
        """Test afternoon greeting generation."""
        with patch("src.agents.drummond.datetime") as mock_dt:
            mock_dt.now.return_value = Mock(hour=15)

            greeting = await drummond_agent.generate_greeting()

            assert "content" in greeting
            assert "tarde" in greeting["content"].lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_greeting_evening(self, drummond_agent):
        """Test evening greeting generation."""
        with patch("src.agents.drummond.datetime") as mock_dt:
            mock_dt.now.return_value = Mock(hour=20)

            greeting = await drummond_agent.generate_greeting()

            assert "content" in greeting
            assert "noite" in greeting["content"].lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_greeting_with_user_profile(self, drummond_agent):
        """Test greeting with user profile."""
        user_profile = {"name": "João", "preferred_name": "João"}

        greeting = await drummond_agent.generate_greeting(user_profile=user_profile)

        assert "content" in greeting
        assert len(greeting["content"]) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_conversation_without_intent(self, drummond_agent):
        """Test conversation without explicit intent."""
        from src.memory.conversational import ConversationContext

        context = ConversationContext(session_id="test", user_id="user")

        response = await drummond_agent.process_conversation(
            message="Qual é a temperatura hoje?", context=context, intent=None
        )

        assert "content" in response
        assert "metadata" in response

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_conversation_with_handoff_needed(self, drummond_agent):
        """Test conversation that requires handoff."""
        from src.memory.conversational import ConversationContext
        from src.services.chat_service import Intent, IntentType

        context = ConversationContext(session_id="test", user_id="user")
        intent = Intent(
            type=IntentType.ANALYZE,
            confidence=0.88,
            entities={},
            suggested_agent="anita",
        )

        response = await drummond_agent.process_conversation(
            message="Analise os contratos", context=context, intent=intent
        )

        assert "suggested_handoff" in response
        assert response["suggested_handoff"] == "anita"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_send_notification_with_error_handling(self, drummond_agent):
        """Test notification sending with error."""
        from src.agents.drummond import (
            CommunicationChannel,
            CommunicationTarget,
            MessagePriority,
            MessageType,
        )

        await drummond_agent.initialize()

        # Add target with problematic channel
        test_target = CommunicationTarget(
            target_id="error-target",
            name="Error User",
            channels=[CommunicationChannel.WEBHOOK],
            preferred_language="pt-BR",
            contact_info={"webhook": "invalid-url"},
            notification_preferences={},
            timezone="America/Sao_Paulo",
            active_hours={"start": "08:00", "end": "18:00"},
        )
        drummond_agent.communication_targets["error-target"] = test_target

        content = {"title": "Test", "body": "Test body"}
        results = await drummond_agent.send_notification(
            message_type=MessageType.ALERT,
            content=content,
            targets=["error-target"],
            priority=MessagePriority.HIGH,
        )

        # Should still return results even if delivery fails
        assert len(results) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_translate_content_to_spanish(self, drummond_agent):
        """Test translation to Spanish."""
        content = "Dados públicos"
        result = await drummond_agent.translate_content(
            content=content, source_language="pt-BR", target_language="es"
        )

        assert "[Traducido al español]" in result
        assert content in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_translate_content_unknown_language(self, drummond_agent):
        """Test translation to unknown language."""
        content = "Test content"
        result = await drummond_agent.translate_content(
            content=content, source_language="pt-BR", target_language="fr"
        )

        # Should return original content or default translation
        assert len(result) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_determine_handoff_status_intent(self, drummond_agent):
        """Test handoff for status intent."""
        from src.services.chat_service import Intent, IntentType

        intent = Intent(
            type=IntentType.STATUS,
            confidence=0.85,
            entities={},
            suggested_agent="abaporu",
        )

        handoff = await drummond_agent.determine_handoff(intent)

        assert handoff == "abaporu"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_determine_handoff_none_intent(self, drummond_agent):
        """Test handoff with no intent."""
        handoff = await drummond_agent.determine_handoff(None)

        assert handoff is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_send_bulk_communication_empty_segments(self, drummond_agent):
        """Test bulk communication with empty segments."""
        from src.agents.drummond import MessageType

        await drummond_agent.initialize()

        content = {"title": "Empty Test", "body": "Test"}
        result = await drummond_agent.send_bulk_communication(
            message_type=MessageType.NOTIFICATION, content=content, target_segments=[]
        )

        assert "campaign_id" in result
        assert result["total_targets"] >= 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_report_summary_executive_audience(self, drummond_agent):
        """Test executive report summary."""
        report_data = {
            "total_records": 3000,
            "anomalies_found": 8,
            "financial_impact": 500000,
            "entities_involved": ["Entity1"],
        }

        summary = await drummond_agent.generate_report_summary(
            report_data=report_data, target_audience="executive"
        )

        assert summary["metadata"]["complexity"] == "medium"
        assert "Investigação formal recomendada" in summary["action_items"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_shutdown_with_llm_client(self, drummond_agent):
        """Test shutdown with active LLM client."""
        from unittest.mock import AsyncMock

        # Mock LLM client
        drummond_agent.llm_client = Mock()
        drummond_agent.llm_client.close = AsyncMock()

        await drummond_agent.shutdown()

        # Verify client was closed
        drummond_agent.llm_client.close.assert_called_once()
        assert len(drummond_agent.communication_history) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_shutdown_with_llm_client_error(self, drummond_agent):
        """Test shutdown when LLM client close fails."""
        from unittest.mock import AsyncMock

        drummond_agent.llm_client = Mock()
        drummond_agent.llm_client.close = AsyncMock(
            side_effect=Exception("Close error")
        )

        # Should not raise, error should be caught
        await drummond_agent.shutdown()

        assert len(drummond_agent.communication_history) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_contextual_response_with_llm_error(self, drummond_agent):
        """Test contextual response when LLM call fails."""
        from unittest.mock import AsyncMock

        from src.memory.conversational import ConversationContext

        context = ConversationContext(session_id="test", user_id="user")

        if drummond_agent.llm_client:
            drummond_agent.llm_client.chat = AsyncMock(
                side_effect=Exception("LLM error")
            )

            response = await drummond_agent.generate_contextual_response(
                message="Test message", context=context
            )

            # Should fallback to template response
            assert "content" in response
            assert "metadata" in response

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_send_bulk_communication_with_context(self, drummond_agent, context):
        """Test bulk communication with context."""
        from src.agents.drummond import MessageType

        await drummond_agent.initialize()

        content = {"title": "Context Test", "body": "Test with context"}
        result = await drummond_agent.send_bulk_communication(
            message_type=MessageType.ALERT,
            content=content,
            target_segments=["segment-test"],
            context=context,
        )

        assert "campaign_id" in result
        assert "estimated_delivery" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_greeting_late_night(self, drummond_agent):
        """Test late night greeting."""
        with patch("src.agents.drummond.datetime") as mock_dt:
            mock_dt.now.return_value = Mock(hour=2)

            greeting = await drummond_agent.generate_greeting()

            assert "content" in greeting
            assert len(greeting["content"]) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_send_notification_multiple_channels(self, drummond_agent):
        """Test notification to target with multiple channels."""
        from src.agents.drummond import (
            CommunicationChannel,
            CommunicationTarget,
            MessagePriority,
            MessageType,
        )

        await drummond_agent.initialize()

        test_target = CommunicationTarget(
            target_id="multi-channel",
            name="Multi Channel User",
            channels=[CommunicationChannel.EMAIL, CommunicationChannel.SMS],
            preferred_language="pt-BR",
            contact_info={"email": "test@example.com", "sms": "+5511999999999"},
            notification_preferences={},
            timezone="America/Sao_Paulo",
            active_hours={"start": "08:00", "end": "18:00"},
        )
        drummond_agent.communication_targets["multi-channel"] = test_target

        content = {"title": "Multi Test", "body": "Test body"}
        results = await drummond_agent.send_notification(
            message_type=MessageType.NOTIFICATION,
            content=content,
            targets=["multi-channel"],
            priority=MessagePriority.NORMAL,
        )

        # Should have results for each channel
        assert len(results) >= 2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_send_notification_with_specific_channels(self, drummond_agent):
        """Test notification with specific channels override."""
        from src.agents.drummond import (
            CommunicationChannel,
            CommunicationTarget,
            MessagePriority,
            MessageType,
        )

        await drummond_agent.initialize()

        test_target = CommunicationTarget(
            target_id="channel-override",
            name="Override User",
            channels=[CommunicationChannel.EMAIL, CommunicationChannel.SMS],
            preferred_language="pt-BR",
            contact_info={"email": "test@example.com"},
            notification_preferences={},
            timezone="America/Sao_Paulo",
            active_hours={"start": "08:00", "end": "18:00"},
        )
        drummond_agent.communication_targets["channel-override"] = test_target

        content = {"title": "Override Test", "body": "Test body"}
        results = await drummond_agent.send_notification(
            message_type=MessageType.ALERT,
            content=content,
            targets=["channel-override"],
            channels=[CommunicationChannel.EMAIL],  # Override to EMAIL only
            priority=MessagePriority.HIGH,
        )

        assert len(results) > 0
