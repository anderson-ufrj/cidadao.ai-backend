"""
Agent Performance Metrics Service.
Collects and exposes metrics for agent performance monitoring.
"""

import asyncio
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Optional

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from src.core import get_logger
from src.services.cache_service import cache_result

logger = get_logger("agent.metrics")

# Prometheus metrics registry
registry = CollectorRegistry()

# Agent metrics
agent_requests_total = Counter(
    "agent_requests_total",
    "Total number of agent requests",
    ["agent_name", "action", "status"],
    registry=registry,
)

agent_request_duration = Histogram(
    "agent_request_duration_seconds",
    "Agent request duration in seconds",
    ["agent_name", "action"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
    registry=registry,
)

agent_active_requests = Gauge(
    "agent_active_requests",
    "Number of active agent requests",
    ["agent_name"],
    registry=registry,
)

agent_error_rate = Gauge(
    "agent_error_rate",
    "Agent error rate (last 5 minutes)",
    ["agent_name"],
    registry=registry,
)

agent_memory_usage = Gauge(
    "agent_memory_usage_bytes",
    "Agent memory usage in bytes",
    ["agent_name"],
    registry=registry,
)

agent_reflection_iterations = Histogram(
    "agent_reflection_iterations",
    "Number of reflection iterations per request",
    ["agent_name"],
    buckets=(0, 1, 2, 3, 4, 5, 10),
    registry=registry,
)

agent_quality_score = Histogram(
    "agent_quality_score",
    "Agent response quality score",
    ["agent_name", "action"],
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    registry=registry,
)


@dataclass
class AgentMetrics:
    """Detailed metrics for a specific agent."""

    agent_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration_seconds: float = 0.0
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    error_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    actions_count: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_error: Optional[str] = None
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    quality_scores: deque = field(default_factory=lambda: deque(maxlen=100))
    reflection_counts: deque = field(default_factory=lambda: deque(maxlen=100))
    memory_samples: deque = field(default_factory=lambda: deque(maxlen=60))


class AgentMetricsService:
    """Service for collecting and managing agent performance metrics."""

    def __init__(self):
        self.logger = logger
        self._agent_metrics: dict[str, AgentMetrics] = {}
        self._start_time = datetime.now(UTC)
        self._lock = asyncio.Lock()

    def _get_or_create_metrics(self, agent_name: str) -> AgentMetrics:
        """Get or create metrics for an agent."""
        if agent_name not in self._agent_metrics:
            self._agent_metrics[agent_name] = AgentMetrics(agent_name=agent_name)
        return self._agent_metrics[agent_name]

    async def record_request_start(self, agent_name: str, action: str) -> str:
        """Record the start of an agent request."""
        request_id = f"{agent_name}_{action}_{time.time()}"

        # Increment active requests
        agent_active_requests.labels(agent_name=agent_name).inc()

        return request_id

    async def record_request_end(
        self,
        request_id: str,
        agent_name: str,
        action: str,
        duration: float,
        success: bool,
        error: Optional[str] = None,
        quality_score: Optional[float] = None,
        reflection_iterations: int = 0,
    ):
        """Record the end of an agent request."""
        async with self._lock:
            metrics = self._get_or_create_metrics(agent_name)

            # Update counters
            metrics.total_requests += 1
            if success:
                metrics.successful_requests += 1
                metrics.last_success_time = datetime.now(UTC)
                status = "success"
            else:
                metrics.failed_requests += 1
                metrics.last_failure_time = datetime.now(UTC)
                metrics.last_error = error
                metrics.error_times.append(datetime.now(UTC))
                status = "failure"

            # Update duration metrics
            metrics.total_duration_seconds += duration
            metrics.response_times.append(duration)

            # Update action count
            metrics.actions_count[action] += 1

            # Update quality metrics
            if quality_score is not None:
                metrics.quality_scores.append(quality_score)
                agent_quality_score.labels(
                    agent_name=agent_name, action=action
                ).observe(quality_score)

            # Update reflection metrics
            metrics.reflection_counts.append(reflection_iterations)
            agent_reflection_iterations.labels(agent_name=agent_name).observe(
                reflection_iterations
            )

            # Update Prometheus metrics
            agent_requests_total.labels(
                agent_name=agent_name, action=action, status=status
            ).inc()

            agent_request_duration.labels(agent_name=agent_name, action=action).observe(
                duration
            )

            # Decrement active requests
            agent_active_requests.labels(agent_name=agent_name).dec()

            # Update error rate (last 5 minutes)
            error_rate = self._calculate_error_rate(metrics)
            agent_error_rate.labels(agent_name=agent_name).set(error_rate)

    def _calculate_error_rate(self, metrics: AgentMetrics) -> float:
        """Calculate error rate for the last 5 minutes."""
        cutoff_time = datetime.now(UTC) - timedelta(minutes=5)
        recent_errors = sum(1 for t in metrics.error_times if t > cutoff_time)

        # Calculate total requests in the same period
        if metrics.total_requests == 0:
            return 0.0

        # Estimate requests in window (simplified)
        window_ratio = min(1.0, 300 / metrics.total_duration_seconds)  # 5 minutes
        estimated_requests = max(1, int(metrics.total_requests * window_ratio))

        return min(1.0, recent_errors / estimated_requests)

    async def record_memory_usage(self, agent_name: str, memory_bytes: int):
        """Record agent memory usage."""
        async with self._lock:
            metrics = self._get_or_create_metrics(agent_name)
            metrics.memory_samples.append(memory_bytes)

            # Update Prometheus metric
            agent_memory_usage.labels(agent_name=agent_name).set(memory_bytes)

    @cache_result(prefix="agent_stats", ttl=30)
    async def get_agent_stats(self, agent_name: str) -> dict[str, Any]:
        """Get comprehensive stats for a specific agent."""
        async with self._lock:
            metrics = self._agent_metrics.get(agent_name)

            if not metrics:
                return {"agent_name": agent_name, "status": "no_data"}

            response_times = list(metrics.response_times)
            quality_scores = list(metrics.quality_scores)
            reflection_counts = list(metrics.reflection_counts)

            return {
                "agent_name": agent_name,
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "success_rate": (
                    metrics.successful_requests / metrics.total_requests
                    if metrics.total_requests > 0
                    else 0
                ),
                "error_rate": self._calculate_error_rate(metrics),
                "response_time": {
                    "mean": statistics.mean(response_times) if response_times else 0,
                    "median": (
                        statistics.median(response_times) if response_times else 0
                    ),
                    "p95": (
                        self._percentile(response_times, 95) if response_times else 0
                    ),
                    "p99": (
                        self._percentile(response_times, 99) if response_times else 0
                    ),
                    "min": min(response_times) if response_times else 0,
                    "max": max(response_times) if response_times else 0,
                },
                "quality": {
                    "mean": statistics.mean(quality_scores) if quality_scores else 0,
                    "median": (
                        statistics.median(quality_scores) if quality_scores else 0
                    ),
                    "min": min(quality_scores) if quality_scores else 0,
                    "max": max(quality_scores) if quality_scores else 0,
                },
                "reflection": {
                    "mean_iterations": (
                        statistics.mean(reflection_counts) if reflection_counts else 0
                    ),
                    "max_iterations": (
                        max(reflection_counts) if reflection_counts else 0
                    ),
                },
                "actions": dict(metrics.actions_count),
                "last_error": metrics.last_error,
                "last_success_time": (
                    metrics.last_success_time.isoformat()
                    if metrics.last_success_time
                    else None
                ),
                "last_failure_time": (
                    metrics.last_failure_time.isoformat()
                    if metrics.last_failure_time
                    else None
                ),
                "memory_usage": {
                    "current": (
                        metrics.memory_samples[-1] if metrics.memory_samples else 0
                    ),
                    "mean": (
                        statistics.mean(metrics.memory_samples)
                        if metrics.memory_samples
                        else 0
                    ),
                    "max": max(metrics.memory_samples) if metrics.memory_samples else 0,
                },
            }

    async def get_all_agents_summary(self) -> dict[str, Any]:
        """Get summary stats for all agents."""
        async with self._lock:
            summary = {
                "total_agents": len(self._agent_metrics),
                "total_requests": sum(
                    m.total_requests for m in self._agent_metrics.values()
                ),
                "total_successful": sum(
                    m.successful_requests for m in self._agent_metrics.values()
                ),
                "total_failed": sum(
                    m.failed_requests for m in self._agent_metrics.values()
                ),
                "uptime_seconds": (
                    datetime.now(UTC) - self._start_time
                ).total_seconds(),
                "agents": {},
            }

            for agent_name, metrics in self._agent_metrics.items():
                response_times = list(metrics.response_times)
                summary["agents"][agent_name] = {
                    "requests": metrics.total_requests,
                    "success_rate": (
                        metrics.successful_requests / metrics.total_requests
                        if metrics.total_requests > 0
                        else 0
                    ),
                    "avg_response_time": (
                        statistics.mean(response_times) if response_times else 0
                    ),
                    "error_rate": self._calculate_error_rate(metrics),
                }

            return summary

    def _percentile(self, data: list[float], percentile: float) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0

        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))

        if index >= len(sorted_data):
            return sorted_data[-1]

        return sorted_data[index]

    def get_prometheus_metrics(self) -> bytes:
        """Get Prometheus metrics in text format."""
        return generate_latest(registry)

    async def reset_metrics(self, agent_name: Optional[str] = None):
        """Reset metrics for specific agent or all agents."""
        async with self._lock:
            if agent_name:
                if agent_name in self._agent_metrics:
                    self._agent_metrics[agent_name] = AgentMetrics(
                        agent_name=agent_name
                    )
            else:
                self._agent_metrics.clear()
                self._start_time = datetime.now(UTC)


