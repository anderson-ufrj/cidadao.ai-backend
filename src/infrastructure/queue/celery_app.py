"""
Module: infrastructure.queue.celery_app
Description: Celery application configuration and task definitions
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from datetime import datetime, timedelta
from functools import wraps
from typing import Any

from celery import Celery, Task
from celery.utils.log import get_task_logger
from kombu import Exchange, Queue

from src.core.config import get_settings
from src.infrastructure.queue.priority_queue import TaskPriority

# Get settings
settings = get_settings()

# Configure Celery
celery_app = Celery(
    "cidadao_ai",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "src.infrastructure.queue.tasks.investigation_tasks",
        "src.infrastructure.queue.tasks.analysis_tasks",
        "src.infrastructure.queue.tasks.auto_investigation_tasks",
        "src.infrastructure.queue.tasks.katana_tasks",
        "src.infrastructure.queue.tasks.alert_tasks",
        "src.infrastructure.queue.tasks.network_tasks",  # Network graph analysis
        "src.infrastructure.queue.tasks.memory_tasks",  # Nanã memory management
        # Temporarily disabled - missing service dependencies
        # "src.infrastructure.queue.tasks.report_tasks",
        # "src.infrastructure.queue.tasks.export_tasks",
        # "src.infrastructure.queue.tasks.monitoring_tasks",
        # "src.infrastructure.queue.tasks.maintenance_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task execution
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    # Task routing
    task_routes={
        "tasks.critical.*": {"queue": "critical"},
        "tasks.high.*": {"queue": "high"},
        "tasks.normal.*": {"queue": "default"},
        "tasks.low.*": {"queue": "low"},
        "tasks.background.*": {"queue": "background"},
    },
    # Performance
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    # Result backend
    result_expires=3600,  # 1 hour
    result_persistent=True,
    # Task execution limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    # Retries
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Define queues with priorities
celery_app.conf.task_queues = (
    Queue("critical", Exchange("critical"), routing_key="critical", priority=10),
    Queue("high", Exchange("high"), routing_key="high", priority=7),
    Queue("default", Exchange("default"), routing_key="default", priority=5),
    Queue("low", Exchange("low"), routing_key="low", priority=3),
    Queue("background", Exchange("background"), routing_key="background", priority=1),
)

# Logger
logger = get_task_logger(__name__)


class BaseTask(Task):
    """Base task with error handling and monitoring."""

    def __init__(self):
        """Initialize base task."""
        super().__init__()
        self._task_start_time = None

    def before_start(self, task_id, args, kwargs):
        """Called before task execution."""
        self._task_start_time = datetime.now()
        logger.info(
            f"Task started: {self.name} (ID: {task_id}, args: {args}, kwargs: {kwargs})"
        )

    def on_success(self, retval, task_id, args, kwargs):
        """Called on successful task completion."""
        duration = (datetime.now() - self._task_start_time).total_seconds()
        result_size = len(str(retval)) if retval else 0
        logger.info(
            f"Task completed: {self.name} (ID: {task_id}, duration: {duration:.2f}s, result_size: {result_size})"
        )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure."""
        duration = (datetime.now() - self._task_start_time).total_seconds()
        logger.error(
            f"Task failed: {self.name} (ID: {task_id}, duration: {duration:.2f}s, error: {str(exc)})",
            exc_info=einfo,
        )

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried."""
        logger.warning(
            f"Task retry: {self.name} (ID: {task_id}, error: {str(exc)}, retry_count: {self.request.retries})"
        )


# Set default base task
celery_app.Task = BaseTask


def priority_task(priority: TaskPriority = TaskPriority.NORMAL):
    """Decorator to create priority-aware tasks."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract task metadata
            task_id = kwargs.pop("task_id", None)
            callback_url = kwargs.pop("callback_url", None)

            # Execute task
            result = func(*args, **kwargs)

            # Handle callback if provided
            if callback_url and task_id:
                send_task_callback.delay(
                    task_id=task_id,
                    callback_url=callback_url,
                    result=result,
                    status="completed",
                )

            return result

        # Set task options based on priority
        queue_name = {
            TaskPriority.CRITICAL: "critical",
            TaskPriority.HIGH: "high",
            TaskPriority.NORMAL: "default",
            TaskPriority.LOW: "low",
            TaskPriority.BACKGROUND: "background",
        }.get(priority, "default")

        task_options = {
            "queue": queue_name,
            "priority": priority.value,
            "max_retries": 3,
            "default_retry_delay": 60,  # 1 minute
        }

        # Create Celery task
        return celery_app.task(**task_options)(wrapper)

    return decorator


@celery_app.task(name="tasks.send_callback", queue="high")
def send_task_callback(
    task_id: str, callback_url: str, result: Any, status: str
) -> dict[str, Any]:
    """Send task completion callback."""
    import httpx

    try:
        with httpx.Client() as client:
            response = client.post(
                callback_url,
                json={
                    "task_id": task_id,
                    "status": status,
                    "result": result,
                    "completed_at": datetime.now().isoformat(),
                },
                timeout=30.0,
            )

            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
            }

    except Exception as e:
        logger.error(
            f"Callback failed (task_id: {task_id}, url: {callback_url}): {str(e)}"
        )
        return {"success": False, "error": str(e)}


