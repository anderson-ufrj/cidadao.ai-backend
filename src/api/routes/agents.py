"""
Module: api.routes.agents
Description: Direct agent endpoints for specialized AI agents
Author: Anderson H. Silva
Date: 2025-09-25
License: Proprietary - All rights reserved
"""

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from src.agents import (
    AbaporuAgent,
    AgentContext,
    AgentMessage,
    AnitaAgent,
    AyrtonSennaAgent,
    BonifacioAgent,
    CeuciAgent,
    DandaraAgent,
    DrummondAgent,
    LampiaoAgent,
    MachadoAgent,
    MariaQuiteriaAgent,
    NanaAgent,
    ObaluaieAgent,
    OscarNiemeyerAgent,
    OxossiAgent,
    TiradentesAgent,
    ZumbiAgent,
)
from src.api.middleware.authentication import get_current_user
from src.core import get_logger
from src.infrastructure.observability.metrics import count_calls, track_time
from src.infrastructure.rate_limiter import RateLimitTier


# Temporary function until proper rate limit tier detection is implemented
async def get_rate_limit_tier() -> RateLimitTier:
    """Get rate limit tier for current user."""
    return RateLimitTier.BASIC


logger = get_logger(__name__)
router = APIRouter()


class AgentRequest(BaseModel):
    """Base request model for agent operations."""

    query: str = Field(..., description="Query or input for the agent")
    context: dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )
    options: dict[str, Any] = Field(
        default_factory=dict, description="Agent-specific options"
    )


class AgentResponse(BaseModel):
    """Base response model for agent operations."""

    agent: str = Field(..., description="Agent name")
    result: dict[str, Any] = Field(..., description="Agent processing result")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Processing metadata"
    )
    success: bool = Field(default=True, description="Operation success status")
    message: str | None = Field(None, description="Optional status message")


