"""
Module: infrastructure.queue.tasks.auto_investigation_tasks
Description: Celery tasks for 24/7 automatic investigation system
Author: Anderson Henrique da Silva
Date: 2025-10-07 18:11:37
License: Proprietary - All rights reserved

These tasks run continuously to monitor government contracts
and trigger investigations on suspicious patterns.
"""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

from celery.utils.log import get_task_logger

from src.infrastructure.queue.celery_app import celery_app
from src.services.auto_investigation_service import auto_investigation_service

logger = get_task_logger(__name__)


@celery_app.task(name="tasks.auto_monitor_new_contracts", queue="normal")
def auto_monitor_new_contracts(
    lookback_hours: int = 24, organization_codes: list | None = None
) -> dict[str, Any]:
    """
    Monitor and investigate new contracts (runs every N hours).

    Args:
        lookback_hours: Hours to look back for new contracts
        organization_codes: Specific organizations to monitor

    Returns:
        Monitoring results summary
    """
    logger.info(f"Auto-monitor task started (lookback_hours: {lookback_hours})")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                auto_investigation_service.monitor_new_contracts(
                    lookback_hours=lookback_hours, organization_codes=organization_codes
                )
            )

            logger.info(
                f"Auto-monitor task completed (contracts: {result.get('contracts_analyzed')}, "
                f"investigations: {result.get('investigations_created')}, anomalies: {result.get('anomalies_detected')})"
            )

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Auto-monitor task failed: {str(e)}", exc_info=True)
        raise


@celery_app.task(name="tasks.auto_reanalyze_historical", queue="low")
def auto_reanalyze_historical(
    months_back: int = 6, batch_size: int = 100
) -> dict[str, Any]:
    """
    Re-analyze historical contracts with updated ML models (runs weekly).

    Args:
        months_back: Months of historical data to analyze
        batch_size: Contracts per batch

    Returns:
        Reanalysis results summary
    """
    logger.info(f"Historical reanalysis task started (months_back: {months_back})")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                auto_investigation_service.reanalyze_historical_contracts(
                    months_back=months_back, batch_size=batch_size
                )
            )

            logger.info(
                f"Historical reanalysis task completed (contracts: {result.get('contracts_analyzed')}, "
                f"anomalies: {result.get('anomalies_detected')})"
            )

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Historical reanalysis task failed: {str(e)}", exc_info=True)
        raise


@celery_app.task(name="tasks.auto_monitor_priority_orgs", queue="high")
def auto_monitor_priority_orgs() -> dict[str, Any]:
    """
    Monitor high-priority organizations more frequently (runs every 4 hours).

    These are organizations with history of irregularities or high-value contracts.

    Returns:
        Monitoring results for priority organizations
    """
    # Priority organizations (can be loaded from config/database)
    priority_orgs = [
        # Examples - replace with real org codes
        # "26101",  # Ministério da Saúde
        # "20101",  # Ministério da Educação
    ]

    logger.info(f"Priority orgs monitor started (org_count: {len(priority_orgs)})")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                auto_investigation_service.monitor_new_contracts(
                    lookback_hours=4,  # More frequent monitoring
                    organization_codes=priority_orgs if priority_orgs else None,
                )
            )

            logger.info(
                f"Priority orgs monitor completed (contracts: {result.get('contracts_analyzed')}, "
                f"anomalies: {result.get('anomalies_detected')})"
            )

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Priority orgs monitor failed: {str(e)}", exc_info=True)
        raise


@celery_app.task(name="tasks.auto_investigation_health_check", queue="high")
def auto_investigation_health_check() -> dict[str, Any]:
    """
    Health check for auto-investigation system (runs every hour).

    Verifies that the system is functioning correctly and reports metrics.

    Returns:
        System health status
    """
    logger.info("Auto-investigation health check started")

    try:
        # Check system components
        health = {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "components": {
                "transparency_api": "checking",
                "investigation_service": "checking",
                "agent_pool": "checking",
            },
        }

        # Test transparency API
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Quick test fetch
                from datetime import timedelta

                from src.tools.transparency_api import (
                    TransparencyAPIClient,
                    TransparencyAPIFilter,
                )

                api = TransparencyAPIClient()
                filters = TransparencyAPIFilter(
                    codigo_orgao="26000",  # Ministério da Saúde (test org)
                    data_inicio=(datetime.now(UTC) - timedelta(days=1)).strftime(
                        "%d/%m/%Y"
                    ),
                    data_fim=datetime.now(UTC).strftime("%d/%m/%Y"),
                )

                loop.run_until_complete(api.get_contracts(filters=filters))

                health["components"]["transparency_api"] = "healthy"

            finally:
                loop.close()

        except Exception as e:
            health["components"]["transparency_api"] = f"unhealthy: {str(e)}"
            health["status"] = "degraded"

        # Test investigation service
        try:

            health["components"]["investigation_service"] = "healthy"
        except Exception as e:
            health["components"]["investigation_service"] = f"unhealthy: {str(e)}"
            health["status"] = "degraded"

        # Test agent pool
        try:
            from src.agents import get_agent_pool

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(get_agent_pool())
                health["components"]["agent_pool"] = "healthy"
            finally:
                loop.close()

        except Exception as e:
            health["components"]["agent_pool"] = f"unhealthy: {str(e)}"
            health["status"] = "degraded"

        logger.info(
            f"Auto-investigation health check completed (status: {health['status']})"
        )

        return health

    except Exception as e:
        logger.error(f"Auto-investigation health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


@celery_app.task(name="tasks.cleanup_stuck_investigations", queue="high")
def cleanup_stuck_investigations(stuck_threshold_hours: int = 1) -> dict[str, Any]:
    """
    Cleanup investigations stuck in 'running' state for too long.

    This task runs every 15 minutes and marks old running investigations
    as failed to prevent database pollution and allow users to retry.

    Args:
        stuck_threshold_hours: Hours after which a running investigation is considered stuck

    Returns:
        Cleanup results summary
    """
    logger.info(
        f"Cleanup stuck investigations started (threshold: {stuck_threshold_hours}h)"
    )

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                _cleanup_stuck_investigations_async(stuck_threshold_hours)
            )

            if result["fixed_count"] > 0:
                logger.warning(
                    f"Cleanup completed: {result['fixed_count']} stuck investigations marked as failed"
                )
            else:
                logger.info("Cleanup completed: no stuck investigations found")

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Cleanup stuck investigations failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "fixed_count": 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }


