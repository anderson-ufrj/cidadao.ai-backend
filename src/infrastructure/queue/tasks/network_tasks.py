"""
Module: infrastructure.queue.tasks.network_tasks
Description: Celery tasks for network graph analysis and suspicious pattern detection
Author: Anderson Henrique da Silva
Date: 2025-10-09
License: Proprietary - All rights reserved
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from celery import Task
from celery.utils.log import get_task_logger

from src.infrastructure.queue.celery_app import celery_app
from src.services.network_analysis_service import get_network_analysis_service
from src.services.graph_integration_service import get_graph_integration_service
from src.db.session import get_db
from sqlalchemy import select, func
from src.models.entity_graph import EntityNode, SuspiciousNetwork

logger = get_task_logger(__name__)


@celery_app.task(
    name="tasks.calculate_network_metrics",
    queue="background",
    bind=True,
    max_retries=3
)
def calculate_network_metrics(self: Task) -> Dict[str, Any]:
    """
    Calculate network centrality metrics for all entities.

    Runs daily to update:
    - Degree centrality (number of connections)
    - Betweenness centrality (bridge between networks)
    - Closeness centrality (average distance to others)
    - Eigenvector centrality (influence score)
    """
    logger.info("starting_network_metrics_calculation")

    try:
        async def _calculate():
            async with get_db() as db:
                network_service = get_network_analysis_service(db)
                metrics = await network_service.calculate_network_metrics()
                return metrics

        import asyncio
        metrics = asyncio.run(_calculate())

        logger.info(
            "network_metrics_completed",
            entities_updated=metrics.get("entities_updated", 0),
            execution_time=metrics.get("execution_time_seconds", 0)
        )

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }

    except Exception as e:
        logger.error(
            "network_metrics_failed",
            error=str(e),
            exc_info=True
        )
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(
    name="tasks.detect_suspicious_networks",
    queue="high",
    bind=True,
    max_retries=3
)
def detect_suspicious_networks(self: Task, lookback_days: int = 7) -> Dict[str, Any]:
    """
    Detect suspicious networks (cartels, concentration, shell networks).

    Args:
        lookback_days: Analyze investigations from last N days

    Detects:
    - Cartels: Companies with shared ownership contracting same agency
    - Concentration: Few suppliers dominating contracts
    - Shell networks: Complex ownership chains with low contract values
    """
    logger.info(
        "starting_suspicious_network_detection",
        lookback_days=lookback_days
    )

    try:
        async def _detect():
            async with get_db() as db:
                # Get recent investigation IDs
                from src.models.investigation import Investigation

                cutoff_date = datetime.now() - timedelta(days=lookback_days)
                query = select(Investigation.id).where(
                    Investigation.created_at >= cutoff_date
                )
                result = await db.execute(query)
                investigation_ids = [row[0] for row in result]

                if not investigation_ids:
                    return {"networks_detected": 0, "message": "No recent investigations"}

                # Detect suspicious networks
                network_service = get_network_analysis_service(db)
                all_networks = []

                for inv_id in investigation_ids:
                    networks = await network_service.detect_suspicious_networks(inv_id)
                    all_networks.extend(networks)

                # Deduplicate by network signature
                unique_networks = {}
                for net in all_networks:
                    key = f"{net.network_type}_{'-'.join(sorted(net.entity_ids))}"
                    if key not in unique_networks:
                        unique_networks[key] = net

                return {
                    "networks_detected": len(unique_networks),
                    "networks": [
                        {
                            "id": net.id,
                            "type": net.network_type,
                            "severity": net.severity,
                            "entity_count": net.entity_count,
                            "confidence": net.confidence_score
                        }
                        for net in unique_networks.values()
                    ]
                }

        import asyncio
        result = asyncio.run(_detect())

        logger.info(
            "suspicious_networks_detected",
            networks_count=result.get("networks_detected", 0),
            lookback_days=lookback_days
        )

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            **result
        }

    except Exception as e:
        logger.error(
            "suspicious_network_detection_failed",
            error=str(e),
            lookback_days=lookback_days,
            exc_info=True
        )
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(
    name="tasks.enrich_recent_investigations_with_graph",
    queue="normal",
    bind=True
)
def enrich_recent_investigations_with_graph(self: Task, lookback_hours: int = 6) -> Dict[str, Any]:
    """
    Enrich recent investigations with network graph data.

    Adds cross-investigation insights like:
    - Entity appeared in X previous investigations
    - Risk score based on history
    - Network connections and influence
    """
    logger.info(
        "starting_investigation_graph_enrichment",
        lookback_hours=lookback_hours
    )

    try:
        async def _enrich():
            async with get_db() as db:
                # Get recent investigations
                from src.models.investigation import Investigation

                cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
                query = select(Investigation).where(
                    Investigation.created_at >= cutoff_time,
                    Investigation.status.in_(["completed", "running"])
                )
                result = await db.execute(query)
                investigations = list(result.scalars().all())

                if not investigations:
                    return {"enriched": 0, "message": "No recent investigations"}

                # Enrich each investigation
                graph_service = get_graph_integration_service(db)
                enriched_count = 0

                for inv in investigations:
                    # Get forensic results from investigation
                    if inv.results and isinstance(inv.results, list):
                        from src.models.forensic_investigation import ForensicAnomalyResult

                        # Convert dict results to ForensicAnomalyResult objects
                        forensic_results = []
                        for result_data in inv.results:
                            if isinstance(result_data, dict):
                                # Reconstruct ForensicAnomalyResult from dict
                                # (simplified - you may need to adjust based on actual structure)
                                forensic_results.append(result_data)

                        if forensic_results:
                            await graph_service.integrate_investigation_with_graph(
                                investigation_id=inv.id,
                                forensic_results=forensic_results,
                                contract_data=inv.filters
                            )
                            enriched_count += 1

                return {
                    "enriched": enriched_count,
                    "total_processed": len(investigations)
                }

        import asyncio
        result = asyncio.run(_enrich())

        logger.info(
            "investigation_enrichment_completed",
            enriched=result.get("enriched", 0),
            lookback_hours=lookback_hours
        )

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            **result
        }

    except Exception as e:
        logger.error(
            "investigation_enrichment_failed",
            error=str(e),
            exc_info=True
        )
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(
    name="tasks.update_entity_risk_scores",
    queue="background",
    bind=True
)
def update_entity_risk_scores(self: Task) -> Dict[str, Any]:
    """
    Update risk scores for all entities based on:
    - Number of investigations involved
    - Total anomalies detected
    - Network centrality metrics
    - Sanctioned status
    """
    logger.info("starting_entity_risk_score_update")

    try:
        async def _update_scores():
            async with get_db() as db:
                # Get all entities
                query = select(EntityNode)
                result = await db.execute(query)
                entities = list(result.scalars().all())

                updated_count = 0

                for entity in entities:
                    # Calculate risk score (0-10)
                    risk_score = 0.0

                    # Factor 1: Number of investigations (max 3 points)
                    if entity.total_investigations > 0:
                        risk_score += min(entity.total_investigations * 0.3, 3.0)

                    # Factor 2: Anomalies ratio (max 3 points)
                    if entity.total_investigations > 0:
                        anomaly_ratio = entity.total_anomalies / entity.total_investigations
                        risk_score += min(anomaly_ratio * 3.0, 3.0)

                    # Factor 3: Network centrality (max 2 points)
                    if entity.degree_centrality > 10:
                        risk_score += min(entity.degree_centrality / 10, 2.0)

                    # Factor 4: Sanctioned (automatic +2 points)
                    if entity.is_sanctioned:
                        risk_score += 2.0

                    # Ensure 0-10 range
                    entity.risk_score = min(max(risk_score, 0.0), 10.0)
                    updated_count += 1

                await db.commit()

                return {
                    "entities_updated": updated_count,
                    "total_entities": len(entities)
                }

        import asyncio
        result = asyncio.run(_update_scores())

        logger.info(
            "risk_scores_updated",
            entities_updated=result.get("entities_updated", 0)
        )

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            **result
        }

    except Exception as e:
        logger.error(
            "risk_score_update_failed",
            error=str(e),
            exc_info=True
        )
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(
    name="tasks.network_health_check",
    queue="high"
)
def network_health_check() -> Dict[str, Any]:
    """
    Health check for network graph system.

    Verifies:
    - Tables exist and accessible
    - Recent data is being added
    - Network metrics are being calculated
    """
    logger.info("starting_network_health_check")

    try:
        async def _health_check():
            async with get_db() as db:
                # Count entities
                entity_count = await db.scalar(select(func.count(EntityNode.id)))

                # Count recent suspicious networks
                cutoff = datetime.now() - timedelta(hours=24)
                recent_networks = await db.scalar(
                    select(func.count(SuspiciousNetwork.id)).where(
                        SuspiciousNetwork.created_at >= cutoff
                    )
                )

                # Check if metrics are being calculated
                entities_with_metrics = await db.scalar(
                    select(func.count(EntityNode.id)).where(
                        EntityNode.degree_centrality > 0
                    )
                )

                metrics_percentage = (
                    (entities_with_metrics / entity_count * 100)
                    if entity_count > 0 else 0
                )

                return {
                    "total_entities": entity_count or 0,
                    "suspicious_networks_24h": recent_networks or 0,
                    "entities_with_metrics": entities_with_metrics or 0,
                    "metrics_coverage_percent": round(metrics_percentage, 2),
                    "healthy": entity_count > 0 and metrics_percentage > 50
                }

        import asyncio
        result = asyncio.run(_health_check())

        health_status = "healthy" if result.get("healthy") else "degraded"

        logger.info(
            "network_health_check_completed",
            status=health_status,
            **result
        )

        return {
            "status": health_status,
            "timestamp": datetime.now().isoformat(),
            **result
        }

    except Exception as e:
        logger.error(
            "network_health_check_failed",
            error=str(e),
            exc_info=True
        )
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
