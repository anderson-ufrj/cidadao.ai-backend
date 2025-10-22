"""
Focused tests to boost Drummond agent coverage to >80%.

This file contains targeted tests for uncovered code paths.
"""

import pytest

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
