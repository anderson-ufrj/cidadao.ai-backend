"""
Sistema de Monitoramento e Observabilidade Enterprise
OpenTelemetry, Prometheus, Distributed Tracing, Health Checks Avançados
"""

import asyncio
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Optional

import psutil

# Try to import OpenTelemetry, use stubs if not available
try:
    from opentelemetry import metrics, trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    # Use minimal implementation
    OPENTELEMETRY_AVAILABLE = False
    from src.core.monitoring_minimal import MockTracer as trace

    class MockInstrumentor:
        @staticmethod
        def instrument(*args, **kwargs):
            pass

    FastAPIInstrumentor = HTTPXClientInstrumentor = RedisInstrumentor = (
        SQLAlchemyInstrumentor
    ) = MockInstrumentor

import structlog
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class HealthStatus(Enum):
    """Status de saúde dos componentes"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """Tipos de métricas"""

    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    SUMMARY = "summary"


class MonitoringConfig(BaseModel):
    """Configuração do sistema de monitoramento"""

    # Service information
    service_name: str = "cidadao-ai"
    service_version: str = "1.0.0"
    environment: str = "production"

    # OpenTelemetry
    jaeger_endpoint: str = "http://localhost:14268/api/traces"
    enable_tracing: bool = True
    trace_sample_rate: float = 1.0

    # Prometheus
    prometheus_port: int = 8000
    enable_metrics: bool = True
    metrics_path: str = "/metrics"

    # Health checks
    health_check_interval: int = 30
    health_check_timeout: int = 5
    enable_deep_health_checks: bool = True

    # Performance monitoring
    slow_query_threshold_ms: float = 1000.0
    high_memory_threshold_mb: float = 1024.0
    high_cpu_threshold_percent: float = 80.0

    # Alerting
    enable_alerting: bool = True
    alert_webhook_url: Optional[str] = None


class PerformanceMetrics(BaseModel):
    """Métricas de performance do sistema"""

    # System metrics
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_usage_percent: float
    disk_usage_percent: float

    # Application metrics
    active_investigations: int
    total_requests: int
    failed_requests: int
    average_response_time_ms: float

    # ML metrics
    ml_inference_time_ms: float
    anomalies_detected: int
    detection_accuracy: float

    # Database metrics
    db_connections_active: int
    db_query_time_ms: float
    cache_hit_rate: float

    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AlertSeverity(Enum):
    """Severidade dos alertas"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Alert(BaseModel):
    """Modelo de alerta"""

    id: str
    title: str
    description: str
    severity: AlertSeverity
    component: str
    metric_name: str
    metric_value: float
    threshold: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution_time: Optional[datetime] = None


class HealthCheck(BaseModel):
    """Resultado de health check"""

    component: str
    status: HealthStatus
    details: dict[str, Any] = Field(default_factory=dict)
    latency_ms: Optional[float] = None
    last_check: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None


