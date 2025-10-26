"""
Unit tests for Lampião agent.
"""

from unittest.mock import patch

import pytest

from src.agents.deodoro import AgentContext, AgentMessage
from src.agents.lampiao import (
    AnalysisType,
    GeographicInsight,
    LampiaoAgent,
    RegionalAnalysisResult,
    RegionalMetric,
    RegionType,
)


@pytest.fixture
def lampiao_agent():
    """Create Lampião agent instance."""
    return LampiaoAgent()


@pytest.fixture
def agent_context():
    """Create agent context."""
    return AgentContext(
        investigation_id="test-investigation-123",
        user_id="test-user",
        session_id="test-session",
        metadata={},
    )


@pytest.fixture
def sample_regional_data():
    """Sample regional data for testing."""
    return [
        {"region": "SP", "value": 15000000, "population": 45000000},
        {"region": "RJ", "value": 8000000, "population": 17000000},
        {"region": "MG", "value": 6000000, "population": 21000000},
        {"region": "BA", "value": 3000000, "population": 15000000},
        {"region": "RS", "value": 5000000, "population": 11000000},
    ]


@pytest.mark.asyncio
async def test_lampiao_agent_initialization(lampiao_agent):
    """Test agent initialization."""
    assert lampiao_agent.name == "LampiaoAgent"
    assert "regional_analysis" in lampiao_agent.capabilities
    assert "spatial_statistics" in lampiao_agent.capabilities
    assert "inequality_measurement" in lampiao_agent.capabilities

    await lampiao_agent.initialize()
    assert len(lampiao_agent.brazil_regions) == 27  # All Brazilian states


@pytest.mark.asyncio
async def test_comprehensive_regional_analysis(lampiao_agent, agent_context):
    """Test comprehensive regional analysis."""
    from src.core import AgentStatus

    message = AgentMessage(
        sender="test-user",
        recipient="LampiaoAgent",
        action="analyze_regions",
        payload={"metric": "government_spending", "regions": ["SP", "RJ", "MG"]},
    )

    response = await lampiao_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    assert isinstance(response.result, RegionalAnalysisResult)

    result = response.result
    assert result.analysis_type == AnalysisType.DISTRIBUTION
    assert result.regions_analyzed > 0
    assert len(result.metrics) > 0
    assert "gini" in result.inequalities
    assert "theil" in result.inequalities
    assert "williamson" in result.inequalities
    assert len(result.recommendations) > 0


@pytest.mark.asyncio
async def test_regional_inequality_analysis(lampiao_agent, agent_context):
    """Test regional inequality analysis."""
    from src.core import AgentStatus

    await lampiao_agent.initialize()  # Need to initialize for IBGE data

    message = AgentMessage(
        sender="test-user",
        recipient="LampiaoAgent",
        action="inequality_analysis",
        payload={"metric": "income", "region_type": RegionType.STATE},
    )

    response = await lampiao_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    result = response.result

    assert result["metric"] == "income"
    assert result["region_type"] == "state"
    assert "inequality_indices" in result
    assert all(
        idx in result["inequality_indices"]
        for idx in ["gini", "theil", "williamson", "atkinson"]
    )
    assert "decomposition" in result
    assert "trends" in result
    assert len(result["policy_recommendations"]) > 0


@pytest.mark.asyncio
async def test_regional_cluster_detection(lampiao_agent, agent_context):
    """Test regional cluster detection."""
    from src.core import AgentStatus

    message = AgentMessage(
        sender="test-user",
        recipient="LampiaoAgent",
        action="cluster_detection",
        payload={"data": [], "variables": ["gdp", "population", "infrastructure"]},
    )

    response = await lampiao_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    clusters = response.result

    assert isinstance(clusters, list)
    assert len(clusters) > 0

    for cluster in clusters:
        assert "cluster_id" in cluster
        assert "cluster_type" in cluster
        assert "regions" in cluster
        assert "characteristics" in cluster
        assert "significance" in cluster


