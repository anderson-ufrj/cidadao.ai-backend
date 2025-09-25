"""
Module: infrastructure.queue.priority_queue
Description: Priority queue system for task management
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import asyncio
import heapq
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, TypeVar, Generic
from enum import IntEnum
from dataclasses import dataclass, field
from uuid import uuid4
import json

from pydantic import BaseModel, Field

from src.core import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class TaskPriority(IntEnum):
    """Task priority levels."""
    CRITICAL = 1  # Highest priority
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5  # Lowest priority


class TaskStatus(str):
    """Task status constants."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


@dataclass(order=True)
class PriorityTask:
    """Priority task with comparison support for heapq."""
    priority: int
    timestamp: float = field(compare=False)
    task_id: str = field(compare=False)
    task_type: str = field(compare=False)
    payload: Dict[str, Any] = field(compare=False)
    retry_count: int = field(default=0, compare=False)
    max_retries: int = field(default=3, compare=False)
    timeout: int = field(default=300, compare=False)  # 5 minutes default
    callback: Optional[str] = field(default=None, compare=False)
    metadata: Dict[str, Any] = field(default_factory=dict, compare=False)


class TaskResult(BaseModel):
    """Task execution result."""
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    retry_count: int = 0


class QueueStats(BaseModel):
    """Queue statistics."""
    pending_tasks: int
    processing_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_processed: int
    average_processing_time: float
    tasks_by_priority: Dict[str, int]
    tasks_by_type: Dict[str, int]


