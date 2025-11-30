"""
Dashboard API Routes.

Provides REST endpoints for the Agent Metrics Dashboard.
"""

import asyncio
import json
from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from src.core import get_logger
from src.schemas.dashboard import (
    AgentDashboardSummary,
    AgentDetailedMetrics,
    AgentHealthMatrix,
    AgentRanking,
)
from src.services.dashboard import AgentDashboardService

logger = get_logger("api.dashboard")

router = APIRouter(prefix="/dashboard/agents", tags=["Dashboard"])


@lru_cache(maxsize=1)
def get_dashboard_service() -> AgentDashboardService:
    """Get or create dashboard service instance."""
    return AgentDashboardService()


@router.get(
    "/summary",
    response_model=AgentDashboardSummary,
    summary="Get Dashboard Summary",
    description="Returns a consolidated view of all agent metrics including health status, "
    "performance metrics, top performers, and recent errors.",
)
async def get_dashboard_summary(
    period: Literal["1h", "6h", "24h", "7d"] = Query(
        default="24h",
        description="Time period for metrics aggregation",
    ),
) -> AgentDashboardSummary:
    """Get complete dashboard summary with all agent metrics."""
    service = get_dashboard_service()
    return await service.get_summary(period=period)


@router.get(
    "/leaderboard",
    response_model=list[AgentRanking],
    summary="Get Agent Leaderboard",
    description="Returns agents ranked by the specified metric.",
)
async def get_agent_leaderboard(
    metric: Literal[
        "success_rate", "response_time", "requests", "quality_score"
    ] = Query(
        default="success_rate",
        description="Metric to rank agents by",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=16,
        description="Maximum number of agents to return",
    ),
    order: Literal["asc", "desc"] = Query(
        default="desc",
        description="Sort order (desc = best first for most metrics)",
    ),
) -> list[AgentRanking]:
    """Get agent leaderboard ranked by specified metric."""
    service = get_dashboard_service()
    return await service.get_leaderboard(metric=metric, limit=limit, order=order)


@router.get(
    "/health",
    response_model=AgentHealthMatrix,
    summary="Get Health Matrix",
    description="Returns health status for all agents with detailed metrics and issues.",
)
async def get_health_matrix() -> AgentHealthMatrix:
    """Get health status matrix for all agents."""
    service = get_dashboard_service()
    return await service.get_health_matrix()


@router.get(
    "/stream",
    summary="Stream Metrics (SSE)",
    description="Server-Sent Events stream of dashboard metrics. "
    "Updates every 5 seconds by default.",
)
async def stream_dashboard_metrics(
    request: Request,
    interval: int = Query(
        default=5,
        ge=1,
        le=60,
        description="Update interval in seconds",
    ),
) -> StreamingResponse:
    """Stream dashboard metrics via Server-Sent Events."""
    service = get_dashboard_service()

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events with dashboard metrics."""
        try:
            async for metrics in service.stream_metrics(interval_seconds=interval):
                if await request.is_disconnected():
                    break

                event_data = json.dumps(metrics, default=str)
                yield f"event: {metrics.get('event', 'metrics_update')}\n"
                yield f"data: {event_data}\n\n"

        except asyncio.CancelledError:
            logger.info("SSE stream cancelled by client")
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
            error_data = json.dumps({"error": str(e)})
            yield f"event: error\ndata: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/{agent_name}",
    response_model=AgentDetailedMetrics,
    summary="Get Agent Details",
    description="Returns detailed metrics for a specific agent.",
)
async def get_agent_detail(agent_name: str) -> AgentDetailedMetrics:
    """Get detailed metrics for a specific agent."""
    service = get_dashboard_service()
    result = await service.get_agent_detail(agent_name)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found. Valid agents: zumbi, anita, "
            "tiradentes, ayrton_senna, bonifacio, maria_quiteria, machado, "
            "oxossi, lampiao, oscar_niemeyer, abaporu, nana, drummond, "
            "ceuci, obaluaie, dandara",
        )

    return result
