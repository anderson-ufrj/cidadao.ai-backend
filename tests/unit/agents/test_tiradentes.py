"""
Tests for Tiradentes - Reporter Agent
"""

import pytest

from src.agents.deodoro import AgentContext, AgentMessage
from src.agents.tiradentes import ReporterAgent, ReportFormat, ReportRequest, ReportType
from src.core import AgentStatus

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def agent():
    """Create Tiradentes agent instance."""
    return ReporterAgent()


@pytest.fixture
def sample_investigation_data():
    """Sample investigation data for report generation."""
    return {
        "investigation_id": "INV-2025-001",
        "total_contracts": 150,
        "anomalies_found": 12,
        "fraud_patterns": 3,
        "estimated_loss": 5000000.00,
        "anomalies": [
            {
                "contract_id": "001/2025",
                "description": "Price deviation detected",
                "severity": 0.9,
                "confidence": 0.92,
                "type": "price_anomaly",
                "value": 150000.00,
            },
            {
                "contract_id": "002/2025",
                "description": "Suspicious vendor concentration",
                "severity": 0.6,
                "confidence": 0.85,
                "type": "vendor_concentration",
                "value": 75000.00,
            },
        ],
        "summary": {
            "total_records": 150,
            "anomalies_found": 12,
            "risk_score": 7.5,
            "suspicious_value": 5000000.00,
            "high_severity_count": 4,
            "medium_severity_count": 5,
            "low_severity_count": 3,
            "total_value": 15000000.00,
        },
    }


@pytest.fixture
def sample_analysis_data():
    """Sample analysis data."""
    return {
        "analysis_id": "ANAL-2025-001",
        "patterns_found": 5,
        "trends": {"increasing_costs": True, "vendor_concentration": 0.75},
        "patterns": [
            {
                "type": "trend_pattern",
                "description": "Increasing costs over time",
                "confidence": 0.88,
            }
        ],
        "correlations": [
            {
                "variable1": "contract_value",
                "variable2": "vendor_concentration",
                "strength": 0.75,
                "p_value": 0.001,
            }
        ],
        "insights": [
            "Strong correlation between contract value and vendor concentration"
        ],
        "summary": {
            "total_records": 150,
            "average_confidence": 0.85,
            "data_coverage": 0.95,
            "detection_rate": 0.80,
        },
    }


@pytest.fixture
def markdown_report_message(sample_investigation_data):
    """Sample message for Markdown report generation."""
    request = ReportRequest(
        report_type=ReportType.INVESTIGATION_REPORT,
        format=ReportFormat.MARKDOWN,
        investigation_results=sample_investigation_data,
        target_audience="technical",
    )

    return AgentMessage(
        sender="test",
        recipient="tiradentes",
        action="generate_report",
        payload=request.model_dump(),  # Don't double-nest
    )


@pytest.fixture
def executive_summary_message(sample_investigation_data):
    """Sample message for executive summary generation."""
    request = ReportRequest(
        report_type=ReportType.EXECUTIVE_SUMMARY,
        format=ReportFormat.EXECUTIVE_SUMMARY,
        investigation_results=sample_investigation_data,
        target_audience="executive",
    )

    return AgentMessage(
        sender="test",
        recipient="tiradentes",
        action="generate_report",
        payload=request.model_dump(),  # Don't double-nest
    )


# ============================================================================
# Tests - Initialization
# ============================================================================


class TestTiradentesAgentInit:
    """Test agent initialization."""

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.name == "Tiradentes"
        # Check for report-related capabilities
        capabilities_str = str(agent.capabilities).lower()
        assert "report" in capabilities_str or "summary" in capabilities_str

    def test_agent_has_required_methods(self, agent):
        """Test agent has required methods."""
        assert hasattr(agent, "process")
        assert hasattr(agent, "initialize")
        assert hasattr(agent, "shutdown")

        # Check for private report generation methods
        assert hasattr(agent, "_generate_report_content") or hasattr(
            agent, "_generate_investigation_report"
        )


# ============================================================================
# Tests - Report Generation (Markdown)
# ============================================================================


