"""
API routes for data visualization endpoints.
Provides aggregated and formatted data optimized for frontend consumption.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.oscar_niemeyer import (
    OscarNiemeyerAgent,
    AggregationType,
    VisualizationType,
    TimeGranularity,
)
from src.agents.lampiao import LampiaoAgent, RegionType
from src.api.middleware.authentication import get_current_user
from src.db.session import get_session as get_db
from src.services.cache_service import CacheService
from src.infrastructure.rate_limiter import RateLimiter, rate_limit
from src.core import get_logger
from src.services.agent_lazy_loader import AgentLazyLoader
from src.agents.deodoro import AgentContext


logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/visualization", tags=["visualization"])

# Rate limiter for visualization endpoints
viz_rate_limiter = RateLimiter(calls=30, period=60)  # 30 calls per minute

# Lazy load agents
agent_loader = AgentLazyLoader()


class DatasetType(str, Enum):
    """Types of datasets available for visualization."""
    CONTRACTS = "contracts"
    SPENDING = "spending"
    TRANSFERS = "transfers"
    BIDDINGS = "biddings"
    AUDIT = "audit"
    REGIONAL = "regional"


class ChartDataRequest(BaseModel):
    """Request model for chart data."""
    
    dataset_type: DatasetType
    chart_type: Optional[VisualizationType] = None
    time_range: Optional[str] = Field(default="30d", description="Time range: 7d, 30d, 90d, 1y, all")
    granularity: Optional[TimeGranularity] = TimeGranularity.DAY
    dimensions: List[str] = Field(default_factory=list, description="Dimensions for grouping")
    metrics: List[str] = Field(default_factory=list, description="Metrics to calculate")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Additional filters")
    limit: int = Field(default=100, le=1000, description="Maximum number of data points")


class RegionalDataRequest(BaseModel):
    """Request model for regional data visualization."""
    
    metric: str = Field(..., description="Metric to analyze")
    region_type: RegionType = RegionType.STATE
    aggregation: AggregationType = AggregationType.SUM
    normalize: bool = Field(default=False, description="Normalize by population/area")
    include_metadata: bool = Field(default=True, description="Include regional metadata")
    filters: Dict[str, Any] = Field(default_factory=dict)


class TimeSeriesRequest(BaseModel):
    """Request model for time series data."""
    
    metric: str = Field(..., description="Metric to analyze over time")
    entity_id: Optional[str] = Field(None, description="Specific entity to track")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    granularity: TimeGranularity = TimeGranularity.DAY
    aggregation: AggregationType = AggregationType.SUM
    include_forecast: bool = Field(default=False, description="Include forecast data")
    comparison_period: Optional[str] = Field(None, description="Compare with previous period")


class VisualizationResponse(BaseModel):
    """Standard response for visualization data."""
    
    visualization_id: str
    title: str
    subtitle: Optional[str]
    chart_type: VisualizationType
    data: Union[List[Dict[str, Any]], Dict[str, Any]]
    metadata: Dict[str, Any]
    cache_timestamp: datetime
    expires_at: datetime


@router.post("/chart-data", response_model=VisualizationResponse)
@rate_limit(viz_rate_limiter)
async def get_chart_data(
    request: ChartDataRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get aggregated data optimized for chart visualization.
    
    This endpoint uses the Oscar Niemeyer agent to process and aggregate data
    in formats optimized for various chart types.
    """
    try:
        logger.info(
            "Processing chart data request",
            user_id=current_user["id"],
            dataset_type=request.dataset_type.value,
            chart_type=request.chart_type.value if request.chart_type else "auto",
        )
        
        # Get Oscar Niemeyer agent
        oscar_agent = await agent_loader.get_agent("oscar_niemeyer")
        if not oscar_agent:
            oscar_agent = OscarNiemeyerAgent()
            await oscar_agent.initialize()
        
        # Create agent context
        context = AgentContext(
            investigation_id=f"viz_{datetime.utcnow().timestamp()}",
            user_id=current_user["id"],
            session_id=current_user.get("session_id", "default"),
            metadata={
                "request_type": "chart_data",
                "dataset": request.dataset_type.value
            }
        )
        
        # Prepare message for Oscar agent
        from src.agents.deodoro import AgentMessage
        message = AgentMessage(
            role="user",
            content=f"Generate chart data for {request.dataset_type.value}",
            type="visualization_metadata",
            data={
                "data_type": request.dataset_type.value,
                "dimensions": request.dimensions,
                "metrics": request.metrics,
                "filters": request.filters,
                "limit": request.limit,
                "time_range": request.time_range,
                "granularity": request.granularity.value if request.granularity else None,
            }
        )
        
        # Process with Oscar agent
        response = await oscar_agent.process(message, context)
        
        if not response.success:
            raise HTTPException(status_code=500, detail="Failed to generate visualization data")
        
        # Prepare visualization response
        viz_metadata = response.data
        cache_ttl = 3600  # 1 hour cache
        
        return VisualizationResponse(
            visualization_id=viz_metadata.visualization_id,
            title=viz_metadata.title,
            subtitle=viz_metadata.subtitle,
            chart_type=viz_metadata.visualization_type,
            data={
                "series": viz_metadata.series,
                "x_axis": viz_metadata.x_axis,
                "y_axis": viz_metadata.y_axis,
                "data_url": viz_metadata.data_url,
            },
            metadata={
                "filters": viz_metadata.filters,
                "options": viz_metadata.options,
                "dataset_type": request.dataset_type.value,
                "record_count": request.limit,
            },
            cache_timestamp=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=cache_ttl),
        )
        
    except Exception as e:
        logger.error(
            "Chart data generation failed",
            error=str(e),
            user_id=current_user["id"],
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Chart data generation failed: {str(e)}")


@router.post("/regional-map", response_model=VisualizationResponse)
@rate_limit(viz_rate_limiter)
async def get_regional_map_data(
    request: RegionalDataRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get regional data formatted for map visualization.
    
    Uses the Lampião agent to analyze regional disparities and format data
    for choropleth maps and other geographic visualizations.
    """
    try:
        logger.info(
            "Processing regional map data request",
            user_id=current_user["id"],
            metric=request.metric,
            region_type=request.region_type.value,
        )
        
        # Get Lampião agent
        lampiao_agent = await agent_loader.get_agent("lampiao")
        if not lampiao_agent:
            lampiao_agent = LampiaoAgent()
            await lampiao_agent.initialize()
        
        # Create agent context
        context = AgentContext(
            investigation_id=f"regional_{datetime.utcnow().timestamp()}",
            user_id=current_user["id"],
            session_id=current_user.get("session_id", "default"),
            metadata={
                "request_type": "regional_map",
                "metric": request.metric
            }
        )
        
        # Get Oscar agent for aggregation
        oscar_agent = await agent_loader.get_agent("oscar_niemeyer")
        if not oscar_agent:
            oscar_agent = OscarNiemeyerAgent()
            await oscar_agent.initialize()
        
        # First, get regional analysis from Lampião
        from src.agents.deodoro import AgentMessage
        lampiao_message = AgentMessage(
            role="user",
            content=f"Analyze regional distribution of {request.metric}",
            data={
                "metric": request.metric,
                "region_type": request.region_type.value,
                "filters": request.filters,
            }
        )
        
        lampiao_response = await lampiao_agent.process(lampiao_message, context)
        
        if not lampiao_response.success:
            raise HTTPException(status_code=500, detail="Regional analysis failed")
        
        # Then aggregate for visualization with Oscar
        regional_data = lampiao_response.data
        oscar_message = AgentMessage(
            role="user",
            content="Aggregate regional data for map visualization",
            type="spatial_aggregation",
            data={
                "data": [
                    {
                        "region": m.region_id,
                        "name": m.region_name,
                        "value": m.value,
                        "normalized_value": m.normalized_value,
                        "rank": m.rank,
                        "percentile": m.percentile,
                        **m.metadata
                    }
                    for m in regional_data.metrics
                ],
                "region_type": request.region_type.value,
                "metrics": [request.metric],
            }
        )
        
        oscar_response = await oscar_agent.process(oscar_message, context)
        
        if not oscar_response.success:
            raise HTTPException(status_code=500, detail="Data aggregation failed")
        
        # Format response
        aggregated_data = oscar_response.data
        
        return VisualizationResponse(
            visualization_id=f"map_{context.investigation_id}",
            title=f"{request.metric.replace('_', ' ').title()} por {request.region_type.value}",
            subtitle=f"Análise de disparidades regionais - {len(regional_data.metrics)} regiões",
            chart_type=VisualizationType.MAP,
            data=aggregated_data["regions"],
            metadata={
                "statistics": regional_data.statistics,
                "inequalities": regional_data.inequalities,
                "clusters": regional_data.clusters,
                "visualization": aggregated_data["visualization"],
                "region_type": request.region_type.value,
                "metric": request.metric,
                "normalized": request.normalize,
            },
            cache_timestamp=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=4),
        )
        
    except Exception as e:
        logger.error(
            "Regional map data generation failed",
            error=str(e),
            user_id=current_user["id"],
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Regional map data failed: {str(e)}")


@router.post("/time-series", response_model=VisualizationResponse)
@rate_limit(viz_rate_limiter)
async def get_time_series_data(
    request: TimeSeriesRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get time series data optimized for line charts and trend analysis.
    
    Supports multiple granularities and can include forecast data
    when the include_forecast flag is set.
    """
    try:
        logger.info(
            "Processing time series request",
            user_id=current_user["id"],
            metric=request.metric,
            granularity=request.granularity.value,
        )
        
        # Get Oscar Niemeyer agent
        oscar_agent = await agent_loader.get_agent("oscar_niemeyer")
        if not oscar_agent:
            oscar_agent = OscarNiemeyerAgent()
            await oscar_agent.initialize()
        
        # Create agent context
        context = AgentContext(
            investigation_id=f"ts_{datetime.utcnow().timestamp()}",
            user_id=current_user["id"],
            session_id=current_user.get("session_id", "default"),
            metadata={
                "request_type": "time_series",
                "metric": request.metric
            }
        )
        
        # Generate time series data
        time_series_data = await oscar_agent.generate_time_series(
            request.metric,
            request.start_date.isoformat() if request.start_date else None,
            request.end_date.isoformat() if request.end_date else None,
            request.granularity,
            context
        )
        
        # Format data for visualization
        chart_data = []
        for i, (time_point, value) in enumerate(zip(time_series_data.time_points, time_series_data.values)):
            chart_data.append({
                "timestamp": time_point.isoformat(),
                "value": value,
                "metric": request.metric,
                "index": i
            })
        
        # Add forecast data if requested
        forecast_data = []
        if request.include_forecast:
            # TODO: Integrate with Ceuci predictive agent for actual forecasting
            last_value = time_series_data.values[-1] if time_series_data.values else 0
            last_time = time_series_data.time_points[-1] if time_series_data.time_points else datetime.utcnow()
            
            for i in range(7):  # 7 periods forecast
                if request.granularity == TimeGranularity.DAY:
                    next_time = last_time + timedelta(days=i+1)
                else:
                    next_time = last_time + timedelta(days=(i+1)*30)
                
                forecast_data.append({
                    "timestamp": next_time.isoformat(),
                    "value": last_value * (1 + 0.02 * (i+1)),  # Simple 2% growth
                    "is_forecast": True,
                    "confidence_lower": last_value * (1 + 0.01 * (i+1)),
                    "confidence_upper": last_value * (1 + 0.03 * (i+1)),
                })
        
        return VisualizationResponse(
            visualization_id=time_series_data.series_id,
            title=f"{request.metric.replace('_', ' ').title()} - Série Temporal",
            subtitle=f"Granularidade: {request.granularity.value}",
            chart_type=VisualizationType.LINE_CHART,
            data={
                "historical": chart_data,
                "forecast": forecast_data if request.include_forecast else [],
                "metadata": time_series_data.metadata,
            },
            metadata={
                "metric": request.metric,
                "granularity": request.granularity.value,
                "aggregation_type": time_series_data.aggregation_type.value,
                "start_date": time_series_data.time_points[0].isoformat() if time_series_data.time_points else None,
                "end_date": time_series_data.time_points[-1].isoformat() if time_series_data.time_points else None,
                "data_points": len(chart_data),
                "has_forecast": request.include_forecast,
            },
            cache_timestamp=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        
    except Exception as e:
        logger.error(
            "Time series generation failed",
            error=str(e),
            user_id=current_user["id"],
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Time series generation failed: {str(e)}")


@router.get("/dashboard-summary")
@rate_limit(viz_rate_limiter)
async def get_dashboard_summary(
    time_range: str = Query("30d", description="Time range for summary"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a summary of key metrics formatted for dashboard display.
    
    Returns multiple visualization-ready datasets for a complete dashboard view.
    """
    try:
        logger.info(
            "Generating dashboard summary",
            user_id=current_user["id"],
            time_range=time_range,
        )
        
        # This would aggregate data from multiple sources
        # For now, returning a structured summary
        
        return {
            "summary_id": f"dashboard_{datetime.utcnow().timestamp()}",
            "time_range": time_range,
            "key_metrics": [
                {
                    "metric": "total_contracts",
                    "value": 15420,
                    "change": 12.5,
                    "change_type": "increase",
                    "visualization_type": "gauge",
                },
                {
                    "metric": "total_value",
                    "value": 2547890000,
                    "formatted_value": "R$ 2.55B",
                    "change": -3.2,
                    "change_type": "decrease",
                    "visualization_type": "gauge",
                },
                {
                    "metric": "anomalies_detected",
                    "value": 47,
                    "severity_high": 12,
                    "severity_medium": 20,
                    "severity_low": 15,
                    "visualization_type": "gauge",
                },
                {
                    "metric": "investigations_active",
                    "value": 8,
                    "completed_this_period": 23,
                    "visualization_type": "gauge",
                },
            ],
            "charts": [
                {
                    "id": "spending_trend",
                    "title": "Gastos ao Longo do Tempo",
                    "type": "line_chart",
                    "endpoint": "/api/v1/visualization/time-series",
                    "params": {"metric": "spending", "granularity": "day"},
                },
                {
                    "id": "regional_distribution",
                    "title": "Distribuição Regional de Contratos",
                    "type": "map",
                    "endpoint": "/api/v1/visualization/regional-map",
                    "params": {"metric": "contract_value", "region_type": "state"},
                },
                {
                    "id": "top_categories",
                    "title": "Principais Categorias de Gastos",
                    "type": "bar_chart",
                    "endpoint": "/api/v1/visualization/chart-data",
                    "params": {"dataset_type": "spending", "dimensions": ["category"]},
                },
            ],
            "alerts": [
                {
                    "id": "alert_001",
                    "type": "anomaly",
                    "severity": "high",
                    "message": "Padrão incomum detectado em contratos de TI",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            ],
            "cache_timestamp": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=15),
        }
        
    except Exception as e:
        logger.error(
            "Dashboard summary generation failed",
            error=str(e),
            user_id=current_user["id"],
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Dashboard summary failed: {str(e)}")


@router.get("/supported-charts")
async def get_supported_chart_types():
    """
    Get list of supported chart types and their configurations.
    
    This helps the frontend know what visualizations are available.
    """
    return {
        "chart_types": [
            {
                "type": "line_chart",
                "name": "Gráfico de Linhas",
                "description": "Ideal para séries temporais e tendências",
                "supports": ["time_series", "comparisons", "trends"],
                "required_dimensions": 1,
                "max_series": 10,
            },
            {
                "type": "bar_chart",
                "name": "Gráfico de Barras",
                "description": "Comparação entre categorias",
                "supports": ["categories", "rankings", "distributions"],
                "required_dimensions": 1,
                "max_series": 5,
            },
            {
                "type": "pie_chart",
                "name": "Gráfico de Pizza",
                "description": "Proporções e percentuais",
                "supports": ["proportions", "composition"],
                "required_dimensions": 1,
                "max_series": 1,
                "max_slices": 8,
            },
            {
                "type": "scatter_plot",
                "name": "Gráfico de Dispersão",
                "description": "Correlações entre variáveis",
                "supports": ["correlations", "outliers"],
                "required_dimensions": 2,
                "max_points": 1000,
            },
            {
                "type": "heatmap",
                "name": "Mapa de Calor",
                "description": "Densidade e intensidade em duas dimensões",
                "supports": ["density", "matrix", "correlations"],
                "required_dimensions": 2,
            },
            {
                "type": "map",
                "name": "Mapa Coroplético",
                "description": "Dados geográficos por região",
                "supports": ["geographic", "regional"],
                "required_dimensions": 0,
                "regions": ["state", "municipality", "macro_region"],
            },
            {
                "type": "gauge",
                "name": "Medidor",
                "description": "Valor único com indicador de meta",
                "supports": ["kpi", "single_value"],
                "required_dimensions": 0,
                "max_series": 1,
            },
            {
                "type": "table",
                "name": "Tabela",
                "description": "Dados tabulares detalhados",
                "supports": ["detailed_data", "multi_dimension"],
                "max_rows": 1000,
            },
        ],
        "aggregation_types": [a.value for a in AggregationType],
        "time_granularities": [g.value for g in TimeGranularity],
        "region_types": [r.value for r in RegionType],
    }