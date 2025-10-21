"""
Unit tests for Tiradentes Agent (ReporterAgent) - Report generation specialist.
Tests report generation, formatting, and multi-language support.
"""

import pytest

from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse, AgentStatus
from src.agents.tiradentes import ReporterAgent


@pytest.fixture
def investigation_results():
    """Sample investigation results from Zumbi agent."""
    return {
        "anomalies": [
            {
                "anomaly_type": "price_anomaly",
                "severity": 0.85,
                "confidence": 0.92,
                "description": "Contract value 3.5x above market average",
                "explanation": "Significant price deviation detected",
                "evidence": {
                    "contract_id": "123/2024",
                    "value": 5000000.0,
                    "market_average": 1428571.0,
                },
                "recommendations": [
                    "Review pricing justification",
                    "Compare with similar contracts",
                ],
            }
        ],
        "summary": {
            "total_records": 100,
            "anomalies_found": 3,
            "investigation_id": "inv-123",
        },
    }


@pytest.fixture
def analysis_results():
    """Sample analysis results from Anita agent."""
    return {
        "patterns": [
            {
                "pattern_type": "temporal",
                "description": "End-of-year spending spike",
                "significance": 0.78,
                "confidence": 0.85,
                "direction": "upward",  # Added for trend analysis
                "insights": ["Budget execution rush", "Possible inefficiency"],
                "evidence": {"period": "Q4 2023", "increase_percentage": 145},
            },
            {
                "pattern_type": "seasonal",
                "description": "Q1 contraction in procurement",
                "significance": 0.65,
                "confidence": 0.72,
                "direction": "downward",  # Added for trend analysis
                "insights": ["Post-holiday slowdown"],
                "evidence": {"period": "Q1 2024", "decrease_percentage": 28},
            },
        ],
        "correlations": [
            {
                "correlation_type": "vendor_concentration",
                "variables": ["vendor_id", "contract_count"],
                "correlation_coefficient": 0.82,
                "significance_level": "high",
            }
        ],
    }


@pytest.fixture
def agent_context():
    """Create agent context for testing."""
    return AgentContext(
        investigation_id="test-report-123",
        user_id="test_user",
        session_id="test_session",
        metadata={"purpose": "testing"},
    )


@pytest.fixture
def tiradentes_agent():
    """Create Tiradentes agent (ReporterAgent)."""
    return ReporterAgent(default_language="pt", max_report_length=10000)