@router.post("/zumbi", response_model=AgentResponse)
@track_time("agent_zumbi_process")
@count_calls("agent_zumbi_requests")
async def process_zumbi_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Zumbi dos Palmares agent.

    Zumbi specializes in anomaly detection and investigation:
    - Price anomalies and overpricing
    - Vendor concentration and cartels
    - Temporal pattern irregularities
    - Contract duplication
    - Payment irregularities
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Zumbi agent
        zumbi = ZumbiAgent()

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="zumbi",
            action="investigate",
            payload={
                "query": request.query,
                "data_source": request.options.get("data_source", "contracts"),
                "anomaly_types": request.options.get(
                    "anomaly_types", ["price", "vendor"]
                ),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await zumbi.process(message=agent_message, context=context)

        return AgentResponse(
            agent="zumbi_dos_palmares",
            result=(
                result.data if hasattr(result, "data") else {"analysis": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "anomalies_detected": (
                    result.metadata.get("anomalies_detected", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
            },
            success=True,
            message="Anomaly detection completed successfully",
        )

    except Exception as e:
        logger.error(f"Zumbi agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Zumbi agent processing failed: {str(e)}"
        )


@router.post("/anita", response_model=AgentResponse)
@track_time("agent_anita_process")
@count_calls("agent_anita_requests")
async def process_anita_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Anita Garibaldi agent.

    Anita specializes in pattern analysis and correlation:
    - Spending trends and patterns
    - Organizational behavior analysis
    - Vendor relationship mapping
    - Seasonal pattern detection
    - Efficiency metrics calculation
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Anita agent
        anita = AnitaAgent()

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="anita",
            action="analyze",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await anita.process(message=agent_message, context=context)

        return AgentResponse(
            agent="anita_garibaldi",
            result=(
                result.data if hasattr(result, "data") else {"analysis": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "patterns_found": (
                    result.metadata.get("patterns_found", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
            },
            success=True,
            message="Pattern analysis completed successfully",
        )

    except Exception as e:
        logger.error(f"Anita agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Anita agent processing failed: {str(e)}"
        )


@router.post("/tiradentes", response_model=AgentResponse)
@track_time("agent_tiradentes_process")
@count_calls("agent_tiradentes_requests")
async def process_tiradentes_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Tiradentes agent.

    Tiradentes specializes in report generation:
    - Executive summaries
    - Detailed investigation reports
    - Multi-format output (JSON, Markdown, HTML)
    - Natural language explanations
    - Actionable recommendations
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Tiradentes agent
        tiradentes = TiradentesAgent()

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="tiradentes",
            action="analyze",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await tiradentes.process(message=agent_message, context=context)

        return AgentResponse(
            agent="tiradentes",
            result=result.data if hasattr(result, "data") else {"report": str(result)},
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "report_format": request.options.get("format", "markdown"),
            },
            success=True,
            message="Report generation completed successfully",
        )

    except Exception as e:
        logger.error(f"Tiradentes agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Tiradentes agent processing failed: {str(e)}"
        )


@router.post("/bonifacio", response_model=AgentResponse)
@track_time("agent_bonifacio_process")
@count_calls("agent_bonifacio_requests")
async def process_bonifacio_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with José Bonifácio agent.

    Bonifácio specializes in legal and compliance analysis:
    - Legal framework verification
    - Compliance assessment
    - Regulatory requirement checking
    - Constitutional alignment analysis
    - Legal risk identification
    - Jurisprudence application
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Bonifacio agent
        bonifacio = BonifacioAgent()

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="bonifacio",
            action="analyze",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await bonifacio.process(message=agent_message, context=context)

        return AgentResponse(
            agent="jose_bonifacio",
            result=(
                result.data if hasattr(result, "data") else {"analysis": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "compliance_issues": (
                    result.metadata.get("compliance_issues", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "legal_risks": (
                    result.metadata.get("legal_risks", [])
                    if hasattr(result, "metadata")
                    else []
                ),
            },
            success=True,
            message="Legal and compliance analysis completed successfully",
        )

    except Exception as e:
        logger.error(f"Bonifacio agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Bonifacio agent processing failed: {str(e)}"
        )


@router.post("/maria-quiteria", response_model=AgentResponse)
@track_time("agent_maria_quiteria_process")
@count_calls("agent_maria_quiteria_requests")
async def process_maria_quiteria_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Maria Quitéria agent.

    Maria Quitéria specializes in security auditing and system protection:
    - Security threat detection
    - Vulnerability assessment
    - Compliance verification (LGPD, ISO27001, etc.)
    - Intrusion detection
    - Digital forensics
    - Risk assessment
    - Security monitoring
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Maria Quiteria agent
        maria_quiteria = MariaQuiteriaAgent()

        # Process request
        result = await maria_quiteria.process(
            message=request.query, context=context, **request.options
        )

        return AgentResponse(
            agent="maria_quiteria",
            result=(
                result.data if hasattr(result, "data") else {"analysis": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "threats_detected": (
                    result.metadata.get("threats_detected", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "security_score": (
                    result.metadata.get("security_score", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
            },
            success=True,
            message="Security audit completed successfully",
        )

    except Exception as e:
        logger.error(f"Maria Quiteria agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Maria Quiteria agent processing failed: {str(e)}"
        )


@router.post("/machado", response_model=AgentResponse)
@track_time("agent_machado_process")
@count_calls("agent_machado_requests")
async def process_machado_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Machado de Assis agent.

    Machado specializes in textual analysis and document processing:
    - Document parsing and classification
    - Named Entity Recognition (NER)
    - Semantic analysis
    - Legal compliance checking
    - Ambiguity detection
    - Readability assessment (Flesch adapted for PT-BR)
    - Contract analysis
    - Suspicious clause identification
    - Linguistic complexity analysis
    - Transparency scoring
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Machado agent
        machado = MachadoAgent()

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="machado",
            action="analyze",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await machado.process(message=agent_message, context=context)

        return AgentResponse(
            agent="machado_de_assis",
            result=(
                result.data if hasattr(result, "data") else {"analysis": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "entities_found": (
                    result.metadata.get("entities_found", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "alerts_detected": (
                    result.metadata.get("alerts_detected", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "complexity_score": (
                    result.metadata.get("complexity_score", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "transparency_score": (
                    result.metadata.get("transparency_score", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
            },
            success=True,
            message="Textual analysis completed successfully",
        )

    except Exception as e:
        logger.error(f"Machado agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Machado agent processing failed: {str(e)}"
        )


@router.post("/dandara", response_model=AgentResponse)
@track_time("agent_dandara_process")
@count_calls("agent_dandara_requests")
async def process_dandara_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Dandara dos Palmares agent.

    Dandara specializes in social equity and justice analysis:
    - Social equity analysis
    - Inclusion policy monitoring
    - Gini coefficient calculation (from real IBGE data)
    - Demographic disparity detection
    - Social justice violation identification
    - Distributive justice assessment
    - Policy effectiveness evaluation
    - Intersectional analysis
    - Vulnerability mapping
    - Equity gap identification

    Real API Integrations:
    - IBGE (demographic, poverty, housing data)
    - DataSUS (health indicators, facilities, vaccination)
    - INEP (education indicators, IDEB, infrastructure)
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Dandara agent
        dandara = DandaraAgent()

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="dandara",
            action="analyze",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await dandara.process(message=agent_message, context=context)

        return AgentResponse(
            agent="dandara_dos_palmares",
            result=(
                result.data if hasattr(result, "data") else {"analysis": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "equity_score": (
                    result.metadata.get("equity_score", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "gini_coefficient": (
                    result.metadata.get("gini_coefficient", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "violations_detected": (
                    result.metadata.get("violations_detected", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "population_affected": (
                    result.metadata.get("population_affected", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "confidence_level": (
                    result.metadata.get("confidence_level", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
            },
            success=True,
            message="Social equity analysis completed successfully",
        )

    except Exception as e:
        logger.error(f"Dandara agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Dandara agent processing failed: {str(e)}"
        )


@router.post("/lampiao", response_model=AgentResponse)
@track_time("agent_lampiao_process")
@count_calls("agent_lampiao_requests")
async def process_lampiao_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Lampião agent.

    Lampião specializes in regional analysis and spatial statistics:
    - Regional inequality measurement (Gini, Theil, Williamson, Atkinson indices)
    - Spatial autocorrelation analysis (Moran's I, LISA)
    - Hotspot detection (Getis-Ord G*)
    - Geographic boundary analysis with IBGE data
    - Regional disparity mapping
    - Spatial pattern detection
    - Lorenz curve analysis
    - Coefficient of variation calculations
    - Integration with real IBGE demographic and economic data
    - All 27 Brazilian states coverage
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Lampiao agent
        lampiao = LampiaoAgent()

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="lampiao",
            action="analyze",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await lampiao.process(message=agent_message, context=context)

        return AgentResponse(
            agent="lampiao",
            result=(
                result.data if hasattr(result, "data") else {"analysis": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "gini_index": (
                    result.metadata.get("gini_index", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "theil_index": (
                    result.metadata.get("theil_index", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "moran_i": (
                    result.metadata.get("moran_i", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "hotspots_detected": (
                    result.metadata.get("hotspots_detected", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
            },
            success=True,
            message="Regional analysis completed successfully",
        )

    except Exception as e:
        logger.error(f"Lampiao agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Lampiao agent processing failed: {str(e)}"
        )


@router.post("/oscar", response_model=AgentResponse)
@track_time("agent_oscar_process")
@count_calls("agent_oscar_requests")
async def process_oscar_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Oscar Niemeyer agent.

    Oscar specializes in data aggregation and visualization architecture:
    - Network graph visualization (NetworkX + Plotly)
    - Fraud relationship network detection
    - Choropleth maps for Brazilian states/municipalities
    - Time series generation with trend and seasonality
    - Geographic aggregation by region (North, Northeast, etc.)
    - Multi-dimensional data aggregation
    - Data export formats (JSON, CSV)
    - Intelligent metadata generation
    - Interactive graph layouts (force-directed, circular, hierarchical)
    - IBGE GeoJSON integration for accurate boundaries
    - Plotly Express for high-quality visualizations
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Oscar agent
        oscar = OscarNiemeyerAgent()

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="oscar",
            action="analyze",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await oscar.process(message=agent_message, context=context)

        return AgentResponse(
            agent="oscar_niemeyer",
            result=(
                result.data if hasattr(result, "data") else {"analysis": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "nodes_count": (
                    result.metadata.get("nodes_count", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "edges_count": (
                    result.metadata.get("edges_count", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "visualization_type": (
                    result.metadata.get("visualization_type", "")
                    if hasattr(result, "metadata")
                    else ""
                ),
                "data_points": (
                    result.metadata.get("data_points", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
            },
            success=True,
            message="Data aggregation and visualization completed successfully",
        )

    except Exception as e:
        logger.error(f"Oscar agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Oscar agent processing failed: {str(e)}"
        )


@router.post("/drummond", response_model=AgentResponse)
@track_time("agent_drummond_process")
@count_calls("agent_drummond_requests")
async def process_drummond_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Drummond agent.

    Drummond specializes in communication and content creation:
    - Blog posts and articles generation
    - Social media content creation
    - Technical documentation
    - Press releases
    - Multi-format content (Markdown, HTML, PDF)
    - SEO optimization
    - Tone and style adaptation
    - Content strategy
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Drummond agent
        drummond = DrummondAgent()

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="drummond",
            action="analyze",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await drummond.process(message=agent_message, context=context)

        return AgentResponse(
            agent="drummond",
            result=(
                result.data if hasattr(result, "data") else {"content": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "content_type": (
                    result.metadata.get("content_type", "")
                    if hasattr(result, "metadata")
                    else ""
                ),
            },
            success=True,
            message="Communication processing completed successfully",
        )

    except Exception as e:
        logger.error(f"Drummond agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Drummond agent processing failed: {str(e)}"
        )


@router.post("/obaluaie", response_model=AgentResponse)
@track_time("agent_obaluaie_process")
@count_calls("agent_obaluaie_requests")
async def process_obaluaie_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Obaluaiê agent.

    Obaluaiê specializes in corruption detection and risk assessment:
    - Corruption pattern detection
    - Risk score calculation
    - Fraud scheme identification
    - Network analysis for corruption rings
    - Political connection mapping
    - Financial anomaly detection
    - Behavioral pattern analysis
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Obaluaie agent
        obaluaie = ObaluaieAgent()

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="obaluaie",
            action="investigate",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await obaluaie.process(message=agent_message, context=context)

        return AgentResponse(
            agent="obaluaie",
            result=(
                result.data if hasattr(result, "data") else {"analysis": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "risk_score": (
                    result.metadata.get("risk_score", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "corruption_indicators": (
                    result.metadata.get("corruption_indicators", [])
                    if hasattr(result, "metadata")
                    else []
                ),
            },
            success=True,
            message="Corruption detection completed successfully",
        )

    except Exception as e:
        logger.error(f"Obaluaie agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Obaluaie agent processing failed: {str(e)}"
        )


@router.post("/oxossi", response_model=AgentResponse)
@track_time("agent_oxossi_process")
@count_calls("agent_oxossi_requests")
async def process_oxossi_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Oxossi agent.

    Oxossi specializes in data hunting and discovery:
    - Multi-source data discovery
    - API integration and data fetching
    - Database querying and extraction
    - Web scraping (Portal da Transparência)
    - Data validation and enrichment
    - Entity resolution
    - Cross-reference analysis
    - Data quality assessment
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Oxossi agent
        oxossi = OxossiAgent()

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="oxossi",
            action="analyze",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await oxossi.process(message=agent_message, context=context)

        return AgentResponse(
            agent="oxossi",
            result=(
                result.data if hasattr(result, "data") else {"discovery": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "sources_queried": (
                    result.metadata.get("sources_queried", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "records_found": (
                    result.metadata.get("records_found", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
            },
            success=True,
            message="Data hunting completed successfully",
        )

    except Exception as e:
        logger.error(f"Oxossi agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Oxossi agent processing failed: {str(e)}"
        )


@router.post("/ceuci", response_model=AgentResponse)
@track_time("agent_ceuci_process")
@count_calls("agent_ceuci_requests")
async def process_ceuci_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Ceuci agent.

    Ceuci specializes in ETL and predictive analytics:
    - Data extraction, transformation, loading
    - Time series forecasting
    - Trend prediction
    - Seasonality detection
    - Budget forecasting
    - Resource allocation optimization
    - Anomaly prediction
    - Machine learning pipeline management
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Ceuci agent
        ceuci = CeuciAgent()

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="ceuci",
            action="analyze",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await ceuci.process(message=agent_message, context=context)

        return AgentResponse(
            agent="ceuci",
            result=(
                result.data if hasattr(result, "data") else {"prediction": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "forecast_horizon": (
                    result.metadata.get("forecast_horizon", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "confidence": (
                    result.metadata.get("confidence", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
            },
            success=True,
            message="ETL and prediction completed successfully",
        )

    except Exception as e:
        logger.error(f"Ceuci agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Ceuci agent processing failed: {str(e)}"
        )


@router.post("/abaporu", response_model=AgentResponse)
@track_time("agent_abaporu_process")
@count_calls("agent_abaporu_requests")
async def process_abaporu_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Abaporu (Master) agent.

    Abaporu orchestrates multi-agent investigations:
    - Multi-agent workflow coordination
    - Investigation planning and execution
    - Task delegation and monitoring
    - Result synthesis across agents
    - Strategic decision making
    - Resource allocation
    - Quality control
    - Complex analysis orchestration
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Abaporu agent with required dependencies
        from src.agents import NanaAgent
        from src.core.cache import get_redis_client
        from src.infrastructure.vector_store import VectorStore
        from src.services.maritaca_client import MaritacaClient

        # Create dependencies for Abaporu (master orchestrator)
        maritaca_client = MaritacaClient()

        # Create Nana as memory agent for Abaporu
        redis_client = await get_redis_client()
        vector_store = VectorStore()
        memory_agent = NanaAgent(redis_client=redis_client, vector_store=vector_store)

        abaporu = AbaporuAgent(
            maritaca_client=maritaca_client, memory_agent=memory_agent
        )

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="abaporu",
            action="analyze",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await abaporu.process(message=agent_message, context=context)

        return AgentResponse(
            agent="abaporu",
            result=(
                result.data
                if hasattr(result, "data")
                else {"orchestration": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "agents_used": (
                    result.metadata.get("agents_used", [])
                    if hasattr(result, "metadata")
                    else []
                ),
                "tasks_completed": (
                    result.metadata.get("tasks_completed", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
            },
            success=True,
            message="Multi-agent orchestration completed successfully",
        )

    except Exception as e:
        logger.error(f"Abaporu agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Abaporu agent processing failed: {str(e)}"
        )


@router.post("/ayrton-senna", response_model=AgentResponse)
@track_time("agent_ayrton_senna_process")
@count_calls("agent_ayrton_senna_requests")
async def process_ayrton_senna_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Ayrton Senna (Semantic Router) agent.

    Ayrton Senna specializes in intent detection and routing:
    - Natural language understanding
    - Intent classification
    - Entity extraction
    - Query understanding
    - Agent selection and routing
    - Context analysis
    - Semantic similarity
    - Multi-language support (PT-BR focus)
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Ayrton Senna agent with required dependencies
        from src.services.maritaca_client import MaritacaClient

        # Create LLM service for Senna (semantic router)
        llm_service = MaritacaClient()

        ayrton_senna = AyrtonSennaAgent(llm_service=llm_service)

        # Process request
        result = await ayrton_senna.process(
            message=request.query, context=context, **request.options
        )

        return AgentResponse(
            agent="ayrton_senna",
            result=(
                result.data if hasattr(result, "data") else {"routing": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "detected_intent": (
                    result.metadata.get("detected_intent", "")
                    if hasattr(result, "metadata")
                    else ""
                ),
                "confidence": (
                    result.metadata.get("confidence", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "recommended_agent": (
                    result.metadata.get("recommended_agent", "")
                    if hasattr(result, "metadata")
                    else ""
                ),
            },
            success=True,
            message="Semantic routing completed successfully",
        )

    except Exception as e:
        logger.error(f"Ayrton Senna agent error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ayrton Senna agent processing failed: {str(e)}",
        )


@router.post("/nana", response_model=AgentResponse)
@track_time("agent_nana_process")
@count_calls("agent_nana_requests")
async def process_nana_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier),
):
    """
    Process request with Nanã (Memory) agent.

    Nanã specializes in memory management and context:
    - Episodic memory (event sequences)
    - Semantic memory (knowledge graphs)
    - Conversation memory (dialogue history)
    - Context retrieval and storage
    - Long-term memory management
    - Working memory optimization
    - Memory consolidation
    - Context-aware recommendations
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=(
                current_user.get("user_id", "anonymous")
                if current_user
                else "anonymous"
            ),
            session_id=str(request.context.get("session_id", "default")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                "request_id": str(request.context.get("request_id", "unknown")),
                **request.context,
            },
        )

        # Initialize Nana agent with required dependencies
        from src.core.cache import get_redis_client
        from src.infrastructure.vector_store import VectorStore

        # Create dependencies for Nana (memory agent)
        redis_client = await get_redis_client()
        vector_store = VectorStore()

        nana = NanaAgent(redis_client=redis_client, vector_store=vector_store)

        # Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="nana",
            action="analyze",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options,
            },
            context=request.context,
        )

        # Process request with proper message object
        result = await nana.process(message=agent_message, context=context)

        return AgentResponse(
            agent="nana",
            result=(
                result.data if hasattr(result, "data") else {"memory": str(result)}
            ),
            metadata={
                "processing_time": (
                    result.metadata.get("processing_time", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "memories_retrieved": (
                    result.metadata.get("memories_retrieved", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
                "context_relevance": (
                    result.metadata.get("context_relevance", 0)
                    if hasattr(result, "metadata")
                    else 0
                ),
            },
            success=True,
            message="Memory processing completed successfully",
        )

    except Exception as e:
        logger.error(f"Nana agent error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Nana agent processing failed: {str(e)}"
        )


@router.get("/status")
async def get_agents_status(current_user: dict = Depends(get_current_user)):
    """Get status of all available agents."""
    agents = {
        "zumbi_dos_palmares": {
            "name": "Zumbi dos Palmares",
            "role": "Anomaly Detection Specialist",
            "status": "active",
            "capabilities": [
                "Price anomaly detection",
                "Vendor concentration analysis",
                "Temporal pattern recognition",
                "Contract duplication detection",
                "Payment irregularity identification",
            ],
        },
        "anita_garibaldi": {
            "name": "Anita Garibaldi",
            "role": "Pattern Analysis Specialist",
            "status": "active",
            "capabilities": [
                "Spending trend analysis",
                "Organizational behavior mapping",
                "Vendor relationship analysis",
                "Seasonal pattern detection",
                "Efficiency metrics calculation",
            ],
        },
        "tiradentes": {
            "name": "Tiradentes",
            "role": "Report Generation Specialist",
            "status": "active",
            "capabilities": [
                "Executive summary generation",
                "Detailed investigation reports",
                "Multi-format output",
                "Natural language explanations",
                "Actionable recommendations",
            ],
        },
        "jose_bonifacio": {
            "name": "José Bonifácio",
            "role": "Legal & Compliance Specialist",
            "status": "active",
            "capabilities": [
                "Legal framework verification",
                "Compliance assessment",
                "Regulatory requirement checking",
                "Constitutional alignment analysis",
                "Legal risk identification",
            ],
        },
        "maria_quiteria": {
            "name": "Maria Quitéria",
            "role": "Security Auditor & System Guardian",
            "status": "active",
            "capabilities": [
                "Security threat detection",
                "Vulnerability assessment",
                "Compliance verification (LGPD, ISO27001)",
                "Intrusion detection",
                "Digital forensics",
                "Risk assessment",
            ],
        },
        "machado_de_assis": {
            "name": "Machado de Assis",
            "role": "Textual Analysis & Document Processing Specialist",
            "status": "active",
            "capabilities": [
                "Document parsing and classification",
                "Named Entity Recognition (NER)",
                "Semantic analysis",
                "Legal compliance checking",
                "Ambiguity detection",
                "Readability assessment (Flesch PT-BR)",
                "Contract analysis",
                "Suspicious clause identification",
                "Linguistic complexity analysis",
                "Transparency scoring",
            ],
        },
        "dandara_dos_palmares": {
            "name": "Dandara dos Palmares",
            "role": "Social Equity & Justice Analysis Specialist",
            "status": "active",
            "capabilities": [
                "Social equity analysis",
                "Inclusion policy monitoring",
                "Gini coefficient calculation (IBGE data)",
                "Demographic disparity detection",
                "Social justice violation identification",
                "Distributive justice assessment",
                "Policy effectiveness evaluation",
                "Intersectional analysis",
                "Vulnerability mapping",
                "Real API integrations (IBGE, DataSUS, INEP)",
            ],
        },
        "lampiao": {
            "name": "Lampião",
            "role": "Regional Analysis & Spatial Statistics Specialist",
            "status": "active",
            "capabilities": [
                "Regional inequality measurement (Gini, Theil, Williamson, Atkinson)",
                "Spatial autocorrelation analysis (Moran's I, LISA)",
                "Hotspot detection (Getis-Ord G*)",
                "Geographic boundary analysis with IBGE data",
                "Regional disparity mapping",
                "Spatial pattern detection",
                "Lorenz curve analysis",
                "All 27 Brazilian states coverage",
            ],
        },
        "oscar_niemeyer": {
            "name": "Oscar Niemeyer",
            "role": "Data Aggregation & Visualization Architect",
            "status": "active",
            "capabilities": [
                "Network graph visualization (NetworkX + Plotly)",
                "Fraud relationship network detection",
                "Choropleth maps for Brazilian states/municipalities",
                "Time series generation with trends",
                "Geographic aggregation by region",
                "Multi-dimensional data aggregation",
                "Data export formats (JSON, CSV)",
                "Interactive graph layouts",
                "IBGE GeoJSON integration",
            ],
        },
        "drummond": {
            "name": "Carlos Drummond de Andrade",
            "role": "Communication & Content Creation Specialist",
            "status": "active",
            "capabilities": [
                "Blog posts and articles generation",
                "Social media content creation",
                "Technical documentation",
                "Press releases",
                "Multi-format content (Markdown, HTML, PDF)",
                "SEO optimization",
                "Tone and style adaptation",
                "Content strategy",
            ],
        },
        "obaluaie": {
            "name": "Obaluaiê",
            "role": "Corruption Detection & Risk Assessment Specialist",
            "status": "active",
            "capabilities": [
                "Corruption pattern detection",
                "Risk score calculation",
                "Fraud scheme identification",
                "Network analysis for corruption rings",
                "Political connection mapping",
                "Financial anomaly detection",
                "Behavioral pattern analysis",
            ],
        },
        "oxossi": {
            "name": "Oxossi",
            "role": "Data Hunting & Discovery Specialist",
            "status": "active",
            "capabilities": [
                "Multi-source data discovery",
                "API integration and data fetching",
                "Database querying and extraction",
                "Web scraping (Portal da Transparência)",
                "Data validation and enrichment",
                "Entity resolution",
                "Cross-reference analysis",
                "Data quality assessment",
            ],
        },
        "ceuci": {
            "name": "Ceuci",
            "role": "ETL & Predictive Analytics Specialist",
            "status": "active",
            "capabilities": [
                "Data extraction, transformation, loading",
                "Time series forecasting",
                "Trend prediction",
                "Seasonality detection",
                "Budget forecasting",
                "Resource allocation optimization",
                "Anomaly prediction",
                "Machine learning pipeline management",
            ],
        },
        "abaporu": {
            "name": "Abaporu (Master Agent)",
            "role": "Multi-Agent Orchestration Specialist",
            "status": "active",
            "capabilities": [
                "Multi-agent workflow coordination",
                "Investigation planning and execution",
                "Task delegation and monitoring",
                "Result synthesis across agents",
                "Strategic decision making",
                "Resource allocation",
                "Quality control",
                "Complex analysis orchestration",
            ],
        },
        "ayrton_senna": {
            "name": "Ayrton Senna",
            "role": "Semantic Routing & Intent Detection Specialist",
            "status": "active",
            "capabilities": [
                "Natural language understanding",
                "Intent classification",
                "Entity extraction",
                "Query understanding",
                "Agent selection and routing",
                "Context analysis",
                "Semantic similarity",
                "Multi-language support (PT-BR focus)",
            ],
        },
        "nana": {
            "name": "Nanã",
            "role": "Memory Management & Context Specialist",
            "status": "active",
            "capabilities": [
                "Episodic memory (event sequences)",
                "Semantic memory (knowledge graphs)",
                "Conversation memory (dialogue history)",
                "Context retrieval and storage",
                "Long-term memory management",
                "Working memory optimization",
                "Memory consolidation",
                "Context-aware recommendations",
            ],
        },
    }

    return {
        "agents": agents,
        "total_active": sum(1 for a in agents.values() if a["status"] == "active"),
        "timestamp": "2025-09-25T14:30:00Z",
    }


@router.get("/")
async def list_agents():
    """List all available agents with their endpoints."""
    return {
        "message": "Cidadão.AI Agent System",
        "version": "2.0.0",
        "agents": [
            {
                "name": "Zumbi dos Palmares",
                "endpoint": "/api/v1/agents/zumbi",
                "description": "Anomaly detection and investigation specialist",
            },
            {
                "name": "Anita Garibaldi",
                "endpoint": "/api/v1/agents/anita",
                "description": "Pattern analysis and correlation specialist",
            },
            {
                "name": "Tiradentes",
                "endpoint": "/api/v1/agents/tiradentes",
                "description": "Report generation and natural language specialist",
            },
            {
                "name": "José Bonifácio",
                "endpoint": "/api/v1/agents/bonifacio",
                "description": "Legal and compliance analysis specialist",
            },
            {
                "name": "Maria Quitéria",
                "endpoint": "/api/v1/agents/maria-quiteria",
                "description": "Security auditing and system protection specialist",
            },
            {
                "name": "Machado de Assis",
                "endpoint": "/api/v1/agents/machado",
                "description": "Textual analysis and document processing specialist",
            },
            {
                "name": "Dandara dos Palmares",
                "endpoint": "/api/v1/agents/dandara",
                "description": "Social equity and justice analysis specialist with real API integrations",
            },
            {
                "name": "Lampião",
                "endpoint": "/api/v1/agents/lampiao",
                "description": "Regional analysis and spatial statistics specialist with IBGE integration",
            },
            {
                "name": "Oscar Niemeyer",
                "endpoint": "/api/v1/agents/oscar",
                "description": "Data aggregation and visualization architect with NetworkX and Plotly",
            },
            {
                "name": "Carlos Drummond de Andrade",
                "endpoint": "/api/v1/agents/drummond",
                "description": "Communication and content creation specialist",
            },
            {
                "name": "Obaluaiê",
                "endpoint": "/api/v1/agents/obaluaie",
                "description": "Corruption detection and risk assessment specialist",
            },
            {
                "name": "Oxossi",
                "endpoint": "/api/v1/agents/oxossi",
                "description": "Data hunting and discovery specialist",
            },
            {
                "name": "Ceuci",
                "endpoint": "/api/v1/agents/ceuci",
                "description": "ETL and predictive analytics specialist",
            },
            {
                "name": "Abaporu (Master Agent)",
                "endpoint": "/api/v1/agents/abaporu",
                "description": "Multi-agent orchestration and investigation coordination",
            },
            {
                "name": "Ayrton Senna",
                "endpoint": "/api/v1/agents/ayrton-senna",
                "description": "Semantic routing and intent detection specialist",
            },
            {
                "name": "Nanã",
                "endpoint": "/api/v1/agents/nana",
                "description": "Memory management and context specialist",
            },
        ],
    }
