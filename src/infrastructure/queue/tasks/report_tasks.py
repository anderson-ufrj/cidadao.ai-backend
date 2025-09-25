"""
Module: infrastructure.queue.tasks.report_tasks
Description: Celery tasks for report generation and processing
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from celery import chain, group
from celery.utils.log import get_task_logger

from src.infrastructure.queue.celery_app import celery_app, priority_task, TaskPriority
from src.services.report_service import ReportService
from src.services.export_service import ExportService
from src.core.dependencies import get_db_session
from src.agents import get_agent_pool

logger = get_task_logger(__name__)


@celery_app.task(name="tasks.generate_report", bind=True, queue="normal")
def generate_report(
    self,
    report_id: str,
    report_type: str,
    investigation_ids: List[str],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a comprehensive report.
    
    Args:
        report_id: Unique report ID
        report_type: Type of report to generate
        investigation_ids: List of investigation IDs to include
        config: Report configuration
        
    Returns:
        Generated report data
    """
    try:
        logger.info(
            "report_generation_started",
            report_id=report_id,
            report_type=report_type,
            investigations=len(investigation_ids)
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={
                "current": 0,
                "total": 100,
                "status": "Initializing report generation..."
            }
        )
        
        # Run async report generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _generate_report_async(
                    self,
                    report_id,
                    report_type,
                    investigation_ids,
                    config
                )
            )
            
            logger.info(
                "report_generation_completed",
                report_id=report_id,
                word_count=result.get("word_count", 0)
            )
            
            return result
            
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(
            "report_generation_failed",
            report_id=report_id,
            error=str(e),
            exc_info=True
        )
        
        # Retry with exponential backoff
        raise self.retry(
            exc=e,
            countdown=60 * (2 ** self.request.retries),
            max_retries=3
        )


