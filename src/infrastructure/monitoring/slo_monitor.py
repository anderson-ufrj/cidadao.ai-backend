"""
SLA/SLO monitoring system for tracking service level objectives.

This module provides comprehensive SLA/SLO tracking with automated
alerting and reporting capabilities.
"""

import asyncio
import statistics
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from src.infrastructure.observability import BusinessMetrics, get_structured_logger

logger = get_structured_logger(__name__, component="slo_monitor")


class SLOType(str, Enum):
    """Types of SLO metrics."""

    AVAILABILITY = "availability"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    CUSTOM = "custom"


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class TimeWindow(str, Enum):
    """Time windows for SLO calculations."""

    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    HOUR_24 = "24h"
    DAY_7 = "7d"
    DAY_30 = "30d"


@dataclass
class SLOTarget:
    """SLO target definition."""

    name: str
    slo_type: SLOType
    target_value: float  # Target threshold (e.g., 99.9 for 99.9% availability)
    time_window: TimeWindow
    description: str
    warning_threshold: float = 95.0  # % of target that triggers warning
    critical_threshold: float = 90.0  # % of target that triggers critical alert

    def get_warning_value(self) -> float:
        """Get warning threshold value."""
        return self.target_value * (self.warning_threshold / 100)

    def get_critical_value(self) -> float:
        """Get critical threshold value."""
        return self.target_value * (self.critical_threshold / 100)


@dataclass
class SLOMetric:
    """Single SLO metric measurement."""

    timestamp: datetime
    value: float
    success: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SLOViolation:
    """SLO violation record."""

    slo_name: str
    violation_time: datetime
    actual_value: float
    target_value: float
    severity: AlertSeverity
    duration_minutes: float
    details: dict[str, Any] = field(default_factory=dict)


class SLOCalculator:
    """Calculator for different types of SLO metrics."""

    @staticmethod
    def calculate_availability(metrics: list[SLOMetric]) -> float:
        """Calculate availability percentage."""
        if not metrics:
            return 0.0

        successful = sum(1 for m in metrics if m.success)
        total = len(metrics)

        return (successful / total) * 100

    @staticmethod
    def calculate_latency_percentile(
        metrics: list[SLOMetric], percentile: float = 95.0
    ) -> float:
        """Calculate latency percentile."""
        if not metrics:
            return 0.0

        values = [m.value for m in metrics]
        return (
            statistics.quantiles(values, n=100)[int(percentile) - 1]
            if len(values) > 1
            else values[0]
        )

    @staticmethod
    def calculate_error_rate(metrics: list[SLOMetric]) -> float:
        """Calculate error rate percentage."""
        if not metrics:
            return 0.0

        errors = sum(1 for m in metrics if not m.success)
        total = len(metrics)

        return (errors / total) * 100

    @staticmethod
    def calculate_throughput(
        metrics: list[SLOMetric], time_window_minutes: float
    ) -> float:
        """Calculate throughput (requests per minute)."""
        if not metrics or time_window_minutes <= 0:
            return 0.0

        return len(metrics) / time_window_minutes

    @staticmethod
    def calculate_custom(metrics: list[SLOMetric], calculation_func: Callable) -> float:
        """Calculate custom metric using provided function."""
        return calculation_func(metrics)


