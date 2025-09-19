"""
Comprehensive monitoring and observability system.
Provides metrics collection, distributed tracing, and health monitoring.
"""

import time
import psutil
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import logging

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace, baggage
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

from src.core.config import get_settings
from src.core import get_logger

logger = get_logger(__name__)
settings = get_settings()


# Prometheus Metrics
REQUEST_COUNT = Counter(
    'cidadao_ai_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'cidadao_ai_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

AGENT_TASK_COUNT = Counter(
    'cidadao_ai_agent_tasks_total',
    'Total number of agent tasks',
    ['agent_type', 'task_type', 'status']
)

AGENT_TASK_DURATION = Histogram(
    'cidadao_ai_agent_task_duration_seconds',
    'Agent task duration in seconds',
    ['agent_type', 'task_type']
)

DATABASE_QUERIES = Counter(
    'cidadao_ai_database_queries_total',
    'Total number of database queries',
    ['operation', 'table']
)

DATABASE_QUERY_DURATION = Histogram(
    'cidadao_ai_database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table']
)

TRANSPARENCY_API_CALLS = Counter(
    'cidadao_ai_transparency_api_calls_total',
    'Total calls to transparency API',
    ['endpoint', 'status']
)

TRANSPARENCY_API_DURATION = Histogram(
    'cidadao_ai_transparency_api_duration_seconds',
    'Transparency API call duration',
    ['endpoint']
)

SYSTEM_CPU_USAGE = Gauge(
    'cidadao_ai_system_cpu_percent',
    'System CPU usage percentage'
)

SYSTEM_MEMORY_USAGE = Gauge(
    'cidadao_ai_system_memory_percent',
    'System memory usage percentage'
)

REDIS_OPERATIONS = Counter(
    'cidadao_ai_redis_operations_total',
    'Total Redis operations',
    ['operation', 'status']
)

ACTIVE_CONNECTIONS = Gauge(
    'cidadao_ai_active_connections',
    'Number of active connections',
    ['connection_type']
)

# Investigation and Anomaly Detection Metrics
INVESTIGATIONS_TOTAL = Counter(
    'cidadao_ai_investigations_total',
    'Total number of investigations started',
    ['agent_type', 'investigation_type', 'status']
)

ANOMALIES_DETECTED = Counter(
    'cidadao_ai_anomalies_detected_total',
    'Total number of anomalies detected',
    ['anomaly_type', 'severity', 'agent']
)

INVESTIGATION_DURATION = Histogram(
    'cidadao_ai_investigation_duration_seconds',
    'Time taken for investigations',
    ['agent_type', 'investigation_type']
)

DATA_RECORDS_PROCESSED = Counter(
    'cidadao_ai_data_records_processed_total',
    'Total number of data records processed',
    ['data_source', 'agent', 'operation']
)

TRANSPARENCY_API_DATA_FETCHED = Counter(
    'cidadao_ai_transparency_data_fetched_total',
    'Total data fetched from transparency API',
    ['endpoint', 'organization', 'status']
)


class PerformanceMetrics:
    """System performance metrics collector."""
    
    def __init__(self):
        self.response_times = deque(maxlen=1000)
        self.error_rates = defaultdict(int)
        self.throughput_counter = 0
        self.last_throughput_reset = time.time()
    
    def record_request(self, duration: float, status_code: int, endpoint: str):
        """Record request metrics."""
        self.response_times.append(duration)
        
        if status_code >= 400:
            self.error_rates[endpoint] += 1
        
        self.throughput_counter += 1
    
    def get_avg_response_time(self) -> float:
        """Get average response time."""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_p95_response_time(self) -> float:
        """Get 95th percentile response time."""
        if not self.response_times:
            return 0.0
        
        sorted_times = sorted(self.response_times)
        index = int(0.95 * len(sorted_times))
        return sorted_times[min(index, len(sorted_times) - 1)]
    
    def get_throughput(self) -> float:
        """Get requests per second."""
        elapsed = time.time() - self.last_throughput_reset
        if elapsed == 0:
            return 0.0
        return self.throughput_counter / elapsed
    
    def get_error_rate(self, endpoint: str = None) -> float:
        """Get error rate for endpoint or overall."""
        if endpoint:
            total_requests = sum(1 for _ in self.response_times)  # Approximate
            errors = self.error_rates.get(endpoint, 0)
            return errors / max(total_requests, 1)
        
        total_errors = sum(self.error_rates.values())
        total_requests = sum(1 for _ in self.response_times)
        return total_errors / max(total_requests, 1)
    
    def reset_throughput_counter(self):
        """Reset throughput counter."""
        self.throughput_counter = 0
        self.last_throughput_reset = time.time()


