"""
Module: infrastructure.queue.tasks.investigation_tasks
Description: Celery tasks for investigation processing
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from celery import group, chain
from celery.utils.log import get_task_logger

from src.infrastructure.queue.celery_app import celery_app, priority_task, TaskPriority
from src.services.investigation_service_selector import investigation_service as InvestigationService
from src.services.data_service import DataService
from src.db.simple_session import get_db_session
from src.agents import get_agent_pool

logger = get_task_logger(__name__)


@celery_app.task(name="tasks.run_investigation", bind=True, queue="high")
def run_investigation(
    self,
    investigation_id: str,
    query: str,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run a complete investigation asynchronously.
    
    Args:
        investigation_id: Unique investigation ID
        query: Investigation query
        config: Optional investigation configuration
        
    Returns:
        Investigation results
    """
    try:
        logger.info(
            "investigation_started",
            investigation_id=investigation_id,
            query=query[:100]
        )
        
        # Run async investigation in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _run_investigation_async(investigation_id, query, config)
            )
            
            logger.info(
                "investigation_completed",
                investigation_id=investigation_id,
                findings_count=len(result.get("findings", []))
            )
            
            return result
            
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(
            "investigation_failed",
            investigation_id=investigation_id,
            error=str(e),
            exc_info=True
        )
        
        # Retry with exponential backoff
        raise self.retry(
            exc=e,
            countdown=60 * (2 ** self.request.retries),
            max_retries=3
        )


async def _run_investigation_async(
    investigation_id: str,
    query: str,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Async implementation of investigation."""
    async with get_db_session() as db:
        investigation_service = InvestigationService(db)
        agent_pool = get_agent_pool()
        
        # Create investigation
        investigation = await investigation_service.create(
            query=query,
            context=config or {},
            initiated_by="celery_task"
        )
        
        # Run investigation with agents
        result = await investigation_service.run_investigation(
            investigation_id=investigation.id,
            agent_pool=agent_pool
        )
        
        return result.dict()


@celery_app.task(name="tasks.analyze_contracts_batch", queue="normal")
def analyze_contracts_batch(
    contract_ids: List[str],
    analysis_type: str = "anomaly",
    threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Analyze multiple contracts in batch.
    
    Args:
        contract_ids: List of contract IDs to analyze
        analysis_type: Type of analysis (anomaly, compliance, value)
        threshold: Detection threshold
        
    Returns:
        Batch analysis results
    """
    logger.info(
        "batch_analysis_started",
        contract_count=len(contract_ids),
        analysis_type=analysis_type
    )
    
    # Create subtasks for each contract
    tasks = []
    for contract_id in contract_ids:
        task = analyze_single_contract.s(
            contract_id=contract_id,
            analysis_type=analysis_type,
            threshold=threshold
        )
        tasks.append(task)
    
    # Execute tasks in parallel
    job = group(tasks)
    results = job.apply_async()
    
    # Wait for results
    contract_results = results.get(timeout=300)  # 5 minutes timeout
    
    # Aggregate results
    summary = {
        "total_contracts": len(contract_ids),
        "analyzed": len(contract_results),
        "anomalies_found": sum(1 for r in contract_results if r.get("has_anomaly", False)),
        "analysis_type": analysis_type,
        "threshold": threshold,
        "results": contract_results
    }
    
    logger.info(
        "batch_analysis_completed",
        total=summary["total_contracts"],
        anomalies=summary["anomalies_found"]
    )
    
    return summary


@celery_app.task(name="tasks.analyze_single_contract", queue="normal")
def analyze_single_contract(
    contract_id: str,
    analysis_type: str,
    threshold: float
) -> Dict[str, Any]:
    """Analyze a single contract."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _analyze_contract_async(contract_id, analysis_type, threshold)
            )
            return result
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(
            "contract_analysis_failed",
            contract_id=contract_id,
            error=str(e)
        )
        return {
            "contract_id": contract_id,
            "error": str(e),
            "has_anomaly": False
        }


async def _analyze_contract_async(
    contract_id: str,
    analysis_type: str,
    threshold: float
) -> Dict[str, Any]:
    """Async contract analysis."""
    async with get_db_session() as db:
        data_service = DataService(db)
        agent_pool = get_agent_pool()
        
        # Get contract data
        contract = await data_service.get_contract(contract_id)
        if not contract:
            return {
                "contract_id": contract_id,
                "error": "Contract not found",
                "has_anomaly": False
            }
        
        # Get Zumbi agent for anomaly detection
        zumbi = agent_pool.get_agent("zumbi")
        if not zumbi:
            return {
                "contract_id": contract_id,
                "error": "Agent not available",
                "has_anomaly": False
            }
        
        # Analyze contract
        analysis = await zumbi.analyze_contract(
            contract,
            threshold=threshold,
            analysis_type=analysis_type
        )
        
        return {
            "contract_id": contract_id,
            "has_anomaly": analysis.anomaly_detected,
            "anomaly_score": analysis.anomaly_score,
            "indicators": analysis.indicators,
            "recommendations": analysis.recommendations
        }


@celery_app.task(name="tasks.detect_anomalies_batch", queue="high")
def detect_anomalies_batch(
    data_source: str,
    time_range: Dict[str, str],
    detection_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run batch anomaly detection on data source.
    
    Args:
        data_source: Source of data (contracts, transactions, etc.)
        time_range: Time range for analysis
        detection_config: Detection configuration
        
    Returns:
        Anomaly detection results
    """
    logger.info(
        "anomaly_detection_started",
        data_source=data_source,
        time_range=time_range
    )
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _detect_anomalies_async(data_source, time_range, detection_config)
            )
            
            logger.info(
                "anomaly_detection_completed",
                anomalies_found=len(result.get("anomalies", []))
            )
            
            return result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(
            "anomaly_detection_failed",
            error=str(e),
            exc_info=True
        )
        raise


