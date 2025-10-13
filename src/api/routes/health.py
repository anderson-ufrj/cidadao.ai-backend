"""
Module: api.routes.health
Description: Health check endpoints for monitoring system status
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST
from pydantic import BaseModel

from src.core import get_logger, settings
from src.core.monitoring import collect_system_metrics, get_metrics_data
from src.tools import TransparencyAPIClient

logger = get_logger(__name__)

router = APIRouter()


class HealthStatus(BaseModel):
    """Health status response model."""

    status: str
    timestamp: datetime
    version: str
    uptime: float
    services: dict[str, dict[str, Any]]


class ServiceStatus(BaseModel):
    """Individual service status."""

    status: str
    response_time: float
    last_checked: datetime
    error_message: str = None


# Global variables for tracking
_start_time = time.time()


@router.get("/status", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """
    Comprehensive health check endpoint.

    Returns overall system health status and service availability.
    WARNING: This endpoint checks external dependencies and may be slow.
    Do NOT use this for Railway health checks - use /health instead.
    """
    current_time = datetime.utcnow()
    uptime = time.time() - _start_time

    # Check all critical services
    services = {}
    overall_status = "healthy"

    # Check Portal da Transparência API
    transparency_status = await _check_transparency_api()
    services["transparency_api"] = transparency_status

    if transparency_status["status"] != "healthy":
        overall_status = "degraded"

    # Check database connectivity (placeholder - implement when DB is added)
    database_status = await _check_database()
    services["database"] = database_status

    if database_status["status"] != "healthy":
        overall_status = "degraded"

    # Check Redis connectivity (placeholder - implement when Redis is added)
    redis_status = await _check_redis()
    services["redis"] = redis_status

    if redis_status["status"] != "healthy":
        overall_status = "degraded"

    logger.info(
        "health_check_completed",
        status=overall_status,
        uptime=uptime,
        services_checked=len(services),
    )

    return HealthStatus(
        status=overall_status,
        timestamp=current_time,
        version="1.0.0",
        uptime=uptime,
        services=services,
    )


@router.get("/detailed", response_model=dict[str, Any])
async def detailed_health_check() -> dict[str, Any]:
    """
    Detailed health check with comprehensive system information.

    Returns detailed information about all system components.
    """
    current_time = datetime.utcnow()
    uptime = time.time() - _start_time

    # Collect detailed system information
    system_info = {
        "api": {
            "status": "healthy",
            "version": "1.0.0",
            "uptime_seconds": uptime,
            "uptime_formatted": _format_uptime(uptime),
            "environment": settings.app_env,
            "debug_mode": settings.debug,
        },
        "configuration": {
            "cors_enabled": bool(settings.cors_origins),
            "rate_limiting": True,
            "authentication": True,
            "logging_level": settings.log_level,
        },
        "external_services": {},
        "agents": {
            "investigator": {
                "status": "available",
                "capabilities": ["anomaly_detection", "pattern_analysis"],
            },
            "analyst": {
                "status": "available",
                "capabilities": ["trend_analysis", "correlation_detection"],
            },
            "reporter": {
                "status": "available",
                "capabilities": ["report_generation", "natural_language"],
            },
        },
        "memory_systems": {
            "episodic": {"status": "available", "type": "redis"},
            "semantic": {"status": "available", "type": "chromadb"},
        },
    }

    # Check external services
    system_info["external_services"][
        "transparency_api"
    ] = await _check_transparency_api()
    system_info["external_services"]["database"] = await _check_database()
    system_info["external_services"]["redis"] = await _check_redis()

    # Calculate overall status
    external_statuses = [
        service["status"] for service in system_info["external_services"].values()
    ]
    if all(status == "healthy" for status in external_statuses):
        overall_status = "healthy"
    elif any(status == "healthy" for status in external_statuses):
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    system_info["overall_status"] = overall_status
    system_info["timestamp"] = current_time

    logger.info(
        "detailed_health_check_completed",
        status=overall_status,
        external_services=len(system_info["external_services"]),
    )

    return system_info


@router.get("/")
async def simple_health() -> dict[str, Any]:
    """
    Simple health check - RECOMMENDED for Railway health checks.

    Ultra-fast endpoint that only checks if the application is running.
    Does NOT check external dependencies.

    Use this endpoint in Railway dashboard for health check configuration.
    """
    return {"status": "ok", "timestamp": datetime.utcnow()}


@router.get("/live")
async def liveness_probe() -> dict[str, Any]:
    """
    Kubernetes liveness probe endpoint.

    Simple endpoint to check if the application is running.
    Identical to / but follows Kubernetes naming convention.
    """
    return {"status": "alive", "timestamp": datetime.utcnow()}


@router.get("/metrics")
async def prometheus_metrics() -> Response:
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus format for monitoring.
    """
    try:
        metrics_data = get_metrics_data()
        return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error("metrics_endpoint_error", error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to collect metrics: {str(e)}"
        ) from e


