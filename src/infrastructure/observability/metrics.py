"""
Prometheus metrics implementation for comprehensive monitoring.

This module provides custom metrics collection and exposure
for monitoring system performance and business metrics.
"""

import time
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from enum import Enum
from dataclasses import dataclass
import asyncio

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info, Enum as PrometheusEnum,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
    multiprocess, values
)

# Try to import OpenMetricsHandler - not available in all versions
try:
    from prometheus_client.openmetrics.exposition import OpenMetricsHandler
    OPENMETRICS_AVAILABLE = True
except ImportError:
    OPENMETRICS_AVAILABLE = False
    OpenMetricsHandler = None

from src.core import get_logger

logger = get_logger(__name__)


class MetricType(str, Enum):
    """Types of metrics supported."""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    SUMMARY = "summary"
    INFO = "info"
    ENUM = "enum"


@dataclass
class MetricConfig:
    """Configuration for a metric."""
    name: str
    description: str
    labels: Optional[List[str]] = None
    buckets: Optional[List[float]] = None  # For histograms
    states: Optional[List[str]] = None     # For enums


class MetricsManager:
    """
    Centralized metrics management for Prometheus integration.
    
    Provides a unified interface for creating, updating, and
    exposing custom application metrics.
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """
        Initialize metrics manager.
        
        Args:
            registry: Custom registry (uses default if None)
        """
        self.registry = registry or CollectorRegistry()
        self._metrics: Dict[str, Any] = {}
        self._metric_configs: Dict[str, MetricConfig] = {}
        
        # Initialize default metrics
        self._setup_default_metrics()
        
        logger.info("Metrics manager initialized")
    
    def _setup_default_metrics(self):
        """Setup default application metrics."""
        # Agent execution metrics
        self.register_metric(MetricConfig(
            name="cidadao_ai_agent_tasks_total",
            description="Total number of agent tasks executed",
            labels=["agent_name", "task_type", "status"]
        ), MetricType.COUNTER)
        
        self.register_metric(MetricConfig(
            name="cidadao_ai_agent_task_duration_seconds",
            description="Duration of agent task execution",
            labels=["agent_name", "task_type"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        ), MetricType.HISTOGRAM)
        
        # Investigation metrics
        self.register_metric(MetricConfig(
            name="cidadao_ai_investigations_total",
            description="Total number of investigations",
            labels=["status", "priority", "user_type"]
        ), MetricType.COUNTER)
        
        self.register_metric(MetricConfig(
            name="cidadao_ai_investigation_duration_seconds",
            description="Duration of investigation processing",
            labels=["investigation_type"],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
        ), MetricType.HISTOGRAM)
        
        # Anomaly detection metrics
        self.register_metric(MetricConfig(
            name="cidadao_ai_anomalies_detected_total",
            description="Total number of anomalies detected",
            labels=["anomaly_type", "severity", "data_source"]
        ), MetricType.COUNTER)
        
        self.register_metric(MetricConfig(
            name="cidadao_ai_anomaly_confidence_score",
            description="Confidence score of detected anomalies",
            labels=["anomaly_type"]
        ), MetricType.HISTOGRAM)
        
        # External API metrics
        self.register_metric(MetricConfig(
            name="cidadao_ai_transparency_api_requests_total",
            description="Total requests to transparency APIs",
            labels=["api_name", "endpoint", "status_code"]
        ), MetricType.COUNTER)
        
        self.register_metric(MetricConfig(
            name="cidadao_ai_transparency_data_fetched_total",
            description="Total data records fetched from transparency APIs",
            labels=["data_type", "source"]
        ), MetricType.COUNTER)
        
        # System performance metrics
        self.register_metric(MetricConfig(
            name="cidadao_ai_request_duration_seconds",
            description="HTTP request duration",
            labels=["method", "endpoint", "status_code"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
        ), MetricType.HISTOGRAM)
        
        self.register_metric(MetricConfig(
            name="cidadao_ai_active_investigations",
            description="Number of currently active investigations"
        ), MetricType.GAUGE)
        
        self.register_metric(MetricConfig(
            name="cidadao_ai_cache_operations_total",
            description="Total cache operations",
            labels=["operation", "cache_type", "result"]
        ), MetricType.COUNTER)
        
        # Circuit breaker metrics
        self.register_metric(MetricConfig(
            name="cidadao_ai_circuit_breaker_state",
            description="Current state of circuit breakers",
            labels=["service_name"],
            states=["closed", "open", "half_open"]
        ), MetricType.ENUM)
        
        self.register_metric(MetricConfig(
            name="cidadao_ai_circuit_breaker_failures_total",
            description="Total circuit breaker failures",
            labels=["service_name"]
        ), MetricType.COUNTER)
        
        # Bulkhead metrics
        self.register_metric(MetricConfig(
            name="cidadao_ai_bulkhead_active_requests",
            description="Currently active requests in bulkhead",
            labels=["resource_type"]
        ), MetricType.GAUGE)
        
        self.register_metric(MetricConfig(
            name="cidadao_ai_bulkhead_queued_requests",
            description="Currently queued requests in bulkhead",
            labels=["resource_type"]
        ), MetricType.GAUGE)
        
        # Business metrics
        self.register_metric(MetricConfig(
            name="cidadao_ai_public_spending_analyzed",
            description="Total amount of public spending analyzed",
            labels=["year", "ministry", "analysis_type"]
        ), MetricType.COUNTER)
        
        self.register_metric(MetricConfig(
            name="cidadao_ai_contracts_processed_total",
            description="Total number of contracts processed",
            labels=["contract_type", "status"]
        ), MetricType.COUNTER)
        
        # Application info
        self.register_metric(MetricConfig(
            name="cidadao_ai_info",
            description="Application information"
        ), MetricType.INFO)
    
    def register_metric(
        self,
        config: MetricConfig,
        metric_type: MetricType
    ) -> Any:
        """
        Register a new metric.
        
        Args:
            config: Metric configuration
            metric_type: Type of metric
            
        Returns:
            Created metric instance
        """
        if config.name in self._metrics:
            logger.warning(f"Metric {config.name} already registered")
            return self._metrics[config.name]
        
        # Create metric based on type
        if metric_type == MetricType.COUNTER:
            metric = Counter(
                config.name,
                config.description,
                labelnames=config.labels or [],
                registry=self.registry
            )
        elif metric_type == MetricType.HISTOGRAM:
            metric = Histogram(
                config.name,
                config.description,
                labelnames=config.labels or [],
                buckets=config.buckets,
                registry=self.registry
            )
        elif metric_type == MetricType.GAUGE:
            metric = Gauge(
                config.name,
                config.description,
                labelnames=config.labels or [],
                registry=self.registry
            )
        elif metric_type == MetricType.SUMMARY:
            metric = Summary(
                config.name,
                config.description,
                labelnames=config.labels or [],
                registry=self.registry
            )
        elif metric_type == MetricType.INFO:
            metric = Info(
                config.name,
                config.description,
                registry=self.registry
            )
        elif metric_type == MetricType.ENUM:
            metric = PrometheusEnum(
                config.name,
                config.description,
                labelnames=config.labels or [],
                states=config.states or [],
                registry=self.registry
            )
        else:
            raise ValueError(f"Unsupported metric type: {metric_type}")
        
        self._metrics[config.name] = metric
        self._metric_configs[config.name] = config
        
        logger.debug(f"Registered {metric_type} metric: {config.name}")
        return metric
    
    def get_metric(self, name: str) -> Optional[Any]:
        """Get metric by name."""
        return self._metrics.get(name)
    
    def increment_counter(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None,
        amount: float = 1.0
    ):
        """Increment a counter metric."""
        metric = self.get_metric(name)
        if metric and hasattr(metric, 'inc'):
            if labels:
                metric.labels(**labels).inc(amount)
            else:
                metric.inc(amount)
    
    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Set a gauge metric value."""
        metric = self.get_metric(name)
        if metric and hasattr(metric, 'set'):
            if labels:
                metric.labels(**labels).set(value)
            else:
                metric.set(value)
    
    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Observe a value in histogram metric."""
        metric = self.get_metric(name)
        if metric and hasattr(metric, 'observe'):
            if labels:
                metric.labels(**labels).observe(value)
            else:
                metric.observe(value)
    
    def time_histogram(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None
    ):
        """Context manager for timing histogram metrics."""
        metric = self.get_metric(name)
        if metric and hasattr(metric, 'time'):
            if labels:
                return metric.labels(**labels).time()
            else:
                return metric.time()
        else:
            # Fallback no-op context manager
            class NoOpTimer:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
            return NoOpTimer()
    
    def set_enum(
        self,
        name: str,
        state: str,
        labels: Optional[Dict[str, str]] = None
    ):
        """Set enum metric state."""
        metric = self.get_metric(name)
        if metric and hasattr(metric, 'state'):
            if labels:
                metric.labels(**labels).state(state)
            else:
                metric.state(state)
    
    def set_info(
        self,
        name: str,
        info: Dict[str, str]
    ):
        """Set info metric."""
        metric = self.get_metric(name)
        if metric and hasattr(metric, 'info'):
            metric.info(info)
    
    def generate_metrics(self) -> str:
        """Generate metrics in Prometheus format."""
        return generate_latest(self.registry).decode('utf-8')
    
    def get_metrics_content_type(self) -> str:
        """Get content type for metrics endpoint."""
        return CONTENT_TYPE_LATEST
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics about registered metrics."""
        return {
            "total_metrics": len(self._metrics),
            "metric_types": {
                metric_type.value: sum(
                    1 for config in self._metric_configs.values()
                    if self._get_metric_type(config.name) == metric_type
                )
                for metric_type in MetricType
            },
            "metrics": list(self._metrics.keys())
        }
    
    def _get_metric_type(self, name: str) -> Optional[MetricType]:
        """Get the type of a registered metric."""
        metric = self._metrics.get(name)
        if metric:
            if hasattr(metric, 'inc'):
                return MetricType.COUNTER
            elif hasattr(metric, 'observe') and hasattr(metric, '_buckets'):
                return MetricType.HISTOGRAM
            elif hasattr(metric, 'set'):
                return MetricType.GAUGE
            elif hasattr(metric, 'observe'):
                return MetricType.SUMMARY
            elif hasattr(metric, 'info'):
                return MetricType.INFO
            elif hasattr(metric, 'state'):
                return MetricType.ENUM
        return None


