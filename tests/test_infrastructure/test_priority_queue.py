"""
Module: tests.test_infrastructure.test_priority_queue
Description: Tests for priority queue system
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from src.infrastructure.queue.priority_queue import (
    PriorityQueueService,
    TaskPriority,
    TaskResult,
    TaskStatus,
)


class TestPriorityQueue:
    """Test suite for priority queue."""

    @pytest.fixture
    async def queue_service(self):
        """Create queue service instance."""
        service = PriorityQueueService(max_workers=2)
        await service.start()
        yield service
        await service.stop()

    @pytest.mark.asyncio
    async def test_queue_initialization(self):
        """Test queue initialization."""
        service = PriorityQueueService(max_workers=5)

        assert service.max_workers == 5
        assert len(service._queue) == 0
        assert len(service._processing) == 0
        assert service._running is False

    @pytest.mark.asyncio
    async def test_start_stop(self, queue_service):
        """Test starting and stopping queue."""
        assert queue_service._running is True
        assert len(queue_service._workers) == 2

        await queue_service.stop()
        assert queue_service._running is False
        assert len(queue_service._workers) == 0

    @pytest.mark.asyncio
    async def test_enqueue_task(self, queue_service):
        """Test enqueueing tasks."""
        task_id = await queue_service.enqueue(
            task_type="test_task", payload={"data": "test"}, priority=TaskPriority.HIGH
        )

        assert task_id is not None
        assert len(queue_service._queue) == 1

        # Enqueue with different priorities
        task2 = await queue_service.enqueue(
            task_type="test_task",
            payload={"data": "test2"},
            priority=TaskPriority.CRITICAL,
        )

        task3 = await queue_service.enqueue(
            task_type="test_task", payload={"data": "test3"}, priority=TaskPriority.LOW
        )

        # Verify queue ordering (heap property)
        assert len(queue_service._queue) == 3

    @pytest.mark.asyncio
    async def test_dequeue_priority_order(self, queue_service):
        """Test dequeue respects priority."""
        # Enqueue tasks with different priorities
        await queue_service.enqueue(
            task_type="low", payload={}, priority=TaskPriority.LOW
        )

        await queue_service.enqueue(
            task_type="high", payload={}, priority=TaskPriority.HIGH
        )

        await queue_service.enqueue(
            task_type="critical", payload={}, priority=TaskPriority.CRITICAL
        )

        # Dequeue should get critical first
        task1 = await queue_service.dequeue()
        assert task1.task_type == "critical"

        task2 = await queue_service.dequeue()
        assert task2.task_type == "high"

        task3 = await queue_service.dequeue()
        assert task3.task_type == "low"

    @pytest.mark.asyncio
    async def test_task_handler_registration(self, queue_service):
        """Test registering task handlers."""

        # Create mock handler
        async def test_handler(payload, metadata):
            return {"result": "success", "data": payload}

        queue_service.register_handler("test_type", test_handler)

        assert "test_type" in queue_service._handlers
        assert queue_service._handlers["test_type"] == test_handler

    @pytest.mark.asyncio
    async def test_task_execution(self, queue_service):
        """Test task execution with handler."""
        result_data = {"processed": True}

        # Register handler
        async def handler(payload, metadata):
            await asyncio.sleep(0.1)  # Simulate work
            return result_data

        queue_service.register_handler("process", handler)

        # Enqueue and wait for processing
        task_id = await queue_service.enqueue(
            task_type="process", payload={"input": "data"}, priority=TaskPriority.NORMAL
        )

        # Wait for task to complete
        await asyncio.sleep(0.5)

        # Check result
        result = await queue_service.get_task_result(task_id)
        assert result is not None
        assert result.status == TaskStatus.COMPLETED
        assert result.result == result_data

    @pytest.mark.asyncio
    async def test_task_failure_handling(self, queue_service):
        """Test handling of failed tasks."""

        # Register failing handler
        async def failing_handler(payload, metadata):
            raise ValueError("Task failed")

        queue_service.register_handler("fail", failing_handler)

        # Enqueue task with no retries
        task_id = await queue_service.enqueue(
            task_type="fail", payload={}, priority=TaskPriority.NORMAL, max_retries=0
        )

        # Wait for processing
        await asyncio.sleep(0.5)

        # Check result
        result = await queue_service.get_task_result(task_id)
        assert result is not None
        assert result.status == TaskStatus.FAILED
        assert "Task failed" in result.error

    @pytest.mark.asyncio
    async def test_task_retry_logic(self, queue_service):
        """Test task retry mechanism."""
        attempt_count = 0

        # Handler that fails first time, succeeds second
        async def retry_handler(payload, metadata):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError("Temporary failure")
            return {"attempts": attempt_count}

        queue_service.register_handler("retry", retry_handler)

        # Enqueue with retries
        task_id = await queue_service.enqueue(
            task_type="retry", payload={}, priority=TaskPriority.NORMAL, max_retries=3
        )

        # Wait for retry and completion
        await asyncio.sleep(3.0)  # Account for retry backoff

        # Check result
        result = await queue_service.get_task_result(task_id)
        assert result is not None
        assert result.status == TaskStatus.COMPLETED
        assert result.result["attempts"] == 2

    @pytest.mark.asyncio
    async def test_task_timeout(self, queue_service):
        """Test task timeout handling."""

        # Register slow handler
        async def slow_handler(payload, metadata):
            await asyncio.sleep(5.0)  # Longer than timeout
            return {"completed": True}

        queue_service.register_handler("slow", slow_handler)

        # Enqueue with short timeout
        task_id = await queue_service.enqueue(
            task_type="slow",
            payload={},
            priority=TaskPriority.NORMAL,
            timeout=1,  # 1 second timeout
            max_retries=0,
        )

        # Wait for timeout
        await asyncio.sleep(2.0)

        # Check result
        result = await queue_service.get_task_result(task_id)
        assert result is not None
        assert result.status == TaskStatus.FAILED
        assert "timeout" in result.error.lower()

    @pytest.mark.asyncio
    async def test_task_cancellation(self, queue_service):
        """Test cancelling pending tasks."""
        # Enqueue multiple tasks
        task_id1 = await queue_service.enqueue(
            task_type="test", payload={}, priority=TaskPriority.LOW
        )

        task_id2 = await queue_service.enqueue(
            task_type="test", payload={}, priority=TaskPriority.LOW
        )

        # Cancel one task
        cancelled = await queue_service.cancel_task(task_id1)
        assert cancelled is True

        # Verify task is not in queue
        status = await queue_service.get_task_status(task_id1)
        assert status is None

        # Other task should still be there
        status2 = await queue_service.get_task_status(task_id2)
        assert status2 == TaskStatus.PENDING

    @pytest.mark.asyncio
    async def test_queue_statistics(self, queue_service):
        """Test queue statistics."""

        # Register handler
        async def handler(payload, metadata):
            return {"success": True}

        queue_service.register_handler("stats_test", handler)

        # Enqueue tasks
        for i in range(3):
            await queue_service.enqueue(
                task_type="stats_test",
                payload={"index": i},
                priority=TaskPriority.NORMAL,
            )

        # Wait for processing
        await asyncio.sleep(0.5)

        # Get stats
        stats = await queue_service.get_stats()

        assert stats.total_processed > 0
        assert stats.average_processing_time > 0
        assert stats.completed_tasks > 0

    @pytest.mark.asyncio
    async def test_task_callback(self, queue_service):
        """Test task completion callbacks."""
        callback_called = False
        callback_result = None

        # Mock HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_client.return_value.__aenter__.return_value.post = mock_response

            # Register handler
            async def handler(payload, metadata):
                return {"processed": True}

            queue_service.register_handler("callback_test", handler)

            # Enqueue with callback
            task_id = await queue_service.enqueue(
                task_type="callback_test",
                payload={},
                priority=TaskPriority.NORMAL,
                callback="http://example.com/callback",
            )

            # Wait for processing
            await asyncio.sleep(0.5)

            # Verify callback was called
            assert mock_response.called
            call_args = mock_response.call_args
            assert call_args[0][0] == "http://example.com/callback"
            assert "task_id" in call_args[1]["json"]

    @pytest.mark.asyncio
    async def test_cleanup_old_tasks(self, queue_service):
        """Test cleaning up old completed tasks."""
        # Add some completed tasks
        old_time = datetime.now() - timedelta(hours=2)
        queue_service._completed["old_task"] = TaskResult(
            task_id="old_task",
            status=TaskStatus.COMPLETED,
            started_at=old_time,
            completed_at=old_time,
            duration_seconds=1.0,
        )

        recent_time = datetime.now() - timedelta(minutes=10)
        queue_service._completed["recent_task"] = TaskResult(
            task_id="recent_task",
            status=TaskStatus.COMPLETED,
            started_at=recent_time,
            completed_at=recent_time,
            duration_seconds=1.0,
        )

        # Clean up tasks older than 1 hour
        queue_service.clear_completed(older_than_minutes=60)

        # Old task should be removed
        assert "old_task" not in queue_service._completed
        assert "recent_task" in queue_service._completed
