"""
Unit tests for Oscar Niemeyer agent.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json

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
from src.core import AgentStatus


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
        sender="test-user",
        recipient="OscarNiemeyerAgent",
        action="aggregate_data",
        payload={
            "dimensions": ["category", "region"],
            "metrics": ["total", "average"],
            "filters": {}
        }
    )

    response = await oscar_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    assert "aggregation" in response.result
    assert "visualization" in response.result

    agg_data = response.result["aggregation"]
    assert agg_data["dimensions"] == ["category", "region"]
    assert agg_data["metrics"] == ["total", "average"]
    assert len(agg_data["data_points"]) > 0
    assert "summary" in agg_data


@pytest.mark.asyncio
async def test_time_series_generation(oscar_agent, agent_context):
    """Test time series data generation."""
    message = AgentMessage(
        sender="test-user",
        recipient="OscarNiemeyerAgent",
        action="time_series",
        payload={
            "metric": "contract_value",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "granularity": "day"
        }
    )

    response = await oscar_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    assert isinstance(response.result, TimeSeriesData)
    assert response.result.metric_name == "contract_value"
    assert response.result.granularity == TimeGranularity.DAY
    assert len(response.result.time_points) == len(response.result.values)
    assert all(isinstance(tp, datetime) for tp in response.result.time_points)


@pytest.mark.asyncio
async def test_spatial_aggregation(oscar_agent, agent_context):
    """Test spatial/geographic aggregation."""
    message = AgentMessage(
        sender="test-user",
        recipient="OscarNiemeyerAgent",
        action="spatial_aggregation",
        payload={
            "data": [],
            "region_type": "state",
            "metrics": ["total_contracts", "average_value"]
        }
    )

    response = await oscar_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    assert "aggregation_type" in response.result
    assert response.result["aggregation_type"] == "geographic"
    assert "regions" in response.result
    assert "visualization" in response.result

    viz_data = response.result["visualization"]
    assert viz_data["type"] == "choropleth_map"
    assert "geo_json_url" in viz_data


@pytest.mark.asyncio
async def test_visualization_metadata_generation(oscar_agent, agent_context):
    """Test visualization metadata generation."""
    message = AgentMessage(
        sender="test-user",
        recipient="OscarNiemeyerAgent",
        action="visualization_metadata",
        payload={
            "data_type": "contracts",
            "dimensions": ["month", "category"],
            "metrics": ["total_value", "count"]
        }
    )

    response = await oscar_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    assert isinstance(response.result, VisualizationMetadata)
    assert response.result.title == "Contracts Analysis"
    assert response.result.visualization_type in VisualizationType
    assert len(response.result.series) == 2
    assert response.result.x_axis["field"] == "month"
    assert response.result.y_axis["field"] == "total_value"


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
    message = AgentMessage(
        sender="test-user",
        recipient="OscarNiemeyerAgent",
        action="invalid_action",
        payload=None
    )

    with patch.object(oscar_agent, '_perform_multidimensional_aggregation',
                      side_effect=Exception("Aggregation failed")):
        response = await oscar_agent.process(message, agent_context)

    assert response.status == AgentStatus.ERROR
    assert response.error is not None
    assert "Aggregation failed" in response.error


@pytest.mark.asyncio
async def test_cache_metadata(oscar_agent, agent_context):
    """Test cache metadata generation."""
    message = AgentMessage(
        sender="test-user",
        recipient="OscarNiemeyerAgent",
        action="aggregate_data",
        payload={"dimensions": ["type"], "metrics": ["sum"]}
    )

    response = await oscar_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    metadata = response.result["metadata"]
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


@pytest.mark.asyncio
async def test_fraud_network_creation(oscar_agent, agent_context):
    """Test fraud network graph creation with NetworkX + Plotly."""
    # Sample entities and relationships
    entities = [
        {"id": "E1", "name": "Supplier A", "type": "empresa", "score": 0.8},
        {"id": "E2", "name": "Supplier B", "type": "empresa", "score": 0.6},
        {"id": "E3", "name": "Agency X", "type": "orgao_publico", "score": 0.3},
        {"id": "E4", "name": "Shell Company", "type": "empresa", "score": 0.9},
    ]

    relationships = [
        {"source": "E1", "target": "E3", "type": "contracts_with", "strength": 0.9},
        {"source": "E2", "target": "E3", "type": "contracts_with", "strength": 0.85},
        {"source": "E1", "target": "E4", "type": "shared_ownership", "strength": 0.75},
    ]

    message = AgentMessage(
        sender="test-user",
        recipient="OscarNiemeyerAgent",
        action="network_graph",
        payload={
            "entities": entities,
            "relationships": relationships,
            "threshold": 0.7
        }
    )

    response = await oscar_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    assert response.result["type"] == "network_graph"
    assert "visualization" in response.result
    assert "metadata" in response.result

    # Verify metadata
    metadata = response.result["metadata"]
    assert "nodes" in metadata
    assert "edges" in metadata
    assert metadata["threshold_applied"] == 0.7
    assert "avg_suspicion_score" in metadata
    assert "max_suspicion_score" in metadata

    # Verify visualization is valid Plotly JSON
    viz_json = response.result["visualization"]
    assert isinstance(viz_json, str)
    viz_data = json.loads(viz_json)
    assert "data" in viz_data
    assert "layout" in viz_data


@pytest.mark.asyncio
async def test_choropleth_map_creation(oscar_agent, agent_context):
    """Test choropleth map creation for Brazilian states."""
    # Sample state data
    data = [
        {"state_code": "SP", "value": 85000, "name": "São Paulo"},
        {"state_code": "RJ", "value": 62000, "name": "Rio de Janeiro"},
        {"state_code": "MG", "value": 51000, "name": "Minas Gerais"},
        {"state_code": "BA", "value": 38000, "name": "Bahia"},
    ]

    message = AgentMessage(
        sender="test-user",
        recipient="OscarNiemeyerAgent",
        action="choropleth_map",
        payload={
            "data": data,
            "color_column": "value",
            "location_column": "state_code"
        }
    )

    # Mock httpx to avoid actual HTTP calls
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "type": "FeatureCollection",
            "features": []
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        response = await oscar_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    assert response.result["type"] == "choropleth"
    assert "visualization" in response.result
    assert "metadata" in response.result

    # Verify metadata
    metadata = response.result["metadata"]
    assert metadata["data_points"] == 4
    assert metadata["color_column"] == "value"
    assert metadata["location_column"] == "state_code"
    assert "statistics" in metadata

    # Verify statistics
    stats = metadata["statistics"]
    assert "min" in stats
    assert "max" in stats
    assert "mean" in stats
    assert stats["min"] == 38000
    assert stats["max"] == 85000


@pytest.mark.asyncio
async def test_network_api_integration(oscar_agent, agent_context):
    """Test integration with Network Graph API."""
    entity_id = "test-entity-123"

    message = AgentMessage(
        sender="test-user",
        recipient="OscarNiemeyerAgent",
        action="fetch_network_data",
        payload={
            "entity_id": entity_id,
            "depth": 2
        }
    )

    # Mock httpx to simulate Network Graph API response
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "nodes": [
                {"id": "E1", "name": "Entity 1", "entity_type": "empresa", "risk_score": 0.7},
                {"id": "E2", "name": "Entity 2", "entity_type": "orgao_publico", "risk_score": 0.3}
            ],
            "edges": [
                {"source_entity_id": "E1", "target_entity_id": "E2", "relationship_type": "contracts_with", "strength": 0.9}
            ],
            "node_count": 2,
            "edge_count": 1
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        response = await oscar_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    assert "entities" in response.result
    assert "relationships" in response.result
    assert "metadata" in response.result

    # Verify entities
    entities = response.result["entities"]
    assert len(entities) == 2
    assert entities[0]["id"] == "E1"
    assert entities[0]["name"] == "Entity 1"
    assert entities[0]["type"] == "empresa"
    assert entities[0]["score"] == 0.7

    # Verify relationships
    relationships = response.result["relationships"]
    assert len(relationships) == 1
    assert relationships[0]["source"] == "E1"
    assert relationships[0]["target"] == "E2"
    assert relationships[0]["type"] == "contracts_with"
    assert relationships[0]["strength"] == 0.9

    # Verify metadata
    metadata = response.result["metadata"]
    assert metadata["center_entity_id"] == entity_id
    assert metadata["depth"] == 2
    assert metadata["node_count"] == 2
    assert metadata["edge_count"] == 1


@pytest.mark.asyncio
async def test_network_graph_edge_case_empty_data(oscar_agent, agent_context):
    """Test network graph with empty data."""
    message = AgentMessage(
        sender="test-user",
        recipient="OscarNiemeyerAgent",
        action="network_graph",
        payload={
            "entities": [],
            "relationships": [],
            "threshold": 0.5
        }
    )

    response = await oscar_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    assert response.result["type"] == "network_graph"
    metadata = response.result["metadata"]
    assert metadata["nodes"] == 0
    assert metadata["edges"] == 0


@pytest.mark.asyncio
async def test_choropleth_geojson_fallback(oscar_agent, agent_context):
    """Test choropleth map with GeoJSON loading failure."""
    data = [{"state_code": "SP", "value": 1000}]

    message = AgentMessage(
        sender="test-user",
        recipient="OscarNiemeyerAgent",
        action="choropleth_map",
        payload={
            "data": data,
            "geojson_url": "https://invalid-url.com/geojson",
            "color_column": "value"
        }
    )

    # Mock httpx to simulate failure
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = Exception("Network error")
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        response = await oscar_agent.process(message, agent_context)

    assert response.status == AgentStatus.COMPLETED
    assert response.result["type"] == "choropleth"
    assert "error" in response.result