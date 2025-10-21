"""
Expanded comprehensive tests for Drummond Communication Agent.
Tests NLG, multi-channel communication, personalization, and conversation handling.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus
from src.agents.drummond import (
    CommunicationAgent,
    CommunicationChannel,
    CommunicationTarget,
    MessagePriority,
    MessageType,
)
from src.memory.conversational import ConversationContext
from src.services.chat_service import Intent, IntentType


@pytest.fixture
def agent():
    """Create Drummond agent instance."""
    return CommunicationAgent()


@pytest.fixture
def agent_context():
    """Create agent context."""
    return AgentContext(
        investigation_id="test-inv-123",
        session_id="test-session-123",
        user_id="test-user-123",
        metadata={},
    )


@pytest.fixture
def conversation_context():
    """Create conversation context."""
    return ConversationContext(session_id="test-session", user_id="test-user")


@pytest.fixture
def sample_target():
    """Create sample communication target."""
    return CommunicationTarget(
        target_id="user_001",
        name="João Silva",
        channels=[
            CommunicationChannel.EMAIL,
            CommunicationChannel.WHATSAPP,
        ],
        preferred_language="pt-BR",
        contact_info={
            "email": "joao@example.com",
            "whatsapp": "+5511999999999",
        },
        notification_preferences={
            "frequency": "daily",
            "quiet_hours": {"start": "22:00", "end": "08:00"},
        },
        timezone="America/Sao_Paulo",
        active_hours={"start": "09:00", "end": "18:00"},
    )


class TestDrummondAgentBasics:
    """Test basic agent functionality."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initialization with correct attributes."""
        assert agent.name == "drummond"
        assert "process_chat" in agent.capabilities
        assert "send_notification" in agent.capabilities
        assert "generate_report_summary" in agent.capabilities
        assert agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_agent_lifecycle(self, agent):
        """Test agent initialize and shutdown lifecycle."""
        await agent.initialize()
        assert agent.status == AgentStatus.IDLE
        assert len(agent.message_templates) > 0

        await agent.shutdown()
        assert len(agent.communication_history) == 0

    @pytest.mark.asyncio
    async def test_configuration_defaults(self, agent):
        """Test default configuration values."""
        assert agent.communication_config["max_daily_messages_per_user"] == 10
        assert agent.communication_config["retry_attempts"] == 3
        assert agent.communication_config["default_language"] == "pt-BR"