class SLOMonitor:
    """
    Monitor for tracking SLA/SLO compliance.

    Features:
    - Real-time SLO tracking
    - Automated violation detection
    - Alert generation
    - Historical trend analysis
    - Error budget tracking
    """

    def __init__(self, max_history_size: int = 10000):
        """
        Initialize SLO monitor.

        Args:
            max_history_size: Maximum number of metrics to keep in memory
        """
        self.max_history_size = max_history_size

        # SLO definitions
        self.slo_targets: dict[str, SLOTarget] = {}

        # Metric storage
        self.metrics: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_history_size)
        )

        # Violation tracking
        self.violations: dict[str, list[SLOViolation]] = defaultdict(list)
        self.current_violations: dict[str, SLOViolation] = {}

        # Alert callbacks
        self.alert_callbacks: list[Callable] = []

        # Calculator
        self.calculator = SLOCalculator()

        # Statistics
        self.stats = {"total_measurements": 0, "total_violations": 0, "alerts_sent": 0}

        self.logger = get_structured_logger(__name__, component="slo_monitor")

        # Initialize default SLOs
        self._initialize_default_slos()

    def _initialize_default_slos(self):
        """Initialize default SLO targets for Cidadão.AI."""
        # API Availability
        self.register_slo(
            SLOTarget(
                name="api_availability",
                slo_type=SLOType.AVAILABILITY,
                target_value=99.9,  # 99.9% uptime
                time_window=TimeWindow.HOUR_24,
                description="API endpoint availability over 24 hours",
                warning_threshold=98.0,
                critical_threshold=95.0,
            )
        )

        # API Response Time
        self.register_slo(
            SLOTarget(
                name="api_latency_p95",
                slo_type=SLOType.LATENCY,
                target_value=2000.0,  # 2 seconds P95
                time_window=TimeWindow.HOUR_1,
                description="95th percentile API response time under 2 seconds",
                warning_threshold=90.0,
                critical_threshold=80.0,
            )
        )

        # Investigation Success Rate
        self.register_slo(
            SLOTarget(
                name="investigation_success_rate",
                slo_type=SLOType.AVAILABILITY,
                target_value=95.0,  # 95% success rate
                time_window=TimeWindow.HOUR_4,
                description="Investigation completion success rate",
                warning_threshold=92.0,
                critical_threshold=88.0,
            )
        )

        # Agent Task Error Rate
        self.register_slo(
            SLOTarget(
                name="agent_error_rate",
                slo_type=SLOType.ERROR_RATE,
                target_value=1.0,  # < 1% error rate
                time_window=TimeWindow.HOUR_1,
                description="Agent task error rate under 1%",
                warning_threshold=80.0,
                critical_threshold=60.0,
            )
        )

        # Database Query Performance
        self.register_slo(
            SLOTarget(
                name="database_latency_p90",
                slo_type=SLOType.LATENCY,
                target_value=500.0,  # 500ms P90
                time_window=TimeWindow.MINUTE_15,
                description="90th percentile database query time under 500ms",
                warning_threshold=85.0,
                critical_threshold=70.0,
            )
        )

        # Anomaly Detection Accuracy
        self.register_slo(
            SLOTarget(
                name="anomaly_detection_accuracy",
                slo_type=SLOType.CUSTOM,
                target_value=90.0,  # 90% accuracy
                time_window=TimeWindow.HOUR_24,
                description="Anomaly detection accuracy rate",
                warning_threshold=95.0,
                critical_threshold=90.0,
            )
        )

    def register_slo(self, slo_target: SLOTarget):
        """Register an SLO target for monitoring."""
        self.slo_targets[slo_target.name] = slo_target

        self.logger.info(
            f"Registered SLO: {slo_target.name}",
            operation="register_slo",
            slo_type=slo_target.slo_type.value,
            target_value=slo_target.target_value,
            time_window=slo_target.time_window.value,
        )

    def register_alert_callback(self, callback: Callable[[SLOViolation], None]):
        """Register callback for SLO violation alerts."""
        self.alert_callbacks.append(callback)

    def record_metric(
        self,
        slo_name: str,
        value: float,
        success: bool = True,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """
        Record a metric for SLO monitoring.

        Args:
            slo_name: Name of the SLO
            value: Metric value
            success: Whether the operation was successful
            metadata: Additional metadata
        """
        if slo_name not in self.slo_targets:
            self.logger.warning(f"Unknown SLO: {slo_name}")
            return

        metric = SLOMetric(
            timestamp=datetime.utcnow(),
            value=value,
            success=success,
            metadata=metadata or {},
        )

        self.metrics[slo_name].append(metric)
        self.stats["total_measurements"] += 1

        # Check for violations
        asyncio.create_task(self._check_slo_compliance(slo_name))

        self.logger.debug(
            f"Recorded metric for SLO: {slo_name}",
            operation="record_metric",
            value=value,
            success=success,
        )

    async def _check_slo_compliance(self, slo_name: str):
        """Check SLO compliance and trigger alerts if needed."""
        if slo_name not in self.slo_targets:
            return

        slo_target = self.slo_targets[slo_name]
        current_value = await self.calculate_current_slo(slo_name)

        if current_value is None:
            return

        # Determine violation severity
        violation_severity = None

        if current_value < slo_target.get_critical_value():
            violation_severity = AlertSeverity.CRITICAL
        elif current_value < slo_target.get_warning_value():
            violation_severity = AlertSeverity.WARNING

        # Handle violation
        if violation_severity:
            await self._handle_violation(slo_name, current_value, violation_severity)
        else:
            # No violation, clear any existing violation
            await self._clear_violation(slo_name)

    async def _handle_violation(
        self, slo_name: str, actual_value: float, severity: AlertSeverity
    ):
        """Handle SLO violation."""
        slo_target = self.slo_targets[slo_name]
        now = datetime.utcnow()

        # Check if this is a new violation or continuation
        if slo_name in self.current_violations:
            # Update existing violation
            violation = self.current_violations[slo_name]
            violation.duration_minutes = (
                now - violation.violation_time
            ).total_seconds() / 60
            violation.actual_value = actual_value
            violation.severity = severity
        else:
            # New violation
            violation = SLOViolation(
                slo_name=slo_name,
                violation_time=now,
                actual_value=actual_value,
                target_value=slo_target.target_value,
                severity=severity,
                duration_minutes=0.0,
                details={
                    "slo_type": slo_target.slo_type.value,
                    "time_window": slo_target.time_window.value,
                    "description": slo_target.description,
                },
            )

            self.current_violations[slo_name] = violation
            self.violations[slo_name].append(violation)
            self.stats["total_violations"] += 1

            # Send alerts
            await self._send_alert(violation)

        self.logger.warning(
            f"SLO violation: {slo_name}",
            operation="slo_violation",
            actual_value=actual_value,
            target_value=slo_target.target_value,
            severity=severity.value,
            duration_minutes=violation.duration_minutes,
        )

    async def _clear_violation(self, slo_name: str):
        """Clear SLO violation when back in compliance."""
        if slo_name in self.current_violations:
            violation = self.current_violations.pop(slo_name)

            self.logger.info(
                f"SLO violation cleared: {slo_name}",
                operation="slo_violation_cleared",
                total_duration_minutes=violation.duration_minutes,
            )

    async def _send_alert(self, violation: SLOViolation):
        """Send alert for SLO violation."""
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(violation)
                else:
                    callback(violation)

                self.stats["alerts_sent"] += 1

            except Exception as e:
                self.logger.error(
                    f"Failed to send alert for {violation.slo_name}",
                    operation="send_alert",
                    error=e,
                )

    async def calculate_current_slo(self, slo_name: str) -> Optional[float]:
        """Calculate current SLO value."""
        if slo_name not in self.slo_targets:
            return None

        slo_target = self.slo_targets[slo_name]
        metrics = self._get_metrics_for_window(slo_name, slo_target.time_window)

        if not metrics:
            return None

        # Calculate based on SLO type
        if slo_target.slo_type == SLOType.AVAILABILITY:
            return self.calculator.calculate_availability(metrics)

        elif slo_target.slo_type == SLOType.LATENCY:
            # For latency SLOs, we want percentage under threshold
            under_threshold = sum(
                1 for m in metrics if m.value <= slo_target.target_value
            )
            return (under_threshold / len(metrics)) * 100

        elif slo_target.slo_type == SLOType.ERROR_RATE:
            error_rate = self.calculator.calculate_error_rate(metrics)
            # For error rate SLOs, we want percentage compliance (low error rate)
            return max(0, 100 - error_rate)

        elif slo_target.slo_type == SLOType.THROUGHPUT:
            time_window_minutes = self._get_time_window_minutes(slo_target.time_window)
            throughput = self.calculator.calculate_throughput(
                metrics, time_window_minutes
            )
            # Calculate percentage of target throughput achieved
            return min(100, (throughput / slo_target.target_value) * 100)

        elif slo_target.slo_type == SLOType.CUSTOM:
            # For custom SLOs, use the metric values directly
            if metrics:
                return statistics.mean(m.value for m in metrics)

        return None

    def _get_metrics_for_window(
        self, slo_name: str, time_window: TimeWindow
    ) -> list[SLOMetric]:
        """Get metrics for the specified time window."""
        if slo_name not in self.metrics:
            return []

        now = datetime.utcnow()
        window_minutes = self._get_time_window_minutes(time_window)
        cutoff_time = now - timedelta(minutes=window_minutes)

        return [
            metric
            for metric in self.metrics[slo_name]
            if metric.timestamp > cutoff_time
        ]

    def _get_time_window_minutes(self, time_window: TimeWindow) -> float:
        """Convert time window to minutes."""
        window_map = {
            TimeWindow.MINUTE_1: 1,
            TimeWindow.MINUTE_5: 5,
            TimeWindow.MINUTE_15: 15,
            TimeWindow.HOUR_1: 60,
            TimeWindow.HOUR_4: 240,
            TimeWindow.HOUR_24: 1440,
            TimeWindow.DAY_7: 10080,
            TimeWindow.DAY_30: 43200,
        }
        return window_map.get(time_window, 60)

    def get_slo_status(self, slo_name: str) -> dict[str, Any]:
        """Get current status of an SLO."""
        if slo_name not in self.slo_targets:
            return {"error": f"Unknown SLO: {slo_name}"}

        slo_target = self.slo_targets[slo_name]
        current_value = asyncio.run(self.calculate_current_slo(slo_name))

        # Calculate error budget
        if current_value is not None:
            error_budget_consumed = max(
                0,
                (slo_target.target_value - current_value)
                / slo_target.target_value
                * 100,
            )
        else:
            error_budget_consumed = 0

        # Get violation history
        recent_violations = [
            {
                "timestamp": v.violation_time.isoformat(),
                "severity": v.severity.value,
                "duration_minutes": v.duration_minutes,
                "actual_value": v.actual_value,
            }
            for v in self.violations[slo_name][-10:]  # Last 10 violations
        ]

        return {
            "slo_name": slo_name,
            "target": slo_target.target_value,
            "current_value": current_value,
            "compliance_percentage": (
                (current_value / slo_target.target_value * 100) if current_value else 0
            ),
            "error_budget_consumed_percentage": error_budget_consumed,
            "status": (
                "compliant" if slo_name not in self.current_violations else "violated"
            ),
            "time_window": slo_target.time_window.value,
            "description": slo_target.description,
            "current_violation": (
                {
                    "severity": self.current_violations[slo_name].severity.value,
                    "duration_minutes": self.current_violations[
                        slo_name
                    ].duration_minutes,
                    "started_at": self.current_violations[
                        slo_name
                    ].violation_time.isoformat(),
                }
                if slo_name in self.current_violations
                else None
            ),
            "recent_violations": recent_violations,
            "total_metrics": len(self.metrics[slo_name]),
        }

    def get_all_slo_status(self) -> dict[str, Any]:
        """Get status of all SLOs."""
        slo_statuses = {}

        for slo_name in self.slo_targets.keys():
            slo_statuses[slo_name] = self.get_slo_status(slo_name)

        # Calculate overall compliance
        compliant_slos = sum(
            1 for status in slo_statuses.values() if status.get("status") == "compliant"
        )

        total_slos = len(slo_statuses)
        overall_compliance = (
            (compliant_slos / total_slos * 100) if total_slos > 0 else 100
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_compliance_percentage": overall_compliance,
            "total_slos": total_slos,
            "compliant_slos": compliant_slos,
            "violated_slos": total_slos - compliant_slos,
            "statistics": self.stats,
            "slo_details": slo_statuses,
        }

    def get_error_budget_report(self) -> dict[str, Any]:
        """Get error budget consumption report."""
        report = {"timestamp": datetime.utcnow().isoformat(), "error_budgets": {}}

        for slo_name, slo_target in self.slo_targets.items():
            current_value = asyncio.run(self.calculate_current_slo(slo_name))

            if current_value is not None:
                # Calculate error budget
                budget_remaining = max(0, current_value - slo_target.target_value)
                budget_consumed = max(0, slo_target.target_value - current_value)
                budget_total = (
                    100 - slo_target.target_value
                )  # Assuming percentage-based

                consumption_percentage = (
                    (budget_consumed / budget_total * 100) if budget_total > 0 else 0
                )

                report["error_budgets"][slo_name] = {
                    "target": slo_target.target_value,
                    "current_value": current_value,
                    "budget_consumed": budget_consumed,
                    "budget_remaining": budget_remaining,
                    "consumption_percentage": consumption_percentage,
                    "status": (
                        "healthy"
                        if consumption_percentage < 50
                        else "warning" if consumption_percentage < 80 else "critical"
                    ),
                    "time_window": slo_target.time_window.value,
                }

        return report


# Global SLO monitor
slo_monitor = SLOMonitor()


# Convenience functions for common metrics
def record_api_request(endpoint: str, response_time_ms: float, success: bool):
    """Record API request metrics for SLO monitoring."""
    slo_monitor.record_metric("api_availability", 1.0, success, {"endpoint": endpoint})
    slo_monitor.record_metric(
        "api_latency_p95", response_time_ms, success, {"endpoint": endpoint}
    )


def record_investigation_result(
    investigation_id: str, success: bool, duration_ms: float
):
    """Record investigation result for SLO monitoring."""
    slo_monitor.record_metric(
        "investigation_success_rate",
        1.0,
        success,
        {"investigation_id": investigation_id, "duration_ms": duration_ms},
    )


def record_agent_task(
    agent_name: str, task_type: str, success: bool, duration_ms: float
):
    """Record agent task for SLO monitoring."""
    slo_monitor.record_metric(
        "agent_error_rate",
        1.0,
        success,
        {"agent_name": agent_name, "task_type": task_type, "duration_ms": duration_ms},
    )


def record_database_query(query_type: str, duration_ms: float, success: bool):
    """Record database query for SLO monitoring."""
    slo_monitor.record_metric(
        "database_latency_p90", duration_ms, success, {"query_type": query_type}
    )


def record_anomaly_detection(true_positive: bool, false_positive: bool):
    """Record anomaly detection accuracy."""
    if true_positive:
        accuracy = 100.0
    elif false_positive:
        accuracy = 0.0
    else:
        accuracy = 50.0  # Unknown case

    slo_monitor.record_metric(
        "anomaly_detection_accuracy",
        accuracy,
        True,
        {"true_positive": true_positive, "false_positive": false_positive},
    )


# Default alert callback
async def default_alert_callback(violation: SLOViolation):
    """Default alert callback that logs violations."""
    logger.warning(
        f"SLO VIOLATION ALERT: {violation.slo_name}",
        operation="slo_alert",
        severity=violation.severity.value,
        actual_value=violation.actual_value,
        target_value=violation.target_value,
        duration_minutes=violation.duration_minutes,
    )

    # Record alert metric
    BusinessMetrics.record_investigation_created()  # Using as example metric


# Register default alert callback
slo_monitor.register_alert_callback(default_alert_callback)
