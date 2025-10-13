"""
CQRS API endpoints for command and query operations.

This module provides RESTful endpoints that use the CQRS pattern
for better scalability and separation of concerns.
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

from src.api.auth import get_current_user
from src.core import get_logger
from src.infrastructure.cqrs.commands import (
    CancelInvestigationCommand,
    CommandBus,
    CreateInvestigationCommand,
    ExecuteAgentTaskCommand,
    UpdateInvestigationCommand,
)
from src.infrastructure.cqrs.queries import (
    GetAgentPerformanceQuery,
    GetInvestigationByIdQuery,
    GetInvestigationStatsQuery,
    QueryBus,
    SearchContractsQuery,
    SearchInvestigationsQuery,
)
from src.infrastructure.events.event_bus import get_event_bus

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/cqrs", tags=["CQRS"])


# Request/Response models
class CreateInvestigationRequest(BaseModel):
    """Request to create investigation."""

    query: str
    data_sources: Optional[list[str]] = None
    priority: str = "medium"


class UpdateInvestigationRequest(BaseModel):
    """Request to update investigation."""

    status: str
    results: Optional[dict[str, Any]] = None


class SearchInvestigationsRequest(BaseModel):
    """Request to search investigations."""

    filters: dict[str, Any] = {}
    sort_by: str = "created_at"
    sort_order: str = "desc"
    limit: int = 20
    offset: int = 0


class SearchContractsRequest(BaseModel):
    """Request to search contracts."""

    search_term: Optional[str] = None
    orgao: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    year: Optional[int] = None
    limit: int = 50
    offset: int = 0


class ExecuteAgentTaskRequest(BaseModel):
    """Request to execute agent task."""

    agent_name: str
    task_type: str
    payload: dict[str, Any]
    timeout: Optional[float] = None


# Global instances
command_bus: Optional[CommandBus] = None
query_bus: Optional[QueryBus] = None


async def get_command_bus() -> CommandBus:
    """Get command bus instance."""
    global command_bus
    if command_bus is None:
        event_bus = await get_event_bus()
        command_bus = CommandBus(event_bus)
    return command_bus


async def get_query_bus() -> QueryBus:
    """Get query bus instance."""
    global query_bus
    if query_bus is None:
        query_bus = QueryBus()
    return query_bus


# Command endpoints
@router.post("/investigations", response_model=dict[str, Any])
async def create_investigation(
    request: CreateInvestigationRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    cmd_bus: CommandBus = Depends(get_command_bus),
):
    """
    Create a new investigation using CQRS command.

    This endpoint demonstrates the command side of CQRS:
    - Accepts write operations
    - Publishes events
    - Returns minimal response
    """
    command = CreateInvestigationCommand(
        user_id=current_user["sub"],
        query=request.query,
        data_sources=request.data_sources,
        priority=request.priority,
    )

    result = await cmd_bus.execute(command)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return {
        "investigation_id": result.data["investigation_id"],
        "command_id": result.command_id,
        "events_published": result.events_published,
    }


@router.put("/investigations/{investigation_id}", response_model=dict[str, Any])
async def update_investigation(
    investigation_id: str,
    request: UpdateInvestigationRequest,
    current_user=Depends(get_current_user),
    cmd_bus: CommandBus = Depends(get_command_bus),
):
    """Update investigation status."""
    command = UpdateInvestigationCommand(
        user_id=current_user["sub"],
        investigation_id=investigation_id,
        status=request.status,
        results=request.results,
    )

    result = await cmd_bus.execute(command)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return {"success": True, "command_id": result.command_id}


@router.delete("/investigations/{investigation_id}", response_model=dict[str, Any])
async def cancel_investigation(
    investigation_id: str,
    reason: Optional[str] = None,
    current_user=Depends(get_current_user),
    cmd_bus: CommandBus = Depends(get_command_bus),
):
    """Cancel an investigation."""
    command = CancelInvestigationCommand(
        user_id=current_user["sub"], investigation_id=investigation_id, reason=reason
    )

    result = await cmd_bus.execute(command)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return {"success": True, "command_id": result.command_id}


@router.post("/agents/execute", response_model=dict[str, Any])
async def execute_agent_task(
    request: ExecuteAgentTaskRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    cmd_bus: CommandBus = Depends(get_command_bus),
):
    """Execute an agent task."""
    command = ExecuteAgentTaskCommand(
        user_id=current_user["sub"],
        agent_name=request.agent_name,
        task_type=request.task_type,
        payload=request.payload,
        timeout=request.timeout,
    )

    result = await cmd_bus.execute(command)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return {
        "success": True,
        "command_id": result.command_id,
        "task_id": result.data.get("task_id") if result.data else None,
    }


# Query endpoints
@router.get("/investigations/{investigation_id}", response_model=dict[str, Any])
async def get_investigation(
    investigation_id: str,
    include_findings: bool = True,
    include_anomalies: bool = True,
    current_user=Depends(get_current_user),
    q_bus: QueryBus = Depends(get_query_bus),
):
    """
    Get investigation by ID using CQRS query.

    This endpoint demonstrates the query side of CQRS:
    - Optimized for reads
    - Uses caching
    - Returns denormalized data
    """
    query = GetInvestigationByIdQuery(
        user_id=current_user["sub"],
        investigation_id=investigation_id,
        include_findings=include_findings,
        include_anomalies=include_anomalies,
    )

    result = await q_bus.execute(query)

    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)

    return {
        "investigation": result.data,
        "from_cache": result.from_cache,
        "execution_time_ms": result.execution_time_ms,
    }


@router.post("/investigations/search", response_model=dict[str, Any])
async def search_investigations(
    request: SearchInvestigationsRequest,
    current_user=Depends(get_current_user),
    q_bus: QueryBus = Depends(get_query_bus),
):
    """Search investigations with filters."""
    query = SearchInvestigationsQuery(
        user_id=current_user["sub"],
        filters=request.filters,
        sort_by=request.sort_by,
        sort_order=request.sort_order,
        limit=request.limit,
        offset=request.offset,
    )

    result = await q_bus.execute(query)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return {
        "investigations": result.data,
        "metadata": result.metadata,
        "execution_time_ms": result.execution_time_ms,
    }


@router.get("/investigations/stats", response_model=dict[str, Any])
async def get_investigation_stats(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user=Depends(get_current_user),
    q_bus: QueryBus = Depends(get_query_bus),
):
    """Get investigation statistics."""
    query = GetInvestigationStatsQuery(
        user_id=current_user["sub"], date_from=date_from, date_to=date_to
    )

    result = await q_bus.execute(query)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return {
        "stats": result.data,
        "from_cache": result.from_cache,
        "execution_time_ms": result.execution_time_ms,
    }


@router.post("/contracts/search", response_model=dict[str, Any])
async def search_contracts(
    request: SearchContractsRequest,
    current_user=Depends(get_current_user),
    q_bus: QueryBus = Depends(get_query_bus),
):
    """Search contracts with filters."""
    query = SearchContractsQuery(
        user_id=current_user["sub"],
        search_term=request.search_term,
        orgao=request.orgao,
        min_value=request.min_value,
        max_value=request.max_value,
        year=request.year,
        limit=request.limit,
        offset=request.offset,
        use_cache=True,
        cache_ttl=300,  # 5 minutes
    )

    result = await q_bus.execute(query)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return {
        "contracts": result.data,
        "from_cache": result.from_cache,
        "execution_time_ms": result.execution_time_ms,
    }


@router.get("/agents/performance", response_model=dict[str, Any])
async def get_agent_performance(
    agent_name: Optional[str] = None,
    time_period: str = "1h",
    current_user=Depends(get_current_user),
    q_bus: QueryBus = Depends(get_query_bus),
):
    """Get agent performance metrics."""
    query = GetAgentPerformanceQuery(
        user_id=current_user["sub"],
        agent_name=agent_name,
        time_period=time_period,
        use_cache=True,
        cache_ttl=60,  # 1 minute for recent metrics
    )

    result = await q_bus.execute(query)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return {
        "performance": result.data,
        "from_cache": result.from_cache,
        "execution_time_ms": result.execution_time_ms,
    }


# Bus statistics endpoints
@router.get("/stats/commands", response_model=dict[str, Any])
async def get_command_bus_stats(
    current_user=Depends(get_current_user),
    cmd_bus: CommandBus = Depends(get_command_bus),
):
    """Get command bus statistics."""
    return cmd_bus.get_stats()


@router.get("/stats/queries", response_model=dict[str, Any])
async def get_query_bus_stats(
    current_user=Depends(get_current_user), q_bus: QueryBus = Depends(get_query_bus)
):
    """Get query bus statistics."""
    return q_bus.get_stats()


# Health check
@router.get("/health", response_model=dict[str, Any])
async def cqrs_health_check():
    """Check CQRS system health."""
    try:
        cmd_bus = await get_command_bus()
        q_bus = await get_query_bus()
        event_bus = await get_event_bus()

        return {
            "status": "healthy",
            "command_bus": "ready",
            "query_bus": "ready",
            "event_bus": "ready",
            "event_bus_stats": event_bus.get_stats(),
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
