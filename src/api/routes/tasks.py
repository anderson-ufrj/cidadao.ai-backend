"""
Module: api.routes.tasks
Description: API endpoints for manually triggering Celery tasks
Author: Anderson H. Silva
Date: 2025-10-07
License: Proprietary - All rights reserved
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel

from src.api.routes.auth import get_current_user
from src.infrastructure.queue.tasks.katana_tasks import (
    monitor_katana_dispensas,
    katana_health_check
)
from src.infrastructure.queue.tasks.auto_investigation_tasks import (
    auto_monitor_new_contracts,
    auto_monitor_priority_orgs,
    auto_investigation_health_check
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


class TaskResponse(BaseModel):
    """Response model for task execution."""
    task_id: str
    task_name: str
    status: str
    message: str


@router.post("/trigger/katana-monitor", response_model=Dict[str, Any])
async def trigger_katana_monitor(
    current_user: Dict = Depends(get_current_user)
):
    """
    Manually trigger Katana dispensas monitoring task.

    **Requires authentication.**

    This will:
    - Fetch all dispensas from Katana API
    - Analyze each with Zumbi agent
    - Create investigations for anomalies
    """
    try:
        # Trigger task asynchronously
        task = monitor_katana_dispensas.delay()

        return {
            "task_id": task.id,
            "task_name": "monitor_katana_dispensas",
            "status": "queued",
            "message": "Katana monitoring task has been queued. Check /tasks/status/{task_id} for progress."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger Katana monitoring: {str(e)}"
        )


@router.post("/trigger/auto-monitor-contracts", response_model=Dict[str, Any])
async def trigger_auto_monitor_contracts(
    lookback_hours: int = 24,
    current_user: Dict = Depends(get_current_user)
):
    """
    Manually trigger automatic contract monitoring.

    **Requires authentication.**

    Args:
        lookback_hours: Hours to look back for new contracts (default: 24)
    """
    try:
        task = auto_monitor_new_contracts.delay(lookback_hours=lookback_hours)

        return {
            "task_id": task.id,
            "task_name": "auto_monitor_new_contracts",
            "status": "queued",
            "parameters": {"lookback_hours": lookback_hours},
            "message": f"Auto-monitoring task queued to check last {lookback_hours} hours of contracts."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger contract monitoring: {str(e)}"
        )


@router.post("/trigger/priority-orgs", response_model=Dict[str, Any])
async def trigger_priority_orgs_monitor(
    current_user: Dict = Depends(get_current_user)
):
    """
    Manually trigger priority organizations monitoring.

    **Requires authentication.**
    """
    try:
        task = auto_monitor_priority_orgs.delay()

        return {
            "task_id": task.id,
            "task_name": "auto_monitor_priority_orgs",
            "status": "queued",
            "message": "Priority organizations monitoring task has been queued."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger priority orgs monitoring: {str(e)}"
        )


@router.get("/health/katana", response_model=Dict[str, Any])
async def check_katana_health():
    """
    Check Katana API health status.

    **No authentication required.**
    """
    try:
        task = katana_health_check.delay()
        result = task.get(timeout=10)  # Wait up to 10 seconds

        return result
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Katana health check failed: {str(e)}"
        )


@router.get("/health/auto-investigation", response_model=Dict[str, Any])
async def check_auto_investigation_health():
    """
    Check auto-investigation system health.

    **No authentication required.**
    """
    try:
        task = auto_investigation_health_check.delay()
        result = task.get(timeout=30)  # Wait up to 30 seconds

        return result
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Auto-investigation health check failed: {str(e)}"
        )


@router.get("/status/{task_id}", response_model=Dict[str, Any])
async def get_task_status(task_id: str):
    """
    Get status of a running or completed task.

    **No authentication required.**

    Args:
        task_id: The task ID returned when triggering a task
    """
    from celery.result import AsyncResult
    from src.infrastructure.queue.celery_app import celery_app

    try:
        result = AsyncResult(task_id, app=celery_app)

        response = {
            "task_id": task_id,
            "status": result.state,
            "ready": result.ready(),
        }

        if result.ready():
            if result.successful():
                response["result"] = result.result
            else:
                response["error"] = str(result.result)

        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )


@router.get("/list/scheduled", response_model=Dict[str, Any])
async def list_scheduled_tasks():
    """
    List all scheduled periodic tasks.

    **No authentication required.**
    """
    from src.infrastructure.queue.celery_app import celery_app

    schedule = celery_app.conf.beat_schedule

    tasks = []
    for name, config in schedule.items():
        tasks.append({
            "name": name,
            "task": config["task"],
            "schedule": str(config["schedule"]),
            "args": config.get("args", []),
            "kwargs": config.get("kwargs", {}),
            "options": config.get("options", {})
        })

    return {
        "total_scheduled": len(tasks),
        "tasks": tasks
    }