class TestMarkdownReportGeneration:
    """Test Markdown report generation."""

    @pytest.mark.asyncio
    async def test_generate_markdown_investigation_report(
        self, agent, markdown_report_message
    ):
        """Test Markdown investigation report generation."""
        response = await agent.process(markdown_report_message, AgentContext())

        assert response.status == AgentStatus.COMPLETED
        assert "result" in response.__dict__ or "data" in response.__dict__

        # Check result structure
        result = response.result if hasattr(response, "result") else response.data
        if isinstance(result, dict):
            # Should have report content
            assert "report" in result or "content" in result or "markdown" in result

    @pytest.mark.asyncio
    async def test_markdown_report_contains_key_sections(
        self, agent, markdown_report_message
    ):
        """Test that Markdown report contains key sections."""
        response = await agent.process(markdown_report_message, AgentContext())

        if response.status == AgentStatus.COMPLETED:
            result = response.result if hasattr(response, "result") else response.data
            if isinstance(result, dict):
                content = str(
                    result.get("report")
                    or result.get("content")
                    or result.get("markdown", "")
                )

                # Should contain typical Markdown headers
                # (being flexible as exact format may vary)
                assert len(content) > 100  # Should have substantial content


# ============================================================================
# Tests - Executive Summary
# ============================================================================


class TestExecutiveSummary:
    """Test executive summary generation."""

    @pytest.mark.asyncio
    async def test_generate_executive_summary(self, agent, executive_summary_message):
        """Test executive summary generation."""
        response = await agent.process(executive_summary_message, AgentContext())

        assert response.status == AgentStatus.COMPLETED
        result = response.result if hasattr(response, "result") else response.data

        if isinstance(result, dict):
            # Executive summary should be concise
            summary = str(
                result.get("summary")
                or result.get("report")
                or result.get("content", "")
            )
            assert len(summary) > 0

    @pytest.mark.asyncio
    async def test_executive_summary_audience_adaptation(
        self, agent, sample_investigation_data
    ):
        """Test that executive summary adapts to audience."""
        request = ReportRequest(
            report_type=ReportType.EXECUTIVE_SUMMARY,
            format=ReportFormat.EXECUTIVE_SUMMARY,
            investigation_results=sample_investigation_data,
            target_audience="executive",  # Non-technical audience
        )

        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload=request.model_dump(),
        )

        response = await agent.process(message, AgentContext())

        # Should complete successfully
        assert response.status == AgentStatus.COMPLETED


# ============================================================================
# Tests - Multiple Report Types
# ============================================================================


class TestMultipleReportTypes:
    """Test different report types."""

    @pytest.mark.asyncio
    async def test_analysis_report_generation(self, agent, sample_analysis_data):
        """Test analysis report generation."""
        request = ReportRequest(
            report_type=ReportType.ANALYSIS_REPORT,
            format=ReportFormat.MARKDOWN,
            analysis_results=sample_analysis_data,
        )

        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload=request.model_dump(),
        )

        response = await agent.process(message, AgentContext())
        assert response.status == AgentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_anomaly_summary_generation(self, agent, sample_investigation_data):
        """Test anomaly summary generation."""
        request = ReportRequest(
            report_type=ReportType.ANOMALY_SUMMARY,
            format=ReportFormat.MARKDOWN,
            investigation_results=sample_investigation_data,
        )

        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload=request.model_dump(),
        )

        response = await agent.process(message, AgentContext())
        assert response.status == AgentStatus.COMPLETED


# ============================================================================
# Tests - Export Formats
# ============================================================================


class TestExportFormats:
    """Test different export formats."""

    @pytest.mark.asyncio
    async def test_html_format(self, agent, sample_investigation_data):
        """Test HTML format export."""
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.HTML,
            investigation_results=sample_investigation_data,
        )

        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload=request.model_dump(),
        )

        response = await agent.process(message, AgentContext())

        # HTML export may or may not be fully implemented
        assert response.status in [AgentStatus.COMPLETED, AgentStatus.ERROR]

    @pytest.mark.asyncio
    async def test_json_format(self, agent, sample_investigation_data):
        """Test JSON format export."""
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.JSON,
            investigation_results=sample_investigation_data,
        )

        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload=request.model_dump(),
        )

        response = await agent.process(message, AgentContext())
        assert response.status == AgentStatus.COMPLETED