async def _generate_report_async(
    task,
    report_id: str,
    report_type: str,
    investigation_ids: List[str],
    config: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Async report generation implementation."""
    async with get_db_session() as db:
        report_service = ReportService(db)
        agent_pool = get_agent_pool()
        
        # Get Tiradentes agent for report generation
        tiradentes = agent_pool.get_agent("tiradentes")
        if not tiradentes:
            raise RuntimeError("Report generation agent not available")
        
        # Update progress
        task.update_state(
            state="PROGRESS",
            meta={
                "current": 20,
                "total": 100,
                "status": "Loading investigation data..."
            }
        )
        
        # Load investigations
        investigations = await report_service.load_investigations(investigation_ids)
        
        # Update progress
        task.update_state(
            state="PROGRESS",
            meta={
                "current": 40,
                "total": 100,
                "status": "Analyzing findings..."
            }
        )
        
        # Generate report content
        report_content = await tiradentes.generate_report(
            report_type=report_type,
            investigations=investigations,
            config=config or {}
        )
        
        # Update progress
        task.update_state(
            state="PROGRESS",
            meta={
                "current": 80,
                "total": 100,
                "status": "Finalizing report..."
            }
        )
        
        # Save report
        report = await report_service.save_report(
            report_id=report_id,
            report_type=report_type,
            content=report_content,
            metadata={
                "investigation_ids": investigation_ids,
                "generated_by": "tiradentes",
                "config": config
            }
        )
        
        # Update progress
        task.update_state(
            state="PROGRESS",
            meta={
                "current": 100,
                "total": 100,
                "status": "Report completed!"
            }
        )
        
        return {
            "report_id": report.id,
            "report_type": report_type,
            "title": report.title,
            "word_count": len(report_content.split()),
            "status": "completed",
            "created_at": report.created_at.isoformat()
        }


@celery_app.task(name="tasks.generate_executive_summary", queue="high")
def generate_executive_summary(
    investigation_ids: List[str],
    max_length: int = 500
) -> Dict[str, Any]:
    """
    Generate executive summary from investigations.
    
    Args:
        investigation_ids: Investigation IDs to summarize
        max_length: Maximum summary length in words
        
    Returns:
        Executive summary
    """
    logger.info(
        "executive_summary_started",
        investigations=len(investigation_ids),
        max_length=max_length
    )
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _generate_executive_summary_async(
                    investigation_ids,
                    max_length
                )
            )
            
            return result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(
            "executive_summary_failed",
            error=str(e),
            exc_info=True
        )
        raise


async def _generate_executive_summary_async(
    investigation_ids: List[str],
    max_length: int
) -> Dict[str, Any]:
    """Async executive summary generation."""
    async with get_db_session() as db:
        report_service = ReportService(db)
        agent_pool = get_agent_pool()
        
        # Get Tiradentes agent
        tiradentes = agent_pool.get_agent("tiradentes")
        if not tiradentes:
            raise RuntimeError("Report agent not available")
        
        # Load investigations
        investigations = await report_service.load_investigations(investigation_ids)
        
        # Generate summary
        summary = await tiradentes.generate_executive_summary(
            investigations=investigations,
            max_length=max_length
        )
        
        return {
            "summary": summary,
            "word_count": len(summary.split()),
            "investigation_count": len(investigations),
            "key_findings": await tiradentes.extract_key_findings(investigations),
            "generated_at": datetime.now().isoformat()
        }


@celery_app.task(name="tasks.batch_report_generation", queue="normal")
def batch_report_generation(
    report_configs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate multiple reports in batch.
    
    Args:
        report_configs: List of report configurations
        
    Returns:
        Batch generation results
    """
    logger.info(
        "batch_report_generation_started",
        report_count=len(report_configs)
    )
    
    # Create subtasks for each report
    tasks = []
    for config in report_configs:
        task = generate_report.s(
            report_id=config["report_id"],
            report_type=config["report_type"],
            investigation_ids=config["investigation_ids"],
            config=config.get("config")
        )
        tasks.append(task)
    
    # Execute in parallel
    job = group(tasks)
    results = job.apply_async()
    
    # Wait for results
    report_results = results.get(timeout=1800)  # 30 minutes timeout
    
    # Aggregate results
    summary = {
        "total_reports": len(report_configs),
        "completed": sum(1 for r in report_results if r.get("status") == "completed"),
        "failed": sum(1 for r in report_results if r.get("status") == "failed"),
        "total_words": sum(r.get("word_count", 0) for r in report_results),
        "results": report_results
    }
    
    logger.info(
        "batch_report_generation_completed",
        total=summary["total_reports"],
        completed=summary["completed"]
    )
    
    return summary


@priority_task(priority=TaskPriority.HIGH)
def generate_urgent_report(
    investigation_id: str,
    reason: str,
    recipients: List[str]
) -> Dict[str, Any]:
    """
    Generate urgent report with notifications.
    
    Args:
        investigation_id: Investigation to report on
        reason: Reason for urgency
        recipients: Email recipients for notification
        
    Returns:
        Report generation results
    """
    logger.warning(
        "urgent_report_requested",
        investigation_id=investigation_id,
        reason=reason,
        recipients=len(recipients)
    )
    
    # Generate report with high priority
    report_id = f"URGENT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Chain tasks: generate report → export to PDF → send notifications
    workflow = chain(
        generate_report.s(
            report_id=report_id,
            report_type="urgent",
            investigation_ids=[investigation_id],
            config={"reason": reason, "priority": "urgent"}
        ),
        export_report_to_pdf.s(),
        send_report_notifications.s(recipients=recipients)
    )
    
    result = workflow.apply_async(priority=9)
    return result.get()


@celery_app.task(name="tasks.export_report_to_pdf", queue="normal")
def export_report_to_pdf(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """Export report to PDF format."""
    try:
        export_service = ExportService()
        
        pdf_content = asyncio.run(
            export_service.generate_pdf(
                content=report_data.get("content", ""),
                title=report_data.get("title", "Report"),
                metadata=report_data
            )
        )
        
        return {
            **report_data,
            "pdf_size": len(pdf_content),
            "pdf_generated": True
        }
        
    except Exception as e:
        logger.error(
            "pdf_export_failed",
            report_id=report_data.get("report_id"),
            error=str(e)
        )
        raise


@celery_app.task(name="tasks.send_report_notifications", queue="high")
def send_report_notifications(
    report_data: Dict[str, Any],
    recipients: List[str]
) -> Dict[str, Any]:
    """Send report notifications."""
    logger.info(
        "sending_notifications",
        report_id=report_data.get("report_id"),
        recipients=len(recipients)
    )
    
    # In production, this would send actual emails
    # For now, just log the action
    
    return {
        "report_id": report_data.get("report_id"),
        "notifications_sent": len(recipients),
        "timestamp": datetime.now().isoformat()
    }