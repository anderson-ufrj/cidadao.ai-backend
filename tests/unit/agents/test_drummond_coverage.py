"""
Focused tests to boost Drummond agent coverage to >90%.

This file contains targeted tests for uncovered code paths.
Target: 87.78% → 90%+
"""

import pytest

from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus
from src.agents.drummond import CommunicationAgent


@pytest.fixture
def agent():
    """Create Drummond agent instance."""
    return CommunicationAgent()


class TestReportGeneration:
    """Test report generation features."""

    @pytest.mark.asyncio
    async def test_generate_report_summary_technical(self, agent):
        """Test report summary for technical audience."""
        report_data = {
            "total_records": 1000,
            "anomalies_found": 25,
            "financial_impact": 500000,
            "entities_involved": ["Entity1", "Entity2", "Entity3"],
        }

        summary = await agent.generate_report_summary(
            report_data=report_data,
            target_audience="technical",
            language="pt-BR",
        )

        assert "executive_summary" in summary
        assert "key_findings" in summary
        assert "action_items" in summary
        assert (
            "1000" in summary["executive_summary"]
            or "1.000" in summary["executive_summary"]
            or "1,000" in summary["executive_summary"]
        )
        assert "25" in summary["key_findings"]

    @pytest.mark.asyncio
    async def test_generate_report_summary_executive(self, agent):
        """Test report summary for executive audience."""
        report_data = {
            "total_records": 500,
            "anomalies_found": 3,
            "financial_impact": 50000,
            "entities_involved": ["Entity1"],
        }

        summary = await agent.generate_report_summary(
            report_data=report_data,
            target_audience="executive",
            language="pt-BR",
        )

        assert "executive_summary" in summary
        assert "key_findings" in summary
        assert "500" in summary["executive_summary"]

    @pytest.mark.asyncio
    async def test_generate_report_summary_citizen(self, agent):
        """Test report summary for general/citizen audience."""
        report_data = {
            "total_records": 200,
            "anomalies_found": 0,
            "financial_impact": 0,
            "entities_involved": [],
        }

        summary = await agent.generate_report_summary(
            report_data=report_data,
            target_audience="citizen",
            language="pt-BR",
        )

        assert "executive_summary" in summary
        assert "key_findings" in summary
        assert "citizen_impact" in summary
        # Should mention no critical anomalies
        assert "Nenhuma irregularidade" in summary["executive_summary"]

    @pytest.mark.asyncio
    async def test_generate_report_summary_high_anomalies(self, agent):
        """Test report summary with many anomalies (triggers action items)."""
        report_data = {
            "total_records": 100,
            "anomalies_found": 10,  # > 5, should trigger investigation recommendation
            "financial_impact": 0,
            "entities_involved": [],
        }

        summary = await agent.generate_report_summary(
            report_data=report_data,
            target_audience="citizen",
            language="pt-BR",
        )

        assert "action_items" in summary
        # Should recommend formal investigation
        assert (
            "Investigação" in summary["action_items"]
            or "investigação" in summary["action_items"]
        )

    @pytest.mark.asyncio
    async def test_generate_report_summary_high_financial_impact(self, agent):
        """Test report summary with high financial impact."""
        report_data = {
            "total_records": 100,
            "anomalies_found": 2,
            "financial_impact": 2000000,  # > 1M, should trigger notification recommendation
            "entities_involved": [],
        }

        summary = await agent.generate_report_summary(
            report_data=report_data,
            target_audience="executive",
            language="pt-BR",
        )

        assert "action_items" in summary
        # Should recommend notifying control agencies
        assert (
            "Notificar" in summary["action_items"]
            or "notificar" in summary["action_items"]
        )


class TestTranslation:
    """Test translation features."""

    @pytest.mark.asyncio
    async def test_translate_content_pt_to_en(self, agent):
        """Test translating Portuguese to English."""
        content_text = "Este é um relatório de transparência sobre gastos públicos."

        translation = await agent.translate_content(
            content=content_text,
            source_language="pt-BR",
            target_language="en-US",
        )

        assert isinstance(translation, str)
        assert len(translation) > 0

    @pytest.mark.asyncio
    async def test_translate_content_en_to_pt(self, agent):
        """Test translating English to Portuguese."""
        content_text = "This is a transparency report about public spending."

        translation = await agent.translate_content(
            content=content_text,
            source_language="en-US",
            target_language="pt-BR",
        )

        assert isinstance(translation, str)
        assert len(translation) > 0


