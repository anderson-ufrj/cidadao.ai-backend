"""
Module: infrastructure.queue.tasks.monitoring_tasks
Description: Celery tasks for system monitoring and alerting
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from celery.utils.log import get_task_logger

from src.infrastructure.queue.celery_app import celery_app, priority_task, TaskPriority
from src.services.data_service import DataService
from src.services.notification_service import NotificationService
from src.core.dependencies import get_db_session
from src.agents import get_agent_pool

logger = get_task_logger(__name__)


@celery_app.task(name="tasks.monitor_anomalies", queue="normal")
def monitor_anomalies(
    monitoring_config: Dict[str, Any],
    alert_threshold: float = 0.8
) -> Dict[str, Any]:
    """
    Monitor for anomalies in real-time data.
    
    Args:
        monitoring_config: Configuration for monitoring
        alert_threshold: Threshold for triggering alerts
        
    Returns:
        Monitoring results
    """
    logger.info(
        "anomaly_monitoring_started",
        config=monitoring_config,
        threshold=alert_threshold
    )
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _monitor_anomalies_async(monitoring_config, alert_threshold)
            )
            
            return result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(
            "anomaly_monitoring_failed",
            error=str(e),
            exc_info=True
        )
        raise


async def _monitor_anomalies_async(
    monitoring_config: Dict[str, Any],
    alert_threshold: float
) -> Dict[str, Any]:
    """Async anomaly monitoring implementation."""
    async with get_db_session() as db:
        data_service = DataService(db)
        agent_pool = get_agent_pool()
        notification_service = NotificationService()
        
        # Get monitoring parameters
        data_source = monitoring_config.get("data_source", "contracts")
        time_window = monitoring_config.get("time_window", 60)  # minutes
        categories = monitoring_config.get("categories", [])
        
        # Get recent data
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=time_window)
        
        if data_source == "contracts":
            data = await data_service.get_contracts_in_range(
                start_date=start_time.isoformat(),
                end_date=end_time.isoformat(),
                categories=categories
            )
        else:
            data = []
        
        # Get Zumbi agent for anomaly detection
        zumbi = agent_pool.get_agent("zumbi")
        if not zumbi:
            raise RuntimeError("Anomaly detection agent not available")
        
        # Detect anomalies
        anomalies = []
        alerts = []
        
        for item in data:
            result = await zumbi.detect_anomalies(
                data=item,
                threshold=alert_threshold
            )
            
            if result.anomaly_detected:
                anomaly = {
                    "id": item.get("id"),
                    "type": result.anomaly_type,
                    "score": result.anomaly_score,
                    "description": result.description,
                    "data": item
                }
                anomalies.append(anomaly)
                
                # Create alert if above threshold
                if result.anomaly_score >= alert_threshold:
                    alert = {
                        "level": "critical" if result.anomaly_score >= 0.9 else "high",
                        "type": result.anomaly_type,
                        "description": f"Anomaly detected in {data_source}: {result.description}",
                        "score": result.anomaly_score,
                        "data_id": item.get("id"),
                        "timestamp": datetime.now().isoformat()
                    }
                    alerts.append(alert)
        
        # Send notifications for alerts
        if alerts:
            await notification_service.send_anomaly_alerts(alerts)
        
        return {
            "monitoring_window": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "data_source": data_source,
            "items_analyzed": len(data),
            "anomalies_detected": len(anomalies),
            "alerts_triggered": len(alerts),
            "anomalies": anomalies,
            "alerts": alerts
        }


@celery_app.task(name="tasks.check_data_updates", queue="normal")
def check_data_updates(
    sources: List[str],
    check_interval_hours: int = 24
) -> Dict[str, Any]:
    """
    Check for data source updates.
    
    Args:
        sources: List of data sources to check
        check_interval_hours: Hours since last check
        
    Returns:
        Update check results
    """
    logger.info(
        "data_update_check_started",
        sources=sources,
        interval=check_interval_hours
    )
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _check_data_updates_async(sources, check_interval_hours)
            )
            
            return result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(
            "data_update_check_failed",
            error=str(e),
            exc_info=True
        )
        raise


async def _check_data_updates_async(
    sources: List[str],
    check_interval_hours: int
) -> Dict[str, Any]:
    """Async data update check implementation."""
    async with get_db_session() as db:
        data_service = DataService(db)
        
        updates = {}
        cutoff_time = datetime.now() - timedelta(hours=check_interval_hours)
        
        for source in sources:
            if source == "contracts":
                recent_count = await data_service.count_contracts_since(cutoff_time)
                last_update = await data_service.get_last_contract_update()
                updates[source] = {
                    "new_items": recent_count,
                    "last_update": last_update.isoformat() if last_update else None,
                    "status": "updated" if recent_count > 0 else "no_updates"
                }
            elif source == "suppliers":
                recent_count = await data_service.count_suppliers_since(cutoff_time)
                last_update = await data_service.get_last_supplier_update()
                updates[source] = {
                    "new_items": recent_count,
                    "last_update": last_update.isoformat() if last_update else None,
                    "status": "updated" if recent_count > 0 else "no_updates"
                }
        
        # Calculate summary
        total_updates = sum(u.get("new_items", 0) for u in updates.values())
        
        return {
            "check_time": datetime.now().isoformat(),
            "cutoff_time": cutoff_time.isoformat(),
            "sources_checked": len(sources),
            "total_updates": total_updates,
            "updates": updates
        }


@celery_app.task(name="tasks.send_alerts", queue="high")
def send_alerts(
    alert_configs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Send alerts based on configurations.
    
    Args:
        alert_configs: List of alert configurations
        
    Returns:
        Alert sending results
    """
    logger.info(
        "sending_alerts",
        alert_count=len(alert_configs)
    )
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _send_alerts_async(alert_configs)
            )
            
            return result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(
            "alert_sending_failed",
            error=str(e),
            exc_info=True
        )
        raise


