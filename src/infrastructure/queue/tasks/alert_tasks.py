"""
Module: infrastructure.queue.tasks.alert_tasks
Description: Celery tasks for alert management and notifications
Author: Anderson H. Silva
Date: 2025-10-07
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime
from typing import Any

from celery.utils.log import get_task_logger

from src.infrastructure.queue.celery_app import celery_app
from src.services.alert_service import alert_service

logger = get_task_logger(__name__)


@celery_app.task(name="tasks.send_critical_anomalies_summary", queue="normal")
def send_critical_anomalies_summary(period_hours: int = 24) -> dict[str, Any]:
    """
    Send summary of critical anomalies detected in the last N hours.

    This task runs daily to provide a summary of all critical anomalies.

    Args:
        period_hours: Number of hours to look back (default: 24)

    Returns:
        Summary of sent alerts
    """
    logger.info("critical_anomalies_summary_task_started", period_hours=period_hours)

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                alert_service.send_critical_alert_summary(period_hours=period_hours)
            )

            logger.info(
                "critical_anomalies_summary_sent",
                webhooks_sent=result.get("webhooks_sent", 0),
                webhooks_failed=result.get("webhooks_failed", 0),
            )

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error("critical_anomalies_summary_failed", error=str(e), exc_info=True)
        raise


@celery_app.task(name="tasks.process_pending_alerts", queue="high")
def process_pending_alerts() -> dict[str, Any]:
    """
    Process pending alerts that failed to send.

    This task retries sending alerts that previously failed.

    Returns:
        Processing results
    """
    logger.info("process_pending_alerts_started")

    try:
        # TODO: Implement retry logic for failed alerts
        # Get pending alerts from Supabase
        # Retry sending them
        # Update status

        logger.info("process_pending_alerts_completed")

        return {
            "status": "completed",
            "alerts_processed": 0,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error("process_pending_alerts_failed", error=str(e), exc_info=True)
        raise
