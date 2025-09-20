"""
Comprehensive health check system with dependency monitoring.

This module provides advanced health checking capabilities for all
system dependencies and components.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json

import httpx
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_logger, settings
from src.infrastructure.observability import BusinessMetrics, get_structured_logger

logger = get_structured_logger(__name__, component="health_checker")


class HealthStatus(str, Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class DependencyType(str, Enum):
    """Types of dependencies."""
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    MESSAGE_QUEUE = "message_queue"
    FILE_SYSTEM = "file_system"
    LLM_SERVICE = "llm_service"
    INTERNAL_SERVICE = "internal_service"


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""
    name: str
    status: HealthStatus
    dependency_type: DependencyType
    response_time_ms: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "dependency_type": self.dependency_type.value,
            "response_time_ms": self.response_time_ms,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error
        }


class HealthCheckConfig:
    """Configuration for health checks."""
    
    def __init__(
        self,
        timeout_seconds: float = 5.0,
        warning_threshold_ms: float = 1000.0,
        critical_threshold_ms: float = 3000.0,
        max_retries: int = 2,
        retry_delay_seconds: float = 0.5
    ):
        self.timeout_seconds = timeout_seconds
        self.warning_threshold_ms = warning_threshold_ms
        self.critical_threshold_ms = critical_threshold_ms
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds


class BaseHealthCheck:
    """Base class for health checks."""
    
    def __init__(
        self,
        name: str,
        dependency_type: DependencyType,
        config: Optional[HealthCheckConfig] = None
    ):
        self.name = name
        self.dependency_type = dependency_type
        self.config = config or HealthCheckConfig()
        self.logger = get_structured_logger(f"health.{name}")
    
    async def check(self) -> HealthCheckResult:
        """Perform health check with retries."""
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                start_time = time.time()
                
                # Perform the actual health check
                result = await asyncio.wait_for(
                    self._perform_check(),
                    timeout=self.config.timeout_seconds
                )
                
                response_time_ms = (time.time() - start_time) * 1000
                
                # Determine status based on response time
                if response_time_ms > self.config.critical_threshold_ms:
                    status = HealthStatus.UNHEALTHY
                    message = f"Response time {response_time_ms:.2f}ms exceeds critical threshold"
                elif response_time_ms > self.config.warning_threshold_ms:
                    status = HealthStatus.DEGRADED
                    message = f"Response time {response_time_ms:.2f}ms exceeds warning threshold"
                else:
                    status = HealthStatus.HEALTHY
                    message = "Dependency is healthy"
                
                # Override status if check returned specific status
                if hasattr(result, 'status'):
                    status = result.status
                    message = result.get('message', message)
                
                health_result = HealthCheckResult(
                    name=self.name,
                    status=status,
                    dependency_type=self.dependency_type,
                    response_time_ms=response_time_ms,
                    message=message,
                    details=result if isinstance(result, dict) else {}
                )
                
                # Log the result
                self.logger.info(
                    f"Health check passed: {self.name}",
                    operation="health_check",
                    duration_ms=response_time_ms,
                    status=status.value,
                    attempt=attempt + 1
                )
                
                return health_result
                
            except asyncio.TimeoutError:
                last_error = f"Health check timed out after {self.config.timeout_seconds}s"
                self.logger.warning(
                    f"Health check timeout: {self.name}",
                    operation="health_check",
                    timeout_seconds=self.config.timeout_seconds,
                    attempt=attempt + 1
                )
                
            except Exception as e:
                last_error = str(e)
                self.logger.error(
                    f"Health check failed: {self.name}",
                    operation="health_check",
                    error=e,
                    attempt=attempt + 1
                )
            
            # Wait before retry
            if attempt < self.config.max_retries:
                await asyncio.sleep(self.config.retry_delay_seconds)
        
        # All attempts failed
        return HealthCheckResult(
            name=self.name,
            status=HealthStatus.UNHEALTHY,
            dependency_type=self.dependency_type,
            response_time_ms=self.config.timeout_seconds * 1000,
            message=f"Health check failed after {self.config.max_retries + 1} attempts",
            error=last_error
        )
    
    async def _perform_check(self) -> Union[Dict[str, Any], bool]:
        """Override this method to implement specific health check logic."""
        raise NotImplementedError("Subclasses must implement _perform_check")


class DatabaseHealthCheck(BaseHealthCheck):
    """Health check for database connectivity."""
    
    def __init__(self, session_factory: Callable, config: Optional[HealthCheckConfig] = None):
        super().__init__("database", DependencyType.DATABASE, config)
        self.session_factory = session_factory
    
    async def _perform_check(self) -> Dict[str, Any]:
        """Check database connectivity and basic operations."""
        async with self.session_factory() as session:
            # Test basic connectivity
            result = await session.execute(text("SELECT 1"))
            row = result.fetchone()
            
            if row[0] != 1:
                raise Exception("Database query returned unexpected result")
            
            # Get database stats
            stats_result = await session.execute(text("""
                SELECT 
                    count(*) as active_connections,
                    (SELECT setting FROM pg_settings WHERE name = 'max_connections') as max_connections
                FROM pg_stat_activity 
                WHERE state = 'active'
            """))
            
            stats = stats_result.fetchone()
            
            return {
                "connection_status": "active",
                "active_connections": stats[0],
                "max_connections": int(stats[1]),
                "utilization": stats[0] / int(stats[1]) if stats[1] else 0
            }


class RedisHealthCheck(BaseHealthCheck):
    """Health check for Redis connectivity."""
    
    def __init__(self, redis_url: str, config: Optional[HealthCheckConfig] = None):
        super().__init__("redis", DependencyType.CACHE, config)
        self.redis_url = redis_url
    
    async def _perform_check(self) -> Dict[str, Any]:
        """Check Redis connectivity and basic operations."""
        redis_client = redis.from_url(self.redis_url)
        
        try:
            # Test basic operations
            test_key = "health_check_test"
            test_value = f"test_{int(time.time())}"
            
            # Set and get test value
            await redis_client.set(test_key, test_value, ex=60)
            retrieved_value = await redis_client.get(test_key)
            
            if retrieved_value.decode() != test_value:
                raise Exception("Redis get/set test failed")
            
            # Clean up test key
            await redis_client.delete(test_key)
            
            # Get Redis info
            info = await redis_client.info()
            
            return {
                "connection_status": "active",
                "version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "operations_per_sec": info.get("instantaneous_ops_per_sec", 0)
            }
        
        finally:
            await redis_client.close()


class ExternalAPIHealthCheck(BaseHealthCheck):
    """Health check for external APIs."""
    
    def __init__(
        self,
        name: str,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200,
        config: Optional[HealthCheckConfig] = None
    ):
        super().__init__(name, DependencyType.EXTERNAL_API, config)
        self.url = url
        self.method = method.upper()
        self.headers = headers or {}
        self.expected_status = expected_status
    
    async def _perform_check(self) -> Dict[str, Any]:
        """Check external API availability."""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                self.method,
                self.url,
                headers=self.headers,
                timeout=self.config.timeout_seconds
            )
            
            if response.status_code != self.expected_status:
                raise Exception(
                    f"API returned status {response.status_code}, expected {self.expected_status}"
                )
            
            return {
                "status_code": response.status_code,
                "response_size": len(response.content),
                "headers": dict(response.headers),
                "url": self.url
            }


class LLMServiceHealthCheck(BaseHealthCheck):
    """Health check for LLM services (Groq, OpenAI, etc)."""
    
    def __init__(
        self,
        name: str,
        api_key: str,
        base_url: str,
        config: Optional[HealthCheckConfig] = None
    ):
        super().__init__(name, DependencyType.LLM_SERVICE, config)
        self.api_key = api_key
        self.base_url = base_url
    
    async def _perform_check(self) -> Dict[str, Any]:
        """Check LLM service availability with a simple test."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Simple test prompt
        test_payload = {
            "model": "llama3-8b-8192",  # Groq model
            "messages": [
                {"role": "user", "content": "Say 'OK' if you can respond."}
            ],
            "max_tokens": 10,
            "temperature": 0
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=test_payload,
                timeout=self.config.timeout_seconds
            )
            
            if response.status_code != 200:
                raise Exception(f"LLM service returned status {response.status_code}")
            
            result = response.json()
            
            # Verify response structure
            if "choices" not in result or not result["choices"]:
                raise Exception("Invalid response structure from LLM service")
            
            return {
                "status_code": response.status_code,
                "model": result.get("model"),
                "usage": result.get("usage", {}),
                "response_content": result["choices"][0]["message"]["content"][:50],
                "service_name": name
            }


