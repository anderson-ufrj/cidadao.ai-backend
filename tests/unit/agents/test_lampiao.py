"""
Unit tests for Lampião agent.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.lampiao import (
    LampiaoAgent,
    RegionType,
    AnalysisType,
    RegionalMetric,
    RegionalAnalysisResult,
    GeographicInsight
)
from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse


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
        metadata={}
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
    message = AgentMessage(
        role="user",
        content="Analyze regional distribution",
        data={"metric": "government_spending", "regions": ["SP", "RJ", "MG"]}
    )
    
    response = await lampiao_agent.process(message, agent_context)
    
    assert response.success
    assert response.response_type == "regional_analysis"
    assert isinstance(response.data, RegionalAnalysisResult)
    
    result = response.data
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
    message = AgentMessage(
        role="user",
        content="Analyze inequality",
        type="inequality_analysis",
        data={
            "metric": "income",
            "region_type": "state"
        }
    )
    
    response = await lampiao_agent.process(message, agent_context)
    
    assert response.success
    result = response.data
    
    assert result["metric"] == "income"
    assert result["region_type"] == "state"
    assert "inequality_indices" in result
    assert all(idx in result["inequality_indices"] for idx in ["gini", "theil", "williamson", "atkinson"])
    assert "decomposition" in result
    assert "trends" in result
    assert len(result["policy_recommendations"]) > 0


@pytest.mark.asyncio
async def test_regional_cluster_detection(lampiao_agent, agent_context):
    """Test regional cluster detection."""
    message = AgentMessage(
        role="user",
        content="Detect clusters",
        type="cluster_detection",
        data={
            "data": [],
            "variables": ["gdp", "population", "infrastructure"]
        }
    )
    
    response = await lampiao_agent.process(message, agent_context)
    
    assert response.success
    clusters = response.data
    
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
    message = AgentMessage(
        role="user",
        content="Identify hotspots",
        type="hotspot_analysis",
        data={
            "metric": "contract_value",
            "threshold": 0.9
        }
    )
    
    response = await lampiao_agent.process(message, agent_context)
    
    assert response.success
    insights = response.data
    
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
    result = await lampiao_agent.analyze_spatial_correlation(
        "income",
        RegionType.STATE
    )
    
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
        constraints={"min_per_region": 10000000}
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
        {"cluster_id": "medium", "regions": ["BA", "PE"]}
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
    for state, info in regions.items():
        assert "name" in info
        assert "region" in info
        assert "capital" in info
        assert "area" in info


@pytest.mark.asyncio
async def test_error_handling(lampiao_agent, agent_context):
    """Test error handling in regional analysis."""
    # Create message that will cause an error
    message = MagicMock()
    message.type = "invalid_analysis"
    message.data = None
    
    with patch.object(lampiao_agent, '_perform_comprehensive_regional_analysis',
                      side_effect=Exception("Analysis failed")):
        response = await lampiao_agent.process(message, agent_context)
    
    assert not response.success
    assert response.response_type == "error"
    assert "error" in response.data
    assert "Analysis failed" in response.data["error"]


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
        metadata={"population": 45000000}
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
        confidence=0.9
    )
    
    assert insight.severity == "high"
    assert len(insight.affected_regions) == 3
    assert insight.confidence == 0.9
    assert len(insight.recommendations) == 1