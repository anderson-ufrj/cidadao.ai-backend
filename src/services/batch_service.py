"""
Module: services.batch_service
Description: Batch processing service integrating Celery and priority queue
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from celery import chain, group
from celery.result import AsyncResult
from pydantic import BaseModel, Field

from src.core import get_logger
from src.infrastructure.queue.celery_app import celery_app, get_celery_app
from src.infrastructure.queue.priority_queue import (
    QueueStats,
    TaskPriority,
    priority_queue,
)
from src.infrastructure.queue.tasks import (
    analyze_contracts_batch,
    analyze_patterns,
    export_to_pdf,
    generate_report,
    monitor_anomalies,
    run_investigation,
)

logger = get_logger(__name__)


class BatchType(str, Enum):
    """Batch processing types."""

    INVESTIGATION = "investigation"
    ANALYSIS = "analysis"
    REPORT = "report"
    EXPORT = "export"
    MONITORING = "monitoring"


class BatchJobRequest(BaseModel):
    """Batch job request model."""

    batch_type: BatchType
    items: list[dict[str, Any]]
    priority: TaskPriority = TaskPriority.NORMAL
    parallel: bool = True
    max_workers: int = 5
    callback_url: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BatchJobStatus(BaseModel):
    """Batch job status model."""

    job_id: str
    batch_type: BatchType
    total_items: int
    completed: int
    failed: int
    pending: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    results: list[dict[str, Any]] = Field(default_factory=list)


class BatchProcessingService:
    """Service for batch processing operations."""

    def __init__(self):
        """Initialize batch processing service."""
        self.celery_app = get_celery_app()
        self._active_jobs: dict[str, BatchJobStatus] = {}
        self._job_results: dict[str, list[AsyncResult]] = {}

        logger.info("batch_service_initialized")

    async def start(self):
        """Start batch processing service."""
        # Start priority queue
        await priority_queue.start()

        # Register handlers
        self._register_handlers()

        logger.info("batch_service_started")

    async def stop(self):
        """Stop batch processing service."""
        # Stop priority queue
        await priority_queue.stop()

        # Cancel active jobs
        for job_id, results in self._job_results.items():
            for result in results:
                if not result.ready():
                    result.revoke(terminate=True)

        logger.info("batch_service_stopped")

    def _register_handlers(self):
        """Register task handlers with priority queue."""

        # Investigation handler
        async def investigation_handler(
            payload: dict[str, Any], metadata: dict[str, Any]
        ):
            result = run_investigation.delay(
                investigation_id=payload["investigation_id"],
                query=payload["query"],
                config=payload.get("config"),
            )
            return result.id

        priority_queue.register_handler("investigation", investigation_handler)

        # Analysis handler
        async def analysis_handler(payload: dict[str, Any], metadata: dict[str, Any]):
            result = analyze_patterns.delay(
                data_type=payload["data_type"],
                time_range=payload["time_range"],
                pattern_types=payload.get("pattern_types"),
                min_confidence=payload.get("min_confidence", 0.7),
            )
            return result.id

        priority_queue.register_handler("analysis", analysis_handler)

    async def submit_batch_job(self, request: BatchJobRequest) -> BatchJobStatus:
        """
        Submit a batch job for processing.

        Args:
            request: Batch job request

        Returns:
            Batch job status
        """
        job_id = f"BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create job status
        job_status = BatchJobStatus(
            job_id=job_id,
            batch_type=request.batch_type,
            total_items=len(request.items),
            completed=0,
            failed=0,
            pending=len(request.items),
            status="submitted",
            started_at=datetime.now(),
        )

        self._active_jobs[job_id] = job_status

        logger.info(
            "batch_job_submitted",
            job_id=job_id,
            batch_type=request.batch_type.value,
            items=len(request.items),
            priority=request.priority.name,
        )

        # Create tasks based on batch type
        if request.batch_type == BatchType.INVESTIGATION:
            await self._process_investigation_batch(job_id, request)
        elif request.batch_type == BatchType.ANALYSIS:
            await self._process_analysis_batch(job_id, request)
        elif request.batch_type == BatchType.REPORT:
            await self._process_report_batch(job_id, request)
        elif request.batch_type == BatchType.EXPORT:
            await self._process_export_batch(job_id, request)
        elif request.batch_type == BatchType.MONITORING:
            await self._process_monitoring_batch(job_id, request)

        # Update status
        job_status.status = "processing"

        return job_status

    async def _process_investigation_batch(self, job_id: str, request: BatchJobRequest):
        """Process investigation batch."""
        tasks = []

        for item in request.items:
            task = run_investigation.s(
                investigation_id=item.get("id", f"{job_id}-{len(tasks)}"),
                query=item["query"],
                config=item.get("config", {}),
            )
            tasks.append(task)

        # Execute based on parallelism
        if request.parallel:
            job = group(tasks)
        else:
            job = chain(tasks)

        # Submit to Celery
        result = job.apply_async(
            priority=request.priority.value,
            link=self._create_callback_task(job_id, request.callback_url),
        )

        self._job_results[job_id] = [result]

    async def _process_analysis_batch(self, job_id: str, request: BatchJobRequest):
        """Process analysis batch."""
        tasks = []

        for item in request.items:
            if item.get("type") == "contracts":
                task = analyze_contracts_batch.s(
                    contract_ids=item["contract_ids"],
                    analysis_type=item.get("analysis_type", "anomaly"),
                    threshold=item.get("threshold", 0.7),
                )
            elif item.get("type") == "patterns":
                task = analyze_patterns.s(
                    data_type=item["data_type"],
                    time_range=item["time_range"],
                    pattern_types=item.get("pattern_types"),
                    min_confidence=item.get("min_confidence", 0.7),
                )
            else:
                continue

            tasks.append(task)

        # Execute in parallel
        job = group(tasks)
        result = job.apply_async(
            priority=request.priority.value,
            link=self._create_callback_task(job_id, request.callback_url),
        )

        self._job_results[job_id] = [result]

    async def _process_report_batch(self, job_id: str, request: BatchJobRequest):
        """Process report batch."""
        tasks = []

        for item in request.items:
            task = generate_report.s(
                report_id=item.get("id", f"{job_id}-{len(tasks)}"),
                report_type=item["report_type"],
                investigation_ids=item["investigation_ids"],
                config=item.get("config", {}),
            )
            tasks.append(task)

        # Generate reports in parallel
        job = group(tasks)
        result = job.apply_async(
            priority=request.priority.value,
            link=self._create_callback_task(job_id, request.callback_url),
        )

        self._job_results[job_id] = [result]

    async def _process_export_batch(self, job_id: str, request: BatchJobRequest):
        """Process export batch."""
        tasks = []

        for item in request.items:
            task = export_to_pdf.s(
                content_type=item["content_type"],
                content_id=item["content_id"],
                options=item.get("options", {}),
            )
            tasks.append(task)

        # Export in parallel with limited workers
        job = group(tasks)
        result = job.apply_async(
            priority=request.priority.value,
            link=self._create_callback_task(job_id, request.callback_url),
            queue="normal",
        )

        self._job_results[job_id] = [result]

    async def _process_monitoring_batch(self, job_id: str, request: BatchJobRequest):
        """Process monitoring batch."""
        tasks = []

        for item in request.items:
            task = monitor_anomalies.s(
                monitoring_config=item["config"],
                alert_threshold=item.get("threshold", 0.8),
            )
            tasks.append(task)

        # Run monitoring tasks
        job = group(tasks)
        result = job.apply_async(
            priority=request.priority.value,
            link=self._create_callback_task(job_id, request.callback_url),
        )

        self._job_results[job_id] = [result]

    def _create_callback_task(self, job_id: str, callback_url: Optional[str]):
        """Create callback task for job completion."""
        if not callback_url:
            return None

        @celery_app.task
        def batch_completion_callback(results):
            # Update job status
            job_status = self._active_jobs.get(job_id)
            if job_status:
                job_status.completed_at = datetime.now()
                job_status.duration_seconds = (
                    job_status.completed_at - job_status.started_at
                ).total_seconds()
                job_status.status = "completed"
                job_status.results = results

            # Send callback
            import httpx

            with httpx.Client() as client:
                client.post(
                    callback_url,
                    json={
                        "job_id": job_id,
                        "status": "completed",
                        "results": results,
                        "completed_at": datetime.now().isoformat(),
                    },
                    timeout=30.0,
                )

        return batch_completion_callback.s()

    async def get_job_status(self, job_id: str) -> Optional[BatchJobStatus]:
        """
        Get batch job status.

        Args:
            job_id: Job ID

        Returns:
            Job status or None
        """
        job_status = self._active_jobs.get(job_id)
        if not job_status:
            return None

        # Update status from Celery results
        if job_id in self._job_results:
            results = self._job_results[job_id]
            completed = 0
            failed = 0

            for result in results:
                if result.ready():
                    if result.successful():
                        completed += 1
                    else:
                        failed += 1

            job_status.completed = completed
            job_status.failed = failed
            job_status.pending = job_status.total_items - completed - failed

            if job_status.pending == 0:
                job_status.status = (
                    "completed" if failed == 0 else "completed_with_errors"
                )
                if not job_status.completed_at:
                    job_status.completed_at = datetime.now()
                    job_status.duration_seconds = (
                        job_status.completed_at - job_status.started_at
                    ).total_seconds()

        return job_status

    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a batch job.

        Args:
            job_id: Job ID

        Returns:
            True if cancelled
        """
        if job_id not in self._job_results:
            return False

        # Revoke Celery tasks
        for result in self._job_results[job_id]:
            if not result.ready():
                result.revoke(terminate=True)

        # Update status
        job_status = self._active_jobs.get(job_id)
        if job_status:
            job_status.status = "cancelled"
            job_status.completed_at = datetime.now()
            job_status.duration_seconds = (
                job_status.completed_at - job_status.started_at
            ).total_seconds()

        logger.info("batch_job_cancelled", job_id=job_id)

        return True

    async def get_queue_stats(self) -> QueueStats:
        """Get queue statistics."""
        return await priority_queue.get_stats()

    async def cleanup_old_jobs(self, days: int = 7):
        """Clean up old completed jobs."""
        cutoff_time = datetime.now() - timedelta(days=days)

        jobs_to_remove = []
        for job_id, job_status in self._active_jobs.items():
            if job_status.completed_at and job_status.completed_at < cutoff_time:
                jobs_to_remove.append(job_id)

        for job_id in jobs_to_remove:
            del self._active_jobs[job_id]
            if job_id in self._job_results:
                del self._job_results[job_id]

        logger.info(
            "old_jobs_cleaned",
            removed=len(jobs_to_remove),
            remaining=len(self._active_jobs),
        )


# Global batch service instance
batch_service = BatchProcessingService()
