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

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_trend_analysis_with_upward_trends(
        self, tiradentes_agent, agent_context
    ):
        """Test trend analysis content creation with upward trends."""
        patterns = [
            {
                "type": "temporal",
                "description": "Spending increase in Q4",
                "direction": "upward",
                "confidence": 0.92,
                "rate": 45.3,
                "significance": "high",
            },
            {
                "type": "temporal",
                "description": "Contract count growth",
                "direction": "upward",
                "confidence": 0.85,
                "rate": 23.1,
            },
        ]

        content = tiradentes_agent._create_trend_analysis_content(patterns)

        assert "Tendências Ascendentes" in content
        assert "Spending increase in Q4" in content
        assert "92.0%" in content  # Confidence
        assert "45.3% ao período" in content  # Rate

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_trend_analysis_with_downward_trends(
        self, tiradentes_agent, agent_context
    ):
        """Test trend analysis content creation with downward trends."""
        patterns = [
            {
                "type": "temporal",
                "description": "Reduction in anomalies",
                "direction": "downward",
                "confidence": 0.88,
                "rate": -32.5,
                "significance": "medium",
            }
        ]

        content = tiradentes_agent._create_trend_analysis_content(patterns)

        assert "Tendências Descendentes" in content
        assert "Reduction in anomalies" in content
        assert "88.0%" in content
        assert "32.5% ao período" in content  # Absolute value

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_trend_analysis_with_seasonal_patterns(
        self, tiradentes_agent, agent_context
    ):
        """Test trend analysis with seasonal patterns."""
        patterns = [
            {
                "type": "seasonal",
                "description": "Year-end budget rush",
                "direction": "upward",
                "confidence": 0.75,
            },
            {
                "type": "seasonal",
                "description": "Post-holiday slowdown",
                "direction": "downward",
                "confidence": 0.70,
            },
        ]

        content = tiradentes_agent._create_trend_analysis_content(patterns)

        assert "Padrões Sazonais" in content
        assert "Year-end budget rush" in content
        assert "Post-holiday slowdown" in content

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_trend_analysis_with_cyclical_patterns(
        self, tiradentes_agent, agent_context
    ):
        """Test trend analysis with cyclical patterns."""
        patterns = [
            {
                "type": "cyclical",
                "description": "Quarterly procurement cycle",
                "direction": "stable",
                "confidence": 0.82,
            }
        ]

        content = tiradentes_agent._create_trend_analysis_content(patterns)

        assert "Padrões Cíclicos" in content
        assert "Quarterly procurement cycle" in content

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_trend_analysis_with_stable_trends(
        self, tiradentes_agent, agent_context
    ):
        """Test trend analysis with stable trends."""
        patterns = [
            {
                "type": "temporal",
                "description": "Consistent spending pattern",
                "direction": "stable",
                "confidence": 0.90,
            }
        ]

        content = tiradentes_agent._create_trend_analysis_content(patterns)

        assert "Tendências estáveis:** 1" in content  # With markdown bold formatting
        assert "Distribuição de Tendências" in content

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_trend_analysis_with_empty_patterns(
        self, tiradentes_agent, agent_context
    ):
        """Test trend analysis with no patterns."""
        content = tiradentes_agent._create_trend_analysis_content([])

        assert "Nenhuma tendência significativa" in content

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_trend_analysis_comprehensive(self, tiradentes_agent, agent_context):
        """Test comprehensive trend analysis with all trend types."""
        patterns = [
            {
                "type": "temporal",
                "description": "Upward trend A",
                "direction": "upward",
                "confidence": 0.95,
                "rate": 50.0,
            },
            {
                "type": "temporal",
                "description": "Downward trend B",
                "direction": "downward",
                "confidence": 0.85,
                "rate": -30.0,
            },
            {
                "type": "seasonal",
                "description": "Seasonal pattern C",
                "direction": "upward",
                "confidence": 0.75,
            },
            {
                "type": "cyclical",
                "description": "Cyclical pattern D",
                "direction": "stable",
                "confidence": 0.80,
            },
        ]

        content = tiradentes_agent._create_trend_analysis_content(patterns)

        # Check all sections are present
        assert "Tendências Ascendentes" in content
        assert "Tendências Descendentes" in content
        assert "Padrões Sazonais" in content
        assert "Padrões Cíclicos" in content
        assert "Recomendações Baseadas em Tendências" in content
        assert "Projeções e Implicações" in content

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_correlation_analysis_with_strong_correlations(
        self, tiradentes_agent, agent_context
    ):
        """Test correlation analysis content with strong correlations."""
        correlations = [
            {
                "variable1": "contract_value",
                "variable2": "supplier_count",
                "strength": 0.85,
                "p_value": 0.001,
                "interpretation": "Strong positive correlation",
            },
            {
                "variable1": "anomaly_rate",
                "variable2": "contract_complexity",
                "strength": -0.72,
                "p_value": 0.005,
                "interpretation": "Strong negative correlation",
            },
        ]

        content = tiradentes_agent._create_correlation_section(correlations)

        assert "Correlações Fortes" in content
        assert "contract_value" in content
        assert "0.85 (positiva)" in content
        assert "0.0010" in content  # p-value formatted to 4 decimals
        assert "Strong positive correlation" in content

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_correlation_analysis_with_moderate_correlations(
        self, tiradentes_agent, agent_context
    ):
        """Test correlation analysis with moderate correlations."""
        correlations = [
            {
                "variable1": "time_to_award",
                "variable2": "vendor_experience",
                "strength": 0.55,
                "p_value": 0.02,
            }
        ]

        content = tiradentes_agent._create_correlation_section(correlations)

        assert "Correlações Moderadas" in content
        assert "time_to_award" in content
        assert "0.55" in content

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_executive_summary_with_high_importance_sections(
        self, tiradentes_agent, agent_context
    ):
        """Test executive summary creation with high importance sections."""
        from src.agents.tiradentes import ReportRequest, ReportSection, ReportType

        sections = [
            ReportSection(
                title="Critical Finding",
                content="This is the first paragraph.\n\nThis is the second paragraph.\n\nThis is the third paragraph.",
                importance=5,
            ),
            ReportSection(
                title="Important Discovery",
                content="Key point 1\nKey point 2\nKey point 3",
                importance=4,
            ),
            ReportSection(
                title="Low Priority",
                content="Not important",
                importance=2,
            ),
        ]

        request = ReportRequest(report_type=ReportType.INVESTIGATION_REPORT)
        summary = await tiradentes_agent._render_executive_summary(
            sections, request, agent_context
        )

        assert "RESUMO EXECUTIVO" in summary
        assert "Critical Finding" in summary
        assert "Important Discovery" in summary
        assert "Low Priority" not in summary  # Low importance excluded