class HealthCheckManager:
    """
    Manager for coordinating multiple health checks.
    
    Provides centralized health monitoring with dependency tracking
    and aggregated health status reporting.
    """
    
    def __init__(self):
        self.health_checks: List[BaseHealthCheck] = []
        self.last_check_results: Dict[str, HealthCheckResult] = {}
        self.check_history: Dict[str, List[HealthCheckResult]] = {}
        self.max_history_size = 100
        
        self.logger = get_structured_logger(__name__, component="health_manager")
    
    def register_check(self, health_check: BaseHealthCheck):
        """Register a health check."""
        self.health_checks.append(health_check)
        self.check_history[health_check.name] = []
        
        self.logger.info(
            f"Registered health check: {health_check.name}",
            operation="register_health_check",
            dependency_type=health_check.dependency_type.value
        )
    
    def register_default_checks(self):
        """Register default health checks for the application."""
        # Database check
        try:
            from src.database import get_async_session
            db_check = DatabaseHealthCheck(get_async_session)
            self.register_check(db_check)
        except ImportError:
            self.logger.warning("Database session factory not available, skipping DB health check")
        
        # Redis check
        if hasattr(settings, 'redis_url') and settings.redis_url:
            redis_check = RedisHealthCheck(settings.redis_url)
            self.register_check(redis_check)
        
        # Portal da Transparência API check
        transparency_check = ExternalAPIHealthCheck(
            name="portal_transparencia",
            url="https://api.portaldatransparencia.gov.br/api-de-dados/versao",
            headers={"accept": "application/json"}
        )
        self.register_check(transparency_check)
        
        # LLM service check (Groq)
        if hasattr(settings, 'groq_api_key') and settings.groq_api_key:
            groq_check = LLMServiceHealthCheck(
                name="groq_llm",
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.register_check(groq_check)
    
    async def check_all(self, parallel: bool = True) -> Dict[str, HealthCheckResult]:
        """
        Run all registered health checks.
        
        Args:
            parallel: Whether to run checks in parallel
            
        Returns:
            Dictionary of check results by name
        """
        start_time = time.time()
        
        if parallel:
            # Run all checks in parallel
            tasks = [check.check() for check in self.health_checks]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            check_results = {}
            for i, result in enumerate(results):
                check_name = self.health_checks[i].name
                
                if isinstance(result, Exception):
                    # Handle exceptions
                    check_results[check_name] = HealthCheckResult(
                        name=check_name,
                        status=HealthStatus.UNHEALTHY,
                        dependency_type=self.health_checks[i].dependency_type,
                        response_time_ms=0,
                        message="Health check failed with exception",
                        error=str(result)
                    )
                else:
                    check_results[check_name] = result
        else:
            # Run checks sequentially
            check_results = {}
            for check in self.health_checks:
                try:
                    result = await check.check()
                    check_results[check.name] = result
                except Exception as e:
                    check_results[check.name] = HealthCheckResult(
                        name=check.name,
                        status=HealthStatus.UNHEALTHY,
                        dependency_type=check.dependency_type,
                        response_time_ms=0,
                        message="Health check failed with exception",
                        error=str(e)
                    )
        
        # Update history and last results
        for name, result in check_results.items():
            self.last_check_results[name] = result
            
            if name in self.check_history:
                self.check_history[name].append(result)
                # Keep only recent history
                if len(self.check_history[name]) > self.max_history_size:
                    self.check_history[name] = self.check_history[name][-self.max_history_size:]
        
        total_time = (time.time() - start_time) * 1000
        
        self.logger.info(
            f"Completed health checks for {len(check_results)} dependencies",
            operation="health_check_all",
            duration_ms=total_time,
            parallel=parallel,
            results_summary=self._get_status_summary(check_results)
        )
        
        return check_results
    
    def get_overall_status(self, results: Optional[Dict[str, HealthCheckResult]] = None) -> HealthStatus:
        """
        Get overall system health status.
        
        Args:
            results: Optional specific results to evaluate
            
        Returns:
            Overall health status
        """
        if results is None:
            results = self.last_check_results
        
        if not results:
            return HealthStatus.UNKNOWN
        
        statuses = [result.status for result in results.values()]
        
        # If any dependency is unhealthy, system is unhealthy
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        
        # If any dependency is degraded, system is degraded
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        
        # All dependencies are healthy
        return HealthStatus.HEALTHY
    
    def _get_status_summary(self, results: Dict[str, HealthCheckResult]) -> Dict[str, int]:
        """Get summary of health check statuses."""
        summary = {status.value: 0 for status in HealthStatus}
        
        for result in results.values():
            summary[result.status.value] += 1
        
        return summary
    
    def get_health_report(self) -> Dict[str, Any]:
        """
        Get comprehensive health report.
        
        Returns:
            Detailed health report with all dependency information
        """
        overall_status = self.get_overall_status()
        status_summary = self._get_status_summary(self.last_check_results)
        
        # Calculate availability metrics
        total_checks = len(self.last_check_results)
        healthy_checks = status_summary.get(HealthStatus.HEALTHY.value, 0)
        availability = healthy_checks / total_checks if total_checks > 0 else 0
        
        # Group dependencies by type
        dependencies_by_type = {}
        for result in self.last_check_results.values():
            dep_type = result.dependency_type.value
            if dep_type not in dependencies_by_type:
                dependencies_by_type[dep_type] = []
            dependencies_by_type[dep_type].append(result.to_dict())
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": overall_status.value,
            "availability_percentage": availability * 100,
            "summary": {
                "total_dependencies": total_checks,
                "healthy_dependencies": healthy_checks,
                "degraded_dependencies": status_summary.get(HealthStatus.DEGRADED.value, 0),
                "unhealthy_dependencies": status_summary.get(HealthStatus.UNHEALTHY.value, 0),
                "status_distribution": status_summary
            },
            "dependencies_by_type": dependencies_by_type,
            "all_dependencies": {
                name: result.to_dict() 
                for name, result in self.last_check_results.items()
            }
        }
    
    def get_dependency_trends(self, dependency_name: str, hours: int = 24) -> Dict[str, Any]:
        """
        Get trend analysis for a specific dependency.
        
        Args:
            dependency_name: Name of the dependency
            hours: Number of hours to analyze
            
        Returns:
            Trend analysis data
        """
        if dependency_name not in self.check_history:
            return {"error": f"No history found for dependency: {dependency_name}"}
        
        history = self.check_history[dependency_name]
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter recent history
        recent_history = [
            result for result in history
            if result.timestamp > cutoff_time
        ]
        
        if not recent_history:
            return {"error": f"No recent history for dependency: {dependency_name}"}
        
        # Calculate metrics
        response_times = [result.response_time_ms for result in recent_history]
        status_counts = {}
        for result in recent_history:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        uptime_percentage = (
            status_counts.get(HealthStatus.HEALTHY.value, 0) / len(recent_history) * 100
        )
        
        return {
            "dependency_name": dependency_name,
            "time_window_hours": hours,
            "total_checks": len(recent_history),
            "uptime_percentage": uptime_percentage,
            "avg_response_time_ms": sum(response_times) / len(response_times),
            "min_response_time_ms": min(response_times),
            "max_response_time_ms": max(response_times),
            "status_distribution": status_counts,
            "recent_incidents": [
                {
                    "timestamp": result.timestamp.isoformat(),
                    "status": result.status.value,
                    "message": result.message,
                    "response_time_ms": result.response_time_ms
                }
                for result in recent_history
                if result.status != HealthStatus.HEALTHY
            ]
        }


# Global health check manager
health_manager = HealthCheckManager()


async def initialize_health_checks():
    """Initialize default health checks."""
    health_manager.register_default_checks()
    
    # Run initial health check
    await health_manager.check_all()
    
    logger.info(
        "Health check system initialized",
        operation="initialize_health_checks",
        total_checks=len(health_manager.health_checks)
    )