class ObservabilityManager:
    """Gerenciador avançado de observabilidade e monitoramento"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.tracer = None
        self.meter = None
        self.registry = CollectorRegistry()

        # Health checks
        self.health_checks: dict[str, HealthCheck] = {}
        self.health_check_functions: dict[str, Callable] = {}

        # Metrics
        self.metrics: dict[str, Any] = {}
        self.performance_history: list[PerformanceMetrics] = []

        # Alerts
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history: list[Alert] = []

        # Performance tracking
        self.request_times: list[float] = []
        self.ml_inference_times: list[float] = []

        self._monitoring_task = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Inicializar sistema de monitoramento"""

        try:
            logger.info("Inicializando sistema de observabilidade...")

            # Setup OpenTelemetry
            await self._setup_tracing()

            # Setup Prometheus metrics
            await self._setup_metrics()

            # Setup health checks
            await self._setup_health_checks()

            # Start monitoring loop
            await self._start_monitoring_loop()

            self._initialized = True
            logger.info("✅ Sistema de observabilidade inicializado")

            return True

        except Exception as e:
            logger.error(f"❌ Falha na inicialização do monitoramento: {e}")
            return False

    async def _setup_tracing(self):
        """Configurar distributed tracing"""

        if not self.config.enable_tracing:
            return

        # Resource information
        resource = Resource.create(
            {
                "service.name": self.config.service_name,
                "service.version": self.config.service_version,
                "deployment.environment": self.config.environment,
            }
        )

        # Tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource))

        # Jaeger exporter
        jaeger_exporter = JaegerExporter(endpoint=self.config.jaeger_endpoint)

        # Span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)

        # Get tracer
        self.tracer = trace.get_tracer(__name__)

        # Auto-instrumentation
        FastAPIInstrumentor.instrument()
        HTTPXClientInstrumentor.instrument()
        RedisInstrumentor.instrument()
        SQLAlchemyInstrumentor.instrument()

        logger.info("✅ Distributed tracing configurado")

    async def _setup_metrics(self):
        """Configurar métricas Prometheus"""

        if not self.config.enable_metrics:
            return

        # Prometheus metrics
        self.metrics = {
            # HTTP metrics
            "http_requests_total": Counter(
                "http_requests_total",
                "Total HTTP requests",
                ["method", "endpoint", "status"],
                registry=self.registry,
            ),
            "http_request_duration": Histogram(
                "http_request_duration_seconds",
                "HTTP request duration",
                ["method", "endpoint"],
                registry=self.registry,
            ),
            # ML metrics
            "ml_inference_duration": Histogram(
                "ml_inference_duration_seconds",
                "ML inference duration",
                ["model", "task"],
                registry=self.registry,
            ),
            "anomalies_detected_total": Counter(
                "anomalies_detected_total",
                "Total anomalies detected",
                ["severity"],
                registry=self.registry,
            ),
            # System metrics
            "cpu_usage_percent": Gauge(
                "cpu_usage_percent", "CPU usage percentage", registry=self.registry
            ),
            "memory_usage_bytes": Gauge(
                "memory_usage_bytes", "Memory usage in bytes", registry=self.registry
            ),
            # Investigation metrics
            "active_investigations": Gauge(
                "active_investigations",
                "Number of active investigations",
                registry=self.registry,
            ),
            "investigation_duration": Histogram(
                "investigation_duration_seconds",
                "Investigation duration",
                ["status"],
                registry=self.registry,
            ),
            # Database metrics
            "db_connections_active": Gauge(
                "db_connections_active",
                "Active database connections",
                registry=self.registry,
            ),
            "cache_hit_rate": Gauge(
                "cache_hit_rate",
                "Cache hit rate",
                ["cache_type"],
                registry=self.registry,
            ),
        }

        logger.info("✅ Métricas Prometheus configuradas")

    async def _setup_health_checks(self):
        """Configurar health checks"""

        # Register default health checks
        self.register_health_check("system", self._check_system_health)
        self.register_health_check("database", self._check_database_health)
        self.register_health_check("redis", self._check_redis_health)
        self.register_health_check("ml_models", self._check_ml_models_health)

        logger.info("✅ Health checks configurados")

    async def _start_monitoring_loop(self):
        """Iniciar loop de monitoramento contínuo"""

        async def monitoring_loop():
            while True:
                try:
                    await self._collect_performance_metrics()
                    await self._run_health_checks()
                    await self._check_alerts()
                    await asyncio.sleep(self.config.health_check_interval)
                except Exception as e:
                    logger.error(f"❌ Erro no loop de monitoramento: {e}")
                    await asyncio.sleep(5)

        self._monitoring_task = asyncio.create_task(monitoring_loop())
        logger.info("✅ Loop de monitoramento iniciado")

    def register_health_check(self, name: str, check_function: Callable):
        """Registrar função de health check"""
        self.health_check_functions[name] = check_function
        logger.info(f"✅ Health check '{name}' registrado")

    async def _run_health_checks(self):
        """Executar todos os health checks"""

        for name, check_function in self.health_check_functions.items():
            try:
                start_time = time.time()
                result = await check_function()
                latency = (time.time() - start_time) * 1000

                if isinstance(result, dict):
                    status = result.get("status", HealthStatus.UNKNOWN)
                    details = result.get("details", {})
                    error_message = result.get("error")
                else:
                    status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                    details = {}
                    error_message = None

                self.health_checks[name] = HealthCheck(
                    component=name,
                    status=status,
                    details=details,
                    latency_ms=round(latency, 2),
                    error_message=error_message,
                )

            except Exception as e:
                self.health_checks[name] = HealthCheck(
                    component=name,
                    status=HealthStatus.UNHEALTHY,
                    error_message=str(e),
                    latency_ms=None,
                )

    async def _check_system_health(self) -> dict[str, Any]:
        """Health check do sistema"""

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Update metrics
            if "cpu_usage_percent" in self.metrics:
                self.metrics["cpu_usage_percent"].set(cpu_percent)

            if "memory_usage_bytes" in self.metrics:
                self.metrics["memory_usage_bytes"].set(memory.used)

            # Determine status
            status = HealthStatus.HEALTHY
            if cpu_percent > self.config.high_cpu_threshold_percent:
                status = HealthStatus.DEGRADED
            if memory.percent > 90:
                status = HealthStatus.UNHEALTHY

            return {
                "status": status,
                "details": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "load_average": (
                        psutil.getloadavg() if hasattr(psutil, "getloadavg") else None
                    ),
                },
            }

        except Exception as e:
            return {"status": HealthStatus.UNHEALTHY, "error": str(e)}

    async def _check_database_health(self) -> dict[str, Any]:
        """Health check do banco de dados"""

        try:
            # Import here to avoid circular dependency
            from .database import get_database_manager

            db = await get_database_manager()
            health_status = await db.get_health_status()

            # Determine overall status
            pg_healthy = health_status["postgresql"]["status"] == "healthy"
            redis_healthy = health_status["redis"]["status"] == "healthy"

            if pg_healthy and redis_healthy:
                status = HealthStatus.HEALTHY
            elif pg_healthy or redis_healthy:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY

            return {"status": status, "details": health_status}

        except Exception as e:
            return {"status": HealthStatus.UNHEALTHY, "error": str(e)}

    async def _check_redis_health(self) -> dict[str, Any]:
        """Health check específico do Redis"""

        try:
            from .database import get_database_manager

            db = await get_database_manager()
            start_time = time.time()
            await db.redis_cluster.ping()
            latency = (time.time() - start_time) * 1000

            status = HealthStatus.HEALTHY if latency < 100 else HealthStatus.DEGRADED

            return {
                "status": status,
                "details": {
                    "latency_ms": round(latency, 2),
                    "connection_pool": "active",
                },
            }

        except Exception as e:
            return {"status": HealthStatus.UNHEALTHY, "error": str(e)}

    async def _check_ml_models_health(self) -> dict[str, Any]:
        """Health check dos modelos ML"""

        try:
            # Check if Cidadão.AI is available
            from ..ml.hf_integration import get_cidadao_manager

            manager = get_cidadao_manager()
            model_info = manager.get_model_info()

            if model_info.get("status") == "loaded":
                status = HealthStatus.HEALTHY
            else:
                status = HealthStatus.UNHEALTHY

            return {"status": status, "details": model_info}

        except Exception as e:
            return {"status": HealthStatus.UNHEALTHY, "error": str(e)}

    async def _collect_performance_metrics(self):
        """Coletar métricas de performance"""

        try:
            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Calculate averages
            avg_response_time = (
                sum(self.request_times[-100:]) / len(self.request_times[-100:])
                if self.request_times
                else 0
            )
            avg_ml_time = (
                sum(self.ml_inference_times[-50:]) / len(self.ml_inference_times[-50:])
                if self.ml_inference_times
                else 0
            )

            # Create metrics object
            metrics = PerformanceMetrics(
                cpu_usage_percent=cpu_percent,
                memory_usage_mb=memory.used / (1024 * 1024),
                memory_usage_percent=memory.percent,
                disk_usage_percent=disk.percent,
                active_investigations=len(getattr(self, "_active_investigations", [])),
                total_requests=len(self.request_times),
                failed_requests=0,  # TODO: track failed requests
                average_response_time_ms=avg_response_time * 1000,
                ml_inference_time_ms=avg_ml_time * 1000,
                anomalies_detected=0,  # TODO: track anomalies
                detection_accuracy=0.0,  # TODO: track accuracy
                db_connections_active=0,  # TODO: get from DB manager
                db_query_time_ms=0.0,  # TODO: track query time
                cache_hit_rate=0.0,  # TODO: get from cache manager
            )

            # Store metrics
            self.performance_history.append(metrics)

            # Keep only last 1000 metrics
            if len(self.performance_history) > 1000:
                self.performance_history = self.performance_history[-1000:]

        except Exception as e:
            logger.error(f"❌ Erro ao coletar métricas: {e}")

    async def _check_alerts(self):
        """Verificar condições de alerta"""

        if not self.performance_history:
            return

        latest_metrics = self.performance_history[-1]

        # CPU alert
        if latest_metrics.cpu_usage_percent > self.config.high_cpu_threshold_percent:
            await self._trigger_alert(
                "high_cpu",
                "High CPU Usage",
                f"CPU usage is {latest_metrics.cpu_usage_percent:.1f}%",
                AlertSeverity.WARNING,
                "system",
                "cpu_usage_percent",
                latest_metrics.cpu_usage_percent,
                self.config.high_cpu_threshold_percent,
            )

        # Memory alert
        if latest_metrics.memory_usage_percent > 85:
            await self._trigger_alert(
                "high_memory",
                "High Memory Usage",
                f"Memory usage is {latest_metrics.memory_usage_percent:.1f}%",
                AlertSeverity.ERROR,
                "system",
                "memory_usage_percent",
                latest_metrics.memory_usage_percent,
                85.0,
            )

        # Response time alert
        if (
            latest_metrics.average_response_time_ms
            > self.config.slow_query_threshold_ms
        ):
            await self._trigger_alert(
                "slow_response",
                "Slow Response Time",
                f"Average response time is {latest_metrics.average_response_time_ms:.1f}ms",
                AlertSeverity.WARNING,
                "api",
                "average_response_time_ms",
                latest_metrics.average_response_time_ms,
                self.config.slow_query_threshold_ms,
            )

    async def _trigger_alert(
        self,
        alert_id: str,
        title: str,
        description: str,
        severity: AlertSeverity,
        component: str,
        metric_name: str,
        metric_value: float,
        threshold: float,
    ):
        """Disparar alerta"""

        # Check if alert already active
        if alert_id in self.active_alerts:
            return

        alert = Alert(
            id=alert_id,
            title=title,
            description=description,
            severity=severity,
            component=component,
            metric_name=metric_name,
            metric_value=metric_value,
            threshold=threshold,
        )

        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)

        logger.warning(f"🚨 ALERTA: {title} - {description}")

        # Send webhook if configured
        if self.config.alert_webhook_url:
            await self._send_alert_webhook(alert)

    async def _send_alert_webhook(self, alert: Alert):
        """Enviar alerta via webhook"""

        try:
            import httpx

            payload = {
                "alert_id": alert.id,
                "title": alert.title,
                "description": alert.description,
                "severity": alert.severity.value,
                "component": alert.component,
                "timestamp": alert.timestamp.isoformat(),
                "metric": {
                    "name": alert.metric_name,
                    "value": alert.metric_value,
                    "threshold": alert.threshold,
                },
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.config.alert_webhook_url, json=payload, timeout=10.0
                )

                if response.status_code == 200:
                    logger.info(f"✅ Alerta {alert.id} enviado via webhook")
                else:
                    logger.error(
                        f"❌ Falha ao enviar alerta via webhook: {response.status_code}"
                    )

        except Exception as e:
            logger.error(f"❌ Erro ao enviar webhook: {e}")

    @asynccontextmanager
    async def trace_span(self, name: str, attributes: dict[str, Any] = None):
        """Context manager para criar spans de tracing"""

        if not self.tracer:
            yield None
            return

        with self.tracer.start_as_current_span(name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            yield span

    def track_request_time(self, duration_seconds: float):
        """Rastrear tempo de request"""
        self.request_times.append(duration_seconds)

        # Keep only last 1000
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]

    def track_ml_inference_time(
        self, duration_seconds: float, model: str = "cidadao-gpt"
    ):
        """Rastrear tempo de inferência ML"""
        self.ml_inference_times.append(duration_seconds)

        # Update Prometheus metric
        if "ml_inference_duration" in self.metrics:
            self.metrics["ml_inference_duration"].labels(
                model=model, task="inference"
            ).observe(duration_seconds)

        # Keep only last 500
        if len(self.ml_inference_times) > 500:
            self.ml_inference_times = self.ml_inference_times[-500:]

    def increment_anomaly_count(self, severity: str = "medium"):
        """Incrementar contador de anomalias"""
        if "anomalies_detected_total" in self.metrics:
            self.metrics["anomalies_detected_total"].labels(severity=severity).inc()

    async def get_health_summary(self) -> dict[str, Any]:
        """Obter resumo de saúde do sistema"""

        overall_status = HealthStatus.HEALTHY

        # Check individual components
        for component, health in self.health_checks.items():
            if health.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
                break
            elif (
                health.status == HealthStatus.DEGRADED
                and overall_status == HealthStatus.HEALTHY
            ):
                overall_status = HealthStatus.DEGRADED

        return {
            "overall_status": overall_status.value,
            "components": {
                name: health.dict() for name, health in self.health_checks.items()
            },
            "active_alerts": len(self.active_alerts),
            "last_check": datetime.utcnow().isoformat(),
            "uptime_seconds": time.time() - getattr(self, "_start_time", time.time()),
        }

    async def get_metrics_summary(self) -> dict[str, Any]:
        """Obter resumo de métricas"""

        if not self.performance_history:
            return {"error": "No metrics available"}

        latest = self.performance_history[-1]

        return {
            "timestamp": latest.timestamp.isoformat(),
            "system": {
                "cpu_usage_percent": latest.cpu_usage_percent,
                "memory_usage_mb": latest.memory_usage_mb,
                "memory_usage_percent": latest.memory_usage_percent,
                "disk_usage_percent": latest.disk_usage_percent,
            },
            "application": {
                "active_investigations": latest.active_investigations,
                "total_requests": latest.total_requests,
                "average_response_time_ms": latest.average_response_time_ms,
                "ml_inference_time_ms": latest.ml_inference_time_ms,
            },
            "alerts": {
                "active_count": len(self.active_alerts),
                "total_count": len(self.alert_history),
            },
        }

    def get_prometheus_metrics(self) -> str:
        """Obter métricas no formato Prometheus"""
        return generate_latest(self.registry)

    async def cleanup(self):
        """Cleanup de recursos"""

        try:
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass

            logger.info("✅ Cleanup do sistema de monitoramento concluído")

        except Exception as e:
            logger.error(f"❌ Erro no cleanup: {e}")