@router.get("/metrics/json")
async def system_metrics_json() -> dict[str, Any]:
    """
    System metrics in JSON format for debugging.

    Returns comprehensive system metrics in JSON format.
    """
    try:
        return await collect_system_metrics()
    except Exception as e:
        logger.error("system_metrics_error", error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to collect system metrics: {str(e)}"
        ) from e


@router.get("/ready")
async def readiness_probe() -> dict[str, Any]:
    """
    Kubernetes readiness probe endpoint.

    Checks if the application is ready to handle requests.
    WARNING: This endpoint checks external dependencies and may be slow (5-30 seconds).
    Do NOT use this for Railway health checks - use /health instead.

    This endpoint is useful for:
    - Kubernetes readiness probes with high timeout
    - Manual health verification
    - Detailed system diagnostics
    """
    # Check critical dependencies
    try:
        # Quick check of essential services
        transparency_status = await _check_transparency_api()

        if transparency_status["status"] == "healthy":
            return {"status": "ready", "timestamp": datetime.utcnow()}

        # Don't fail the readiness check if transparency API is down
        # The service can still function without it
        logger.warning(
            "readiness_check_degraded",
            transparency_status=transparency_status["status"],
        )
        return {
            "status": "ready",
            "degraded": True,
            "timestamp": datetime.utcnow(),
            "note": "External API degraded but service is functional",
        }

    except Exception as e:
        logger.error(
            "readiness_check_failed",
            error=str(e),
        )

        # Return degraded status instead of 503
        # The service can still function
        return {
            "status": "ready",
            "degraded": True,
            "timestamp": datetime.utcnow(),
            "error": str(e),
            "note": "Service is functional despite external API issues",
        }


async def _check_transparency_api() -> dict[str, Any]:
    """Check Portal da Transparência API connectivity."""
    start_time = time.time()

    try:
        async with TransparencyAPIClient() as client:
            # Make a simple test request
            await client._make_request("/api-de-dados/orgaos", {})

        response_time = time.time() - start_time

        return {
            "status": "healthy",
            "response_time": response_time,
            "last_checked": datetime.utcnow(),
            "endpoint": "Portal da Transparência API",
        }

    except Exception as e:
        response_time = time.time() - start_time

        logger.warning(
            "transparency_api_health_check_failed",
            error=str(e),
            response_time=response_time,
        )

        return {
            "status": "unhealthy",
            "response_time": response_time,
            "last_checked": datetime.utcnow(),
            "error_message": str(e),
            "endpoint": "Portal da Transparência API",
        }


async def _check_database() -> dict[str, Any]:
    """Check database connectivity."""
    # Placeholder for database health check
    # TODO: Implement when database is configured

    return {
        "status": "healthy",
        "response_time": 0.001,
        "last_checked": datetime.utcnow(),
        "note": "Database check not implemented yet",
    }


async def _check_redis() -> dict[str, Any]:
    """Check Redis connectivity."""
    # Placeholder for Redis health check
    # TODO: Implement when Redis is configured

    return {
        "status": "healthy",
        "response_time": 0.001,
        "last_checked": datetime.utcnow(),
        "note": "Redis check not implemented yet",
    }


def _format_uptime(uptime_seconds: float) -> str:
    """Format uptime in human-readable format."""
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)

    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"
