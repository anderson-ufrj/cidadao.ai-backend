"""
Resilience monitoring endpoints.

This module provides endpoints for monitoring circuit breakers,
bulkheads, and overall system resilience.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends

from src.core import get_logger
from src.api.auth import get_current_user
from src.infrastructure.resilience import circuit_breaker_manager, bulkhead_manager

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/resilience", tags=["Resilience"])


@router.get("/circuit-breakers", response_model=Dict[str, Any])
async def get_circuit_breaker_stats(
    current_user = Depends(get_current_user)
):
    """
    Get statistics for all circuit breakers.
    
    Returns detailed statistics including:
    - Current state
    - Success/failure rates
    - Request counts
    - Recent state changes
    """
    try:
        stats = circuit_breaker_manager.get_all_stats()
        health_status = circuit_breaker_manager.get_health_status()
        
        return {
            "circuit_breakers": stats,
            "health_status": health_status,
            "summary": {
                "total_breakers": len(stats),
                "healthy_services": len(health_status["healthy_services"]),
                "degraded_services": len(health_status["degraded_services"]),
                "failed_services": len(health_status["failed_services"])
            }
        }
    except Exception as e:
        logger.error(f"Failed to get circuit breaker stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve circuit breaker statistics")


@router.get("/circuit-breakers/{service_name}", response_model=Dict[str, Any])
async def get_circuit_breaker_stats_by_service(
    service_name: str,
    current_user = Depends(get_current_user)
):
    """
    Get statistics for a specific circuit breaker.
    
    Args:
        service_name: Name of the service
        
    Returns:
        Detailed statistics for the specified circuit breaker
    """
    try:
        # Get or create circuit breaker to ensure it exists
        breaker = circuit_breaker_manager.get_circuit_breaker(service_name)
        stats = breaker.get_stats()
        
        return {
            "service_name": service_name,
            "circuit_breaker": stats
        }
    except Exception as e:
        logger.error(f"Failed to get circuit breaker stats for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve circuit breaker statistics for {service_name}")


@router.post("/circuit-breakers/{service_name}/reset", response_model=Dict[str, Any])
async def reset_circuit_breaker(
    service_name: str,
    current_user = Depends(get_current_user)
):
    """
    Reset a specific circuit breaker to closed state.
    
    Args:
        service_name: Name of the service
        
    Returns:
        Success confirmation
    """
    try:
        breaker = circuit_breaker_manager.get_circuit_breaker(service_name)
        await breaker.reset()
        
        logger.info(f"Circuit breaker for {service_name} reset by user {current_user['sub']}")
        
        return {
            "message": f"Circuit breaker for {service_name} reset successfully",
            "service_name": service_name,
            "new_state": breaker.state.value
        }
    except Exception as e:
        logger.error(f"Failed to reset circuit breaker for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset circuit breaker for {service_name}")


@router.post("/circuit-breakers/reset-all", response_model=Dict[str, Any])
async def reset_all_circuit_breakers(
    current_user = Depends(get_current_user)
):
    """
    Reset all circuit breakers to closed state.
    
    Returns:
        Success confirmation
    """
    try:
        await circuit_breaker_manager.reset_all()
        
        logger.warning(f"All circuit breakers reset by user {current_user['sub']}")
        
        return {
            "message": "All circuit breakers reset successfully",
            "reset_by": current_user["sub"]
        }
    except Exception as e:
        logger.error(f"Failed to reset all circuit breakers: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset all circuit breakers")


@router.get("/bulkheads", response_model=Dict[str, Any])
async def get_bulkhead_stats(
    current_user = Depends(get_current_user)
):
    """
    Get statistics for all bulkheads.
    
    Returns detailed statistics including:
    - Current utilization
    - Active/queued operations
    - Performance metrics
    - Resource isolation status
    """
    try:
        stats = bulkhead_manager.get_all_stats()
        utilization = bulkhead_manager.get_resource_utilization()
        
        return {
            "bulkheads": stats,
            "resource_utilization": utilization,
            "summary": {
                "total_bulkheads": len(stats),
                "overall_utilization": utilization["overall_utilization"],
                "total_capacity": utilization["total_capacity"],
                "total_active": utilization["total_active"],
                "total_queued": utilization["total_queued"]
            }
        }
    except Exception as e:
        logger.error(f"Failed to get bulkhead stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve bulkhead statistics")


@router.get("/bulkheads/{resource_type}", response_model=Dict[str, Any])
async def get_bulkhead_stats_by_resource(
    resource_type: str,
    current_user = Depends(get_current_user)
):
    """
    Get statistics for a specific bulkhead.
    
    Args:
        resource_type: Type of resource
        
    Returns:
        Detailed statistics for the specified bulkhead
    """
    try:
        # Get or create bulkhead to ensure it exists
        bulkhead = bulkhead_manager.get_bulkhead(resource_type)
        stats = bulkhead.get_stats()
        
        return {
            "resource_type": resource_type,
            "bulkhead": stats
        }
    except Exception as e:
        logger.error(f"Failed to get bulkhead stats for {resource_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve bulkhead statistics for {resource_type}")


@router.get("/health", response_model=Dict[str, Any])
async def get_resilience_health():
    """
    Get overall resilience health status.
    
    Returns:
        Comprehensive health status of all resilience components
    """
    try:
        circuit_breaker_health = circuit_breaker_manager.get_health_status()
        bulkhead_utilization = bulkhead_manager.get_resource_utilization()
        
        # Determine overall health
        overall_health = "healthy"
        
        # Check circuit breaker health
        if circuit_breaker_health["overall_health"] == "critical":
            overall_health = "critical"
        elif circuit_breaker_health["overall_health"] == "degraded":
            overall_health = "degraded"
        
        # Check bulkhead utilization
        if bulkhead_utilization["overall_utilization"] > 0.9:
            if overall_health == "healthy":
                overall_health = "degraded"
        elif bulkhead_utilization["overall_utilization"] > 0.95:
            overall_health = "critical"
        
        return {
            "overall_health": overall_health,
            "circuit_breakers": {
                "health": circuit_breaker_health["overall_health"],
                "healthy_services": len(circuit_breaker_health["healthy_services"]),
                "failed_services": len(circuit_breaker_health["failed_services"]),
                "health_score": circuit_breaker_health["health_score"]
            },
            "bulkheads": {
                "utilization": bulkhead_utilization["overall_utilization"],
                "active_operations": bulkhead_utilization["total_active"],
                "total_capacity": bulkhead_utilization["total_capacity"],
                "queued_operations": bulkhead_utilization["total_queued"]
            },
            "recommendations": _generate_health_recommendations(
                circuit_breaker_health,
                bulkhead_utilization
            )
        }
    except Exception as e:
        logger.error(f"Failed to get resilience health: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve resilience health status")


@router.get("/metrics", response_model=Dict[str, Any])
async def get_resilience_metrics(
    current_user = Depends(get_current_user)
):
    """
    Get comprehensive resilience metrics.
    
    Returns:
        Detailed metrics for monitoring and alerting
    """
    try:
        circuit_breaker_stats = circuit_breaker_manager.get_all_stats()
        bulkhead_stats = bulkhead_manager.get_all_stats()
        
        # Aggregate metrics
        total_requests = 0
        total_failures = 0
        total_timeouts = 0
        total_rejections = 0
        
        for stats in circuit_breaker_stats.values():
            total_requests += stats["stats"]["total_requests"]
            total_failures += stats["stats"]["failed_requests"]
            total_rejections += stats["stats"]["rejected_requests"]
        
        for stats in bulkhead_stats.values():
            total_requests += stats["stats"]["total_requests"]
            total_failures += stats["stats"]["failed_requests"]
            total_timeouts += stats["stats"]["timeout_requests"]
            total_rejections += stats["stats"]["rejected_requests"]
        
        success_rate = (
            (total_requests - total_failures) / total_requests
            if total_requests > 0 else 1.0
        )
        
        return {
            "circuit_breakers": circuit_breaker_stats,
            "bulkheads": bulkhead_stats,
            "aggregate_metrics": {
                "total_requests": total_requests,
                "total_failures": total_failures,
                "total_timeouts": total_timeouts,
                "total_rejections": total_rejections,
                "success_rate": success_rate,
                "failure_rate": total_failures / total_requests if total_requests > 0 else 0,
                "rejection_rate": total_rejections / total_requests if total_requests > 0 else 0
            }
        }
    except Exception as e:
        logger.error(f"Failed to get resilience metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve resilience metrics")


def _generate_health_recommendations(
    circuit_breaker_health: Dict[str, Any],
    bulkhead_utilization: Dict[str, Any]
) -> list[str]:
    """Generate health recommendations based on current status."""
    recommendations = []
    
    # Circuit breaker recommendations
    if circuit_breaker_health["failed_services"]:
        recommendations.append(
            f"⚠️ {len(circuit_breaker_health['failed_services'])} services have failing circuit breakers. "
            f"Check: {', '.join(circuit_breaker_health['failed_services'])}"
        )
    
    if circuit_breaker_health["degraded_services"]:
        recommendations.append(
            f"⚡ {len(circuit_breaker_health['degraded_services'])} services are in recovery mode. "
            f"Monitor: {', '.join(circuit_breaker_health['degraded_services'])}"
        )
    
    # Bulkhead recommendations
    if bulkhead_utilization["overall_utilization"] > 0.8:
        recommendations.append(
            f"📊 High resource utilization ({bulkhead_utilization['overall_utilization']:.1%}). "
            "Consider scaling or optimizing workloads."
        )
    
    high_util_resources = [
        name for name, resource in bulkhead_utilization["resources"].items()
        if resource["utilization"] > 0.9
    ]
    
    if high_util_resources:
        recommendations.append(
            f"🔥 High utilization resources: {', '.join(high_util_resources)}. "
            "Consider increasing capacity or load balancing."
        )
    
    if bulkhead_utilization["total_queued"] > 0:
        recommendations.append(
            f"⏳ {bulkhead_utilization['total_queued']} operations queued. "
            "Monitor queue lengths and processing times."
        )
    
    if not recommendations:
        recommendations.append("✅ All resilience components are healthy.")
    
    return recommendations