async def _send_alerts_async(
    alert_configs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Async alert sending implementation."""
    notification_service = NotificationService()
    
    sent_alerts = []
    failed_alerts = []
    
    for config in alert_configs:
        try:
            alert_type = config.get("type")
            recipients = config.get("recipients", [])
            content = config.get("content", {})
            
            if alert_type == "email":
                result = await notification_service.send_email_alert(
                    recipients=recipients,
                    subject=content.get("subject", "Cidadão.AI Alert"),
                    body=content.get("body", ""),
                    priority=config.get("priority", "normal")
                )
            elif alert_type == "webhook":
                result = await notification_service.send_webhook_alert(
                    url=config.get("webhook_url"),
                    payload=content
                )
            else:
                result = {"success": False, "error": f"Unknown alert type: {alert_type}"}
            
            if result.get("success"):
                sent_alerts.append({
                    "type": alert_type,
                    "recipients": len(recipients) if alert_type == "email" else 1,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                failed_alerts.append({
                    "type": alert_type,
                    "error": result.get("error"),
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            failed_alerts.append({
                "type": config.get("type", "unknown"),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    return {
        "total_alerts": len(alert_configs),
        "sent": len(sent_alerts),
        "failed": len(failed_alerts),
        "sent_alerts": sent_alerts,
        "failed_alerts": failed_alerts
    }


@priority_task(priority=TaskPriority.CRITICAL)
def system_health_check() -> Dict[str, Any]:
    """
    Perform system health check.
    
    Returns:
        Health check results
    """
    logger.info("system_health_check_started")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_system_health_check_async())
            
            # Send alert if any component is unhealthy
            if not result.get("healthy"):
                send_alerts.delay([{
                    "type": "email",
                    "recipients": ["admin@cidadao.ai"],
                    "content": {
                        "subject": "System Health Alert",
                        "body": f"System health check failed: {result}"
                    },
                    "priority": "critical"
                }])
            
            return result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(
            "health_check_failed",
            error=str(e),
            exc_info=True
        )
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


async def _system_health_check_async() -> Dict[str, Any]:
    """Async system health check implementation."""
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "components": {},
        "healthy": True
    }
    
    # Check database
    try:
        async with get_db_session() as db:
            await db.execute("SELECT 1")
            health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {str(e)}"
        health_status["healthy"] = False
    
    # Check agent pool
    try:
        agent_pool = get_agent_pool()
        agent_count = len(agent_pool._agents)
        health_status["components"]["agents"] = f"healthy: {agent_count} agents"
    except Exception as e:
        health_status["components"]["agents"] = f"unhealthy: {str(e)}"
        health_status["healthy"] = False
    
    # Check Redis (cache/queue)
    try:
        from src.core.cache import get_redis_client
        redis = await get_redis_client()
        await redis.ping()
        health_status["components"]["redis"] = "healthy"
    except Exception as e:
        health_status["components"]["redis"] = f"unhealthy: {str(e)}"
        health_status["healthy"] = False
    
    return health_status


# Periodic monitoring tasks
@celery_app.task(name="tasks.continuous_monitoring", queue="normal")
def continuous_monitoring() -> Dict[str, Any]:
    """Run continuous monitoring cycle."""
    logger.info("continuous_monitoring_cycle_started")
    
    # Run monitoring tasks
    results = {}
    
    # Monitor anomalies
    anomaly_result = monitor_anomalies.apply_async(
        args=[{
            "data_source": "contracts",
            "time_window": 60,
            "categories": []
        }],
        kwargs={"alert_threshold": 0.8}
    ).get()
    results["anomalies"] = anomaly_result
    
    # Check data updates
    update_result = check_data_updates.apply_async(
        args=[["contracts", "suppliers"]],
        kwargs={"check_interval_hours": 1}
    ).get()
    results["updates"] = update_result
    
    # System health
    health_result = system_health_check.apply_async().get()
    results["health"] = health_result
    
    logger.info(
        "continuous_monitoring_cycle_completed",
        anomalies_found=results["anomalies"].get("anomalies_detected", 0),
        updates_found=results["updates"].get("total_updates", 0),
        system_healthy=results["health"].get("healthy", False)
    )
    
    return results