class SystemHealthMonitor:
    """System health monitoring."""
    
    def __init__(self):
        self.health_checks = {}
        self.last_check = {}
        self.check_intervals = {
            'database': 30,  # seconds
            'redis': 30,
            'transparency_api': 60,
            'disk_space': 300,  # 5 minutes
            'memory': 60
        }
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            from src.core.database import get_db_session
            
            start_time = time.time()
            
            async with get_db_session() as session:
                # Simple connectivity test
                await session.execute("SELECT 1")
                response_time = time.time() - start_time
                
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "timestamp": datetime.utcnow(),
                    "details": "Database connection successful"
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow()
            }
    
    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance."""
        try:
            from src.core.cache import get_redis_client
            
            start_time = time.time()
            redis = await get_redis_client()
            
            # Test Redis connectivity
            await redis.ping()
            response_time = time.time() - start_time
            
            # Get Redis info
            info = await redis.info()
            memory_usage = info.get('used_memory', 0)
            connected_clients = info.get('connected_clients', 0)
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "memory_usage": memory_usage,
                "connected_clients": connected_clients,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow()
            }
    
    async def check_transparency_api_health(self) -> Dict[str, Any]:
        """Check Portal da Transparência API health."""
        try:
            import aiohttp
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                # Test API availability with a simple request
                url = "https://api.portaldatransparencia.gov.br/api-de-dados/versao"
                headers = {
                    "chave-api-dados": settings.transparency_api_key.get_secret_value()
                }
                
                async with session.get(url, headers=headers, timeout=10) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        return {
                            "status": "healthy",
                            "response_time": response_time,
                            "api_status": response.status,
                            "timestamp": datetime.utcnow()
                        }
                    else:
                        return {
                            "status": "degraded",
                            "response_time": response_time,
                            "api_status": response.status,
                            "timestamp": datetime.utcnow()
                        }
                        
        except Exception as e:
            logger.error(f"Transparency API health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow()
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            SYSTEM_CPU_USAGE.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            SYSTEM_MEMORY_USAGE.set(memory_percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network stats
            network = psutil.net_io_counters()
            
            return {
                "status": "healthy" if cpu_percent < 80 and memory_percent < 80 else "warning",
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "disk_free_gb": disk.free / (1024**3),
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow()
            }
    
    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.utcnow(),
            "checks": {}
        }
        
        # Run all health checks
        checks = {
            "database": self.check_database_health(),
            "redis": self.check_redis_health(),
            "transparency_api": self.check_transparency_api_health(),
            "system_resources": asyncio.create_task(asyncio.coroutine(self.check_system_resources)())
        }
        
        # Execute checks concurrently
        for check_name, check_coro in checks.items():
            try:
                if asyncio.iscoroutine(check_coro):
                    result = await check_coro
                else:
                    result = check_coro
                    
                health_status["checks"][check_name] = result
                
                # Update overall status
                if result["status"] != "healthy":
                    if health_status["overall_status"] == "healthy":
                        health_status["overall_status"] = "degraded"
                    if result["status"] == "unhealthy":
                        health_status["overall_status"] = "unhealthy"
                        
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {e}")
                health_status["checks"][check_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow()
                }
                health_status["overall_status"] = "unhealthy"
        
        return health_status


class DistributedTracing:
    """Distributed tracing configuration and utilities."""
    
    def __init__(self):
        self.tracer_provider = None
        self.tracer = None
        self.setup_tracing()
    
    def setup_tracing(self):
        """Setup OpenTelemetry distributed tracing."""
        try:
            # Skip tracing setup if Jaeger settings not available
            if not hasattr(settings, 'jaeger_host'):
                logger.info("Jaeger configuration not found, skipping distributed tracing setup")
                return
                
            # Configure tracer provider
            self.tracer_provider = TracerProvider()
            trace.set_tracer_provider(self.tracer_provider)
            
            # Configure Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name=settings.jaeger_host,
                agent_port=settings.jaeger_port,
            )
            
            # Add batch span processor
            span_processor = BatchSpanProcessor(jaeger_exporter)
            self.tracer_provider.add_span_processor(span_processor)
            
            # Get tracer
            self.tracer = trace.get_tracer(__name__)
            
            # Instrument frameworks
            FastAPIInstrumentor.instrument()
            SQLAlchemyInstrumentor.instrument()
            RedisInstrumentor.instrument()
            
            logger.info("Distributed tracing configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to configure distributed tracing: {e}")
    
    @asynccontextmanager
    async def trace_operation(self, operation_name: str, **attributes):
        """Context manager for tracing operations."""
        if not self.tracer:
            yield None
            return
        
        with self.tracer.start_as_current_span(operation_name) as span:
            # Add attributes
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
            
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
    
    def add_baggage(self, key: str, value: str):
        """Add baggage to current trace context."""
        baggage.set_baggage(key, value)
    
    def get_baggage(self, key: str) -> Optional[str]:
        """Get baggage from current trace context."""
        return baggage.get_baggage(key)


class AlertManager:
    """Alert management system."""
    
    def __init__(self):
        self.alert_thresholds = {
            'response_time_p95': 2.0,  # seconds
            'error_rate': 0.05,  # 5%
            'cpu_usage': 80.0,  # percent
            'memory_usage': 85.0,  # percent
            'disk_usage': 90.0,  # percent
        }
        self.alert_history = deque(maxlen=1000)
        self.active_alerts = {}
    
    def check_thresholds(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Check if any metrics exceed thresholds."""
        alerts = []
        
        for metric_name, threshold in self.alert_thresholds.items():
            value = metrics.get(metric_name, 0)
            
            if value > threshold:
                alert = {
                    "metric": metric_name,
                    "value": value,
                    "threshold": threshold,
                    "severity": self._get_alert_severity(metric_name, value, threshold),
                    "timestamp": datetime.utcnow(),
                    "message": f"{metric_name} ({value}) exceeds threshold ({threshold})"
                }
                
                alerts.append(alert)
                self.active_alerts[metric_name] = alert
                self.alert_history.append(alert)
                
            elif metric_name in self.active_alerts:
                # Clear resolved alert
                resolved_alert = self.active_alerts.pop(metric_name)
                resolved_alert["resolved_at"] = datetime.utcnow()
                self.alert_history.append(resolved_alert)
        
        return alerts
    
    def _get_alert_severity(self, metric_name: str, value: float, threshold: float) -> str:
        """Determine alert severity based on how much threshold is exceeded."""
        ratio = value / threshold
        
        if ratio > 1.5:
            return "critical"
        elif ratio > 1.2:
            return "high"
        elif ratio > 1.1:
            return "medium"
        else:
            return "low"
    
    async def send_alert(self, alert: Dict[str, Any]):
        """Send alert notification (implement webhook, email, etc.)."""
        # Log alert
        logger.warning(f"ALERT: {alert['message']}")
        
        # Here you would implement actual alerting
        # e.g., send to Slack, PagerDuty, email, etc.
        pass


# Global instances
performance_metrics = PerformanceMetrics()
health_monitor = SystemHealthMonitor()
distributed_tracing = DistributedTracing()
alert_manager = AlertManager()


def get_metrics_data() -> str:
    """Get Prometheus metrics data."""
    return generate_latest()


async def collect_system_metrics() -> Dict[str, Any]:
    """Collect comprehensive system metrics."""
    # Update system metrics
    system_resources = health_monitor.check_system_resources()
    
    # Collect performance metrics
    performance_data = {
        "avg_response_time": performance_metrics.get_avg_response_time(),
        "p95_response_time": performance_metrics.get_p95_response_time(),
        "throughput": performance_metrics.get_throughput(),
        "error_rate": performance_metrics.get_error_rate()
    }
    
    # Check for alerts
    alerts = alert_manager.check_thresholds({
        "response_time_p95": performance_data["p95_response_time"],
        "error_rate": performance_data["error_rate"],
        "cpu_usage": system_resources["cpu_percent"],
        "memory_usage": system_resources["memory_percent"],
        "disk_usage": system_resources["disk_percent"]
    })
    
    return {
        "performance": performance_data,
        "system": system_resources,
        "alerts": alerts,
        "timestamp": datetime.utcnow()
    }