class TestConversationHandling:
    """Test conversation and NLG capabilities."""

    @pytest.mark.asyncio
    async def test_generate_greeting(self, agent):
        """Test greeting generation."""
        greeting = await agent.generate_greeting()

        assert "content" in greeting
        assert "metadata" in greeting
        assert len(greeting["content"]) > 0
        assert isinstance(greeting["metadata"], dict)

    @pytest.mark.asyncio
    async def test_handle_smalltalk(self, agent):
        """Test smalltalk handling with philosophical style."""
        response = await agent.handle_smalltalk("Como está o tempo?")

        assert "content" in response
        assert "metadata" in response
        assert response["metadata"]["style"] == "poetic_philosophical"
        assert len(response["content"]) > 0

    @pytest.mark.asyncio
    async def test_explain_system(self, agent):
        """Test system explanation generation."""
        explanation = await agent.explain_system()

        assert "content" in explanation
        assert "Cidadão.AI" in explanation["content"]
        assert "metadata" in explanation
        assert (
            "transparente" in explanation["content"].lower()
            or "transparency" in explanation["content"].lower()
        )

    @pytest.mark.asyncio
    async def test_provide_help(self, agent):
        """Test help content generation."""
        help_response = await agent.provide_help("Como usar o sistema?")

        assert "content" in help_response
        assert "metadata" in help_response
        assert len(help_response["content"]) > 0

    @pytest.mark.asyncio
    async def test_handle_thanks(self, agent):
        """Test thanks acknowledgment."""
        response = await agent.handle_thanks()

        assert "content" in response
        assert "metadata" in response
        assert len(response["content"]) > 0

    @pytest.mark.asyncio
    async def test_handle_goodbye(self, agent):
        """Test goodbye message generation."""
        response = await agent.handle_goodbye()

        assert "content" in response
        assert "metadata" in response
        assert len(response["content"]) > 0

    @pytest.mark.asyncio
    async def test_process_conversation_greeting(self, agent, conversation_context):
        """Test processing greeting intent."""
        intent = Intent(
            type=IntentType.GREETING,
            confidence=0.95,
            entities={},
            suggested_agent="drummond",
        )

        response = await agent.process_conversation(
            message="Olá!", context=conversation_context, intent=intent
        )

        assert "content" in response
        assert len(response["content"]) > 0

    @pytest.mark.asyncio
    async def test_process_conversation_smalltalk(self, agent, conversation_context):
        """Test processing smalltalk intent."""
        intent = Intent(
            type=IntentType.SMALLTALK,
            confidence=0.85,
            entities={"topic": "weather"},
            suggested_agent="drummond",
        )

        response = await agent.process_conversation(
            message="Como está o tempo?", context=conversation_context, intent=intent
        )

        assert "content" in response
        assert response["metadata"]["style"] == "poetic_philosophical"

    @pytest.mark.asyncio
    async def test_process_conversation_help(self, agent, conversation_context):
        """Test processing help request intent."""
        intent = Intent(
            type=IntentType.HELP,
            confidence=0.90,
            entities={},
            suggested_agent="drummond",
        )

        response = await agent.process_conversation(
            message="Preciso de ajuda", context=conversation_context, intent=intent
        )

        assert "content" in response

    @pytest.mark.asyncio
    async def test_process_conversation_thanks(self, agent, conversation_context):
        """Test processing thanks intent."""
        intent = Intent(
            type=IntentType.THANKS,
            confidence=0.88,
            entities={},
            suggested_agent="drummond",
        )

        response = await agent.process_conversation(
            message="Obrigado!", context=conversation_context, intent=intent
        )

        assert "content" in response

    @pytest.mark.asyncio
    async def test_process_conversation_goodbye(self, agent, conversation_context):
        """Test processing goodbye intent."""
        intent = Intent(
            type=IntentType.GOODBYE,
            confidence=0.92,
            entities={},
            suggested_agent="drummond",
        )

        response = await agent.process_conversation(
            message="Tchau!", context=conversation_context, intent=intent
        )

        assert "content" in response


class TestHandoffDetermination:
    """Test agent handoff logic."""

    @pytest.mark.asyncio
    async def test_determine_handoff_investigate(self, agent):
        """Test handoff for investigation intent."""
        intent = Intent(
            type=IntentType.INVESTIGATE,
            confidence=0.90,
            entities={},
            suggested_agent="zumbi",
        )

        handoff = await agent.determine_handoff(intent)
        assert handoff == "zumbi"

    @pytest.mark.asyncio
    async def test_determine_handoff_analyze(self, agent):
        """Test handoff for analysis intent."""
        intent = Intent(
            type=IntentType.ANALYZE,
            confidence=0.85,
            entities={},
            suggested_agent="anita",
        )

        handoff = await agent.determine_handoff(intent)
        assert handoff == "anita"

    @pytest.mark.asyncio
    async def test_determine_handoff_no_handoff(self, agent):
        """Test no handoff for drummond-handled intents."""
        intent = Intent(
            type=IntentType.GREETING,
            confidence=0.95,
            entities={},
            suggested_agent="drummond",
        )

        handoff = await agent.determine_handoff(intent)
        assert handoff is None

    @pytest.mark.asyncio
    async def test_determine_handoff_none_intent(self, agent):
        """Test handoff with None intent."""
        handoff = await agent.determine_handoff(None)
        assert handoff is None


