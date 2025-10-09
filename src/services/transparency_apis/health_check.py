"""
Health Check System for Transparency APIs

Provides comprehensive health monitoring for all Brazilian transparency APIs.
Tracks API availability, response times, error rates, and generates reports.

Author: Anderson Henrique da Silva
Created: 2025-10-09 15:20:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from .registry import registry
from .cache import get_cache


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheckResult:
    """
    Result of a health check for a single API.
    """

    def __init__(
        self,
        api_name: str,
        status: HealthStatus,
        response_time: float,
        error: Optional[str] = None
    ):
        """
        Initialize health check result.

        Args:
            api_name: Name of the API
            status: Health status
            response_time: Response time in seconds
            error: Error message if failed
        """
        self.api_name = api_name
        self.status = status
        self.response_time = response_time
        self.error = error
        self.checked_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "api_name": self.api_name,
            "status": self.status.value,
            "response_time_ms": round(self.response_time * 1000, 2),
            "error": self.error,
            "checked_at": self.checked_at.isoformat()
        }


class HealthMonitor:
    """
    Monitor health status of all transparency APIs.

    Provides methods to check API health, track metrics over time,
    and generate health reports.
    """

    def __init__(self):
        """Initialize health monitor."""
        self.cache = get_cache()
        self._history: Dict[str, List[HealthCheckResult]] = {}
        self._max_history_per_api = 100

    async def check_api(self, api_key: str) -> HealthCheckResult:
        """
        Check health of a single API.

        Args:
            api_key: API key (e.g., "PE-tce", "RO-state")

        Returns:
            Health check result
        """
        # Check cache first
        cached_result = self.cache.get_health_check(api_key)
        if cached_result is not None:
            return HealthCheckResult(
                api_name=api_key,
                status=HealthStatus.HEALTHY if cached_result else HealthStatus.UNHEALTHY,
                response_time=0.0
            )

        # Get API client
        client = registry.get_client(api_key)
        if client is None:
            return HealthCheckResult(
                api_name=api_key,
                status=HealthStatus.UNKNOWN,
                response_time=0.0,
                error="API client not found"
            )

        # Perform health check
        start_time = datetime.utcnow()
        try:
            is_healthy = await client.test_connection()
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()

            # Cache result
            self.cache.set_health_check(api_key, is_healthy)

            status = HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY

            result = HealthCheckResult(
                api_name=api_key,
                status=status,
                response_time=response_time
            )

        except Exception as e:
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()

            result = HealthCheckResult(
                api_name=api_key,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                error=str(e)
            )

        # Store in history
        if api_key not in self._history:
            self._history[api_key] = []

        self._history[api_key].append(result)

        # Limit history size
        if len(self._history[api_key]) > self._max_history_per_api:
            self._history[api_key].pop(0)

        return result

    async def check_all_apis(self) -> Dict[str, HealthCheckResult]:
        """
        Check health of all registered APIs.

        Returns:
            Dictionary of API keys to health check results
        """
        api_keys = registry.list_available_apis()

        # Run checks in parallel
        tasks = [self.check_api(api_key) for api_key in api_keys]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            api_keys[i]: (
                results[i] if not isinstance(results[i], Exception)
                else HealthCheckResult(
                    api_name=api_keys[i],
                    status=HealthStatus.UNHEALTHY,
                    response_time=0.0,
                    error=str(results[i])
                )
            )
            for i in range(len(api_keys))
        }

    def get_api_stats(self, api_key: str) -> Dict[str, Any]:
        """
        Get statistics for a specific API.

        Args:
            api_key: API key

        Returns:
            Statistics dictionary
        """
        history = self._history.get(api_key, [])

        if not history:
            return {
                "api_name": api_key,
                "checks_performed": 0,
                "status": "unknown"
            }

        # Calculate stats from history
        total_checks = len(history)
        healthy_checks = sum(1 for r in history if r.status == HealthStatus.HEALTHY)
        response_times = [r.response_time for r in history]

        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0

        uptime_percentage = (healthy_checks / total_checks * 100) if total_checks > 0 else 0

        # Get recent status (last check)
        last_check = history[-1]

        return {
            "api_name": api_key,
            "current_status": last_check.status.value,
            "last_checked": last_check.checked_at.isoformat(),
            "checks_performed": total_checks,
            "uptime_percentage": round(uptime_percentage, 2),
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "min_response_time_ms": round(min_response_time * 1000, 2),
            "max_response_time_ms": round(max_response_time * 1000, 2),
            "last_error": last_check.error
        }

    async def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive health report for all APIs.

        Returns:
            Health report dictionary
        """
        # Check all APIs
        check_results = await self.check_all_apis()

        # Categorize by status
        healthy_apis = []
        degraded_apis = []
        unhealthy_apis = []
        unknown_apis = []

        for api_key, result in check_results.items():
            if result.status == HealthStatus.HEALTHY:
                healthy_apis.append(api_key)
            elif result.status == HealthStatus.DEGRADED:
                degraded_apis.append(api_key)
            elif result.status == HealthStatus.UNHEALTHY:
                unhealthy_apis.append(api_key)
            else:
                unknown_apis.append(api_key)

        total_apis = len(check_results)
        overall_health_percentage = (
            len(healthy_apis) / total_apis * 100 if total_apis > 0 else 0
        )

        # Determine overall status
        if overall_health_percentage >= 90:
            overall_status = HealthStatus.HEALTHY
        elif overall_health_percentage >= 70:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNHEALTHY

        # Get detailed stats for each API
        api_details = {
            api_key: self.get_api_stats(api_key)
            for api_key in check_results.keys()
        }

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": overall_status.value,
            "overall_health_percentage": round(overall_health_percentage, 2),
            "summary": {
                "total_apis": total_apis,
                "healthy": len(healthy_apis),
                "degraded": len(degraded_apis),
                "unhealthy": len(unhealthy_apis),
                "unknown": len(unknown_apis)
            },
            "apis": {
                "healthy": healthy_apis,
                "degraded": degraded_apis,
                "unhealthy": unhealthy_apis,
                "unknown": unknown_apis
            },
            "details": api_details
        }

    def get_history(
        self,
        api_key: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get health check history.

        Args:
            api_key: Specific API key (None for all)
            hours: Number of hours to look back

        Returns:
            History dictionary
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        if api_key:
            history = self._history.get(api_key, [])
            filtered = [
                r.to_dict() for r in history
                if r.checked_at >= cutoff_time
            ]
            return {api_key: filtered}

        # Return all histories
        result = {}
        for key, history in self._history.items():
            filtered = [
                r.to_dict() for r in history
                if r.checked_at >= cutoff_time
            ]
            if filtered:
                result[key] = filtered

        return result

    def clear_history(self, api_key: Optional[str] = None) -> None:
        """
        Clear health check history.

        Args:
            api_key: Specific API key (None for all)
        """
        if api_key:
            if api_key in self._history:
                self._history[api_key] = []
        else:
            self._history.clear()


# Global health monitor instance
_global_monitor: Optional[HealthMonitor] = None


def get_health_monitor() -> HealthMonitor:
    """
    Get global health monitor instance (singleton pattern).

    Returns:
        Global HealthMonitor instance
    """
    global _global_monitor

    if _global_monitor is None:
        _global_monitor = HealthMonitor()

    return _global_monitor