class TestProcessMethodCoverage:
    """Tests to cover the process() method - Lines 964-1071."""

    @pytest.mark.asyncio
    async def test_process_chat_action(self, agent):
        """Test process() with process_chat action - Lines 970-1004."""
        from src.agents.deodoro import AgentContext, AgentMessage

        message = AgentMessage(
            sender="test_user",
            recipient="drummond",
            action="process_chat",
            payload={
                "user_message": "Olá, preciso de um relatório sobre contratos",
                "intent": {
                    "type": "report_request",
                    "entities": {"report_type": "contracts"},
                    "confidence": 0.85,
                    "suggested_agent": "tiradentes",
                },
                "session": {
                    "session_id": "test_session_123",
                    "user_id": "user_456",
                },
                "context": {
                    "user_profile": {
                        "name": "Test User",
                        "role": "analyst",
                    }
                },
            },
        )

        context = AgentContext(
            investigation_id="test_inv_1",
            user_id="user_456",
            session_id="test_session_123",
        )

        # Execute process_chat action (lines 970-1004)
        response = await agent.process(message, context)

        # Verify response structure
        assert response.agent_name == "drummond"
        assert response.status.value == "completed"
        assert "message" in response.result
        assert response.result["status"] == "conversation_processed"


class TestProcessActionsCoverage:
    """Test process method actions for coverage boost (lines 1007-1057)."""

    @pytest.mark.asyncio
    async def test_process_send_notification_action(self, agent):
        """Test process with send_notification action - Lines 1007-1031."""
        message = AgentMessage(
            sender="test_agent",
            recipient="drummond",
            action="send_notification",
            payload={
                "message_type": "alert",
                "content": {
                    "title": "Anomalia Detectada",
                    "body": "Contrato suspeito identificado",
                },
                "targets": ["user_1", "user_2"],
                "priority": "high",
            },
        )

        context = AgentContext(
            investigation_id="test_inv_notify",
            user_id="user_123",
            session_id="session_notify_123",
        )

        response = await agent.process(message, context)

        assert response.agent_name == "drummond"
        assert "communication_results" in response.result
        assert "total_targets" in response.result["communication_results"]
        assert response.result["status"] == "communication_completed"

    @pytest.mark.asyncio
    async def test_process_generate_report_summary_action(self, agent):
        """Test process with generate_report_summary action - Lines 1033-1046."""
        message = AgentMessage(
            sender="test_agent",
            recipient="drummond",
            action="generate_report_summary",
            payload={
                "report_data": {
                    "total_records": 500,
                    "anomalies_found": 15,
                    "financial_impact": 250000,
                },
                "target_audience": "executive",
                "language": "pt-BR",
            },
        )

        context = AgentContext(
            investigation_id="test_inv_report",
            user_id="user_456",
            session_id="session_report_123",
        )

        response = await agent.process(message, context)

        assert response.agent_name == "drummond"
        assert "report_summary" in response.result
        assert response.result["status"] == "summary_generated"
        assert response.status == AgentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_process_send_bulk_communication_action(self, agent):
        """Test process with send_bulk_communication action - Lines 1048-1061."""
        message = AgentMessage(
            sender="test_agent",
            recipient="drummond",
            action="send_bulk_communication",
            payload={
                "message_type": "notification",
                "content": {
                    "title": "Atualização Mensal",
                    "body": "Novos dados disponíveis",
                },
                "target_segments": [
                    {"segment_id": "seg_1", "filters": {"city": "São Paulo"}},
                    {"segment_id": "seg_2", "filters": {"interests": ["transparency"]}},
                ],
            },
        )

        context = AgentContext(
            investigation_id="test_inv_bulk",
            user_id="user_789",
            session_id="session_bulk_123",
        )

        response = await agent.process(message, context)

        assert response.agent_name == "drummond"
        assert "bulk_campaign" in response.result
        assert response.result["status"] == "bulk_scheduled"