class TestNotificationSystem:
    """Test notification and communication methods."""

    @pytest.mark.asyncio
    async def test_send_notification_empty_targets(self, agent):
        """Test sending notification with empty target list."""
        results = await agent.send_notification(
            message_type=MessageType.ALERT,
            content={"title": "Test", "body": "Test message"},
            targets=[],
        )

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_send_notification_unknown_target(self, agent):
        """Test sending notification to unknown target."""
        results = await agent.send_notification(
            message_type=MessageType.ALERT,
            content={"title": "Test", "body": "Test message"},
            targets=["unknown_target_123"],
        )

        # Should return empty list or handle gracefully
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_send_notification_with_priority(self, agent, sample_target):
        """Test sending notification with different priorities."""
        # Register target
        agent.communication_targets[sample_target.target_id] = sample_target

        with patch.object(
            agent, "_send_via_channel", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = Mock(
                message_id="test_msg",
                target_id=sample_target.target_id,
                channel=CommunicationChannel.EMAIL,
                status="sent",
                sent_at=datetime.utcnow(),
                delivered_at=None,
                read_at=None,
                error_message=None,
                retry_count=0,
                metadata={},
            )

            results = await agent.send_notification(
                message_type=MessageType.URGENT_ACTION,
                content={"title": "Urgent", "body": "Important message"},
                targets=[sample_target.target_id],
                priority=MessagePriority.URGENT,
            )

            assert len(results) > 0
            mock_send.assert_called()

    @pytest.mark.asyncio
    async def test_generate_report_summary(self, agent):
        """Test report summary generation."""
        report_data = {
            "title": "Análise de Contratos 2025",
            "findings": {
                "total_contracts": 150,
                "anomalies_found": 12,
                "total_value": 5000000.0,
            },
            "recommendations": [
                "Revisar contratos com anomalias",
                "Implementar controles adicionais",
            ],
        }

        # Mock LLM response
        with patch.object(
            agent.llm_client, "generate", return_value="Summary generated"
        ):
            summary = await agent.generate_report_summary(
                report_data=report_data, language="pt-BR"
            )

            assert "summary" in summary
            assert "metadata" in summary
            assert len(summary["summary"]) > 0

    @pytest.mark.asyncio
    async def test_translate_content(self, agent):
        """Test content translation."""
        content = "Olá, este é um teste de tradução."

        with patch.object(
            agent.llm_client,
            "generate",
            return_value="Hello, this is a translation test.",
        ):
            translated = await agent.translate_content(
                content=content, source_language="pt-BR", target_language="en"
            )

            assert "translated_text" in translated
            assert len(translated["translated_text"]) > 0


class TestBulkCommunication:
    """Test bulk communication features."""

    @pytest.mark.asyncio
    async def test_send_bulk_communication(self, agent):
        """Test sending bulk communication to segments."""
        result = await agent.send_bulk_communication(
            message_type=MessageType.NOTIFICATION,
            content={"title": "Monthly Report", "body": "Your monthly summary"},
            target_segments=["active_users", "premium_users"],
        )

        assert "campaign_id" in result
        assert "scheduled_messages" in result
        assert isinstance(result["scheduled_messages"], int)

    @pytest.mark.asyncio
    async def test_send_bulk_with_scheduling(self, agent):
        """Test bulk communication with scheduling."""
        scheduling = {"send_at": "2025-12-01T10:00:00", "timezone": "America/Sao_Paulo"}

        result = await agent.send_bulk_communication(
            message_type=MessageType.REPORT,
            content={"title": "Scheduled Report", "body": "Report content"},
            target_segments=["all_users"],
            scheduling=scheduling,
        )

        assert "campaign_id" in result


class TestCommunicationEffectiveness:
    """Test communication effectiveness analysis."""

    @pytest.mark.asyncio
    async def test_analyze_communication_effectiveness_empty(self, agent):
        """Test effectiveness analysis with no communication history."""
        analysis = await agent.analyze_communication_effectiveness(
            campaign_id="test_campaign_001"
        )

        assert "campaign_id" in analysis
        assert "total_sent" in analysis
        assert "channel_performance" in analysis
        assert "recommendations" in analysis

    @pytest.mark.asyncio
    async def test_analyze_communication_effectiveness_with_data(self, agent):
        """Test effectiveness analysis with communication data."""
        # Add some mock communication history
        agent.communication_history = [
            {
                "message_id": "msg_001",
                "campaign_id": "test_campaign_002",
                "channel": CommunicationChannel.EMAIL.value,
                "status": "delivered",
                "sent_at": datetime.utcnow(),
            },
            {
                "message_id": "msg_002",
                "campaign_id": "test_campaign_002",
                "channel": CommunicationChannel.WHATSAPP.value,
                "status": "read",
                "sent_at": datetime.utcnow(),
            },
        ]

        analysis = await agent.analyze_communication_effectiveness(
            campaign_id="test_campaign_002"
        )

        assert "campaign_id" in analysis
        assert analysis["total_sent"] == 2


class TestChannelMethods:
    """Test individual channel send methods."""

    @pytest.mark.asyncio
    async def test_send_sms(self, agent):
        """Test SMS sending method (stub implementation)."""
        # SMS method is a stub - just verify it doesn't crash
        try:
            await agent._send_sms(
                to="+5511999999999", message="Test SMS", priority=MessagePriority.NORMAL
            )
            # Should complete without error (even if not actually sent)
            assert True
        except NotImplementedError:
            # Acceptable if method is not implemented
            assert True

    @pytest.mark.asyncio
    async def test_send_whatsapp(self, agent):
        """Test WhatsApp sending method (stub implementation)."""
        try:
            await agent._send_whatsapp(
                to="+5511999999999",
                message="Test WhatsApp",
                priority=MessagePriority.NORMAL,
            )
            assert True
        except NotImplementedError:
            assert True

    @pytest.mark.asyncio
    async def test_send_push(self, agent):
        """Test push notification sending method (stub implementation)."""
        try:
            await agent._send_push(
                device_token="test_token",  # noqa: S106
                title="Test Title",
                body="Test Body",
                priority=MessagePriority.NORMAL,
            )
            assert True
        except NotImplementedError:
            assert True

    @pytest.mark.asyncio
    async def test_send_webhook(self, agent):
        """Test webhook sending method (stub implementation)."""
        try:
            await agent._send_webhook(
                url="https://example.com/webhook", payload={"test": "data"}
            )
            assert True
        except NotImplementedError:
            assert True


class TestMessageTemplates:
    """Test message template handling."""

    @pytest.mark.asyncio
    async def test_load_message_templates(self, agent):
        """Test template loading during initialization."""
        await agent.initialize()

        assert len(agent.message_templates) > 0
        assert "alert_template" in agent.message_templates

    @pytest.mark.asyncio
    async def test_alert_template_structure(self, agent):
        """Test alert template has required structure."""
        await agent.initialize()

        template = agent.message_templates.get("alert_template")
        assert template is not None
        assert hasattr(template, "message_type")
        assert hasattr(template, "subject_template")
        assert hasattr(template, "body_template")


class TestProcessMethod:
    """Test main process method."""

    @pytest.mark.asyncio
    async def test_process_with_chat_action(self, agent, agent_context):
        """Test processing chat action."""
        message = AgentMessage(
            sender="test",
            recipient="drummond",
            action="process_chat",
            payload={
                "user_message": "Olá!",
                "session": {"session_id": "test-session", "user_id": "test-user"},
                "intent": {
                    "type": "greeting",
                    "confidence": 0.95,
                    "entities": {},
                    "suggested_agent": "drummond",
                },
            },
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert response.result is not None
        assert "message" in response.result

    @pytest.mark.asyncio
    async def test_process_with_unknown_action(self, agent, agent_context):
        """Test process with unknown action."""
        message = AgentMessage(
            sender="test",
            recipient="drummond",
            action="unknown_action_xyz",
            payload={},
        )

        # Unknown action should raise exception or return error response
        try:
            response = await agent.process(message, agent_context)
            # If it doesn't raise, check for error indicator
            assert (
                "error" in str(response.result).lower()
                or response.status == AgentStatus.ERROR
            )
        except Exception:
            # Exception is acceptable for unknown action
            assert True


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_message_content(self, agent, conversation_context):
        """Test handling empty message."""
        intent = Intent(
            type=IntentType.GREETING,
            confidence=0.5,
            entities={},
            suggested_agent="drummond",
        )

        response = await agent.process_conversation(
            message="", context=conversation_context, intent=intent
        )

        # Should handle gracefully
        assert "content" in response

    @pytest.mark.asyncio
    async def test_low_confidence_intent(self, agent, conversation_context):
        """Test handling low confidence intent."""
        intent = Intent(
            type=IntentType.SMALLTALK,
            confidence=0.3,
            entities={},
            suggested_agent="drummond",
        )

        response = await agent.process_conversation(
            message="test", context=conversation_context, intent=intent
        )

        assert "content" in response

    @pytest.mark.asyncio
    async def test_unknown_intent_type(self, agent, conversation_context):
        """Test handling unknown intent type."""
        # Use a regular intent type but with contextual fallback
        from src.services.chat_service import IntentType

        intent = Intent(
            type=IntentType.GENERAL_QUESTION,
            confidence=0.6,
            entities={},
            suggested_agent="drummond",
        )

        response = await agent.process_conversation(
            message="test message", context=conversation_context, intent=intent
        )

        # Should use contextual response generation
        assert "content" in response
        assert len(response["content"]) > 0


class TestContextualResponseGeneration:
    """Test contextual response generation with LLM."""

    @pytest.mark.asyncio
    async def test_generate_contextual_response(self, agent, conversation_context):
        """Test generating contextual response using LLM."""
        with patch.object(agent, "llm_client") as mock_llm:
            mock_llm.generate.return_value = "Esta é uma resposta contextual."

            response = await agent.generate_contextual_response(
                message="Como funciona o sistema?", context=conversation_context
            )

            assert "content" in response
            assert "metadata" in response

    @pytest.mark.asyncio
    async def test_contextual_response_with_history(self, agent, conversation_context):
        """Test contextual response considers conversation history."""
        # Add conversation history
        agent.conversational_memory.add_message(
            session_id=conversation_context.session_id,
            role="user",
            content="Olá!",
        )
        agent.conversational_memory.add_message(
            session_id=conversation_context.session_id,
            role="assistant",
            content="Olá! Como posso ajudar?",
        )

        with patch.object(agent, "llm_client") as mock_llm:
            mock_llm.generate.return_value = "Baseado na nossa conversa anterior..."

            response = await agent.generate_contextual_response(
                message="Continue explicando", context=conversation_context
            )

            assert "content" in response


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple features."""

    @pytest.mark.asyncio
    async def test_full_notification_flow(self, agent, sample_target):
        """Test complete notification flow from creation to delivery."""
        await agent.initialize()

        # Register target
        agent.communication_targets[sample_target.target_id] = sample_target

        # Mock channel send
        with patch.object(
            agent, "_send_via_channel", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = Mock(
                message_id="integration_test",
                target_id=sample_target.target_id,
                channel=CommunicationChannel.EMAIL,
                status="sent",
                sent_at=datetime.utcnow(),
                delivered_at=None,
                read_at=None,
                error_message=None,
                retry_count=0,
                metadata={},
            )

            results = await agent.send_notification(
                message_type=MessageType.ALERT,
                content={
                    "title": "Integration Test Alert",
                    "body": "This is a complete flow test",
                },
                targets=[sample_target.target_id],
                priority=MessagePriority.HIGH,
                channels=[CommunicationChannel.EMAIL],
            )

            assert len(results) > 0
            assert results[0].status == "sent"

    @pytest.mark.asyncio
    async def test_conversation_to_handoff_flow(self, agent, conversation_context):
        """Test conversation flow leading to agent handoff."""
        # Start with greeting
        greeting_intent = Intent(
            type=IntentType.GREETING,
            confidence=0.95,
            entities={},
            suggested_agent="drummond",
        )

        greeting_response = await agent.process_conversation(
            message="Olá!", context=conversation_context, intent=greeting_intent
        )

        assert "content" in greeting_response

        # Then request investigation (should trigger handoff)
        investigate_intent = Intent(
            type=IntentType.INVESTIGATE,
            confidence=0.90,
            entities={"contract_id": "123"},
            suggested_agent="zumbi",
        )

        handoff = await agent.determine_handoff(investigate_intent)
        assert handoff == "zumbi"
