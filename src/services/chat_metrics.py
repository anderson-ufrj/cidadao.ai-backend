"""
Chat-specific metrics for monitoring the chat system.

This module provides Prometheus metrics for:
1. Response time by intent category
2. Intent detection accuracy
3. Agent usage distribution
4. Error rates by type

Author: Anderson Henrique da Silva
Created: 2025-12-02
"""

import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from src.core import get_logger

logger = get_logger(__name__)

# Try to import prometheus_client
try:
    from prometheus_client import Counter, Gauge, Histogram

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("prometheus_client not available, using in-memory metrics")


class MetricCategory(str, Enum):
    """Categories for response time metrics."""

    GREETING = "greeting"
    HELP = "help"
    INVESTIGATE = "investigate"
    ANALYZE = "analyze"
    REPORT = "report"
    ABOUT_SYSTEM = "about_system"
    QUESTION = "question"
    OTHER = "other"


@dataclass
class ChatMetricsData:
    """In-memory storage for chat metrics when Prometheus is not available."""

    # Response time tracking
    response_times: dict[str, list[float]] = field(default_factory=dict)

    # Intent detection tracking
    intent_detections: dict[str, int] = field(
        default_factory=lambda: {
            "correct": 0,
            "incorrect": 0,
            "unknown": 0,
        }
    )

    # Agent usage tracking
    agent_usage: dict[str, int] = field(default_factory=dict)

    # Error tracking
    errors_by_type: dict[str, int] = field(default_factory=dict)

    # Request tracking
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    # Session tracking
    active_sessions: int = 0
    total_sessions: int = 0


# Singleton metrics data
_metrics_data = ChatMetricsData()


# Prometheus metrics (if available)
if PROMETHEUS_AVAILABLE:
    # Response time histogram by category
    CHAT_RESPONSE_TIME = Histogram(
        "cidadao_chat_response_time_seconds",
        "Chat response time in seconds",
        ["category", "agent_id"],
        buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
    )

    # Intent detection counter
    INTENT_DETECTION_TOTAL = Counter(
        "cidadao_intent_detection_total",
        "Total intent detections",
        ["intent_type", "result"],
    )

    # Agent usage counter
    AGENT_USAGE_TOTAL = Counter(
        "cidadao_agent_usage_total",
        "Total agent usage",
        ["agent_id", "intent_type"],
    )

    # Error counter
    CHAT_ERRORS_TOTAL = Counter(
        "cidadao_chat_errors_total",
        "Total chat errors",
        ["error_type", "agent_id"],
    )

    # Active sessions gauge
    ACTIVE_SESSIONS = Gauge(
        "cidadao_active_sessions",
        "Number of active chat sessions",
    )

    # Request counter
    CHAT_REQUESTS_TOTAL = Counter(
        "cidadao_chat_requests_total",
        "Total chat requests",
        ["status", "endpoint"],
    )

    # Instant response counter
    INSTANT_RESPONSES_TOTAL = Counter(
        "cidadao_instant_responses_total",
        "Total instant responses (no LLM)",
        ["intent_type"],
    )


def record_response_time(
    category: str,
    agent_id: str,
    response_time: float,
) -> None:
    """
    Record chat response time.

    Args:
        category: Intent category (greeting, investigate, etc.)
        agent_id: Agent that handled the request
        response_time: Time in seconds
    """
    if PROMETHEUS_AVAILABLE:
        CHAT_RESPONSE_TIME.labels(category=category, agent_id=agent_id).observe(
            response_time
        )

    # Also store in memory for non-Prometheus access
    key = f"{category}:{agent_id}"
    if key not in _metrics_data.response_times:
        _metrics_data.response_times[key] = []
    _metrics_data.response_times[key].append(response_time)

    # Keep only last MAX_RESPONSE_ENTRIES entries per category
    max_entries = 1000
    if len(_metrics_data.response_times[key]) > max_entries:
        _metrics_data.response_times[key] = _metrics_data.response_times[key][
            -max_entries:
        ]


def record_intent_detection(
    intent_type: str,
    result: str = "detected",
) -> None:
    """
    Record intent detection result.

    Args:
        intent_type: Detected intent type
        result: "correct", "incorrect", or "unknown"
    """
    if PROMETHEUS_AVAILABLE:
        INTENT_DETECTION_TOTAL.labels(intent_type=intent_type, result=result).inc()

    if result in _metrics_data.intent_detections:
        _metrics_data.intent_detections[result] += 1


def record_agent_usage(agent_id: str, intent_type: str) -> None:
    """
    Record agent usage.

    Args:
        agent_id: Agent that handled the request
        intent_type: Intent type for the request
    """
    if PROMETHEUS_AVAILABLE:
        AGENT_USAGE_TOTAL.labels(agent_id=agent_id, intent_type=intent_type).inc()

    if agent_id not in _metrics_data.agent_usage:
        _metrics_data.agent_usage[agent_id] = 0
    _metrics_data.agent_usage[agent_id] += 1


def record_error(error_type: str, agent_id: str = "unknown") -> None:
    """
    Record chat error.

    Args:
        error_type: Type of error (timeout, llm_error, validation_error, etc.)
        agent_id: Agent that encountered the error
    """
    if PROMETHEUS_AVAILABLE:
        CHAT_ERRORS_TOTAL.labels(error_type=error_type, agent_id=agent_id).inc()

    if error_type not in _metrics_data.errors_by_type:
        _metrics_data.errors_by_type[error_type] = 0
    _metrics_data.errors_by_type[error_type] += 1
    _metrics_data.failed_requests += 1