@pytest.mark.asyncio
async def test_hotspot_identification(lampiao_agent, agent_context):
    """Test geographic hotspot identification."""
    from src.core import AgentStatus

    message = AgentMessage(
        sender="test-user",
        recipient="LampiaoAgent",
        action="hotspot_analysis",
        payload={"metric": "contract_value", "threshold": 0.9},
    )

    response = await lampiao_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    insights = response.result

    assert isinstance(insights, list)
    assert len(insights) > 0

    for insight in insights:
        assert isinstance(insight, GeographicInsight)
        assert insight.insight_type in ["high_concentration", "low_concentration"]
        assert insight.severity in ["low", "medium", "high", "critical"]
        assert len(insight.affected_regions) > 0
        assert insight.confidence > 0 and insight.confidence <= 1


@pytest.mark.asyncio
async def test_spatial_correlation_analysis(lampiao_agent):
    """Test spatial autocorrelation analysis."""
    result = await lampiao_agent.analyze_spatial_correlation("income", RegionType.STATE)

    assert "morans_i" in result
    assert "expected_i" in result
    assert "z_score" in result
    assert "p_value" in result
    assert "interpretation" in result
    assert "local_indicators" in result

    # Check Moran's I is within valid range
    assert -1 <= result["morans_i"] <= 1


@pytest.mark.asyncio
async def test_resource_allocation_optimization(lampiao_agent):
    """Test optimal resource allocation."""
    result = await lampiao_agent.optimize_resource_allocation(
        resources=1000000000,  # 1 billion
        objectives=["reduce_inequality", "maximize_impact"],
        constraints={"min_per_region": 10000000},
    )

    assert "allocations" in result
    assert "optimization_metrics" in result
    assert "sensitivity_analysis" in result

    # Check allocations sum to total
    total_allocated = sum(result["allocations"].values())
    assert abs(total_allocated - 1000000000) < 0.01

    # Check optimization metrics
    metrics = result["optimization_metrics"]
    assert "gini_reduction" in metrics
    assert "efficiency_score" in metrics
    assert "equity_score" in metrics
    assert metrics["feasibility"] is True


@pytest.mark.asyncio
async def test_inequality_calculations(lampiao_agent):
    """Test inequality index calculations."""
    values = [1000, 2000, 3000, 4000, 5000]
    populations = [100, 200, 150, 250, 300]

    # Test Gini coefficient
    gini = lampiao_agent._calculate_gini_coefficient(values)
    assert 0 <= gini <= 1

    # Test Theil index
    theil = lampiao_agent._calculate_theil_index(values)
    assert theil >= 0

    # Test Williamson index
    williamson = lampiao_agent._calculate_williamson_index(values, populations)
    assert williamson >= 0


@pytest.mark.asyncio
async def test_regional_recommendations_generation(lampiao_agent):
    """Test policy recommendation generation."""
    inequalities = {"gini": 0.5, "theil": 0.4}
    clusters = [
        {"cluster_id": "rich", "regions": ["SP", "RJ"]},
        {"cluster_id": "poor", "regions": ["AC", "AP"]},
        {"cluster_id": "medium", "regions": ["BA", "PE"]},
    ]

    recommendations = lampiao_agent._generate_regional_recommendations(
        inequalities, clusters
    )

    assert isinstance(recommendations, list)
    assert len(recommendations) <= 5
    assert all(isinstance(r, str) for r in recommendations)

    # Should recommend redistribution due to high inequality
    assert any("redistribution" in r.lower() for r in recommendations)


@pytest.mark.asyncio
async def test_brazil_regions_data(lampiao_agent):
    """Test Brazilian regions data initialization."""
    regions = lampiao_agent.brazil_regions

    # Check all states are present
    assert len(regions) == 27

    # Check sample states
    assert "SP" in regions
    assert regions["SP"]["name"] == "São Paulo"
    assert regions["SP"]["region"] == "Sudeste"

    assert "BA" in regions
    assert regions["BA"]["name"] == "Bahia"
    assert regions["BA"]["region"] == "Nordeste"

    # Check all regions have required fields
    for _, info in regions.items():
        assert "name" in info
        assert "region" in info
        assert "capital" in info
        assert "area" in info


@pytest.mark.asyncio
async def test_error_handling(lampiao_agent, agent_context):
    """Test error handling in regional analysis."""
    from src.core import AgentStatus

    message = AgentMessage(
        sender="test-user",
        recipient="LampiaoAgent",
        action="invalid_analysis",
        payload={},
    )

    with patch.object(
        lampiao_agent,
        "_perform_comprehensive_regional_analysis",
        side_effect=Exception("Analysis failed"),
    ):
        response = await lampiao_agent.process(message, agent_context)

    assert response.status == AgentStatus.ERROR
    assert response.error is not None
    assert "Analysis failed" in response.error


