"""
Module: api.routes.analysis
Description: Analysis endpoints for pattern detection and correlation analysis
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, validator
from pydantic import Field as PydanticField

from src.agents import AgentContext, AnalystAgent
from src.api.middleware.authentication import get_current_user
from src.core import get_logger
from src.tools import TransparencyAPIFilter

logger = get_logger(__name__)

router = APIRouter()


class AnalysisRequest(BaseModel):
    """Request model for pattern analysis."""

    analysis_type: str = PydanticField(description="Type of analysis to perform")
    data_source: str = PydanticField(
        default="contracts", description="Data source to analyze"
    )
    time_range: dict[str, str] = PydanticField(description="Time range for analysis")
    filters: dict[str, Any] = PydanticField(
        default_factory=dict, description="Additional filters"
    )
    include_correlations: bool = PydanticField(
        default=True, description="Include correlation analysis"
    )
    include_trends: bool = PydanticField(
        default=True, description="Include trend analysis"
    )
    include_predictions: bool = PydanticField(
        default=False, description="Include predictive analysis"
    )

    @validator("analysis_type")
    def validate_analysis_type(cls, v):
        """Validate analysis type."""
        allowed_types = [
            "spending_trends",
            "vendor_patterns",
            "organizational_behavior",
            "seasonal_analysis",
            "efficiency_metrics",
            "correlation_analysis",
        ]
        if v not in allowed_types:
            raise ValueError(f"Analysis type must be one of: {allowed_types}")
        return v

    @validator("data_source")
    def validate_data_source(cls, v):
        """Validate data source."""
        allowed_sources = [
            "contracts",
            "expenses",
            "agreements",
            "biddings",
            "servants",
        ]
        if v not in allowed_sources:
            raise ValueError(f"Data source must be one of: {allowed_sources}")
        return v


class AnalysisResponse(BaseModel):
    """Response model for analysis results."""

    analysis_id: str
    analysis_type: str
    data_source: str
    time_range: dict[str, str]
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    results: dict[str, Any]
    insights: list[str]
    recommendations: list[str]
    confidence_score: float
    processing_time: float


class TrendAnalysis(BaseModel):
    """Trend analysis result."""

    metric: str
    direction: str  # increasing, decreasing, stable
    rate_of_change: float
    confidence: float
    time_series: list[dict[str, Any]]
    significant_events: list[dict[str, Any]]


class CorrelationResult(BaseModel):
    """Correlation analysis result."""

    variable_x: str
    variable_y: str
    correlation_coefficient: float
    significance: float
    relationship_type: str  # linear, non-linear, none
    explanation: str


class PatternResult(BaseModel):
    """Pattern detection result."""

    pattern_type: str
    description: str
    frequency: int
    confidence: float
    examples: list[dict[str, Any]]
    implications: list[str]


# In-memory storage for analysis tracking
_active_analyses: dict[str, dict[str, Any]] = {}


@router.post("/start", response_model=dict[str, str])
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Start a new pattern analysis.

    Creates and queues an analysis task that will identify patterns,
    trends, and correlations in government data.
    """
    analysis_id = str(uuid4())

    # Store analysis metadata
    _active_analyses[analysis_id] = {
        "id": analysis_id,
        "status": "started",
        "analysis_type": request.analysis_type,
        "data_source": request.data_source,
        "time_range": request.time_range,
        "filters": request.filters,
        "user_id": current_user.get("user_id"),
        "started_at": datetime.utcnow(),
        "progress": 0.0,
        "current_phase": "initializing",
        "results": {},
        "insights": [],
        "recommendations": [],
    }

    # Start analysis in background
    background_tasks.add_task(_run_analysis, analysis_id, request)

    logger.info(
        "analysis_started",
        analysis_id=analysis_id,
        analysis_type=request.analysis_type,
        data_source=request.data_source,
        user_id=current_user.get("user_id"),
    )

    return {
        "analysis_id": analysis_id,
        "status": "started",
        "message": "Analysis queued for processing",
    }


