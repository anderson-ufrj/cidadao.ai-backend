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
                "insights": ["Budget execution rush", "Possible inefficiency"],
                "evidence": {"period": "Q4 2023", "increase_percentage": 145},
            }
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
        assert "anomalies" in response.result["content"].lower()

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
        assert "patterns" in response.result["content"].lower()

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
            assert response.result["metadata"]["format"] == fmt