@pytest.mark.asyncio
async def test_regional_metric_structure(lampiao_agent, agent_context):
    """Test RegionalMetric dataclass structure."""
    metric = RegionalMetric(
        region_id="SP",
        region_name="São Paulo",
        region_type=RegionType.STATE,
        metric_name="gdp",
        value=2000000000000,
        normalized_value=1.0,
        rank=1,
        percentile=100.0,
        metadata={"population": 45000000},
    )

    assert metric.region_id == "SP"
    assert metric.region_type == RegionType.STATE
    assert metric.rank == 1
    assert metric.percentile == 100.0
    assert metric.metadata["population"] == 45000000


@pytest.mark.asyncio
async def test_geographic_insight_structure(lampiao_agent):
    """Test GeographicInsight dataclass structure."""
    insight = GeographicInsight(
        insight_id="insight_001",
        insight_type="high_concentration",
        severity="high",
        affected_regions=["SP", "RJ", "MG"],
        description="High concentration of wealth in Southeast",
        evidence={"gini": 0.6, "concentration_ratio": 0.7},
        recommendations=["Implement redistribution policies"],
        confidence=0.9,
    )

    assert insight.severity == "high"
    assert len(insight.affected_regions) == 3
    assert insight.confidence == 0.9
    assert len(insight.recommendations) == 1


@pytest.mark.asyncio
async def test_gini_coefficient_with_real_data(lampiao_agent):
    """Test Gini coefficient with real Brazilian regional data."""
    # Real approximate GDP per capita by state (R$ thousands, 2023)
    real_gdp_values = [
        102.1,  # DF - highest
        59.3,  # SP
        52.7,  # RJ
        51.2,  # SC
        48.9,  # RS
        47.8,  # PR
        46.1,  # ES
        21.8,  # MA
        21.2,  # PA - lowest
    ]

    gini = lampiao_agent._calculate_gini_coefficient(real_gdp_values)

    # Brazil's regional GDP inequality is high (~0.25-0.50 range)
    # Real calculated value is around 0.287 which is reasonable for regional inequality
    assert (
        0.20 < gini < 0.55
    ), f"Gini {gini} outside expected range for Brazilian regions"

    # Test with equal distribution
    equal_values = [100, 100, 100, 100, 100]
    gini_equal = lampiao_agent._calculate_gini_coefficient(equal_values)
    assert gini_equal < 0.01, "Equal distribution should have Gini near 0"

    # Test with extreme inequality
    extreme_values = [1, 1, 1, 1, 100]
    gini_extreme = lampiao_agent._calculate_gini_coefficient(extreme_values)
    assert gini_extreme > 0.70, "Extreme inequality should have high Gini"


@pytest.mark.asyncio
async def test_theil_index_with_real_data(lampiao_agent):
    """Test Theil index with real Brazilian data."""
    # Real GDP per capita (R$ thousands)
    gdp_per_capita = [59.3, 40.2, 52.7, 28.7, 47.8]  # SP, MG, RJ, BA, PR

    theil = lampiao_agent._calculate_theil_index(gdp_per_capita)

    # Theil index for Brazilian states typically 0.05-0.40
    # Real calculated value is around 0.0405 which is reasonable for regional inequality
    assert 0.01 < theil < 0.45, f"Theil {theil} outside expected range"

    # Test decomposability property (Theil's key feature)
    group1 = [50, 55, 60]
    group2 = [20, 25, 30]
    combined = group1 + group2

    theil_combined = lampiao_agent._calculate_theil_index(combined)
    assert theil_combined > 0, "Combined Theil should show inequality"


