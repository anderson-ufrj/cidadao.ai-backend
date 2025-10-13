"""
Observability monitoring endpoints.

This module provides endpoints for monitoring distributed tracing,
metrics, correlation IDs, and overall system observability.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse

from src.api.auth import get_current_user
from src.core import get_logger
from src.infrastructure.observability import (
    CorrelationContext,
    metrics_manager,
    request_tracker,
    tracing_manager,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/observability", tags=["Observability"])


@router.get("/metrics", response_class=PlainTextResponse)
async def get_prometheus_metrics():
    """
    Get Prometheus metrics in exposition format.

    Returns metrics in Prometheus format for scraping by monitoring systems.
    """
    try:
        metrics_content = metrics_manager.generate_metrics()
        return PlainTextResponse(
            content=metrics_content,
            media_type=metrics_manager.get_metrics_content_type(),
        )
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate metrics")


@router.get("/metrics/json", response_model=dict[str, Any])
async def get_metrics_json(current_user=Depends(get_current_user)):
    """
    Get metrics in JSON format for API consumption.

    Returns detailed metrics data in JSON format for dashboards and analysis.
    """
    try:
        # Get metrics registry stats
        registry_stats = metrics_manager.get_registry_stats()

        # Get request tracking stats
        request_stats = request_tracker.get_stats()
        active_requests = request_tracker.get_active_requests()

        # Get correlation context
        correlation_info = CorrelationContext.get_all_ids()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics_registry": registry_stats,
            "request_tracking": {
                "stats": request_stats,
                "active_requests": active_requests,
                "active_count": len(active_requests),
            },
            "correlation_context": correlation_info,
            "system_info": {
                "service_name": "cidadao-ai-backend",
                "version": "1.0.0",
                "environment": "production",
            },
        }
    except Exception as e:
        logger.error(f"Failed to get metrics JSON: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@router.get("/tracing/status", response_model=dict[str, Any])
async def get_tracing_status(current_user=Depends(get_current_user)):
    """
    Get distributed tracing status and configuration.

    Returns information about the current tracing setup and health.
    """
    try:
        tracer = tracing_manager.get_tracer()

        return {
            "tracing_enabled": tracing_manager._initialized,
            "service_name": tracing_manager.config.service_name,
            "service_version": tracing_manager.config.service_version,
            "configuration": {
                "jaeger_endpoint": tracing_manager.config.jaeger_endpoint,
                "otlp_endpoint": tracing_manager.config.otlp_endpoint,
                "console_export": tracing_manager.config.enable_console_export,
                "sample_rate": tracing_manager.config.sample_rate,
            },
            "current_trace": {
                "correlation_id": CorrelationContext.get_correlation_id(),
                "span_id": CorrelationContext.get_span_id(),
            },
        }
    except Exception as e:
        logger.error(f"Failed to get tracing status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tracing status")


@router.get("/correlation/current", response_model=dict[str, Any])
async def get_current_correlation(current_user=Depends(get_current_user)):
    """
    Get current correlation context information.

    Returns all correlation IDs associated with the current request.
    """
    try:
        correlation_data = CorrelationContext.get_all_ids()

        return {
            "correlation_context": correlation_data,
            "timestamp": datetime.utcnow().isoformat(),
            "has_correlation_id": correlation_data.get("correlation_id") is not None,
            "has_request_id": correlation_data.get("request_id") is not None,
            "has_user_context": correlation_data.get("user_id") is not None,
        }
    except Exception as e:
        logger.error(f"Failed to get correlation context: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve correlation context"
        )


@router.get("/requests/active", response_model=dict[str, Any])
async def get_active_requests(current_user=Depends(get_current_user)):
    """
    Get information about currently active requests.

    Returns details about requests currently being processed.
    """
    try:
        active_requests = request_tracker.get_active_requests()
        stats = request_tracker.get_stats()

        # Calculate additional metrics
        long_running_requests = [
            req for req in active_requests if req["duration_ms"] > 5000  # > 5 seconds
        ]

        user_request_counts = {}
        for req in active_requests:
            user_id = req.get("user_id", "anonymous")
            user_request_counts[user_id] = user_request_counts.get(user_id, 0) + 1

        return {
            "active_requests": active_requests,
            "statistics": stats,
            "analysis": {
                "total_active": len(active_requests),
                "long_running_count": len(long_running_requests),
                "long_running_threshold_ms": 5000,
                "user_distribution": user_request_counts,
                "avg_active_duration_ms": (
                    sum(req["duration_ms"] for req in active_requests)
                    / len(active_requests)
                    if active_requests
                    else 0
                ),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get active requests: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve active requests"
        )


@router.get("/performance/summary", response_model=dict[str, Any])
async def get_performance_summary(
    current_user=Depends(get_current_user),
    time_window_minutes: int = Query(default=60, ge=1, le=1440),
):
    """
    Get performance summary for the specified time window.

    Args:
        time_window_minutes: Time window in minutes (1-1440)

    Returns:
        Performance metrics and analysis for the time window
    """
    try:
        # Get request stats
        request_stats = request_tracker.get_stats()
        active_requests = request_tracker.get_active_requests()

        # Calculate performance metrics
        performance_summary = {
            "time_window_minutes": time_window_minutes,
            "timestamp": datetime.utcnow().isoformat(),
            "request_metrics": {
                "total_requests": request_stats["total_requests"],
                "active_requests": request_stats["active_requests"],
                "avg_duration_ms": request_stats["avg_duration_ms"],
                "error_rate": request_stats["error_rate"],
                "requests_per_minute": (
                    request_stats["total_requests"] / time_window_minutes
                    if time_window_minutes > 0
                    else 0
                ),
            },
            "performance_analysis": {
                "healthy": request_stats["error_rate"] < 0.05
                and request_stats["avg_duration_ms"] < 2000,
                "error_rate_status": (
                    "healthy"
                    if request_stats["error_rate"] < 0.01
                    else "warning" if request_stats["error_rate"] < 0.05 else "critical"
                ),
                "latency_status": (
                    "healthy"
                    if request_stats["avg_duration_ms"] < 1000
                    else (
                        "warning"
                        if request_stats["avg_duration_ms"] < 2000
                        else "critical"
                    )
                ),
                "active_requests_status": (
                    "healthy"
                    if request_stats["active_requests"] < 10
                    else (
                        "warning"
                        if request_stats["active_requests"] < 20
                        else "critical"
                    )
                ),
            },
            "recommendations": [],
        }

        # Add recommendations based on metrics
        if request_stats["error_rate"] > 0.05:
            performance_summary["recommendations"].append(
                "High error rate detected. Check logs for recurring errors and investigate root causes."
            )

        if request_stats["avg_duration_ms"] > 2000:
            performance_summary["recommendations"].append(
                "High average response time. Consider optimizing slow endpoints and database queries."
            )

        if request_stats["active_requests"] > 20:
            performance_summary["recommendations"].append(
                "High number of concurrent requests. Consider scaling or implementing rate limiting."
            )

        if len(active_requests) > 0:
            long_running = [r for r in active_requests if r["duration_ms"] > 10000]
            if long_running:
                performance_summary["recommendations"].append(
                    f"{len(long_running)} requests running longer than 10 seconds. Investigate potential deadlocks or blocking operations."
                )

        if not performance_summary["recommendations"]:
            performance_summary["recommendations"].append(
                "System performance is within normal parameters."
            )

        return performance_summary

    except Exception as e:
        logger.error(f"Failed to get performance summary: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve performance summary"
        )


@router.get("/health/detailed", response_model=dict[str, Any])
async def get_detailed_health(current_user=Depends(get_current_user)):
    """
    Get detailed health information including observability components.

    Returns comprehensive health status of all observability systems.
    """
    try:
        # Check metrics system
        metrics_healthy = True
        metrics_error = None
        try:
            metrics_manager.get_registry_stats()
        except Exception as e:
            metrics_healthy = False
            metrics_error = str(e)

        # Check tracing system
        tracing_healthy = tracing_manager._initialized
        tracing_error = None if tracing_healthy else "Tracing not initialized"

        # Check request tracking
        tracking_healthy = True
        tracking_error = None
        try:
            request_tracker.get_stats()
        except Exception as e:
            tracking_healthy = False
            tracking_error = str(e)

        # Overall health
        overall_healthy = metrics_healthy and tracing_healthy and tracking_healthy

        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_health": "healthy" if overall_healthy else "degraded",
            "components": {
                "metrics": {
                    "healthy": metrics_healthy,
                    "error": metrics_error,
                    "details": (
                        metrics_manager.get_registry_stats()
                        if metrics_healthy
                        else None
                    ),
                },
                "tracing": {
                    "healthy": tracing_healthy,
                    "error": tracing_error,
                    "details": {
                        "initialized": tracing_manager._initialized,
                        "service_name": tracing_manager.config.service_name,
                    },
                },
                "request_tracking": {
                    "healthy": tracking_healthy,
                    "error": tracking_error,
                    "details": (
                        request_tracker.get_stats() if tracking_healthy else None
                    ),
                },
                "correlation": {
                    "healthy": True,
                    "details": CorrelationContext.get_all_ids(),
                },
            },
            "summary": {
                "healthy_components": sum(
                    [metrics_healthy, tracing_healthy, tracking_healthy]
                ),
                "total_components": 3,
                "health_score": sum(
                    [metrics_healthy, tracing_healthy, tracking_healthy]
                )
                / 3,
            },
        }

        return health_status

    except Exception as e:
        logger.error(f"Failed to get detailed health: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve health information"
        )


@router.post("/tracing/sample-trace", response_model=dict[str, Any])
async def create_sample_trace(
    operation_name: str = Query(default="test_operation"),
    duration_ms: int = Query(default=100, ge=1, le=10000),
    current_user=Depends(get_current_user),
):
    """
    Create a sample trace for testing tracing infrastructure.

    Args:
        operation_name: Name of the test operation
        duration_ms: Simulated operation duration

    Returns:
        Trace information and status
    """
    try:
        import asyncio

        from src.infrastructure.observability import TraceContext, trace_operation

        async with trace_operation(
            f"test.{operation_name}",
            attributes={
                "test.user_id": current_user["sub"],
                "test.duration_ms": duration_ms,
                "test.timestamp": datetime.utcnow().isoformat(),
            },
        ) as span:
            # Set user context
            TraceContext.set_user_context(current_user["sub"])

            # Add events
            TraceContext.add_event("test.started", {"operation": operation_name})

            # Simulate work
            await asyncio.sleep(duration_ms / 1000.0)

            TraceContext.add_event("test.completed", {"success": True})

            # Get trace information
            correlation_id = CorrelationContext.get_correlation_id()
            span_id = CorrelationContext.get_span_id()

            return {
                "trace_created": True,
                "operation_name": operation_name,
                "simulated_duration_ms": duration_ms,
                "correlation_id": correlation_id,
                "span_id": span_id,
                "trace_context": CorrelationContext.get_all_ids(),
                "timestamp": datetime.utcnow().isoformat(),
            }

    except Exception as e:
        logger.error(f"Failed to create sample trace: {e}")
        raise HTTPException(status_code=500, detail="Failed to create sample trace")


@router.get("/debug/context", response_model=dict[str, Any])
async def get_debug_context():
    """
    Get debug information about current execution context.

    Returns detailed information about the current request context
    for debugging observability issues.
    """
    try:
        import os
        import threading

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_context": CorrelationContext.get_all_ids(),
            "thread_info": {
                "thread_id": threading.get_ident(),
                "thread_name": threading.current_thread().name,
                "active_thread_count": threading.active_count(),
            },
            "process_info": {
                "process_id": os.getpid(),
                "process_name": "cidadao-ai-backend",
            },
            "observability_status": {
                "metrics_initialized": hasattr(metrics_manager, "_metrics"),
                "tracing_initialized": tracing_manager._initialized,
                "request_tracker_active": len(request_tracker.active_requests) > 0,
            },
        }

    except Exception as e:
        logger.error(f"Failed to get debug context: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve debug context")