class TestTiradentesReporterAgent:
    """Test suite for Tiradentes (Reporter Agent)."""

    @pytest.mark.unit
    def test_agent_initialization(self, tiradentes_agent):
        """Test Tiradentes agent initialization."""
        assert tiradentes_agent.name == "Tiradentes"
        assert tiradentes_agent.default_language == "pt"
        assert tiradentes_agent.max_length == 10000

        # Check capabilities
        expected_capabilities = [
            "investigation_report_generation",
            "pattern_analysis_reporting",
            "executive_summary_creation",
            "multi_format_rendering",
        ]

        for capability in expected_capabilities:
            assert capability in tiradentes_agent.capabilities

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_initialize_and_shutdown(self, tiradentes_agent):
        """Test agent lifecycle methods."""
        await tiradentes_agent.initialize()
        await tiradentes_agent.shutdown()
        # Should complete without errors

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_investigation_report(
        self, tiradentes_agent, agent_context, investigation_results
    ):
        """Test generation of investigation report."""
        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "investigation_report",
                "format": "markdown",
                "investigation_results": investigation_results,
                "target_audience": "technical",
                "include_visualizations": True,
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert isinstance(response, AgentResponse)
        assert response.agent_name == "Tiradentes"
        assert response.status == AgentStatus.COMPLETED
        assert "content" in response.result
        # Accept both Portuguese "anomalias" and English "anomalies"
        content_lower = response.result["content"].lower()
        assert "anomal" in content_lower  # Works for both languages

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_analysis_report(
        self, tiradentes_agent, agent_context, analysis_results
    ):
        """Test generation of analysis report."""
        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "analysis_report",
                "format": "markdown",
                "analysis_results": analysis_results,
                "language": "pt",
                "detailed_findings": True,
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        # Accept both Portuguese "padrões" and English "patterns"
        content_lower = response.result["content"].lower()
        assert "padr" in content_lower or "pattern" in content_lower

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_executive_summary(
        self, tiradentes_agent, agent_context, investigation_results, analysis_results
    ):
        """Test generation of executive summary."""
        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "executive_summary",
                "format": "executive_summary",
                "investigation_results": investigation_results,
                "analysis_results": analysis_results,
                "target_audience": "executive",
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        # Executive summary should be concise
        assert len(response.result["content"]) < 5000

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_invalid_action(self, tiradentes_agent, agent_context):
        """Test handling of invalid action."""
        message = AgentMessage(
            sender="test", recipient="Tiradentes", action="invalid_action", payload={}
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.ERROR
        assert "Unsupported action" in response.error

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_missing_data_error(self, tiradentes_agent, agent_context):
        """Test error when no data provided."""
        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "investigation_report",
                "format": "markdown",
                # Missing investigation_results and analysis_results
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.ERROR
        assert "No data provided" in response.error

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_multi_language_support(
        self, tiradentes_agent, agent_context, investigation_results
    ):
        """Test report generation in different languages."""
        languages = ["pt", "en"]

        for lang in languages:
            message = AgentMessage(
                sender="test",
                recipient="Tiradentes",
                action="generate_report",
                payload={
                    "report_type": "investigation_report",
                    "format": "markdown",
                    "investigation_results": investigation_results,
                    "language": lang,
                },
            )

            response = await tiradentes_agent.process(message, agent_context)

            assert response.status == AgentStatus.COMPLETED
            assert response.result["metadata"]["language"] == lang

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_report_format_rendering(
        self, tiradentes_agent, agent_context, investigation_results
    ):
        """Test different report format rendering."""
        formats = ["markdown", "html", "json"]

        for fmt in formats:
            message = AgentMessage(
                sender="test",
                recipient="Tiradentes",
                action="generate_report",
                payload={
                    "report_type": "investigation_report",
                    "format": fmt,
                    "investigation_results": investigation_results,
                },
            )

            response = await tiradentes_agent.process(message, agent_context)

            assert response.status == AgentStatus.COMPLETED
            # Format is in result, not result["metadata"]
            assert response.result["format"] == fmt

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_generate_combined_report(
        self, tiradentes_agent, agent_context, investigation_results, analysis_results
    ):
        """Test generation of combined report (investigation + analysis)."""
        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "combined_report",
                "format": "markdown",
                "investigation_results": investigation_results,
                "analysis_results": analysis_results,
                "language": "pt",
                "include_visualizations": True,
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        content = response.result["content"].lower()
        # Should contain both investigation and analysis content
        assert "anomal" in content  # From investigation
        assert "padr" in content or "pattern" in content  # From analysis

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_generate_anomaly_summary(
        self, tiradentes_agent, agent_context, investigation_results
    ):
        """Test generation of anomaly summary."""
        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "anomaly_summary",
                "format": "markdown",
                "investigation_results": investigation_results,
                "language": "pt",
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "content" in response.result
        # Should be a concise summary
        assert len(response.result["content"]) > 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_generate_trend_analysis(
        self, tiradentes_agent, agent_context, analysis_results
    ):
        """Test generation of trend analysis report."""
        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "trend_analysis",
                "format": "markdown",
                "analysis_results": analysis_results,
                "language": "pt",
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "content" in response.result

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_different_target_audiences(
        self, tiradentes_agent, agent_context, investigation_results
    ):
        """Test report generation for different target audiences."""
        audiences = ["technical", "executive", "public"]

        for audience in audiences:
            message = AgentMessage(
                sender="test",
                recipient="Tiradentes",
                action="generate_report",
                payload={
                    "report_type": "investigation_report",
                    "format": "markdown",
                    "investigation_results": investigation_results,
                    "target_audience": audience,
                },
            )

            response = await tiradentes_agent.process(message, agent_context)

            assert response.status == AgentStatus.COMPLETED
            assert response.result["metadata"]["target_audience"] == audience

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_report_without_visualizations(
        self, tiradentes_agent, agent_context, investigation_results
    ):
        """Test report generation without visualizations."""
        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "investigation_report",
                "format": "markdown",
                "investigation_results": investigation_results,
                "include_visualizations": False,
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        # Report should be generated successfully regardless of visualization setting
        assert "content" in response.result

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_report_without_recommendations(
        self, tiradentes_agent, agent_context, investigation_results
    ):
        """Test report generation without recommendations section."""
        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "investigation_report",
                "format": "markdown",
                "investigation_results": investigation_results,
                "recommendations": False,
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        # Report should be generated successfully
        assert "content" in response.result

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_report_with_empty_investigation_results(
        self, tiradentes_agent, agent_context
    ):
        """Test report with empty investigation results."""
        empty_results = {"anomalies": [], "summary": {"total_records": 0}}

        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "investigation_report",
                "format": "markdown",
                "investigation_results": empty_results,
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        # Should still generate a report, even if no anomalies found
        assert response.status == AgentStatus.COMPLETED
        assert "content" in response.result

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_multiple_anomaly_types(self, tiradentes_agent, agent_context):
        """Test report with multiple types of anomalies."""
        multi_anomaly_results = {
            "anomalies": [
                {
                    "anomaly_type": "price_anomaly",
                    "severity": 0.9,
                    "confidence": 0.95,
                    "description": "High price deviation",
                    "explanation": "Price significantly above market",
                    "evidence": {"contract_id": "C1"},
                    "recommendations": ["Review pricing"],
                },
                {
                    "anomaly_type": "vendor_concentration",
                    "severity": 0.75,
                    "confidence": 0.88,
                    "description": "Single vendor dominance",
                    "explanation": "One supplier has 80% of contracts",
                    "evidence": {"vendor_id": "V1", "concentration": 0.8},
                    "recommendations": ["Diversify suppliers"],
                },
                {
                    "anomaly_type": "duplicate_contracts",
                    "severity": 0.65,
                    "confidence": 0.82,
                    "description": "Potentially duplicate contracts",
                    "explanation": "Similar objects and values",
                    "evidence": {"contract_ids": ["C2", "C3"]},
                    "recommendations": ["Investigate duplication"],
                },
            ],
            "summary": {
                "total_records": 150,
                "anomalies_found": 3,
                "high_severity_count": 1,
                "medium_severity_count": 2,
            },
        }

        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "anomaly_summary",
                "format": "markdown",
                "investigation_results": multi_anomaly_results,
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        content = response.result["content"].lower()
        # Should mention different types
        assert "price" in content or "preço" in content

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_english_language_report(
        self, tiradentes_agent, agent_context, investigation_results
    ):
        """Test report generation in English."""
        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "investigation_report",
                "format": "markdown",
                "investigation_results": investigation_results,
                "language": "en",
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert response.result["metadata"]["language"] == "en"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_executive_audience_summary(
        self, tiradentes_agent, agent_context, investigation_results
    ):
        """Test executive-focused summary generation."""
        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "executive_summary",
                "format": "executive_summary",
                "investigation_results": investigation_results,
                "target_audience": "executive",
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        # Executive summaries should be concise
        assert len(response.result["content"]) < 3000

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_public_audience_report(
        self, tiradentes_agent, agent_context, investigation_results
    ):
        """Test public-facing report generation."""
        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "investigation_report",
                "format": "markdown",
                "investigation_results": investigation_results,
                "target_audience": "public",
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert response.result["metadata"]["target_audience"] == "public"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_detailed_trend_analysis_with_directions(
        self, tiradentes_agent, agent_context
    ):
        """Test detailed trend analysis with upward/downward/stable directions."""
        detailed_analysis = {
            "patterns": [
                {
                    "pattern_type": "spending_trend",
                    "description": "Increasing infrastructure investment",
                    "direction": "upward",
                    "confidence": 0.92,
                    "significance": 0.88,
                    "insights": ["Government prioritizing infrastructure"],
                    "evidence": {"period": "2023-2024", "increase": 45},
                },
                {
                    "pattern_type": "procurement_trend",
                    "description": "Decreasing emergency contracts",
                    "direction": "downward",
                    "confidence": 0.85,
                    "significance": 0.75,
                    "insights": ["Better planning reducing emergencies"],
                    "evidence": {"period": "2024", "decrease": 32},
                },
                {
                    "pattern_type": "supplier_trend",
                    "description": "Stable supplier base",
                    "direction": "stable",
                    "confidence": 0.78,
                    "significance": 0.65,
                    "insights": ["Consistent vendor relationships"],
                    "evidence": {"period": "2023-2024", "variation": 5},
                },
            ],
            "correlations": [],
        }

        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="generate_report",
            payload={
                "report_type": "trend_analysis",
                "format": "markdown",
                "analysis_results": detailed_analysis,
                "language": "pt",
            },
        )

        response = await tiradentes_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        # Report should be generated successfully with trends
        assert "content" in response.result
        assert len(response.result["content"]) > 0