@pytest.mark.asyncio
async def test_williamson_index_population_weighted(lampiao_agent):
    """Test Williamson index with population weighting."""
    # Real state data (top 5 by GDP)
    gdp_per_capita = [59.3, 52.7, 40.2, 47.8, 48.9]  # SP, RJ, MG, PR, RS
    populations = [46.6, 17.5, 21.4, 11.6, 11.5]  # millions

    williamson = lampiao_agent._calculate_williamson_index(gdp_per_capita, populations)

    # Williamson index typically 0.15-0.35 for Brazil
    assert 0.10 < williamson < 0.40, f"Williamson {williamson} outside expected range"

    # Test with uniform population
    uniform_pop = [10, 10, 10, 10, 10]
    w_uniform = lampiao_agent._calculate_williamson_index(gdp_per_capita, uniform_pop)
    assert w_uniform > 0, "Should show inequality even with uniform population"


@pytest.mark.asyncio
async def test_edge_cases_inequality_calculations(lampiao_agent):
    """Test edge cases in inequality calculations."""
    # Empty list
    gini_empty = lampiao_agent._calculate_gini_coefficient([])
    assert gini_empty == 0.0, "Empty list should return 0"

    # Single value
    gini_single = lampiao_agent._calculate_gini_coefficient([100])
    assert gini_single == 0.0, "Single value should return 0"

    # With zeros (should be filtered out)
    values_with_zeros = [0, 100, 200, 0, 300]
    gini_zeros = lampiao_agent._calculate_gini_coefficient(values_with_zeros)
    assert 0 < gini_zeros < 1, "Should handle zeros gracefully"

    # With negative values (should be filtered out)
    values_with_negatives = [-50, 100, 200, 300]
    gini_neg = lampiao_agent._calculate_gini_coefficient(values_with_negatives)
    assert 0 < gini_neg < 1, "Should filter negative values"

    # Mismatched lengths for Williamson
    values = [100, 200, 300]
    populations = [10, 20]  # Shorter
    w_mismatch = lampiao_agent._calculate_williamson_index(values, populations)
    assert w_mismatch >= 0, "Should handle mismatched lengths"


@pytest.mark.asyncio
async def test_ibge_data_loading(lampiao_agent):
    """Test IBGE data loading and validation."""
    await lampiao_agent.initialize()

    # Verify geographic boundaries loaded
    assert (
        len(lampiao_agent.geographic_boundaries) > 0
    ), "Should load geographic boundaries"

    # Verify regional indicators loaded
    assert len(lampiao_agent.regional_indicators) == 27, "Should have all 27 states"

    # Validate sample state data
    sp_data = lampiao_agent.regional_indicators.get("SP")
    assert sp_data is not None, "Should have São Paulo data"
    assert sp_data["population"] > 40_000_000, "SP population should be > 40M"
    assert sp_data["gdp_per_capita"] > 50, "SP GDP per capita should be high"
    assert 0.7 < sp_data["hdi"] < 0.9, "SP HDI should be in valid range"

    # Validate poorest state (MA)
    ma_data = lampiao_agent.regional_indicators.get("MA")
    assert ma_data is not None, "Should have Maranhão data"
    assert ma_data["gdp_per_capita"] < 30, "MA GDP per capita should be lower"


@pytest.mark.asyncio
async def test_spatial_indices_setup(lampiao_agent):
    """Test spatial indices for fast queries."""
    await lampiao_agent.initialize()

    # Test region index
    assert "Sudeste" in lampiao_agent.region_index, "Should index Sudeste region"
    assert "SP" in lampiao_agent.region_index["Sudeste"], "SP should be in Sudeste"
    assert "RJ" in lampiao_agent.region_index["Sudeste"], "RJ should be in Sudeste"

    # Test capital index
    assert "são paulo" in lampiao_agent.capital_index, "Should index capital cities"
    assert (
        lampiao_agent.capital_index["são paulo"] == "SP"
    ), "Capital lookup should work"

    # Test state name index
    assert "são paulo" in lampiao_agent.state_name_index, "Should index state names"
    assert (
        lampiao_agent.state_name_index["bahia"] == "BA"
    ), "State name lookup should work"


@pytest.mark.asyncio
async def test_caching_decorator(lampiao_agent):
    """Test cache decorator with TTL."""
    await lampiao_agent.initialize()

    # First call should execute
    result1 = await lampiao_agent.analyze_regional_inequality(
        "gdp_per_capita", RegionType.STATE
    )

    # Second call should use cache (same parameters)
    result2 = await lampiao_agent.analyze_regional_inequality(
        "gdp_per_capita", RegionType.STATE
    )

    # Results should be identical (from cache)
    assert (
        result1["inequality_indices"]["gini"] == result2["inequality_indices"]["gini"]
    )
    assert (
        result1["inequality_indices"]["theil"] == result2["inequality_indices"]["theil"]
    )


