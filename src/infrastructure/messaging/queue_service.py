"""
Message queue service for async processing.

This module implements a distributed task queue using Redis
for background processing and async operations.
"""

import asyncio
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import redis.asyncio as redis

from src.core import get_logger, settings
from src.core.json_utils import dumps, loads

logger = get_logger(__name__)


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Task:
    """Task definition."""

    id: str
    queue: str
    task_type: str
    payload: dict[str, Any]
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    max_retries: int = 3
    retry_count: int = 0
    error: Optional[str] = None
    result: Optional[Any] = None
    metadata: Optional[dict[str, Any]] = None

    @classmethod
    def create(
        cls,
        queue: str,
        task_type: str,
        payload: dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        scheduled_at: Optional[datetime] = None,
        max_retries: int = 3,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "Task":
        """Create a new task."""
        return cls(
            id=str(uuid.uuid4()),
            queue=queue,
            task_type=task_type,
            payload=payload,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow(),
            scheduled_at=scheduled_at,
            max_retries=max_retries,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "queue": self.queue,
            "task_type": self.task_type,
            "payload": self.payload,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "scheduled_at": (
                self.scheduled_at.isoformat() if self.scheduled_at else None
            ),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "error": self.error,
            "result": self.result,
            "metadata": self.metadata,
        }


class TaskHandler:
    """Base class for task handlers."""

    def __init__(self, task_types: list[str]):
        """
        Initialize task handler.

        Args:
            task_types: List of task types this handler can process
        """
        self.task_types = task_types
        self.logger = get_logger(self.__class__.__name__)

    async def handle(self, task: Task) -> Any:
        """
        Handle a task.

        Args:
            task: Task to handle

        Returns:
            Task result
        """
        raise NotImplementedError("Subclasses must implement handle()")

    def can_handle(self, task_type: str) -> bool:
        """Check if this handler can handle the task type."""
        return task_type in self.task_types


class QueueService:
    """
    Distributed task queue service using Redis.

    Features:
    - Multiple queue support
    - Priority-based processing
    - Scheduled tasks
    - Retry mechanism with exponential backoff
    - Dead letter queue
    - Task monitoring and metrics
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        queue_prefix: str = "queue",
        worker_name: Optional[str] = None,
        max_concurrent_tasks: int = 10,
    ):
        """
        Initialize queue service.

        Args:
            redis_client: Redis async client
            queue_prefix: Prefix for queue names
            worker_name: Unique worker name
            max_concurrent_tasks: Maximum concurrent tasks per worker
        """
        self.redis = redis_client
        self.queue_prefix = queue_prefix
        self.worker_name = worker_name or f"worker-{uuid.uuid4().hex[:8]}"
        self.max_concurrent_tasks = max_concurrent_tasks

        # Task handlers
        self._handlers: dict[str, TaskHandler] = {}

        # Running tasks
        self._running_tasks: dict[str, asyncio.Task] = {}

        # Worker state
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None

        # Statistics
        self._stats = {
            "tasks_processed": 0,
            "tasks_succeeded": 0,
            "tasks_failed": 0,
            "tasks_retried": 0,
            "total_processing_time_ms": 0.0,
        }

    def _get_queue_name(self, queue: str) -> str:
        """Get Redis queue name."""
        return f"{self.queue_prefix}:{queue}"

    def _get_priority_score(self, priority: TaskPriority) -> float:
        """Get priority score for Redis sorted set."""
        scores = {
            TaskPriority.LOW: 1.0,
            TaskPriority.MEDIUM: 2.0,
            TaskPriority.HIGH: 3.0,
            TaskPriority.CRITICAL: 4.0,
        }
        return scores.get(priority, 1.0)

    async def enqueue(
        self,
        queue: str,
        task_type: str,
        payload: dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        delay: Optional[timedelta] = None,
        max_retries: int = 3,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Enqueue a task for processing.

        Args:
            queue: Queue name
            task_type: Type of task
            payload: Task payload
            priority: Task priority
            delay: Delay before execution
            max_retries: Maximum retry attempts
            metadata: Additional metadata

        Returns:
            Task ID
        """
        # Create task
        scheduled_at = datetime.utcnow() + delay if delay else None

        task = Task.create(
            queue=queue,
            task_type=task_type,
            payload=payload,
            priority=priority,
            scheduled_at=scheduled_at,
            max_retries=max_retries,
            metadata=metadata,
        )

        # Store task data
        await self.redis.hset(
            f"task:{task.id}",
            mapping={
                "data": dumps(task.to_dict()),
                "created_at": task.created_at.isoformat(),
            },
        )

        # Add to queue
        queue_name = self._get_queue_name(queue)

        if scheduled_at:
            # Add to delayed queue (sorted by timestamp)
            await self.redis.zadd(
                f"{queue_name}:delayed", {task.id: scheduled_at.timestamp()}
            )
        else:
            # Add to priority queue
            priority_score = self._get_priority_score(priority)
            timestamp_score = time.time() / 1000000  # microsecond precision

            # Combine priority and timestamp (priority * 1M + timestamp)
            final_score = priority_score * 1000000 + timestamp_score

            await self.redis.zadd(queue_name, {task.id: final_score})

        logger.info(f"Enqueued task {task.id} in queue {queue}")
        return task.id

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        task_data = await self.redis.hget(f"task:{task_id}", "data")

        if not task_data:
            return None

        data = loads(task_data)

        # Reconstruct task
        task = Task(
            id=data["id"],
            queue=data["queue"],
            task_type=data["task_type"],
            payload=data["payload"],
            priority=TaskPriority(data["priority"]),
            status=TaskStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            scheduled_at=(
                datetime.fromisoformat(data["scheduled_at"])
                if data["scheduled_at"]
                else None
            ),
            started_at=(
                datetime.fromisoformat(data["started_at"])
                if data["started_at"]
                else None
            ),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data["completed_at"]
                else None
            ),
            max_retries=data["max_retries"],
            retry_count=data["retry_count"],
            error=data["error"],
            result=data["result"],
            metadata=data["metadata"],
        )

        return task

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        task = await self.get_task(task_id)

        if not task or task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            return False

        # Update task status
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.utcnow()

        await self._update_task(task)

        # Remove from queues
        await self.redis.zrem(self._get_queue_name(task.queue), task_id)
        await self.redis.zrem(f"{self._get_queue_name(task.queue)}:delayed", task_id)

        logger.info(f"Cancelled task {task_id}")
        return True

    def register_handler(self, handler: TaskHandler):
        """
        Register a task handler.

        Args:
            handler: Task handler to register
        """
        for task_type in handler.task_types:
            self._handlers[task_type] = handler
            logger.info(
                f"Registered handler {handler.__class__.__name__} for {task_type}"
            )

    async def start_worker(self, queues: list[str]):
        """
        Start worker to process tasks.

        Args:
            queues: List of queues to process
        """
        if self._running:
            logger.warning("Worker already running")
            return

        self._running = True
        self._worker_task = asyncio.create_task(self._worker_loop(queues))

        logger.info(f"Worker {self.worker_name} started for queues: {queues}")

    async def stop_worker(self):
        """Stop worker."""
        self._running = False

        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        # Cancel running tasks
        for task in self._running_tasks.values():
            task.cancel()

        await asyncio.gather(*self._running_tasks.values(), return_exceptions=True)
        self._running_tasks.clear()

        logger.info(f"Worker {self.worker_name} stopped")

    async def _worker_loop(self, queues: list[str]):
        """Main worker loop."""
        while self._running:
            try:
                # Check for delayed tasks that are ready
                await self._process_delayed_tasks(queues)

                # Process pending tasks
                if len(self._running_tasks) < self.max_concurrent_tasks:
                    task = await self._get_next_task(queues)

                    if task:
                        # Start processing task
                        task_coro = asyncio.create_task(self._process_task(task))
                        self._running_tasks[task.id] = task_coro

                        # Clean up completed tasks
                        await self._cleanup_completed_tasks()
                    else:
                        # No tasks available, wait a bit
                        await asyncio.sleep(0.1)
                else:
                    # Max concurrent tasks reached, wait for completion
                    await asyncio.sleep(0.1)
                    await self._cleanup_completed_tasks()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(1)

    async def _process_delayed_tasks(self, queues: list[str]):
        """Move delayed tasks that are ready to main queues."""
        now = datetime.utcnow().timestamp()

        for queue in queues:
            queue_name = self._get_queue_name(queue)
            delayed_queue = f"{queue_name}:delayed"

            # Get tasks ready for execution
            ready_tasks = await self.redis.zrangebyscore(
                delayed_queue, 0, now, withscores=True
            )

            for task_id, _ in ready_tasks:
                # Move to main queue
                task = await self.get_task(task_id)

                if task:
                    priority_score = self._get_priority_score(task.priority)
                    timestamp_score = time.time() / 1000000
                    final_score = priority_score * 1000000 + timestamp_score

                    await self.redis.zadd(queue_name, {task_id: final_score})
                    await self.redis.zrem(delayed_queue, task_id)

    async def _get_next_task(self, queues: list[str]) -> Optional[Task]:
        """Get next task from queues (highest priority first)."""
        for queue in queues:
            queue_name = self._get_queue_name(queue)

            # Get highest priority task
            result = await self.redis.zpopmax(queue_name, count=1)

            if result:
                task_id, _ = result[0]
                task = await self.get_task(task_id)

                if task and task.status == TaskStatus.PENDING:
                    return task

        return None

    async def _process_task(self, task: Task):
        """Process a single task."""
        start_time = datetime.utcnow()

        try:
            # Update task status
            task.status = TaskStatus.RUNNING
            task.started_at = start_time
            await self._update_task(task)

            # Find handler
            handler = self._handlers.get(task.task_type)

            if not handler:
                raise ValueError(f"No handler found for task type: {task.task_type}")

            # Execute task
            result = await handler.handle(task)

            # Update task with result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result

            await self._update_task(task)

            # Update statistics
            processing_time = (task.completed_at - start_time).total_seconds() * 1000
            self._stats["tasks_processed"] += 1
            self._stats["tasks_succeeded"] += 1
            self._stats["total_processing_time_ms"] += processing_time

            logger.info(f"Task {task.id} completed successfully")

        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")

            # Update task with error
            task.error = str(e)
            task.completed_at = datetime.utcnow()

            # Check if we should retry
            if task.retry_count < task.max_retries:
                # Schedule retry with exponential backoff
                delay_seconds = 2**task.retry_count
                retry_at = datetime.utcnow() + timedelta(seconds=delay_seconds)

                task.status = TaskStatus.RETRY
                task.retry_count += 1
                task.scheduled_at = retry_at

                # Add to delayed queue
                queue_name = self._get_queue_name(task.queue)
                await self.redis.zadd(
                    f"{queue_name}:delayed", {task.id: retry_at.timestamp()}
                )

                self._stats["tasks_retried"] += 1
                logger.info(f"Task {task.id} scheduled for retry {task.retry_count}")
            else:
                # Max retries exceeded, move to dead letter queue
                task.status = TaskStatus.FAILED

                await self.redis.zadd(
                    f"{self.queue_prefix}:dlq", {task.id: time.time()}
                )

                self._stats["tasks_failed"] += 1
                logger.error(
                    f"Task {task.id} moved to DLQ after {task.max_retries} retries"
                )

            await self._update_task(task)

        finally:
            # Remove from running tasks
            if task.id in self._running_tasks:
                del self._running_tasks[task.id]

    async def _cleanup_completed_tasks(self):
        """Clean up completed task coroutines."""
        completed = []

        for task_id, task_coro in self._running_tasks.items():
            if task_coro.done():
                completed.append(task_id)

        for task_id in completed:
            del self._running_tasks[task_id]

    async def _update_task(self, task: Task):
        """Update task in Redis."""
        await self.redis.hset(
            f"task:{task.id}",
            mapping={
                "data": dumps(task.to_dict()),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

    def get_stats(self) -> dict[str, Any]:
        """Get queue service statistics."""
        return {
            **self._stats,
            "worker_name": self.worker_name,
            "running_tasks": len(self._running_tasks),
            "handlers_registered": len(self._handlers),
            "avg_processing_time_ms": (
                self._stats["total_processing_time_ms"] / self._stats["tasks_succeeded"]
                if self._stats["tasks_succeeded"] > 0
                else 0
            ),
        }


# Example task handlers
class InvestigationTaskHandler(TaskHandler):
    """Handler for investigation tasks."""

    def __init__(self):
        super().__init__(["create_investigation", "analyze_contract", "detect_anomaly"])

    async def handle(self, task: Task) -> Any:
        """Handle investigation tasks."""
        if task.task_type == "create_investigation":
            # Simulate investigation creation
            await asyncio.sleep(2)  # Simulate processing time
            return {
                "investigation_id": task.payload.get("investigation_id"),
                "status": "completed",
                "findings": ["Sample finding 1", "Sample finding 2"],
            }

        elif task.task_type == "analyze_contract":
            # Simulate contract analysis
            await asyncio.sleep(1)
            return {
                "contract_id": task.payload.get("contract_id"),
                "analysis": "Contract appears normal",
                "score": 0.85,
            }

        elif task.task_type == "detect_anomaly":
            # Simulate anomaly detection
            await asyncio.sleep(0.5)
            return {
                "anomalies_found": 2,
                "severity": "medium",
                "details": ["Price anomaly", "Vendor concentration"],
            }


# Global queue service instance
_queue_service: Optional[QueueService] = None


async def get_queue_service() -> QueueService:
    """Get or create the global queue service instance."""
    global _queue_service

    if _queue_service is None:
        # Initialize Redis client
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)

        _queue_service = QueueService(redis_client)

        # Register default handlers
        _queue_service.register_handler(InvestigationTaskHandler())

    return _queue_service