# Singleton instance
_monitoring_manager: Optional[ObservabilityManager] = None


async def get_monitoring_manager() -> ObservabilityManager:
    """Obter instância singleton do monitoring manager"""

    global _monitoring_manager

    if _monitoring_manager is None or not _monitoring_manager._initialized:
        config = MonitoringConfig()
        _monitoring_manager = ObservabilityManager(config)
        await _monitoring_manager.initialize()

    return _monitoring_manager


def trace_async(span_name: str = None, attributes: dict[str, Any] = None):
    """Decorator para tracing automático de funções async"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            monitoring = await get_monitoring_manager()
            name = span_name or f"{func.__module__}.{func.__name__}"

            async with monitoring.trace_span(name, attributes) as span:
                try:
                    start_time = time.time()
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time

                    if span:
                        span.set_attribute("duration_seconds", duration)
                        span.set_attribute("success", True)

                    return result

                except Exception as e:
                    if span:
                        span.set_attribute("error", True)
                        span.set_attribute("error_message", str(e))
                    raise

        return wrapper

    return decorator


async def cleanup_monitoring():
    """Cleanup global do sistema de monitoramento"""

    global _monitoring_manager

    if _monitoring_manager:
        await _monitoring_manager.cleanup()
        _monitoring_manager = None


if __name__ == "__main__":
    # Teste do sistema
    import asyncio

    async def test_monitoring_system():
        """Teste completo do sistema de monitoramento"""

        print("🧪 Testando sistema de monitoramento...")

        # Inicializar
        monitoring = await get_monitoring_manager()

        # Simulate some activity
        monitoring.track_request_time(0.15)
        monitoring.track_ml_inference_time(0.5)
        monitoring.increment_anomaly_count("high")

        # Wait for health checks
        await asyncio.sleep(2)

        # Get health summary
        health = await monitoring.get_health_summary()
        print(f"✅ Health summary: {health['overall_status']}")

        # Get metrics summary
        metrics = await monitoring.get_metrics_summary()
        print(
            f"✅ Metrics summary: {metrics.get('system', {}).get('cpu_usage_percent', 'N/A')}% CPU"
        )

        # Test tracing
        @trace_async("test_function")
        async def test_traced_function():
            await asyncio.sleep(0.1)
            return "success"

        result = await test_traced_function()
        print(f"✅ Traced function result: {result}")

        # Cleanup
        await cleanup_monitoring()
        print("✅ Teste concluído!")

    asyncio.run(test_monitoring_system())