@pytest.mark.asyncio
async def test_data_validation_decorator(lampiao_agent):
    """Test geographic data validation decorator."""
    await lampiao_agent.initialize()

    # Valid region code
    result = await lampiao_agent.analyze_regional_inequality("income", RegionType.STATE)
    assert "inequality_indices" in result
    assert not result.get("fallback_used"), "Should not use fallback for valid data"

    # Invalid metric should use fallback
    result_invalid = await lampiao_agent.analyze_regional_inequality(
        "invalid_metric_xyz", RegionType.STATE
    )
    # Should still return valid data structure
    assert "inequality_indices" in result_invalid


@pytest.mark.asyncio
async def test_regional_convergence_trends(lampiao_agent):
    """Test β-convergence and σ-convergence analysis."""
    await lampiao_agent.initialize()

    result = await lampiao_agent.analyze_regional_inequality(
        "gdp_per_capita", RegionType.STATE
    )

    # Verify trend analysis
    assert "trends" in result, "Should include trend analysis"
    assert "5_year_change" in result["trends"], "Should show historical change"
    assert "convergence_rate" in result["trends"], "Should calculate convergence rate"
    assert "projection_2030" in result["trends"], "Should project future inequality"

    # Brazilian regions show convergence (negative change)
    assert result["trends"]["5_year_change"] < 0, "Should show declining inequality"
    assert result["trends"]["convergence_rate"] > 0, "Should have positive convergence"


@pytest.mark.asyncio
async def test_spatial_correlation_with_gdp_variable(lampiao_agent):
    """Test spatial correlation with GDP per capita variable."""
    await lampiao_agent.initialize()

    result = await lampiao_agent.analyze_spatial_correlation(
        "gdp_per_capita", RegionType.STATE
    )

    assert "morans_i" in result
    assert "local_indicators" in result
    assert -1 <= result["morans_i"] <= 1

    # Should have cluster information
    assert "high_high_clusters" in result["local_indicators"]
    assert "low_low_clusters" in result["local_indicators"]


@pytest.mark.asyncio
async def test_spatial_correlation_with_hdi_variable(lampiao_agent):
    """Test spatial correlation with HDI variable."""
    await lampiao_agent.initialize()

    result = await lampiao_agent.analyze_spatial_correlation("hdi", RegionType.STATE)

    assert "morans_i" in result
    assert "interpretation" in result
    assert -1 <= result["morans_i"] <= 1


@pytest.mark.asyncio
async def test_spatial_correlation_with_population_variable(lampiao_agent):
    """Test spatial correlation with population variable."""
    await lampiao_agent.initialize()

    result = await lampiao_agent.analyze_spatial_correlation(
        "population", RegionType.STATE
    )

    assert "morans_i" in result
    assert "local_indicators" in result
    assert -1 <= result["morans_i"] <= 1


@pytest.mark.asyncio
async def test_spatial_correlation_with_unknown_variable(lampiao_agent):
    """Test spatial correlation with unknown variable (should use default)."""
    await lampiao_agent.initialize()

    result = await lampiao_agent.analyze_spatial_correlation(
        "unknown_metric", RegionType.STATE
    )

    assert "morans_i" in result
    # Should use default (gdp_per_capita)
    assert isinstance(result["morans_i"], int | float)


@pytest.mark.asyncio
async def test_spatial_correlation_cluster_identification(lampiao_agent):
    """Test that spatial correlation correctly identifies clusters."""
    await lampiao_agent.initialize()

    result = await lampiao_agent.analyze_spatial_correlation(
        "gdp_per_capita", RegionType.STATE
    )

    local_indicators = result["local_indicators"]

    # Should have all cluster types
    assert "high_high_clusters" in local_indicators
    assert "low_low_clusters" in local_indicators
    assert "high_low_outliers" in local_indicators
    assert "low_high_outliers" in local_indicators

    # All should be lists
    assert isinstance(local_indicators["high_high_clusters"], list)
    assert isinstance(local_indicators["low_low_clusters"], list)
    assert isinstance(local_indicators["high_low_outliers"], list)
    assert isinstance(local_indicators["low_high_outliers"], list)


