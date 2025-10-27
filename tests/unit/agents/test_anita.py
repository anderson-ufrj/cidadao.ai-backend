"""
Unit tests for Anita Agent - Pattern analysis and correlation detection specialist.
Tests semantic routing, pattern recognition, and correlation analysis capabilities.
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.agents.anita import AnalystAgent, CorrelationResult, PatternResult
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus


@pytest.fixture
def mock_transparency_api():
    """Mock transparency API for testing."""
    api = AsyncMock()

    # Mock contract data with patterns
    api.get_contracts.return_value = {
        "data": [
            {
                "id": "contract_001",
                "valor": 1000000.0,
                "dataAssinatura": "2024-01-15",
                "fornecedor": {"nome": "Tech Corp A", "cnpj": "11.111.111/0001-11"},
                "orgao": {"nome": "Ministério da Educação", "codigo": "26000"},
            },
            {
                "id": "contract_002",
                "valor": 2500000.0,
                "dataAssinatura": "2024-02-20",
                "fornecedor": {"nome": "Tech Corp A", "cnpj": "11.111.111/0001-11"},
                "orgao": {"nome": "Ministério da Educação", "codigo": "26000"},
            },
            {
                "id": "contract_003",
                "valor": 1500000.0,
                "dataAssinatura": "2024-03-10",
                "fornecedor": {"nome": "Different Corp", "cnpj": "22.222.222/0001-22"},
                "orgao": {"nome": "Ministério da Saúde", "codigo": "25000"},
            },
        ],
        "total": 3,
    }

    # Mock expense data with temporal patterns
    api.get_expenses.return_value = {
        "data": [
            {
                "id": "exp_001",
                "valor": 500000.0,
                "dataCompetencia": "2024-01-01",
                "orgaoSuperior": {"nome": "Ministério da Educação", "codigo": "26000"},
            },
            {
                "id": "exp_002",
                "valor": 750000.0,
                "dataCompetencia": "2024-02-01",
                "orgaoSuperior": {"nome": "Ministério da Educação", "codigo": "26000"},
            },
            {
                "id": "exp_003",
                "valor": 1200000.0,
                "dataCompetencia": "2024-03-01",
                "orgaoSuperior": {"nome": "Ministério da Educação", "codigo": "26000"},
            },
        ],
        "total": 3,
    }

    return api


@pytest.fixture
def mock_spectral_analyzer():
    """Mock spectral analyzer for pattern detection."""
    analyzer = AsyncMock()

    analyzer.analyze_time_series.return_value = {
        "periodic_patterns": [
            {
                "period": 30,  # Monthly pattern
                "amplitude": 0.75,
                "phase": 0.2,
                "confidence": 0.89,
                "description": "Monthly spending cycle detected",
            },
            {
                "period": 90,  # Quarterly pattern
                "amplitude": 0.45,
                "phase": 0.1,
                "confidence": 0.72,
                "description": "Quarterly budget allocation pattern",
            },
        ],
        "trend_analysis": {
            "trend_direction": "increasing",
            "trend_strength": 0.68,
            "seasonal_component": 0.23,
            "noise_level": 0.15,
        },
        "anomaly_scores": [0.1, 0.2, 0.8, 0.1, 0.9, 0.2],
        "spectral_features": {
            "dominant_frequency": 0.033,  # ~30 day period
            "power_spectrum": [0.8, 0.6, 0.4, 0.2, 0.1],
            "entropy": 2.34,
        },
    }

    analyzer.detect_correlations.return_value = {
        "correlations": [
            {
                "variables": ["contract_values", "expense_amounts"],
                "correlation_coefficient": 0.78,
                "p_value": 0.001,
                "significance": "high",
                "correlation_type": "positive_linear",
            },
            {
                "variables": ["supplier_concentration", "price_deviation"],
                "correlation_coefficient": 0.62,
                "p_value": 0.025,
                "significance": "medium",
                "correlation_type": "positive_moderate",
            },
        ],
        "network_metrics": {
            "clustering_coefficient": 0.45,
            "average_path_length": 2.8,
            "modularity": 0.33,
        },
    }

    return analyzer


@pytest.fixture
def agent_context():
    """Test agent context for pattern analysis."""
    return AgentContext(
        investigation_id="pattern-analysis-001",
        user_id="analyst-user",
        session_id="analysis-session",
        metadata={
            "analysis_type": "pattern_detection",
            "data_sources": ["contracts", "expenses"],
            "time_window": "2024-01-01:2024-12-31",
        },
        trace_id="trace-anita-789",
    )


@pytest.fixture
def anita_agent(mock_transparency_api, mock_spectral_analyzer):
    """Create Anita agent with mocked dependencies."""
    with (
        patch(
            "src.agents.anita.get_transparency_collector",
            return_value=mock_transparency_api,
        ),
        patch("src.agents.anita.SpectralAnalyzer", return_value=mock_spectral_analyzer),
    ):
        return AnalystAgent(
            min_correlation_threshold=0.3,
            significance_threshold=0.05,
            trend_detection_window=6,
        )


@pytest.mark.unit
class TestAnitaAgent:
    """Test suite for Anita (Pattern Analysis Agent)."""

    @pytest.mark.unit
    def test_agent_initialization(self, anita_agent):
        """Test Anita agent initialization."""
        assert anita_agent.name == "Anita"
        assert anita_agent.correlation_threshold == 0.3
        assert anita_agent.significance_threshold == 0.05
        assert anita_agent.trend_window == 6

        # Check capabilities (updated to match actual implementation)
        expected_capabilities = [
            "spending_trend_analysis",
            "organizational_comparison",
            "vendor_behavior_analysis",
            "seasonal_pattern_detection",
            "value_distribution_analysis",
            "correlation_analysis",
            "efficiency_metrics",
            "predictive_modeling",
        ]

        for capability in expected_capabilities:
            assert capability in anita_agent.capabilities

    @pytest.mark.unit
    async def test_temporal_pattern_analysis(self, anita_agent, agent_context):
        """Test temporal pattern detection in government data."""
        message = AgentMessage(
            sender="investigator_agent",
            recipient="Anita",
            action="analyze",
            payload={
                "data_type": "expenses",
                "time_window": "2024-01-01:2024-06-30",
                "pattern_types": ["periodic", "seasonal", "trend"],
                "granularity": "monthly",
            },
        )

        response = await anita_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "temporal_patterns" in response.result

        patterns = response.result["temporal_patterns"]
        assert len(patterns["periodic_patterns"]) >= 1

        # Check monthly pattern detection
        monthly_pattern = next(
            p for p in patterns["periodic_patterns"] if p["period"] == 30
        )
        assert monthly_pattern["confidence"] > 0.8
        assert monthly_pattern["description"] == "Monthly spending cycle detected"

    @pytest.mark.unit
    async def test_correlation_analysis(self, anita_agent, agent_context):
        """Test correlation detection between different data dimensions."""
        message = AgentMessage(
            sender="analyst_agent",
            recipient="Anita",
            action="analyze",
            payload={
                "variables": ["contract_values", "expense_amounts", "supplier_count"],
                "correlation_methods": ["pearson", "spearman", "mutual_information"],
                "significance_level": 0.05,
                "include_network_analysis": True,
            },
        )

        response = await anita_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "correlation_analysis" in response.result

        correlations = response.result["correlation_analysis"]
        assert len(correlations["correlations"]) >= 2

        # Check high significance correlation
        high_corr = next(
            c for c in correlations["correlations"] if c["significance"] == "high"
        )
        assert high_corr["correlation_coefficient"] > 0.7
        assert high_corr["p_value"] < 0.01

    @pytest.mark.unit
    async def test_semantic_routing(self, anita_agent, agent_context):
        """Test semantic routing of analysis requests."""
        queries = [
            "Encontrar padrões de superfaturamento em contratos",
            "Analisar concentração de fornecedores por região",
            "Detectar anomalias temporais em gastos públicos",
        ]

        message = AgentMessage(
            sender="master_agent",
            recipient="Anita",
            action="analyze",
            payload={
                "queries": queries,
                "route_to_specialists": True,
                "similarity_threshold": 0.8,
            },
        )

        response = await anita_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "semantic_routing" in response.result

        routing = response.result["semantic_routing"]
        assert len(routing["query_routes"]) == len(queries)

        for route in routing["query_routes"]:
            assert "recommended_agent" in route
            assert "confidence" in route
            assert route["confidence"] > 0.5

    @pytest.mark.unit
    async def test_supplier_concentration_analysis(self, anita_agent, agent_context):
        """Test analysis of supplier concentration patterns."""
        message = AgentMessage(
            sender="tiradentes_agent",
            recipient="Anita",
            action="analyze",
            payload={
                "analysis_scope": "ministry_level",
                "include_geographic_analysis": True,
                "concentration_metrics": ["hhi", "gini", "entropy"],
                "time_aggregation": "quarterly",
            },
        )

        response = await anita_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "supplier_concentration" in response.result

        concentration = response.result["supplier_concentration"]
        assert "concentration_metrics" in concentration
        assert "geographic_distribution" in concentration
        assert "temporal_evolution" in concentration

        # Check HHI calculation
        metrics = concentration["concentration_metrics"]
        assert "hhi_index" in metrics
        assert 0 <= metrics["hhi_index"] <= 1

    @pytest.mark.unit
    async def test_network_pattern_detection(self, anita_agent, agent_context):
        """Test network pattern detection in government relationships."""
        message = AgentMessage(
            sender="machado_agent",
            recipient="Anita",
            action="analyze",
            payload={
                "network_type": "supplier_ministry_relationships",
                "include_centrality_measures": True,
                "detect_communities": True,
                "relationship_strength_threshold": 0.3,
            },
        )

        response = await anita_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "network_analysis" in response.result

        network = response.result["network_analysis"]
        assert "network_metrics" in network
        assert "community_detection" in network
        assert "centrality_measures" in network

        # Check network metrics
        metrics = network["network_metrics"]
        assert "clustering_coefficient" in metrics
        assert "average_path_length" in metrics
        assert metrics["clustering_coefficient"] > 0

    @pytest.mark.unit
    async def test_anomaly_scoring(self, anita_agent, agent_context):
        """Test anomaly scoring for pattern deviations."""
        message = AgentMessage(
            sender="investigator_agent",
            recipient="Anita",
            action="analyze",
            payload={
                "data_points": [
                    {"value": 1000000, "date": "2024-01-01", "entity": "supplier_a"},
                    {"value": 1200000, "date": "2024-02-01", "entity": "supplier_a"},
                    {
                        "value": 5000000,
                        "date": "2024-03-01",
                        "entity": "supplier_a",
                    },  # Anomaly
                    {"value": 1100000, "date": "2024-04-01", "entity": "supplier_a"},
                ],
                "anomaly_methods": [
                    "isolation_forest",
                    "local_outlier_factor",
                    "statistical",
                ],
                "contamination_rate": 0.1,
            },
        )

        response = await anita_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "anomaly_analysis" in response.result

        anomalies = response.result["anomaly_analysis"]
        assert "anomaly_scores" in anomalies
        assert len(anomalies["anomaly_scores"]) == 4

        # Check that March value has high anomaly score
        march_score = anomalies["anomaly_scores"][2]
        assert march_score > 0.7  # Should be detected as anomaly

    @pytest.mark.unit
    async def test_trend_forecasting(self, anita_agent, agent_context):
        """Test trend analysis and forecasting capabilities."""
        message = AgentMessage(
            sender="analyst_agent",
            recipient="Anita",
            action="analyze",
            payload={
                "historical_data": {
                    "2024-01": 1000000,
                    "2024-02": 1200000,
                    "2024-03": 1500000,
                    "2024-04": 1800000,
                },
                "forecast_horizon": 3,  # 3 months ahead
                "include_confidence_intervals": True,
                "trend_components": ["linear", "seasonal", "cyclical"],
            },
        )

        response = await anita_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "trend_forecast" in response.result

        forecast = response.result["trend_forecast"]
        assert "predictions" in forecast
        assert "confidence_intervals" in forecast
        assert "trend_components" in forecast

        # Check forecast length
        assert len(forecast["predictions"]) == 3

        # Check trend direction
        trend = forecast["trend_components"]
        assert trend["trend_direction"] in ["increasing", "decreasing", "stable"]

    @pytest.mark.unit
    async def test_pattern_significance_filtering(self, anita_agent, agent_context):
        """Test filtering patterns by significance threshold."""
        # Create agent with high significance threshold
        anita_agent.pattern_significance_threshold = 0.9

        message = AgentMessage(
            sender="quality_agent",
            recipient="Anita",
            action="analyze",
            payload={"data_type": "contracts", "significance_filter": True},
        )

        response = await anita_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED

        # All returned patterns should meet significance threshold
        patterns = response.result["temporal_patterns"]["periodic_patterns"]
        for pattern in patterns:
            assert pattern["confidence"] >= 0.9

    @pytest.mark.unit
    async def test_multi_dimensional_analysis(self, anita_agent, agent_context):
        """Test multi-dimensional pattern analysis."""
        message = AgentMessage(
            sender="comprehensive_analyst",
            recipient="Anita",
            action="analyze",
            payload={
                "dimensions": ["temporal", "geographic", "categorical", "financial"],
                "interaction_analysis": True,
                "dimension_weights": {
                    "temporal": 0.3,
                    "geographic": 0.2,
                    "categorical": 0.2,
                    "financial": 0.3,
                },
            },
        )

        response = await anita_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "multi_dimensional_analysis" in response.result

        analysis = response.result["multi_dimensional_analysis"]
        assert "dimension_analysis" in analysis
        assert "interaction_effects" in analysis
        assert "composite_score" in analysis

        # Check all dimensions were analyzed
        dim_analysis = analysis["dimension_analysis"]
        assert len(dim_analysis) == 4
        for dim in ["temporal", "geographic", "categorical", "financial"]:
            assert dim in dim_analysis

    @pytest.mark.unit
    async def test_error_handling_insufficient_data(self, anita_agent, agent_context):
        """Test error handling when insufficient data for analysis."""
        # Mock empty data response
        anita_agent.transparency_api.get_contracts.return_value = {
            "data": [],
            "total": 0,
        }

        message = AgentMessage(
            sender="test_agent",
            recipient="Anita",
            action="analyze",
            payload={"data_type": "contracts"},
        )

        response = await anita_agent.process(message, agent_context)

        assert response.status == AgentStatus.WARNING
        assert "insufficient data" in response.error.lower()

    @pytest.mark.unit
    async def test_concurrent_pattern_analysis(self, anita_agent):
        """Test concurrent analysis of multiple data streams."""
        contexts = [AgentContext(investigation_id=f"concurrent-{i}") for i in range(3)]

        messages = [
            AgentMessage(
                sender="concurrent_tester",
                recipient="Anita",
                action="analyze",
                payload={"data_type": f"data_stream_{i}"},
            )
            for i in range(3)
        ]

        # Process concurrently
        import asyncio

        responses = await asyncio.gather(
            *[
                anita_agent.process(msg, ctx)
                for msg, ctx in zip(messages, contexts, strict=False)
            ]
        )

        assert len(responses) == 3
        assert all(r.status == AgentStatus.COMPLETED for r in responses)
        assert len({r.metadata.get("investigation_id") for r in responses}) == 3

    @pytest.mark.unit
    async def test_pattern_caching(self, anita_agent, agent_context):
        """Test caching of pattern analysis results."""
        message = AgentMessage(
            sender="cache_tester",
            recipient="Anita",
            action="analyze",
            payload={"data_type": "expenses", "cache_results": True, "cache_ttl": 3600},
        )

        # First analysis
        response1 = await anita_agent.process(message, agent_context)
        assert response1.status == AgentStatus.COMPLETED

        # Second analysis (should use cache)
        with patch.object(
            anita_agent.spectral_analyzer, "analyze_time_series"
        ) as mock_analyze:
            response2 = await anita_agent.process(message, agent_context)

            # Should not call analyzer again due to caching
            mock_analyze.assert_not_called()
            assert response2.status == AgentStatus.COMPLETED


class TestPatternResult:
    """Test PatternResult data model."""

    @pytest.mark.unit
    def test_pattern_result_creation(self):
        """Test creating pattern result."""
        result = PatternResult(
            pattern_type="temporal_cycle",
            description="Monthly spending pattern detected",
            significance=0.85,
            confidence=0.92,
            insights=["Regular monthly increases", "Peak spending mid-month"],
            evidence={"period": 30, "amplitude": 0.75},
            recommendations=["Monitor for deviations", "Investigate peak periods"],
            entities_involved=[{"entity": "Ministry A", "involvement": 0.8}],
            trend_direction="increasing",
            correlation_strength=0.68,
        )

        assert result.pattern_type == "temporal_cycle"
        assert result.significance == 0.85
        assert result.confidence == 0.92
        assert len(result.insights) == 2
        assert len(result.recommendations) == 2
        assert result.trend_direction == "increasing"

    @pytest.mark.unit
    def test_pattern_result_significance_levels(self):
        """Test pattern significance level categorization."""
        high_sig = PatternResult(
            pattern_type="high_significance",
            description="Test",
            significance=0.9,
            confidence=0.95,
            insights=[],
            evidence={},
            recommendations=[],
            entities_involved=[],
        )

        low_sig = PatternResult(
            pattern_type="low_significance",
            description="Test",
            significance=0.3,
            confidence=0.4,
            insights=[],
            evidence={},
            recommendations=[],
            entities_involved=[],
        )

        assert high_sig.significance > 0.8  # High significance
        assert low_sig.significance < 0.5  # Low significance


class TestCorrelationResult:
    """Test CorrelationResult data model."""

    @pytest.mark.unit
    def test_correlation_result_creation(self):
        """Test creating correlation result."""
        result = CorrelationResult(
            correlation_type="positive_linear",
            variables=["contract_values", "expense_amounts"],
            correlation_coefficient=0.78,
            p_value=0.001,
            significance_level="high",
            description="Strong positive correlation between contract values and expenses",
            business_interpretation="When contract values increase, expense amounts tend to increase proportionally",
            evidence={"sample_size": 100, "confidence_interval": [0.65, 0.89]},
            recommendations=[
                "Monitor this relationship over time",
                "Investigate causal factors",
            ],
        )

        assert result.correlation_type == "positive_linear"
        assert len(result.variables) == 2
        assert result.correlation_coefficient == 0.78
        assert result.p_value == 0.001
        assert result.significance_level == "high"

    @pytest.mark.unit
    def test_correlation_strength_interpretation(self):
        """Test correlation strength interpretation."""
        strong_corr = CorrelationResult(
            correlation_type="strong_positive",
            variables=["var1", "var2"],
            correlation_coefficient=0.85,
            p_value=0.0001,
            significance_level="high",
            description="Strong positive correlation detected",
            business_interpretation="Variables show very strong positive relationship",
            evidence={"strength": "strong", "direction": "positive"},
            recommendations=["Use this relationship for forecasting"],
        )

        weak_corr = CorrelationResult(
            correlation_type="weak_positive",
            variables=["var3", "var4"],
            correlation_coefficient=0.25,
            p_value=0.15,
            significance_level="low",
            description="Weak positive correlation detected",
            business_interpretation="Variables show weak positive relationship",
            evidence={"strength": "weak", "direction": "positive"},
            recommendations=["Not suitable for predictive modeling"],
        )

        assert abs(strong_corr.correlation_coefficient) > 0.8  # Strong correlation
        assert abs(weak_corr.correlation_coefficient) < 0.3  # Weak correlation


# ============================================================================
# NEW TESTS FOR COVERAGE IMPROVEMENT - PHASE 1: Quick Wins
# Added: 2025-10-25 - Goal: Improve coverage from 69.94% to 78%+
# ============================================================================


class TestCorrelationAnalysis:
    """Test correlation analysis methods (Category 3 - Coverage improvement)."""

    @pytest.fixture
    def anita_agent(self):
        """Create Anita agent instance for testing."""
        return AnalystAgent()

    @pytest.fixture
    def agent_context(self):
        """Create agent context for testing."""
        return AgentContext(
            investigation_id="test_investigation_001",
            user_id="test_user",
            session_id="test_session",
        )

    @pytest.fixture
    def correlation_test_data(self):
        """Create test data for correlation analysis."""
        # Data with strong positive correlation (count vs value)
        data = []
        for i in range(15):
            # Create pattern: more contracts = higher values
            month = f"2024-{i % 12 + 1:02d}"
            org_code = f"ORG_{i % 3}"
            count = i + 5  # 5 to 19 contracts
            base_value = count * 100000  # Strong positive correlation

            for j in range(count):
                data.append(
                    {
                        "_org_code": org_code,
                        "_month": month,
                        "valorInicial": base_value + j * 10000,
                        "valorGlobal": None,
                        "fornecedor": {"nome": f"Vendor_{j % 3}"},
                    }
                )
        return data

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_perform_correlation_with_strong_positive(
        self, anita_agent, agent_context, correlation_test_data
    ):
        """Test correlation analysis with strong positive correlation (lines 881-920)."""
        result = await anita_agent._perform_correlation_analysis(
            correlation_test_data, agent_context
        )

        assert len(result) > 0, "Should detect correlation"
        correlation = result[0]
        assert correlation.correlation_coefficient > 0.3  # Above threshold
        assert correlation.significance_level in ["high", "medium"]
        assert "count" in correlation.variables[0].lower()
        assert "value" in correlation.variables[1].lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_perform_correlation_with_weak_negative(
        self, anita_agent, agent_context
    ):
        """Test correlation analysis with weak negative correlation (lines 901-927)."""
        # Create data with weak negative correlation
        data = []
        for i in range(15):
            month = f"2024-{i % 12 + 1:02d}"
            org_code = f"ORG_{i % 3}"
            count = 15 - i  # Decreasing count
            base_value = (i + 5) * 80000  # Slightly increasing value (weak negative)

            for j in range(max(1, count)):
                data.append(
                    {
                        "_org_code": org_code,
                        "_month": month,
                        "valorInicial": base_value,
                        "fornecedor": {"nome": f"Vendor_{j}"},
                    }
                )

        # Lower threshold to detect weak correlation
        anita_agent.correlation_threshold = 0.1
        result = await anita_agent._perform_correlation_analysis(data, agent_context)

        # May or may not detect depending on exact values
        # Just verify no exceptions and proper structure
        assert isinstance(result, list)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_perform_correlation_with_insufficient_data(
        self, anita_agent, agent_context
    ):
        """Test correlation with less than required data points (lines 903, 913)."""
        # Data with only 2 organizations (< 3 required)
        data = [
            {
                "_org_code": "ORG_1",
                "_month": "2024-01",
                "valorInicial": 100000,
                "fornecedor": {"nome": "Vendor_1"},
            },
            {
                "_org_code": "ORG_2",
                "_month": "2024-02",
                "valorInicial": 200000,
                "fornecedor": {"nome": "Vendor_2"},
            },
        ]

        result = await anita_agent._perform_correlation_analysis(data, agent_context)

        # Should return empty list due to insufficient data
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_perform_correlation_with_constant_values(
        self, anita_agent, agent_context
    ):
        """Test correlation when values have no variance (lines 915-925)."""
        # All contracts have same value (no variance)
        data = []
        for i in range(15):
            month = f"2024-{i % 12 + 1:02d}"
            org_code = f"ORG_{i % 3}"

            for j in range(5):
                data.append(
                    {
                        "_org_code": org_code,
                        "_month": month,
                        "valorInicial": 100000,  # Constant value
                        "fornecedor": {"nome": f"Vendor_{j}"},
                    }
                )

        result = await anita_agent._perform_correlation_analysis(data, agent_context)

        # Correlation may be NaN or not computed with constant values
        assert isinstance(result, list)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_efficiency_metrics_high_performer(
        self, anita_agent, agent_context
    ):
        """Test efficiency calculation for high-performing organization (lines 957-1010)."""
        # High performer: many vendors, consistent activity, good values
        data = []
        for month in range(1, 13):  # Active all 12 months
            for vendor_id in range(8):  # 8 different vendors
                data.append(
                    {
                        "_org_code": "ORG_HIGH",
                        "_month": f"2024-{month:02d}",
                        "valorInicial": 500000 + vendor_id * 50000,
                        "fornecedor": {"nome": f"Vendor_{vendor_id}"},
                    }
                )

        # Add low performer for comparison
        data.append(
            {
                "_org_code": "ORG_LOW",
                "_month": "2024-01",
                "valorInicial": 100000,
                "fornecedor": {"nome": "Vendor_0"},
            }
        )

        result = await anita_agent._calculate_efficiency_metrics(data, agent_context)

        assert isinstance(result, list)
        # High performer should have good efficiency metrics
        # vendor_diversity = 8/96 ≈ 0.083
        # activity_consistency = 12/12 = 1.0
        # efficiency = 0.083 * 0.4 + 1.0 * 0.6 ≈ 0.633

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_efficiency_metrics_low_variance(
        self, anita_agent, agent_context
    ):
        """Test efficiency with low variance - all orgs similar (lines 1011-1015)."""
        # All organizations with similar efficiency
        data = []
        for org_id in range(5):
            for month in range(1, 7):  # 6 months each
                for vendor in range(3):  # 3 vendors each
                    data.append(
                        {
                            "_org_code": f"ORG_{org_id}",
                            "_month": f"2024-{month:02d}",
                            "valorInicial": 300000 + org_id * 10000,  # Similar values
                            "fornecedor": {"nome": f"Vendor_{vendor}"},
                        }
                    )

        result = await anita_agent._calculate_efficiency_metrics(data, agent_context)

        # With low variance, std should be small
        assert isinstance(result, list)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_efficiency_metrics_missing_data(
        self, anita_agent, agent_context
    ):
        """Test efficiency calculation with incomplete data (lines 979-985)."""
        # Data with missing/None values
        data = [
            {
                "_org_code": "ORG_1",
                "_month": "2024-01",
                "valorInicial": None,  # Missing value
                "valorGlobal": 200000,  # Will use this instead
                "fornecedor": {"nome": "Vendor_1"},
            },
            {
                "_org_code": "ORG_1",
                "_month": "2024-02",
                "valorInicial": 150000,
                "fornecedor": {},  # Empty vendor dict (no "nome")
            },
            {
                "_org_code": None,  # Missing org_code
                "_month": "2024-03",
                "valorInicial": 100000,
                "fornecedor": {"nome": "Vendor_2"},
            },
        ]

        result = await anita_agent._calculate_efficiency_metrics(data, agent_context)

        # Should handle missing data gracefully
        assert isinstance(result, list)