@router.get("/trends", response_model=list[TrendAnalysis])
async def get_spending_trends(
    data_source: str = Query("contracts", description="Data source"),
    time_period: str = Query(
        "6months", description="Time period (3months, 6months, 1year, 2years)"
    ),
    organization: Optional[str] = Query(None, description="Organization code"),
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Get spending trends analysis.

    Returns trend analysis for specified data source and time period.
    """
    # Calculate time range based on period
    end_date = datetime.utcnow()
    period_map = {
        "3months": timedelta(days=90),
        "6months": timedelta(days=180),
        "1year": timedelta(days=365),
        "2years": timedelta(days=730),
    }

    if time_period not in period_map:
        raise HTTPException(status_code=400, detail="Invalid time period")

    start_date = end_date - period_map[time_period]

    try:
        # Create agent context
        context = AgentContext(
            conversation_id=str(uuid4()),
            user_id=current_user.get("user_id"),
            session_data={"analysis_type": "trends"},
        )

        # Initialize AnalystAgent
        analyst = AnalystAgent()

        # Prepare filters
        filters = TransparencyAPIFilter()
        if organization:
            filters.codigo_orgao = organization

        # Get trend analysis
        results = await analyst.analyze_spending_trends(
            data_source=data_source,
            start_date=start_date,
            end_date=end_date,
            filters=filters,
            context=context,
        )

        return [
            TrendAnalysis(
                metric=result["metric"],
                direction=result["direction"],
                rate_of_change=result["rate_of_change"],
                confidence=result["confidence"],
                time_series=result["time_series"],
                significant_events=result.get("significant_events", []),
            )
            for result in results
        ]

    except Exception as e:
        logger.error(
            "trends_analysis_failed",
            error=str(e),
            data_source=data_source,
            time_period=time_period,
        )

        raise HTTPException(status_code=500, detail=f"Trends analysis failed: {str(e)}")


@router.get("/correlations", response_model=list[CorrelationResult])
async def get_correlations(
    data_source: str = Query("contracts", description="Data source"),
    variables: list[str] = Query(description="Variables to correlate"),
    time_range: Optional[str] = Query("6months", description="Time range"),
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Get correlation analysis between variables.

    Returns correlation coefficients and significance tests.
    """
    if len(variables) < 2:
        raise HTTPException(
            status_code=400, detail="At least 2 variables required for correlation"
        )

    try:
        # Create agent context
        context = AgentContext(
            conversation_id=str(uuid4()),
            user_id=current_user.get("user_id"),
            session_data={"analysis_type": "correlations"},
        )

        # Initialize AnalystAgent
        analyst = AnalystAgent()

        # Get correlation analysis
        results = await analyst.analyze_correlations(
            data_source=data_source,
            variables=variables,
            time_range=time_range,
            context=context,
        )

        return [
            CorrelationResult(
                variable_x=result["variable_x"],
                variable_y=result["variable_y"],
                correlation_coefficient=result["correlation_coefficient"],
                significance=result["significance"],
                relationship_type=result["relationship_type"],
                explanation=result["explanation"],
            )
            for result in results
        ]

    except Exception as e:
        logger.error(
            "correlation_analysis_failed",
            error=str(e),
            data_source=data_source,
            variables=variables,
        )

        raise HTTPException(
            status_code=500, detail=f"Correlation analysis failed: {str(e)}"
        )


@router.get("/patterns", response_model=list[PatternResult])
async def detect_patterns(
    data_source: str = Query("contracts", description="Data source"),
    pattern_type: str = Query("all", description="Pattern type to detect"),
    organization: Optional[str] = Query(None, description="Organization code"),
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Detect patterns in government data.

    Returns detected patterns with confidence scores and examples.
    """
    allowed_patterns = [
        "all",
        "vendor",
        "temporal",
        "value",
        "geographic",
        "organizational",
    ]
    if pattern_type not in allowed_patterns:
        raise HTTPException(
            status_code=400, detail=f"Pattern type must be one of: {allowed_patterns}"
        )

    try:
        # Create agent context
        context = AgentContext(
            conversation_id=str(uuid4()),
            user_id=current_user.get("user_id"),
            session_data={"analysis_type": "patterns"},
        )

        # Initialize AnalystAgent
        analyst = AnalystAgent()

        # Prepare filters
        filters = TransparencyAPIFilter()
        if organization:
            filters.codigo_orgao = organization

        # Get pattern analysis
        results = await analyst.detect_patterns(
            data_source=data_source,
            pattern_type=pattern_type,
            filters=filters,
            context=context,
        )

        return [
            PatternResult(
                pattern_type=result["pattern_type"],
                description=result["description"],
                frequency=result["frequency"],
                confidence=result["confidence"],
                examples=result["examples"],
                implications=result.get("implications", []),
            )
            for result in results
        ]

    except Exception as e:
        logger.error(
            "pattern_detection_failed",
            error=str(e),
            data_source=data_source,
            pattern_type=pattern_type,
        )

        raise HTTPException(
            status_code=500, detail=f"Pattern detection failed: {str(e)}"
        )


@router.get("/{analysis_id}/status")
async def get_analysis_status(
    analysis_id: str, current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Get the current status of an analysis.

    Returns progress information and current phase.
    """
    if analysis_id not in _active_analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = _active_analyses[analysis_id]

    # Check user authorization
    if analysis["user_id"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "analysis_id": analysis_id,
        "status": analysis["status"],
        "progress": analysis["progress"],
        "current_phase": analysis["current_phase"],
        "analysis_type": analysis["analysis_type"],
        "started_at": analysis["started_at"],
        "estimated_completion": analysis.get("estimated_completion"),
    }


@router.get("/{analysis_id}/results", response_model=AnalysisResponse)
async def get_analysis_results(
    analysis_id: str, current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Get complete analysis results.

    Returns all patterns, trends, and correlations found.
    """
    if analysis_id not in _active_analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = _active_analyses[analysis_id]

    # Check user authorization
    if analysis["user_id"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    if analysis["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=409, detail="Analysis not yet completed")

    processing_time = 0.0
    if analysis.get("completed_at") and analysis.get("started_at"):
        processing_time = (
            analysis["completed_at"] - analysis["started_at"]
        ).total_seconds()

    return AnalysisResponse(
        analysis_id=analysis_id,
        analysis_type=analysis["analysis_type"],
        data_source=analysis["data_source"],
        time_range=analysis["time_range"],
        started_at=analysis["started_at"],
        completed_at=analysis.get("completed_at"),
        status=analysis["status"],
        results=analysis["results"],
        insights=analysis["insights"],
        recommendations=analysis["recommendations"],
        confidence_score=analysis.get("confidence_score", 0.0),
        processing_time=processing_time,
    )


@router.get("/", response_model=list[dict[str, Any]])
async def list_analyses(
    analysis_type: Optional[str] = Query(None, description="Filter by analysis type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100, description="Number of analyses to return"),
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    List user's analyses.

    Returns a list of analyses owned by the current user.
    """
    user_id = current_user.get("user_id")

    # Filter analyses by user
    user_analyses = [
        analysis
        for analysis in _active_analyses.values()
        if analysis["user_id"] == user_id
    ]

    # Filter by analysis type if provided
    if analysis_type:
        user_analyses = [
            analysis
            for analysis in user_analyses
            if analysis["analysis_type"] == analysis_type
        ]

    # Filter by status if provided
    if status:
        user_analyses = [
            analysis for analysis in user_analyses if analysis["status"] == status
        ]

    # Sort by start time (newest first)
    user_analyses.sort(key=lambda x: x["started_at"], reverse=True)

    # Apply limit
    user_analyses = user_analyses[:limit]

    return [
        {
            "analysis_id": analysis["id"],
            "analysis_type": analysis["analysis_type"],
            "data_source": analysis["data_source"],
            "status": analysis["status"],
            "progress": analysis["progress"],
            "started_at": analysis["started_at"],
            "completed_at": analysis.get("completed_at"),
        }
        for analysis in user_analyses
    ]


async def _run_analysis(analysis_id: str, request: AnalysisRequest):
    """
    Execute the analysis in the background.

    This function runs the actual pattern analysis using AnalystAgent.
    """
    analysis = _active_analyses[analysis_id]

    try:
        # Update status
        analysis["status"] = "running"
        analysis["current_phase"] = "data_collection"
        analysis["progress"] = 0.1

        # Create agent context
        context = AgentContext(
            conversation_id=analysis_id,
            user_id=analysis["user_id"],
            session_data={"analysis_type": request.analysis_type},
        )

        # Initialize AnalystAgent
        analyst = AnalystAgent()

        # Prepare filters for data retrieval
        filters = TransparencyAPIFilter(**request.filters)

        analysis["current_phase"] = "pattern_analysis"
        analysis["progress"] = 0.3

        # Execute analysis based on type
        if request.analysis_type == "spending_trends":
            results = await analyst.analyze_spending_trends(
                data_source=request.data_source, filters=filters, context=context
            )
        elif request.analysis_type == "vendor_patterns":
            results = await analyst.analyze_vendor_patterns(
                data_source=request.data_source, filters=filters, context=context
            )
        elif request.analysis_type == "organizational_behavior":
            results = await analyst.analyze_organizational_behavior(
                data_source=request.data_source, filters=filters, context=context
            )
        else:
            results = await analyst.perform_comprehensive_analysis(
                analysis_type=request.analysis_type,
                data_source=request.data_source,
                filters=filters,
                context=context,
            )

        analysis["current_phase"] = "correlation_analysis"
        analysis["progress"] = 0.6

        # Add correlation analysis if requested
        if request.include_correlations:
            correlations = await analyst.analyze_correlations(
                data_source=request.data_source,
                variables=["valor", "prazo", "fornecedor"],
                context=context,
            )
            results["correlations"] = correlations

        analysis["current_phase"] = "insights_generation"
        analysis["progress"] = 0.8

        # Generate insights and recommendations
        insights = await analyst.generate_insights(results, context)
        recommendations = await analyst.generate_recommendations(results, context)

        analysis["results"] = results
        analysis["insights"] = insights
        analysis["recommendations"] = recommendations
        analysis["confidence_score"] = results.get("confidence", 0.0)

        # Mark as completed
        analysis["status"] = "completed"
        analysis["completed_at"] = datetime.utcnow()
        analysis["progress"] = 1.0
        analysis["current_phase"] = "completed"

        logger.info(
            "analysis_completed",
            analysis_id=analysis_id,
            analysis_type=request.analysis_type,
            insights_count=len(insights),
        )

    except Exception as e:
        logger.error(
            "analysis_failed",
            analysis_id=analysis_id,
            error=str(e),
        )

        analysis["status"] = "failed"
        analysis["completed_at"] = datetime.utcnow()
        analysis["current_phase"] = "failed"
        analysis["error"] = str(e)