class PriorityQueueService:
    """Priority queue service for managing tasks."""
    
    def __init__(self, max_workers: int = 5):
        """Initialize priority queue service."""
        self.max_workers = max_workers
        self._queue: List[PriorityTask] = []
        self._processing: Dict[str, PriorityTask] = {}
        self._completed: Dict[str, TaskResult] = {}
        self._failed: Dict[str, TaskResult] = {}
        self._workers: List[asyncio.Task] = []
        self._handlers: Dict[str, Callable] = {}
        self._running = False
        self._total_processed = 0
        self._total_processing_time = 0.0
        self._lock = asyncio.Lock()
        
        logger.info(
            "priority_queue_initialized",
            max_workers=max_workers
        )
    
    async def start(self):
        """Start queue workers."""
        if self._running:
            return
        
        self._running = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)
        
        logger.info(
            "priority_queue_started",
            workers=len(self._workers)
        )
    
    async def stop(self):
        """Stop queue workers."""
        self._running = False
        
        # Cancel all workers
        for worker in self._workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        
        self._workers.clear()
        
        logger.info("priority_queue_stopped")
    
    def register_handler(self, task_type: str, handler: Callable):
        """Register a task handler."""
        self._handlers[task_type] = handler
        logger.info(
            "task_handler_registered",
            task_type=task_type,
            handler=handler.__name__
        )
    
    async def enqueue(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: int = 300,
        max_retries: int = 3,
        callback: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Enqueue a task with priority.
        
        Args:
            task_type: Type of task to execute
            payload: Task payload data
            priority: Task priority level
            timeout: Task timeout in seconds
            max_retries: Maximum retry attempts
            callback: Optional callback URL
            metadata: Optional task metadata
            
        Returns:
            Task ID
        """
        task_id = str(uuid4())
        
        task = PriorityTask(
            priority=priority.value,
            timestamp=datetime.now().timestamp(),
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            timeout=timeout,
            max_retries=max_retries,
            callback=callback,
            metadata=metadata or {}
        )
        
        async with self._lock:
            heapq.heappush(self._queue, task)
        
        logger.info(
            "task_enqueued",
            task_id=task_id,
            task_type=task_type,
            priority=priority.name,
            queue_size=len(self._queue)
        )
        
        return task_id
    
    async def dequeue(self) -> Optional[PriorityTask]:
        """Dequeue highest priority task."""
        async with self._lock:
            if self._queue:
                task = heapq.heappop(self._queue)
                self._processing[task.task_id] = task
                return task
        return None
    
    async def get_task_status(self, task_id: str) -> Optional[str]:
        """Get task status."""
        # Check if processing
        if task_id in self._processing:
            return TaskStatus.PROCESSING
        
        # Check if completed
        if task_id in self._completed:
            return TaskStatus.COMPLETED
        
        # Check if failed
        if task_id in self._failed:
            return TaskStatus.FAILED
        
        # Check if in queue
        async with self._lock:
            for task in self._queue:
                if task.task_id == task_id:
                    return TaskStatus.PENDING
        
        return None
    
    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task result if completed or failed."""
        if task_id in self._completed:
            return self._completed[task_id]
        elif task_id in self._failed:
            return self._failed[task_id]
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        async with self._lock:
            # Remove from queue if pending
            self._queue = [t for t in self._queue if t.task_id != task_id]
            heapq.heapify(self._queue)
            
            # Cannot cancel if already processing
            if task_id in self._processing:
                return False
            
            return True
    
    async def get_stats(self) -> QueueStats:
        """Get queue statistics."""
        tasks_by_priority = {}
        tasks_by_type = {}
        
        # Count pending tasks
        async with self._lock:
            for task in self._queue:
                priority_name = TaskPriority(task.priority).name
                tasks_by_priority[priority_name] = tasks_by_priority.get(priority_name, 0) + 1
                tasks_by_type[task.task_type] = tasks_by_type.get(task.task_type, 0) + 1
        
        avg_time = (
            self._total_processing_time / self._total_processed
            if self._total_processed > 0
            else 0.0
        )
        
        return QueueStats(
            pending_tasks=len(self._queue),
            processing_tasks=len(self._processing),
            completed_tasks=len(self._completed),
            failed_tasks=len(self._failed),
            total_processed=self._total_processed,
            average_processing_time=avg_time,
            tasks_by_priority=tasks_by_priority,
            tasks_by_type=tasks_by_type
        )
    
    async def _worker(self, worker_id: str):
        """Worker coroutine to process tasks."""
        logger.info(f"Worker {worker_id} started")
        
        while self._running:
            try:
                # Get next task
                task = await self.dequeue()
                if not task:
                    # No tasks, wait a bit
                    await asyncio.sleep(0.1)
                    continue
                
                # Process task
                await self._process_task(task, worker_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    f"Worker {worker_id} error",
                    error=str(e),
                    exc_info=True
                )
                await asyncio.sleep(1)
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def _process_task(self, task: PriorityTask, worker_id: str):
        """Process a single task."""
        start_time = datetime.now()
        
        logger.info(
            "task_processing_started",
            worker_id=worker_id,
            task_id=task.task_id,
            task_type=task.task_type
        )
        
        try:
            # Get handler
            handler = self._handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"No handler registered for task type: {task.task_type}")
            
            # Execute with timeout
            result = await asyncio.wait_for(
                handler(task.payload, task.metadata),
                timeout=task.timeout
            )
            
            # Task completed successfully
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            task_result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                started_at=start_time,
                completed_at=end_time,
                duration_seconds=duration,
                retry_count=task.retry_count
            )
            
            self._completed[task.task_id] = task_result
            self._processing.pop(task.task_id, None)
            
            self._total_processed += 1
            self._total_processing_time += duration
            
            logger.info(
                "task_completed",
                worker_id=worker_id,
                task_id=task.task_id,
                duration=duration
            )
            
            # Execute callback if provided
            if task.callback:
                await self._execute_callback(task, task_result)
            
        except asyncio.TimeoutError:
            await self._handle_task_failure(
                task, worker_id, "Task timeout", start_time
            )
        except Exception as e:
            await self._handle_task_failure(
                task, worker_id, str(e), start_time
            )
    
    async def _handle_task_failure(
        self,
        task: PriorityTask,
        worker_id: str,
        error: str,
        start_time: datetime
    ):
        """Handle task failure with retry logic."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        task.retry_count += 1
        
        if task.retry_count <= task.max_retries:
            # Retry with exponential backoff
            backoff = min(2 ** task.retry_count, 60)  # Max 60 seconds
            await asyncio.sleep(backoff)
            
            # Re-enqueue with same priority
            async with self._lock:
                heapq.heappush(self._queue, task)
            
            self._processing.pop(task.task_id, None)
            
            logger.warning(
                "task_retry",
                worker_id=worker_id,
                task_id=task.task_id,
                retry_count=task.retry_count,
                error=error
            )
        else:
            # Max retries exceeded, mark as failed
            task_result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=error,
                started_at=start_time,
                completed_at=end_time,
                duration_seconds=duration,
                retry_count=task.retry_count
            )
            
            self._failed[task.task_id] = task_result
            self._processing.pop(task.task_id, None)
            
            logger.error(
                "task_failed",
                worker_id=worker_id,
                task_id=task.task_id,
                error=error,
                retry_count=task.retry_count
            )
            
            # Execute callback with failure
            if task.callback:
                await self._execute_callback(task, task_result)
    
    async def _execute_callback(self, task: PriorityTask, result: TaskResult):
        """Execute task callback."""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                await client.post(
                    task.callback,
                    json={
                        "task_id": task.task_id,
                        "task_type": task.task_type,
                        "status": result.status,
                        "result": result.result,
                        "error": result.error,
                        "duration_seconds": result.duration_seconds
                    },
                    timeout=30.0
                )
            
            logger.info(
                "callback_executed",
                task_id=task.task_id,
                callback=task.callback
            )
            
        except Exception as e:
            logger.error(
                "callback_failed",
                task_id=task.task_id,
                callback=task.callback,
                error=str(e)
            )
    
    def clear_completed(self, older_than_minutes: int = 60):
        """Clear old completed tasks."""
        cutoff_time = datetime.now() - timedelta(minutes=older_than_minutes)
        
        # Clear old completed tasks
        self._completed = {
            task_id: result
            for task_id, result in self._completed.items()
            if result.completed_at > cutoff_time
        }
        
        # Clear old failed tasks
        self._failed = {
            task_id: result
            for task_id, result in self._failed.items()
            if result.completed_at > cutoff_time
        }
        
        logger.info(
            "old_tasks_cleared",
            remaining_completed=len(self._completed),
            remaining_failed=len(self._failed)
        )


# Global priority queue instance
priority_queue = PriorityQueueService()