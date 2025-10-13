"""
Module: infrastructure.queue.tasks.katana_tasks
Description: Celery tasks for Katana Scan API integration
Author: Anderson H. Silva
Date: 2025-10-07
License: Proprietary - All rights reserved

These tasks monitor Katana Scan API for new dispensas de licitação
and trigger automatic investigations on suspicious patterns.
"""

import asyncio
from datetime import datetime
from typing import Any

from celery.utils.log import get_task_logger

from src.agents import get_agent_pool
from src.infrastructure.queue.celery_app import celery_app
from src.services.alert_service import alert_service
from src.services.katana_service import KatanaService
from src.services.supabase_anomaly_service import supabase_anomaly_service

logger = get_task_logger(__name__)


@celery_app.task(name="tasks.monitor_katana_dispensas", queue="high")
def monitor_katana_dispensas() -> dict[str, Any]:
    """
    Monitor Katana Scan API for new dispensas de licitação.

    This task runs every 6 hours to fetch new dispensas and analyze them
    for anomalies using the Zumbi agent.

    Returns:
        Summary of monitoring results
    """
    logger.info("katana_monitor_started")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(_monitor_katana_async())

            logger.info(
                "katana_monitor_completed",
                dispensas_fetched=result.get("dispensas_fetched"),
                anomalies_detected=result.get("anomalies_detected"),
                investigations_created=result.get("investigations_created"),
            )

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error("katana_monitor_failed", error=str(e), exc_info=True)
        raise


async def _monitor_katana_async() -> dict[str, Any]:
    """Async implementation of Katana monitoring."""
    katana = KatanaService()

    # Fetch all dispensas
    dispensas = await katana.get_all_dispensas()

    logger.info(f"Fetched {len(dispensas)} dispensas from Katana API")

    # Get agent pool
    agent_pool = await get_agent_pool()
    zumbi = agent_pool.get_agent("zumbi")

    if not zumbi:
        logger.error("Zumbi agent not available for analysis")
        return {
            "error": "Agent not available",
            "dispensas_fetched": len(dispensas),
            "anomalies_detected": 0,
            "investigations_created": 0,
        }

    anomalies = []
    investigations_created = 0

    # Analyze each dispensa
    for dispensa in dispensas:
        try:
            # Format for analysis
            formatted_dispensa = katana.format_dispensa_for_analysis(dispensa)

            # Analyze with Zumbi agent
            analysis = await zumbi.analyze_contract(
                formatted_dispensa, threshold=0.7, analysis_type="anomaly"
            )

            # Save dispensa to Supabase first
            await supabase_anomaly_service.save_katana_dispensa(
                dispensa_id=formatted_dispensa.get("id"),
                dispensa_data=formatted_dispensa,
            )

            # If anomaly detected, create auto investigation and anomaly records
            if analysis.anomaly_detected:
                # Create AUTO investigation in Supabase (not user investigation)
                auto_investigation = await supabase_anomaly_service.create_auto_investigation(
                    query=f"Análise automática de dispensa de licitação - {formatted_dispensa.get('numero')}",
                    context={
                        "source": "katana_scan",
                        "dispensa": formatted_dispensa,
                        "anomaly_analysis": {
                            "score": analysis.anomaly_score,
                            "indicators": analysis.indicators,
                            "recommendations": analysis.recommendations,
                        },
                    },
                    initiated_by="auto_investigation_katana",
                )

                # Create anomaly record in Supabase (linked to auto_investigation)
                anomaly = await supabase_anomaly_service.create_anomaly(
                    investigation_id=None,  # Not a user investigation
                    auto_investigation_id=auto_investigation[
                        "id"
                    ],  # Link to auto investigation
                    source="katana_scan",
                    source_id=formatted_dispensa.get("id"),
                    anomaly_type=(
                        analysis.anomaly_type
                        if hasattr(analysis, "anomaly_type")
                        else "general"
                    ),
                    anomaly_score=analysis.anomaly_score,
                    title=f"Anomalia detectada: Dispensa {formatted_dispensa.get('numero')}",
                    description=f"Análise automática detectou anomalia com score {analysis.anomaly_score:.4f}",
                    indicators=analysis.indicators if analysis.indicators else [],
                    recommendations=(
                        analysis.recommendations if analysis.recommendations else []
                    ),
                    contract_data=formatted_dispensa,
                    metadata={
                        "agent": "zumbi",
                        "analysis_timestamp": datetime.now().isoformat(),
                        "threshold_used": 0.7,
                    },
                )

                anomalies.append(
                    {
                        "anomaly_id": anomaly["id"],
                        "dispensa_id": formatted_dispensa.get("id"),
                        "anomaly_score": analysis.anomaly_score,
                        "severity": anomaly["severity"],
                        "indicators": analysis.indicators,
                    }
                )

                investigations_created += 1

                logger.info(
                    "auto_investigation_and_anomaly_created_in_supabase",
                    dispensa_id=formatted_dispensa.get("id"),
                    auto_investigation_id=auto_investigation["id"],
                    anomaly_id=anomaly["id"],
                    anomaly_score=analysis.anomaly_score,
                    severity=anomaly["severity"],
                )

                # Send alert for high/critical severity anomalies
                if anomaly["severity"] in ("high", "critical"):
                    try:
                        alert_result = await alert_service.send_anomaly_alert(
                            anomaly_id=anomaly["id"],
                            anomaly_data=anomaly,
                            alert_types=["webhook", "dashboard"],
                        )

                        logger.info(
                            "alerts_sent_for_anomaly",
                            anomaly_id=anomaly["id"],
                            alerts_sent=len(alert_result.get("alerts_sent", [])),
                            alerts_failed=len(alert_result.get("alerts_failed", [])),
                        )
                    except Exception as alert_error:
                        logger.error(
                            "failed_to_send_alerts",
                            anomaly_id=anomaly["id"],
                            error=str(alert_error),
                        )

        except Exception as e:
            logger.error(
                "dispensa_analysis_failed", dispensa_id=dispensa.get("id"), error=str(e)
            )
            continue

    return {
        "dispensas_fetched": len(dispensas),
        "anomalies_detected": len(anomalies),
        "investigations_created": investigations_created,
        "anomalies": anomalies,
        "timestamp": datetime.now().isoformat(),
    }


@celery_app.task(name="tasks.katana_health_check", queue="normal")
def katana_health_check() -> dict[str, Any]:
    """
    Check Katana API health and connectivity.

    Returns:
        Health check results
    """
    logger.info("katana_health_check_started")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            katana = KatanaService()
            is_healthy = loop.run_until_complete(katana.health_check())

            result = {
                "status": "healthy" if is_healthy else "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "api_url": katana.base_url,
            }

            logger.info("katana_health_check_completed", status=result["status"])

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error("katana_health_check_failed", error=str(e), exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