# Global metrics manager
metrics_manager = MetricsManager()


def track_time(
    metric_name: str,
    labels: Optional[Dict[str, str]] = None
):
    """
    Decorator to track execution time in histogram metric.
    
    Args:
        metric_name: Name of the histogram metric
        labels: Optional labels for the metric
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Record success
                duration = time.time() - start_time
                metrics_manager.observe_histogram(
                    metric_name,
                    duration,
                    labels
                )
                
                return result
            except Exception as e:
                # Record failure with error label
                duration = time.time() - start_time
                error_labels = (labels or {}).copy()
                error_labels["status"] = "error"
                
                metrics_manager.observe_histogram(
                    metric_name,
                    duration,
                    error_labels
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                metrics_manager.observe_histogram(
                    metric_name,
                    duration,
                    labels
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                error_labels = (labels or {}).copy()
                error_labels["status"] = "error"
                
                metrics_manager.observe_histogram(
                    metric_name,
                    duration,
                    error_labels
                )
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def count_calls(
    metric_name: str,
    labels: Optional[Dict[str, str]] = None
):
    """
    Decorator to count function calls.
    
    Args:
        metric_name: Name of the counter metric
        labels: Optional labels for the metric
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Increment success counter
                success_labels = (labels or {}).copy()
                success_labels["status"] = "success"
                metrics_manager.increment_counter(metric_name, success_labels)
                
                return result
            except Exception as e:
                # Increment error counter
                error_labels = (labels or {}).copy()
                error_labels["status"] = "error"
                error_labels["error_type"] = type(e).__name__
                metrics_manager.increment_counter(metric_name, error_labels)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                success_labels = (labels or {}).copy()
                success_labels["status"] = "success"
                metrics_manager.increment_counter(metric_name, success_labels)
                
                return result
            except Exception as e:
                error_labels = (labels or {}).copy()
                error_labels["status"] = "error"
                error_labels["error_type"] = type(e).__name__
                metrics_manager.increment_counter(metric_name, error_labels)
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class BusinessMetrics:
    """Helper class for tracking business-specific metrics."""
    
    @staticmethod
    def record_investigation_created(
        priority: str = "medium",
        user_type: str = "regular"
    ):
        """Record investigation creation."""
        metrics_manager.increment_counter(
            "cidadao_ai_investigations_total",
            {
                "status": "created",
                "priority": priority,
                "user_type": user_type
            }
        )
    
    @staticmethod
    def record_investigation_completed(
        investigation_type: str,
        duration_seconds: float,
        priority: str = "medium"
    ):
        """Record investigation completion."""
        metrics_manager.increment_counter(
            "cidadao_ai_investigations_total",
            {
                "status": "completed",
                "priority": priority,
                "user_type": "regular"
            }
        )
        
        metrics_manager.observe_histogram(
            "cidadao_ai_investigation_duration_seconds",
            duration_seconds,
            {"investigation_type": investigation_type}
        )
    
    @staticmethod
    def record_anomaly_detected(
        anomaly_type: str,
        severity: str,
        data_source: str,
        confidence_score: float
    ):
        """Record anomaly detection."""
        metrics_manager.increment_counter(
            "cidadao_ai_anomalies_detected_total",
            {
                "anomaly_type": anomaly_type,
                "severity": severity,
                "data_source": data_source
            }
        )
        
        metrics_manager.observe_histogram(
            "cidadao_ai_anomaly_confidence_score",
            confidence_score,
            {"anomaly_type": anomaly_type}
        )
    
    @staticmethod
    def record_transparency_api_call(
        api_name: str,
        endpoint: str,
        status_code: int,
        records_fetched: int = 0
    ):
        """Record transparency API usage."""
        metrics_manager.increment_counter(
            "cidadao_ai_transparency_api_requests_total",
            {
                "api_name": api_name,
                "endpoint": endpoint,
                "status_code": str(status_code)
            }
        )
        
        if records_fetched > 0:
            metrics_manager.increment_counter(
                "cidadao_ai_transparency_data_fetched_total",
                {
                    "data_type": endpoint,
                    "source": api_name
                },
                amount=records_fetched
            )
    
    @staticmethod
    def update_active_investigations(count: int):
        """Update active investigations gauge."""
        metrics_manager.set_gauge(
            "cidadao_ai_active_investigations",
            count
        )
    
    @staticmethod
    def record_agent_task(
        agent_name: str,
        task_type: str,
        duration_seconds: float,
        status: str = "success"
    ):
        """Record agent task execution."""
        metrics_manager.increment_counter(
            "cidadao_ai_agent_tasks_total",
            {
                "agent_name": agent_name,
                "task_type": task_type,
                "status": status
            }
        )
        
        metrics_manager.observe_histogram(
            "cidadao_ai_agent_task_duration_seconds",
            duration_seconds,
            {
                "agent_name": agent_name,
                "task_type": task_type
            }
        )


# Initialize application info metric
def initialize_app_info(
    version: str = "1.0.0",
    environment: str = "development",
    build_info: Optional[Dict[str, str]] = None
):
    """Initialize application info metric."""
    info_data = {
        "version": version,
        "environment": environment
    }
    
    if build_info:
        info_data.update(build_info)
    
    metrics_manager.set_info("cidadao_ai_info", info_data)