async def _cleanup_stuck_investigations_async(
    stuck_threshold_hours: int,
) -> dict[str, Any]:
    """
    Async implementation of stuck investigations cleanup.

    Args:
        stuck_threshold_hours: Hours threshold for stuck detection

    Returns:
        Cleanup results
    """
    from sqlalchemy import text

    from src.db.simple_session import _get_engine

    result = {
        "status": "started",
        "fixed_count": 0,
        "fixed_ids": [],
        "errors": [],
        "timestamp": datetime.now(UTC).isoformat(),
    }

    try:
        engine = _get_engine()

        # Calculate threshold timestamp for stuck detection
        threshold_time = datetime.now(UTC) - timedelta(hours=stuck_threshold_hours)
        error_msg = f"Investigation timed out (stuck in running state for >{stuck_threshold_hours}h). Auto-cleaned by system."

        async with engine.begin() as conn:
            # Find and update stuck investigations using parameterized query
            update_result = await conn.execute(
                text(
                    """
                    UPDATE investigations
                    SET status = 'failed',
                        error_message = :error_message,
                        completed_at = NOW()
                    WHERE status = 'running'
                    AND created_at < :threshold_time
                    RETURNING id, query, created_at
                    """
                ),
                {"error_message": error_msg, "threshold_time": threshold_time},
            )

            fixed_rows = update_result.fetchall()

            for row in fixed_rows:
                result["fixed_ids"].append(
                    {
                        "id": str(row[0]),
                        "query": row[1][:50] if row[1] else "",
                        "created_at": str(row[2]),
                    }
                )

            result["fixed_count"] = len(fixed_rows)
            result["status"] = "completed"

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(
            {
                "error": str(e),
                "type": type(e).__name__,
            }
        )

    return result


@celery_app.task(name="tasks.investigation_metrics_report", queue="low")
def investigation_metrics_report() -> dict[str, Any]:
    """
    Generate metrics report for investigations (runs daily).

    Provides insights on investigation success rates, common failures,
    and system performance.

    Returns:
        Metrics report
    """
    logger.info("Investigation metrics report started")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(_generate_metrics_report_async())
            logger.info(
                f"Metrics report completed (total: {result.get('total_investigations')}, "
                f"success_rate: {result.get('success_rate', 0):.1%})"
            )
            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Metrics report failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


async def _generate_metrics_report_async() -> dict[str, Any]:
    """
    Async implementation of metrics report generation.

    Returns:
        Metrics report data
    """
    from sqlalchemy import text

    from src.db.simple_session import _get_engine

    report = {
        "status": "generating",
        "timestamp": datetime.now(UTC).isoformat(),
        "period": "last_24_hours",
    }

    try:
        engine = _get_engine()

        async with engine.begin() as conn:
            # Total investigations in last 24h
            total_result = await conn.execute(
                text(
                    """
                    SELECT COUNT(*) FROM investigations
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    """
                )
            )
            report["total_investigations"] = total_result.scalar() or 0

            # By status
            status_result = await conn.execute(
                text(
                    """
                    SELECT status, COUNT(*) as count
                    FROM investigations
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY status
                    """
                )
            )
            report["by_status"] = {row[0]: row[1] for row in status_result.fetchall()}

            # Success rate
            completed = report["by_status"].get("completed", 0)
            total = report["total_investigations"]
            report["success_rate"] = completed / total if total > 0 else 0

            # Average processing time for completed investigations
            time_result = await conn.execute(
                text(
                    """
                    SELECT AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_seconds
                    FROM investigations
                    WHERE status = 'completed'
                    AND created_at > NOW() - INTERVAL '24 hours'
                    AND completed_at IS NOT NULL
                    """
                )
            )
            avg_time = time_result.scalar()
            report["avg_processing_time_seconds"] = (
                round(avg_time, 2) if avg_time else None
            )

            # Stuck investigations (still running after 1 hour)
            stuck_result = await conn.execute(
                text(
                    """
                    SELECT COUNT(*) FROM investigations
                    WHERE status = 'running'
                    AND created_at < NOW() - INTERVAL '1 hour'
                    """
                )
            )
            report["currently_stuck"] = stuck_result.scalar() or 0

            report["status"] = "completed"

    except Exception as e:
        report["status"] = "error"
        report["error"] = str(e)

    return report