@celery_app.task(name="tasks.cleanup_old_results", queue="background")
def cleanup_old_results(days: int = 7) -> dict[str, Any]:
    """Clean up old task results."""
    cutoff_date = datetime.now() - timedelta(days=days)

    # This would integrate with your result backend
    # For now, just log the action
    logger.info(f"Cleanup started (cutoff: {cutoff_date.isoformat()}, days: {days})")

    return {"status": "completed", "cutoff_date": cutoff_date.isoformat()}


# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-old-results": {
        "task": "tasks.cleanup_old_results",
        "schedule": timedelta(hours=24),  # Daily
        "args": (7,),  # Keep 7 days
    },
    "health-check": {
        "task": "tasks.health_check",
        "schedule": timedelta(minutes=5),  # Every 5 minutes
    },
    # 24/7 Auto-Investigation Tasks
    "auto-monitor-new-contracts-6h": {
        "task": "tasks.auto_monitor_new_contracts",
        "schedule": timedelta(hours=6),  # Every 6 hours
        "args": (6,),  # Look back 6 hours
        "options": {"queue": "normal"},
    },
    "auto-monitor-priority-orgs-4h": {
        "task": "tasks.auto_monitor_priority_orgs",
        "schedule": timedelta(hours=4),  # Every 4 hours
        "options": {"queue": "high"},
    },
    "auto-reanalyze-historical-weekly": {
        "task": "tasks.auto_reanalyze_historical",
        "schedule": timedelta(days=7),  # Weekly
        "args": (6, 100),  # 6 months back, 100 per batch
        "options": {"queue": "low"},
    },
    "auto-investigation-health-hourly": {
        "task": "tasks.auto_investigation_health_check",
        "schedule": timedelta(hours=1),  # Every hour
        "options": {"queue": "high"},
    },
    # Katana Scan Integration
    "katana-monitor-dispensas-6h": {
        "task": "tasks.monitor_katana_dispensas",
        "schedule": timedelta(hours=6),  # Every 6 hours
        "options": {"queue": "high"},
    },
    "katana-health-check-hourly": {
        "task": "tasks.katana_health_check",
        "schedule": timedelta(hours=1),  # Every hour
        "options": {"queue": "normal"},
    },
    # Alert Tasks
    "critical-anomalies-summary-daily": {
        "task": "tasks.send_critical_anomalies_summary",
        "schedule": timedelta(hours=24),  # Daily summary
        "args": (24,),  # Last 24 hours
        "options": {"queue": "normal"},
    },
    "process-pending-alerts-hourly": {
        "task": "tasks.process_pending_alerts",
        "schedule": timedelta(hours=1),  # Retry failed alerts every hour
        "options": {"queue": "high"},
    },
    # Network Graph Analysis Tasks
    "calculate-network-metrics-daily": {
        "task": "tasks.calculate_network_metrics",
        "schedule": timedelta(hours=24),  # Daily recalculation
        "options": {"queue": "background"},
    },
    "detect-suspicious-networks-6h": {
        "task": "tasks.detect_suspicious_networks",
        "schedule": timedelta(hours=6),  # Every 6 hours
        "args": (7,),  # Analyze last 7 days
        "options": {"queue": "high"},
    },
    "enrich-investigations-with-graph-6h": {
        "task": "tasks.enrich_recent_investigations_with_graph",
        "schedule": timedelta(hours=6),  # Every 6 hours
        "args": (6,),  # Enrich last 6 hours
        "options": {"queue": "normal"},
    },
    "update-entity-risk-scores-daily": {
        "task": "tasks.update_entity_risk_scores",
        "schedule": timedelta(hours=24),  # Daily update
        "options": {"queue": "background"},
    },
    "network-health-check-hourly": {
        "task": "tasks.network_health_check",
        "schedule": timedelta(hours=1),  # Every hour
        "options": {"queue": "high"},
    },
    # Memory Management Tasks (Nanã)
    "memory-decay-daily": {
        "task": "tasks.memory_decay",
        "schedule": timedelta(hours=24),  # Daily memory decay
        "args": (30,),  # Decay memories older than 30 days
        "options": {"queue": "background"},
    },
    "memory-consolidation-weekly": {
        "task": "tasks.memory_consolidation",
        "schedule": timedelta(days=7),  # Weekly consolidation
        "args": (0.85,),  # 85% similarity threshold
        "options": {"queue": "background"},
    },
    "memory-cleanup-weekly": {
        "task": "tasks.memory_cleanup",
        "schedule": timedelta(days=7),  # Weekly cleanup
        "options": {"queue": "background"},
    },
    "memory-health-check-hourly": {
        "task": "tasks.memory_health_check",
        "schedule": timedelta(hours=1),  # Hourly health check
        "options": {"queue": "high"},
    },
}


@celery_app.task(name="tasks.health_check", queue="high")
def health_check() -> dict[str, Any]:
    """Periodic health check task."""
    stats = celery_app.control.inspect().stats()

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "workers": len(stats) if stats else 0,
    }


def get_celery_app() -> Celery:
    """Get Celery application instance."""
    return celery_app
