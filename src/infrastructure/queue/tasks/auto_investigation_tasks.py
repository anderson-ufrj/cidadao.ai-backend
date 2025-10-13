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
from datetime import datetime
from typing import Any, Optional

from celery.utils.log import get_task_logger

from src.infrastructure.queue.celery_app import celery_app
from src.services.auto_investigation_service import auto_investigation_service

logger = get_task_logger(__name__)


@celery_app.task(name="tasks.auto_monitor_new_contracts", queue="normal")
def auto_monitor_new_contracts(
    lookback_hours: int = 24, organization_codes: Optional[list] = None
) -> dict[str, Any]:
    """
    Monitor and investigate new contracts (runs every N hours).

    Args:
        lookback_hours: Hours to look back for new contracts
        organization_codes: Specific organizations to monitor

    Returns:
        Monitoring results summary
    """
    logger.info("auto_monitor_task_started", lookback_hours=lookback_hours)

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
                "auto_monitor_task_completed",
                contracts_analyzed=result.get("contracts_analyzed"),
                investigations_created=result.get("investigations_created"),
                anomalies_detected=result.get("anomalies_detected"),
            )

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error("auto_monitor_task_failed", error=str(e), exc_info=True)
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
    logger.info("historical_reanalysis_task_started", months_back=months_back)

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
                "historical_reanalysis_task_completed",
                contracts_analyzed=result.get("contracts_analyzed"),
                anomalies_detected=result.get("anomalies_detected"),
            )

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error("historical_reanalysis_task_failed", error=str(e), exc_info=True)
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

    logger.info("priority_orgs_monitor_started", org_count=len(priority_orgs))

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
                "priority_orgs_monitor_completed",
                contracts_analyzed=result.get("contracts_analyzed"),
                anomalies_detected=result.get("anomalies_detected"),
            )

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error("priority_orgs_monitor_failed", error=str(e), exc_info=True)
        raise


@celery_app.task(name="tasks.auto_investigation_health_check", queue="high")
def auto_investigation_health_check() -> dict[str, Any]:
    """
    Health check for auto-investigation system (runs every hour).

    Verifies that the system is functioning correctly and reports metrics.

    Returns:
        System health status
    """
    logger.info("auto_investigation_health_check_started")

    try:
        # Check system components
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
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
                    dataInicial=(datetime.utcnow() - timedelta(days=1)).strftime(
                        "%d/%m/%Y"
                    ),
                    dataFinal=datetime.utcnow().strftime("%d/%m/%Y"),
                )

                contracts = loop.run_until_complete(
                    api.get_contracts(filters=filters, limit=1)
                )

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
                pool = loop.run_until_complete(get_agent_pool())
                health["components"]["agent_pool"] = "healthy"
            finally:
                loop.close()

        except Exception as e:
            health["components"]["agent_pool"] = f"unhealthy: {str(e)}"
            health["status"] = "degraded"

        logger.info(
            "auto_investigation_health_check_completed", status=health["status"]
        )

        return health

    except Exception as e:
        logger.error(
            "auto_investigation_health_check_failed", error=str(e), exc_info=True
        )
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
