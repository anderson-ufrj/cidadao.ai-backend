"""
Unit tests for Oscar Niemeyer agent.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.oscar_niemeyer import (
    OscarNiemeyerAgent,
    AggregationType,
    VisualizationType,
    TimeGranularity,
    DataAggregationResult,
    TimeSeriesData,
    VisualizationMetadata
)
from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse


@pytest.fixture
def oscar_agent():
    """Create Oscar Niemeyer agent instance."""
    return OscarNiemeyerAgent()


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
def sample_data():
    """Sample data for aggregation."""
    return [
        {"date": "2024-01-01", "region": "SP", "value": 1000, "category": "A"},
        {"date": "2024-01-01", "region": "RJ", "value": 800, "category": "B"},
        {"date": "2024-01-02", "region": "SP", "value": 1200, "category": "A"},
        {"date": "2024-01-02", "region": "RJ", "value": 900, "category": "B"},
        {"date": "2024-01-03", "region": "MG", "value": 600, "category": "C"},
    ]


@pytest.mark.asyncio
async def test_oscar_agent_initialization(oscar_agent):
    """Test agent initialization."""
    assert oscar_agent.name == "OscarNiemeyerAgent"
    assert "data_aggregation" in oscar_agent.capabilities
    assert "time_series_analysis" in oscar_agent.capabilities
    assert "visualization_metadata" in oscar_agent.capabilities
    
    await oscar_agent.initialize()
    assert oscar_agent.config["max_data_points"] == 10000


@pytest.mark.asyncio
async def test_multidimensional_aggregation(oscar_agent, agent_context):
    """Test multidimensional data aggregation."""
    message = AgentMessage(
        role="user",
        content="Aggregate data",
        type="aggregate_data",
        data={
            "dimensions": ["category", "region"],
            "metrics": ["total", "average"],
            "filters": {}
        }
    )
    
    response = await oscar_agent.process(message, agent_context)
    
    assert response.success
    assert response.response_type == "data_aggregation"
    assert "aggregation" in response.data
    assert "visualization" in response.data
    
    agg_data = response.data["aggregation"]
    assert agg_data["dimensions"] == ["category", "region"]
    assert agg_data["metrics"] == ["total", "average"]
    assert len(agg_data["data_points"]) > 0
    assert "summary" in agg_data


@pytest.mark.asyncio
async def test_time_series_generation(oscar_agent, agent_context):
    """Test time series data generation."""
    message = AgentMessage(
        role="user",
        content="Generate time series",
        type="time_series",
        data={
            "metric": "contract_value",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "granularity": "day"
        }
    )
    
    response = await oscar_agent.process(message, agent_context)
    
    assert response.success
    assert isinstance(response.data, TimeSeriesData)
    assert response.data.metric_name == "contract_value"
    assert response.data.granularity == TimeGranularity.DAY
    assert len(response.data.time_points) == len(response.data.values)
    assert all(isinstance(tp, datetime) for tp in response.data.time_points)


@pytest.mark.asyncio
async def test_spatial_aggregation(oscar_agent, agent_context):
    """Test spatial/geographic aggregation."""
    message = AgentMessage(
        role="user",
        content="Aggregate by region",
        type="spatial_aggregation",
        data={
            "data": [],
            "region_type": "state",
            "metrics": ["total_contracts", "average_value"]
        }
    )
    
    response = await oscar_agent.process(message, agent_context)
    
    assert response.success
    assert "aggregation_type" in response.data
    assert response.data["aggregation_type"] == "geographic"
    assert "regions" in response.data
    assert "visualization" in response.data
    
    viz_data = response.data["visualization"]
    assert viz_data["type"] == "choropleth_map"
    assert "geo_json_url" in viz_data


@pytest.mark.asyncio
async def test_visualization_metadata_generation(oscar_agent, agent_context):
    """Test visualization metadata generation."""
    message = AgentMessage(
        role="user",
        content="Generate viz metadata",
        type="visualization_metadata",
        data={
            "data_type": "contracts",
            "dimensions": ["month", "category"],
            "metrics": ["total_value", "count"]
        }
    )
    
    response = await oscar_agent.process(message, agent_context)
    
    assert response.success
    assert isinstance(response.data, VisualizationMetadata)
    assert response.data.title == "Contracts Analysis"
    assert response.data.visualization_type in VisualizationType
    assert len(response.data.series) == 2
    assert response.data.x_axis["field"] == "month"
    assert response.data.y_axis["field"] == "total_value"


@pytest.mark.asyncio
async def test_export_format_json(oscar_agent):
    """Test JSON export format."""
    data = [{"id": 1, "value": 100}, {"id": 2, "value": 200}]
    
    # Minified JSON
    result = await oscar_agent.create_export_format(data, "json")
    assert '{"id":1,"value":100}' in result
    
    # Pretty JSON
    result_pretty = await oscar_agent.create_export_format(
        data, "json", {"pretty": True}
    )
    assert "{\n" in result_pretty
    assert '"id": 1' in result_pretty


@pytest.mark.asyncio
async def test_export_format_csv(oscar_agent):
    """Test CSV export format."""
    data = [
        {"name": "Item A", "value": 100},
        {"name": "Item B", "value": 200}
    ]
    
    result = await oscar_agent.create_export_format(data, "csv")
    assert "name,value" in result
    assert "Item A,100" in result
    assert "Item B,200" in result
    
    # Custom delimiter
    result_custom = await oscar_agent.create_export_format(
        data, "csv", {"delimiter": ";"}
    )
    assert "name;value" in result_custom


@pytest.mark.asyncio
async def test_visualization_recommendation(oscar_agent):
    """Test visualization type recommendation."""
    # Time series
    viz = oscar_agent._recommend_visualization(["date"], ["value"])
    assert viz == VisualizationType.LINE_CHART
    
    # Single dimension comparison
    viz = oscar_agent._recommend_visualization(["category"], ["total"])
    assert viz == VisualizationType.BAR_CHART
    
    # Geographic data
    viz = oscar_agent._recommend_visualization(["state"], ["value"], "geo_distribution")
    assert viz == VisualizationType.MAP
    
    # Multiple dimensions
    viz = oscar_agent._recommend_visualization(["region", "category"], ["value"])
    assert viz == VisualizationType.HEATMAP
    
    # Single metric
    viz = oscar_agent._recommend_visualization([], ["score"])
    assert viz == VisualizationType.GAUGE


@pytest.mark.asyncio
async def test_error_handling(oscar_agent, agent_context):
    """Test error handling in data aggregation."""
    # Create message that will cause an error
    message = MagicMock()
    message.type = "invalid_type"
    message.data = None  # This will cause an error
    
    with patch.object(oscar_agent, '_perform_multidimensional_aggregation',
                      side_effect=Exception("Aggregation failed")):
        response = await oscar_agent.process(message, agent_context)
    
    assert not response.success
    assert response.response_type == "error"
    assert "error" in response.data
    assert "Aggregation failed" in response.data["error"]


@pytest.mark.asyncio
async def test_cache_metadata(oscar_agent, agent_context):
    """Test cache metadata generation."""
    message = AgentMessage(
        role="user",
        content="Aggregate with cache",
        data={"dimensions": ["type"], "metrics": ["sum"]}
    )
    
    response = await oscar_agent.process(message, agent_context)
    
    assert response.success
    metadata = response.data["metadata"]
    assert "cache_key" in metadata
    assert "expires_at" in metadata
    assert "generated_at" in metadata
    
    # Verify cache expiration
    expires_at = datetime.fromisoformat(metadata["expires_at"].replace("Z", "+00:00"))
    generated_at = datetime.fromisoformat(metadata["generated_at"].replace("Z", "+00:00"))
    diff = (expires_at - generated_at).total_seconds()
    assert diff == oscar_agent.config["cache_ttl_seconds"]


@pytest.mark.asyncio
async def test_time_series_metadata(oscar_agent):
    """Test time series metadata generation."""
    ts_data = await oscar_agent.generate_time_series(
        "revenue",
        "2024-01-01",
        "2024-01-31",
        TimeGranularity.DAY
    )
    
    assert ts_data.series_id.startswith("ts_revenue_day")
    assert ts_data.metric_name == "revenue"
    assert ts_data.aggregation_type == AggregationType.SUM
    
    metadata = ts_data.metadata
    assert "trend_direction" in metadata
    assert "seasonality_detected" in metadata
    assert "forecast_available" in metadata
    assert "anomalies_detected" in metadata


@pytest.mark.asyncio
async def test_regional_aggregation_brazil(oscar_agent):
    """Test Brazilian regional data aggregation."""
    result = await oscar_agent.aggregate_by_region(
        [],  # Empty data for demo
        "state",
        ["total_contracts", "average_value"]
    )
    
    assert result["region_type"] == "state"
    assert "SP" in result["regions"]
    assert "RJ" in result["regions"]
    
    sp_data = result["regions"]["SP"]
    assert sp_data["name"] == "São Paulo"
    assert sp_data["region"] == "Sudeste"
    assert "coordinates" in sp_data
    assert "metrics" in sp_data
    
    for metric in ["total_contracts", "average_value"]:
        assert metric in sp_data["metrics"]
        assert "value" in sp_data["metrics"][metric]
        assert "formatted" in sp_data["metrics"][metric]
        assert "percentage_of_total" in sp_data["metrics"][metric]