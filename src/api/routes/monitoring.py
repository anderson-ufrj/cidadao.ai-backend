"""
Advanced monitoring endpoints for health checks and SLA/SLO tracking.

This module provides comprehensive monitoring capabilities including
dependency health checks, SLO compliance, and alerting.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel

from src.core import get_logger
from src.api.auth import get_current_user
from src.infrastructure.health.dependency_checker import health_manager, HealthStatus
from src.infrastructure.monitoring.slo_monitor import (
    slo_monitor,
    SLOTarget,
    SLOType,
    TimeWindow,
    record_api_request,
    record_investigation_result,
    record_agent_task,
    record_database_query
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring"])


# Request models
class SLOTargetRequest(BaseModel):
    """Request model for creating SLO targets."""
    name: str
    slo_type: str
    target_value: float
    time_window: str
    description: str
    warning_threshold: float = 95.0
    critical_threshold: float = 90.0


class MetricRecordRequest(BaseModel):
    """Request model for recording metrics."""
    slo_name: str
    value: float
    success: bool = True
    metadata: Optional[Dict[str, Any]] = None


# Health Check Endpoints
@router.get("/health", response_model=Dict[str, Any])
async def get_health_status():
    """
    Get overall system health status.
    
    Returns basic health information without authentication
    for load balancer health checks.
    """
    try:
        # Run health checks
        results = await health_manager.check_all(parallel=True)
        overall_status = health_manager.get_overall_status(results)
        
        # Basic response for load balancers
        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "healthy": overall_status == HealthStatus.HEALTHY
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "healthy": False,
            "error": "Health check system failure"
        }


@router.get("/health/detailed", response_model=Dict[str, Any])
async def get_detailed_health_status(
    current_user = Depends(get_current_user),
    run_checks: bool = Query(default=True, description="Whether to run fresh health checks")
):
    """
    Get detailed health status including all dependencies.
    
    Args:
        run_checks: Whether to run fresh health checks or use cached results
        
    Returns:
        Comprehensive health report with dependency details
    """
    try:
        if run_checks:
            results = await health_manager.check_all(parallel=True)
        else:
            results = health_manager.last_check_results
        
        health_report = health_manager.get_health_report()
        
        return {
            **health_report,
            "fresh_check": run_checks,
            "check_duration_ms": sum(
                result.response_time_ms for result in results.values()
            ) if run_checks else 0
        }
    
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve health status")


@router.get("/health/dependencies/{dependency_name}", response_model=Dict[str, Any])
async def get_dependency_health(
    dependency_name: str,
    hours: int = Query(default=24, ge=1, le=168, description="Hours of history to analyze"),
    current_user = Depends(get_current_user)
):
    """
    Get health information for a specific dependency.
    
    Args:
        dependency_name: Name of the dependency
        hours: Hours of history to analyze (1-168)
        
    Returns:
        Detailed dependency health information and trends
    """
    try:
        # Get current status
        if dependency_name in health_manager.last_check_results:
            current_status = health_manager.last_check_results[dependency_name]
        else:
            raise HTTPException(status_code=404, detail=f"Dependency '{dependency_name}' not found")
        
        # Get trends
        trends = health_manager.get_dependency_trends(dependency_name, hours)
        
        return {
            "dependency_name": dependency_name,
            "current_status": current_status.to_dict(),
            "trends": trends,
            "analysis_window_hours": hours
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dependency health for {dependency_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dependency health")


@router.post("/health/check", response_model=Dict[str, Any])
async def trigger_health_check(
    dependency_name: Optional[str] = Query(default=None, description="Specific dependency to check"),
    current_user = Depends(get_current_user)
):
    """
    Trigger a health check for all dependencies or a specific one.
    
    Args:
        dependency_name: Optional specific dependency to check
        
    Returns:
        Health check results
    """
    try:
        if dependency_name:
            # Check specific dependency
            health_check = None
            for check in health_manager.health_checks:
                if check.name == dependency_name:
                    health_check = check
                    break
            
            if not health_check:
                raise HTTPException(status_code=404, detail=f"Dependency '{dependency_name}' not found")
            
            result = await health_check.check()
            return {
                "dependency_name": dependency_name,
                "result": result.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            # Check all dependencies
            results = await health_manager.check_all(parallel=True)
            overall_status = health_manager.get_overall_status(results)
            
            return {
                "overall_status": overall_status.value,
                "results": {name: result.to_dict() for name, result in results.items()},
                "timestamp": datetime.utcnow().isoformat()
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger health check: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger health check")


# SLO Monitoring Endpoints
@router.get("/slo", response_model=Dict[str, Any])
async def get_slo_status(
    current_user = Depends(get_current_user)
):
    """
    Get status of all SLA/SLO targets.
    
    Returns:
        Comprehensive SLO compliance report
    """
    try:
        slo_status = slo_monitor.get_all_slo_status()
        return slo_status
    
    except Exception as e:
        logger.error(f"Failed to get SLO status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve SLO status")


@router.get("/slo/{slo_name}", response_model=Dict[str, Any])
async def get_specific_slo_status(
    slo_name: str,
    current_user = Depends(get_current_user)
):
    """
    Get status of a specific SLO.
    
    Args:
        slo_name: Name of the SLO
        
    Returns:
        Detailed SLO status information
    """
    try:
        slo_status = slo_monitor.get_slo_status(slo_name)
        
        if "error" in slo_status:
            raise HTTPException(status_code=404, detail=slo_status["error"])
        
        return slo_status
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get SLO status for {slo_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve SLO status")


@router.post("/slo", response_model=Dict[str, Any])
async def create_slo_target(
    request: SLOTargetRequest,
    current_user = Depends(get_current_user)
):
    """
    Create a new SLO target.
    
    Args:
        request: SLO target configuration
        
    Returns:
        Created SLO target information
    """
    try:
        # Validate enums
        try:
            slo_type = SLOType(request.slo_type)
            time_window = TimeWindow(request.time_window)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")
        
        # Create SLO target
        slo_target = SLOTarget(
            name=request.name,
            slo_type=slo_type,
            target_value=request.target_value,
            time_window=time_window,
            description=request.description,
            warning_threshold=request.warning_threshold,
            critical_threshold=request.critical_threshold
        )
        
        # Register with monitor
        slo_monitor.register_slo(slo_target)
        
        return {
            "message": f"SLO target '{request.name}' created successfully",
            "slo_target": {
                "name": slo_target.name,
                "slo_type": slo_target.slo_type.value,
                "target_value": slo_target.target_value,
                "time_window": slo_target.time_window.value,
                "description": slo_target.description
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create SLO target: {e}")
        raise HTTPException(status_code=500, detail="Failed to create SLO target")


@router.post("/slo/metric", response_model=Dict[str, Any])
async def record_slo_metric(
    request: MetricRecordRequest,
    current_user = Depends(get_current_user)
):
    """
    Record a metric for SLO monitoring.
    
    Args:
        request: Metric data to record
        
    Returns:
        Confirmation of metric recording
    """
    try:
        slo_monitor.record_metric(
            slo_name=request.slo_name,
            value=request.value,
            success=request.success,
            metadata=request.metadata
        )
        
        return {
            "message": f"Metric recorded for SLO '{request.slo_name}'",
            "timestamp": datetime.utcnow().isoformat(),
            "value": request.value,
            "success": request.success
        }
    
    except Exception as e:
        logger.error(f"Failed to record SLO metric: {e}")
        raise HTTPException(status_code=500, detail="Failed to record SLO metric")


@router.get("/slo/error-budget", response_model=Dict[str, Any])
async def get_error_budget_report(
    current_user = Depends(get_current_user)
):
    """
    Get error budget consumption report for all SLOs.
    
    Returns:
        Error budget analysis for all monitored SLOs
    """
    try:
        error_budget_report = slo_monitor.get_error_budget_report()
        return error_budget_report
    
    except Exception as e:
        logger.error(f"Failed to get error budget report: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve error budget report")


@router.get("/alerts/violations", response_model=Dict[str, Any])
async def get_slo_violations(
    hours: int = Query(default=24, ge=1, le=168, description="Hours of violations to retrieve"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    current_user = Depends(get_current_user)
):
    """
    Get SLO violations for the specified time period.
    
    Args:
        hours: Hours of violations to retrieve (1-168)
        severity: Optional severity filter
        
    Returns:
        List of SLO violations with details
    """
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        all_violations = []
        
        for slo_name, violations in slo_monitor.violations.items():
            for violation in violations:
                if violation.violation_time > cutoff_time:
                    if severity is None or violation.severity.value == severity:
                        all_violations.append({
                            "slo_name": slo_name,
                            "violation_time": violation.violation_time.isoformat(),
                            "severity": violation.severity.value,
                            "actual_value": violation.actual_value,
                            "target_value": violation.target_value,
                            "duration_minutes": violation.duration_minutes,
                            "details": violation.details
                        })
        
        # Sort by violation time (most recent first)
        all_violations.sort(key=lambda x: x["violation_time"], reverse=True)
        
        return {
            "time_window_hours": hours,
            "severity_filter": severity,
            "total_violations": len(all_violations),
            "violations": all_violations
        }
    
    except Exception as e:
        logger.error(f"Failed to get SLO violations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve SLO violations")


# Performance testing endpoints
@router.post("/test/api-performance", response_model=Dict[str, Any])
async def test_api_performance(
    endpoint: str = Query(description="Endpoint to test"),
    requests_count: int = Query(default=10, ge=1, le=100, description="Number of requests to send"),
    current_user = Depends(get_current_user)
):
    """
    Test API performance and record metrics for SLO monitoring.
    
    Args:
        endpoint: API endpoint to test
        requests_count: Number of test requests to send
        
    Returns:
        Performance test results
    """
    try:
        import httpx
        import asyncio
        import time
        
        results = []
        
        async with httpx.AsyncClient() as client:
            # Send test requests
            tasks = []
            for i in range(requests_count):
                task = asyncio.create_task(
                    client.get(f"http://localhost:8000{endpoint}")
                )
                tasks.append(task)
            
            # Execute all requests
            start_time = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # Process results
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    results.append({
                        "request_id": i + 1,
                        "success": False,
                        "error": str(response),
                        "response_time_ms": 0
                    })
                    # Record failure
                    record_api_request(endpoint, 0, False)
                else:
                    response_time_ms = total_time / requests_count * 1000  # Approximate
                    results.append({
                        "request_id": i + 1,
                        "success": True,
                        "status_code": response.status_code,
                        "response_time_ms": response_time_ms
                    })
                    # Record success
                    record_api_request(endpoint, response_time_ms, response.status_code < 400)
        
        # Calculate statistics
        successful_requests = sum(1 for r in results if r["success"])
        avg_response_time = sum(r["response_time_ms"] for r in results if r["success"]) / successful_requests if successful_requests > 0 else 0
        
        return {
            "endpoint": endpoint,
            "total_requests": requests_count,
            "successful_requests": successful_requests,
            "failed_requests": requests_count - successful_requests,
            "success_rate": (successful_requests / requests_count) * 100,
            "avg_response_time_ms": avg_response_time,
            "total_duration_ms": total_time * 1000,
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Failed to test API performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to test API performance")


@router.get("/dashboard/summary", response_model=Dict[str, Any])
async def get_monitoring_dashboard_summary(
    current_user = Depends(get_current_user)
):
    """
    Get summary data for monitoring dashboard.
    
    Returns:
        Comprehensive monitoring summary for dashboard display
    """
    try:
        # Get health status
        health_results = await health_manager.check_all(parallel=True)
        overall_health = health_manager.get_overall_status(health_results)
        
        # Get SLO status
        slo_status = slo_monitor.get_all_slo_status()
        
        # Get error budget report
        error_budget = slo_monitor.get_error_budget_report()
        
        # Get recent violations
        recent_violations = []
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        for slo_name, violations in slo_monitor.violations.items():
            for violation in violations:
                if violation.violation_time > cutoff_time:
                    recent_violations.append({
                        "slo_name": slo_name,
                        "severity": violation.severity.value,
                        "violation_time": violation.violation_time.isoformat()
                    })
        
        # Calculate key metrics
        total_dependencies = len(health_results)
        healthy_dependencies = sum(
            1 for result in health_results.values()
            if result.status == HealthStatus.HEALTHY
        )
        
        dependency_health_score = (healthy_dependencies / total_dependencies * 100) if total_dependencies > 0 else 100
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": {
                "overall_status": overall_health.value,
                "dependency_health_score": dependency_health_score,
                "total_dependencies": total_dependencies,
                "healthy_dependencies": healthy_dependencies,
                "unhealthy_dependencies": total_dependencies - healthy_dependencies
            },
            "slo_compliance": {
                "overall_compliance": slo_status["overall_compliance_percentage"],
                "total_slos": slo_status["total_slos"],
                "compliant_slos": slo_status["compliant_slos"],
                "violated_slos": slo_status["violated_slos"]
            },
            "error_budgets": {
                "budgets_count": len(error_budget["error_budgets"]),
                "critical_budgets": sum(
                    1 for budget in error_budget["error_budgets"].values()
                    if budget["status"] == "critical"
                ),
                "warning_budgets": sum(
                    1 for budget in error_budget["error_budgets"].values()
                    if budget["status"] == "warning"
                )
            },
            "recent_alerts": {
                "count": len(recent_violations),
                "critical_count": sum(
                    1 for v in recent_violations
                    if v["severity"] == "critical"
                ),
                "violations": recent_violations[:5]  # Latest 5
            },
            "performance_indicators": {
                "avg_health_check_time": sum(
                    result.response_time_ms for result in health_results.values()
                ) / len(health_results) if health_results else 0,
                "monitoring_stats": slo_monitor.stats
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to get monitoring dashboard summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve monitoring summary")