class TestTiradentesCoverageBoost:
    """Tests to boost Tiradentes coverage from 91.03% to 95%+."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_render_pdf_method(self, tiradentes_agent, agent_context):
        """Test PDF rendering method - Lines 1915-1934."""
        from unittest.mock import AsyncMock, patch

        from src.agents.tiradentes import ReportRequest, ReportSection, ReportType

        # Create test sections
        sections = [
            ReportSection(
                title="Test Report",
                content="Test content for PDF generation",
                importance=5,
            )
        ]

        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT, target_audience="technical"
        )

        # Mock the export_service to avoid actual PDF generation
        mock_pdf_bytes = b"fake-pdf-content-for-testing"

        with patch(
            "src.agents.tiradentes.export_service.generate_pdf",
            new_callable=AsyncMock,
            return_value=mock_pdf_bytes,
        ):
            # Call the _render_pdf method directly (lines 1915-1934)
            result = await tiradentes_agent._render_pdf(
                sections, request, agent_context
            )

            # Verify it returns base64 encoded string
            assert isinstance(result, str)
            # Verify it's valid base64
            import base64

            decoded = base64.b64decode(result)
            assert decoded == mock_pdf_bytes

    @pytest.mark.unit
    def test_risk_mitigation_critical_risk(self, tiradentes_agent):
        """Test risk mitigation recommendations for critical risk (score >= 7) - Lines 1029-1032."""
        anomalies = [
            {
                "anomaly_type": "price_anomaly",
                "severity": 0.95,
                "description": "Critical price deviation",
            }
        ]

        # Critical risk score (>= 7) should trigger urgent recommendations
        recommendations = tiradentes_agent._generate_risk_mitigation_recommendations(
            risk_score=8.5, anomalies=anomalies
        )

        # Lines 1029-1032 should be executed
        assert "URGENTE" in recommendations
        assert "Suspender processos" in recommendations
        assert "controladoria" in recommendations

    @pytest.mark.unit
    def test_risk_mitigation_medium_risk(self, tiradentes_agent):
        """Test risk mitigation recommendations for medium risk (4 <= score < 7) - Lines 1034-1037."""
        anomalies = [
            {
                "anomaly_type": "temporal_anomaly",
                "severity": 0.65,
                "description": "Medium risk pattern",
            }
        ]

        # Medium risk score (>= 4 but < 7) should trigger monitoring recommendations
        recommendations = tiradentes_agent._generate_risk_mitigation_recommendations(
            risk_score=5.5, anomalies=anomalies
        )

        # Lines 1034-1037 should be executed
        assert "Intensificar monitoramento" in recommendations
        assert "Revisar controles internos" in recommendations
        # Should NOT contain urgent recommendations
        assert "URGENTE" not in recommendations