async def _detect_anomalies_async(
    data_source: str,
    time_range: Dict[str, str],
    detection_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Async anomaly detection."""
    async with get_db_session() as db:
        data_service = DataService(db)
        agent_pool = get_agent_pool()
        
        # Get data for analysis
        if data_source == "contracts":
            data = await data_service.get_contracts_in_range(
                start_date=time_range.get("start"),
                end_date=time_range.get("end")
            )
        else:
            raise ValueError(f"Unknown data source: {data_source}")
        
        # Get Zumbi agent
        zumbi = agent_pool.get_agent("zumbi")
        if not zumbi:
            raise RuntimeError("Anomaly detection agent not available")
        
        # Run detection
        anomalies = []
        for item in data:
            result = await zumbi.detect_anomalies(
                data=item,
                config=detection_config or {}
            )
            
            if result.anomaly_detected:
                anomalies.append({
                    "id": item.get("id"),
                    "type": result.anomaly_type,
                    "score": result.anomaly_score,
                    "description": result.description,
                    "timestamp": datetime.now().isoformat()
                })
        
        return {
            "data_source": data_source,
            "time_range": time_range,
            "total_analyzed": len(data),
            "anomalies_found": len(anomalies),
            "anomalies": anomalies
        }


@priority_task(priority=TaskPriority.CRITICAL)
def emergency_investigation(
    query: str,
    reason: str,
    initiated_by: str
) -> Dict[str, Any]:
    """
    Run emergency investigation with highest priority.
    
    Args:
        query: Investigation query
        reason: Reason for emergency
        initiated_by: Who initiated the investigation
        
    Returns:
        Investigation results
    """
    logger.warning(
        "emergency_investigation_started",
        query=query[:100],
        reason=reason,
        initiated_by=initiated_by
    )
    
    # Create investigation with special handling
    investigation_id = f"EMERGENCY-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Run with increased resources
    result = run_investigation.apply_async(
        args=[investigation_id, query],
        kwargs={"config": {"priority": "critical", "reason": reason}},
        priority=10,  # Highest priority
        time_limit=1800,  # 30 minutes
    )
    
    return result.get()