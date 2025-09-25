"""
API routes for agent performance metrics.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST

from src.core import get_logger
from src.models.user import User
from src.api.dependencies import get_current_user
from src.services.agent_metrics import agent_metrics_service


router = APIRouter()
logger = get_logger("api.agent_metrics")


@router.get("/agents/{agent_name}/stats")
async def get_agent_stats(
    agent_name: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed statistics for a specific agent."""
    try:
        stats = await agent_metrics_service.get_agent_stats(agent_name)
        
        if stats.get("status") == "no_data":
            raise HTTPException(
                status_code=404,
                detail=f"No metrics found for agent: {agent_name}"
            )
        
        return {
            "status": "success",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting agent stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/summary")
async def get_all_agents_summary(
    current_user: User = Depends(get_current_user)
):
    """Get summary statistics for all agents."""
    try:
        summary = await agent_metrics_service.get_all_agents_summary()
        
        return {
            "status": "success",
            "data": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting agents summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prometheus")
async def get_prometheus_metrics():
    """
    Expose metrics in Prometheus format.
    This endpoint is typically not authenticated to allow Prometheus scraping.
    """
    try:
        metrics = agent_metrics_service.get_prometheus_metrics()
        return Response(
            content=metrics,
            media_type=CONTENT_TYPE_LATEST,
            headers={"Content-Type": CONTENT_TYPE_LATEST}
        )
        
    except Exception as e:
        logger.error(f"Error generating Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_name}/reset")
async def reset_agent_metrics(
    agent_name: str,
    current_user: User = Depends(get_current_user)
):
    """Reset metrics for a specific agent."""
    try:
        await agent_metrics_service.reset_metrics(agent_name)
        
        return {
            "status": "success",
            "message": f"Metrics reset for agent: {agent_name}"
        }
        
    except Exception as e:
        logger.error(f"Error resetting agent metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_all_metrics(
    current_user: User = Depends(get_current_user)
):
    """Reset metrics for all agents."""
    try:
        await agent_metrics_service.reset_metrics()
        
        return {
            "status": "success",
            "message": "All agent metrics have been reset"
        }
        
    except Exception as e:
        logger.error(f"Error resetting all metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def metrics_health_check():
    """Check if metrics service is healthy."""
    try:
        # Get summary to verify service is working
        summary = await agent_metrics_service.get_all_agents_summary()
        
        return {
            "status": "healthy",
            "service": "agent_metrics",
            "agents_tracked": summary.get("total_agents", 0),
            "total_requests": summary.get("total_requests", 0)
        }
        
    except Exception as e:
        logger.error(f"Metrics service health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "agent_metrics",
            "error": str(e)
        }