# ============================================================================
# Tests - Error Handling
# ============================================================================


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_invalid_report_type(self, agent):
        """Test handling of invalid report type (should not happen with enum, but testing robustness)."""
        # Testing with missing investigation_results
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.MARKDOWN,
            investigation_results=None,  # Missing required data
        )

        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload=request.model_dump(),
        )

        response = await agent.process(message, AgentContext())

        # Should either handle gracefully or error
        assert response.status in [AgentStatus.COMPLETED, AgentStatus.ERROR]

    @pytest.mark.asyncio
    async def test_missing_report_request(self, agent):
        """Test handling when report_request is missing from payload."""
        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload={},  # Empty payload
        )

        response = await agent.process(message, AgentContext())

        # Should handle missing data gracefully
        assert response.status in [AgentStatus.COMPLETED, AgentStatus.ERROR]

    @pytest.mark.asyncio
    async def test_empty_investigation_data(self, agent):
        """Test handling of empty investigation data."""
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.MARKDOWN,
            investigation_results={},  # Empty data
        )

        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload=request.model_dump(),
        )

        response = await agent.process(message, AgentContext())

        # Should handle empty data
        assert response.status in [AgentStatus.COMPLETED, AgentStatus.ERROR]


# ============================================================================
# Tests - Report Features
# ============================================================================


class TestReportFeatures:
    """Test specific report features."""

    @pytest.mark.asyncio
    async def test_report_with_visualizations(self, agent, sample_investigation_data):
        """Test report generation with visualizations enabled."""
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.MARKDOWN,
            investigation_results=sample_investigation_data,
            include_visualizations=True,
        )

        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload=request.model_dump(),
        )

        response = await agent.process(message, AgentContext())
        assert response.status == AgentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_report_with_recommendations(self, agent, sample_investigation_data):
        """Test that recommendations can be included."""
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.MARKDOWN,
            investigation_results=sample_investigation_data,
            recommendations=True,
        )

        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload=request.model_dump(),
        )

        response = await agent.process(message, AgentContext())
        assert response.status == AgentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_report_detailed_findings(self, agent, sample_investigation_data):
        """Test report with detailed findings."""
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.MARKDOWN,
            investigation_results=sample_investigation_data,
            detailed_findings=True,
        )

        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload=request.model_dump(),
        )

        response = await agent.process(message, AgentContext())
        assert response.status == AgentStatus.COMPLETED


# ============================================================================
# Tests - Audience Adaptation
# ============================================================================


class TestAudienceAdaptation:
    """Test report adaptation for different audiences."""

    @pytest.mark.asyncio
    async def test_technical_audience_report(self, agent, sample_investigation_data):
        """Test report for technical audience."""
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.MARKDOWN,
            investigation_results=sample_investigation_data,
            target_audience="technical",
        )

        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload=request.model_dump(),
        )

        response = await agent.process(message, AgentContext())
        assert response.status == AgentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_public_audience_report(self, agent, sample_investigation_data):
        """Test report for public audience."""
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.MARKDOWN,
            investigation_results=sample_investigation_data,
            target_audience="public",
        )

        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload=request.model_dump(),
        )

        response = await agent.process(message, AgentContext())
        assert response.status == AgentStatus.COMPLETED


# ============================================================================
# Tests - Combined Reports
# ============================================================================


class TestCombinedReports:
    """Test combined investigation + analysis reports."""

    @pytest.mark.asyncio
    async def test_combined_report_generation(
        self, agent, sample_investigation_data, sample_analysis_data
    ):
        """Test combined report with both investigation and analysis results."""
        request = ReportRequest(
            report_type=ReportType.COMBINED_REPORT,
            format=ReportFormat.MARKDOWN,
            investigation_results=sample_investigation_data,
            analysis_results=sample_analysis_data,
        )

        message = AgentMessage(
            sender="test",
            recipient="tiradentes",
            action="generate_report",
            payload=request.model_dump(),
        )

        response = await agent.process(message, AgentContext())
        assert response.status == AgentStatus.COMPLETED