# Global metrics service instance
agent_metrics_service = AgentMetricsService()


class MetricsCollector:
    """Context manager for collecting agent metrics."""

    def __init__(
        self,
        agent_name: str,
        action: str,
        metrics_service: Optional[AgentMetricsService] = None,
    ):
        self.agent_name = agent_name
        self.action = action
        self.metrics_service = metrics_service or agent_metrics_service
        self.start_time = None
        self.request_id = None
        self.quality_score = None
        self.reflection_iterations = 0

    async def __aenter__(self):
        """Start metrics collection."""
        self.start_time = time.time()
        self.request_id = await self.metrics_service.record_request_start(
            self.agent_name, self.action
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """End metrics collection."""
        duration = time.time() - self.start_time
        success = exc_type is None
        error = str(exc_val) if exc_val else None

        await self.metrics_service.record_request_end(
            request_id=self.request_id,
            agent_name=self.agent_name,
            action=self.action,
            duration=duration,
            success=success,
            error=error,
            quality_score=self.quality_score,
            reflection_iterations=self.reflection_iterations,
        )

        # Don't suppress exceptions
        return False

    def set_quality_score(self, score: float):
        """Set the quality score for the response."""
        self.quality_score = score

    def increment_reflection(self):
        """Increment reflection iteration count."""
        self.reflection_iterations += 1


async def collect_system_metrics():
    """Collect system-wide agent metrics periodically."""
    while True:
        try:
            # Collect memory metrics for active agents
            # This would integrate with the agent pool to get actual memory usage

            await asyncio.sleep(60)  # Collect every minute

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            await asyncio.sleep(60)