def record_request(status: str = "success", endpoint: str = "/message") -> None:
    """
    Record chat request.

    Args:
        status: Request status (success, error, timeout)
        endpoint: Chat endpoint (/message, /stream)
    """
    if PROMETHEUS_AVAILABLE:
        CHAT_REQUESTS_TOTAL.labels(status=status, endpoint=endpoint).inc()

    _metrics_data.total_requests += 1
    if status == "success":
        _metrics_data.successful_requests += 1


def record_instant_response(intent_type: str) -> None:
    """
    Record instant response (no LLM call).

    Args:
        intent_type: Intent type that got instant response
    """
    if PROMETHEUS_AVAILABLE:
        INSTANT_RESPONSES_TOTAL.labels(intent_type=intent_type).inc()


def update_active_sessions(count: int) -> None:
    """
    Update active sessions gauge.

    Args:
        count: Number of active sessions
    """
    if PROMETHEUS_AVAILABLE:
        ACTIVE_SESSIONS.set(count)
    _metrics_data.active_sessions = count


def increment_session_count() -> None:
    """Increment total session count."""
    _metrics_data.total_sessions += 1


def get_chat_metrics_summary() -> dict[str, Any]:
    """
    Get summary of chat metrics.

    Returns:
        Dict with metrics summary
    """
    # Calculate response time stats
    response_time_stats = {}
    for key, times in _metrics_data.response_times.items():
        if times:
            response_time_stats[key] = {
                "count": len(times),
                "avg": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
                "p50": sorted(times)[len(times) // 2] if times else 0,
                "p95": (
                    sorted(times)[int(len(times) * 0.95)]
                    if len(times) > 1
                    else (times[0] if times else 0)
                ),
            }

    # Calculate agent usage percentages
    total_agent_usage = sum(_metrics_data.agent_usage.values())
    agent_usage_pct = {}
    if total_agent_usage > 0:
        for agent, count in _metrics_data.agent_usage.items():
            agent_usage_pct[agent] = {
                "count": count,
                "percentage": round(count / total_agent_usage * 100, 2),
            }

    # Calculate intent detection accuracy
    total_intents = sum(_metrics_data.intent_detections.values())
    intent_accuracy = 0.0
    if total_intents > 0:
        correct = _metrics_data.intent_detections.get("correct", 0)
        intent_accuracy = round(correct / total_intents * 100, 2)

    # Calculate error rate
    error_rate = 0.0
    if _metrics_data.total_requests > 0:
        error_rate = round(
            _metrics_data.failed_requests / _metrics_data.total_requests * 100, 2
        )

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "requests": {
            "total": _metrics_data.total_requests,
            "successful": _metrics_data.successful_requests,
            "failed": _metrics_data.failed_requests,
            "error_rate_pct": error_rate,
        },
        "sessions": {
            "active": _metrics_data.active_sessions,
            "total": _metrics_data.total_sessions,
        },
        "response_times": response_time_stats,
        "intent_detection": {
            "total": total_intents,
            "accuracy_pct": intent_accuracy,
            "breakdown": _metrics_data.intent_detections,
        },
        "agent_usage": agent_usage_pct,
        "errors_by_type": _metrics_data.errors_by_type,
    }


def reset_metrics() -> None:
    """Reset all in-memory metrics. Useful for testing."""
    global _metrics_data  # noqa: PLW0603
    _metrics_data = ChatMetricsData()


class ChatMetricsContext:
    """
    Context manager for tracking chat request metrics.

    Usage:
        async with ChatMetricsContext(intent_type="greeting", agent_id="drummond") as ctx:
            # Process chat request
            ctx.mark_success()
    """

    def __init__(
        self,
        intent_type: str = "unknown",
        agent_id: str = "unknown",
        endpoint: str = "/message",
    ) -> None:
        self.intent_type = intent_type
        self.agent_id = agent_id
        self.endpoint = endpoint
        self.start_time = 0.0
        self._success = False
        self._error_type: str | None = None

    async def __aenter__(self) -> "ChatMetricsContext":
        self.start_time = time.time()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        response_time = time.time() - self.start_time

        # Record response time
        record_response_time(self.intent_type, self.agent_id, response_time)

        # Record agent usage
        record_agent_usage(self.agent_id, self.intent_type)

        # Record request status
        if exc_type is not None:
            record_error(str(exc_type.__name__), self.agent_id)
            record_request("error", self.endpoint)
        elif self._error_type:
            record_error(self._error_type, self.agent_id)
            record_request("error", self.endpoint)
        else:
            record_request("success", self.endpoint)

    def mark_success(self) -> None:
        """Mark request as successful."""
        self._success = True

    def mark_error(self, error_type: str) -> None:
        """Mark request as failed with error type."""
        self._error_type = error_type

    def update_agent(self, agent_id: str) -> None:
        """Update agent ID (useful when determined later)."""
        self.agent_id = agent_id

    def update_intent(self, intent_type: str) -> None:
        """Update intent type (useful when determined later)."""
        self.intent_type = intent_type