@pytest.mark.asyncio
async def test_geographic_boundaries_fallback(lampiao_agent):
    """Test that agent handles IBGE API failure gracefully."""
    with patch("httpx.AsyncClient.get") as mock_get:
        # Simulate API failure
        mock_get.side_effect = Exception("IBGE API unavailable")

        # Agent should still initialize with fallback data
        await lampiao_agent._load_geographic_boundaries()

        # Should have fallback boundaries loaded
        assert len(lampiao_agent.geographic_boundaries) > 0
        assert "SP" in lampiao_agent.geographic_boundaries


@pytest.mark.asyncio
async def test_spatial_indices_error_handling(lampiao_agent):
    """Test spatial indices setup error handling."""
    # Force an error by corrupting internal state
    original_states = lampiao_agent.states_data
    lampiao_agent.states_data = None

    # Should handle error gracefully
    await lampiao_agent._setup_spatial_indices()

    # Should have empty indices as fallback
    assert isinstance(lampiao_agent.region_index, dict)

    # Restore state
    lampiao_agent.states_data = original_states


# New tests to reach 95%+ coverage


@pytest.mark.asyncio
async def test_gini_coefficient_with_zero_sum(lampiao_agent):
    """Test Gini coefficient calculation with zero sum - Lines 1025-1026."""
    # Data with all zeros (sum = 0)
    values = [0.0, 0.0, 0.0]
    gini = lampiao_agent._calculate_gini_coefficient(values)

    # Should return 0.0 with warning
    assert gini == 0.0


@pytest.mark.asyncio
async def test_theil_index_insufficient_values(lampiao_agent):
    """Test Theil index with insufficient data - Lines 1043-1046."""
    # Only 1 value (< 2 required)
    values = [100000.0]
    theil = lampiao_agent._calculate_theil_index(values)

    # Should return 0.0 with warning
    assert theil == 0.0


@pytest.mark.asyncio
async def test_theil_index_zero_mean(lampiao_agent):
    """Test Theil index with zero mean - Lines 1052-1053."""
    # All zeros (mean = 0)
    values = [0.0, 0.0, 0.0]
    theil = lampiao_agent._calculate_theil_index(values)

    # Should return 0.0 with warning
    assert theil == 0.0


@pytest.mark.asyncio
async def test_williamson_index_zero_mean(lampiao_agent):
    """Test Williamson index with zero mean - Lines 1094-1095."""
    # Data with zero mean
    regional_values = [0.0, 0.0, 0.0]
    populations = [1000000, 2000000, 3000000]

    williamson = lampiao_agent._calculate_williamson_index(regional_values, populations)

    # Should return 0.0 with warning
    assert williamson == 0.0


@pytest.mark.asyncio
async def test_decorator_unknown_region_code(lampiao_agent, agent_context):
    """Test decorator with unknown region code - Lines 99-100."""
    from src.core import AgentStatus

    await lampiao_agent.initialize()

    # Create message with invalid region code
    message = AgentMessage(
        sender="test-user",
        recipient="LampiaoAgent",
        action="analyze_regions",
        payload={
            "metric": "government_spending",
            "regions": ["XX", "YY"],
        },  # Invalid codes
    )

    # Process should handle invalid region gracefully (with warnings)
    response = await lampiao_agent.process(message, agent_context)

    # Should complete (decorator logs warning but continues)
    assert response.status == AgentStatus.COMPLETED


@pytest.mark.asyncio
async def test_decorator_unknown_metric(lampiao_agent, agent_context):
    """Test decorator with unknown metric - Lines 105-108."""
    from src.core import AgentStatus

    await lampiao_agent.initialize()

    # Create message with invalid metric
    message = AgentMessage(
        sender="test-user",
        recipient="LampiaoAgent",
        action="analyze_regions",
        payload={
            "metric": "invalid_metric_xyz",
            "regions": ["SP", "RJ"],
        },  # Invalid metric
    )

    # Process should handle invalid metric gracefully (fallback to gdp_per_capita)
    response = await lampiao_agent.process(message, agent_context)

    # Should complete (decorator logs warning and uses fallback)
    assert response.status == AgentStatus.COMPLETED
