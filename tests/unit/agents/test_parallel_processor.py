"""
Unit tests for parallel agent processor.
Tests concurrent execution, strategies, and result aggregation.
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
    BaseAgent,
)
from src.agents.parallel_processor import (
    ParallelAgentProcessor,
    ParallelResult,
    ParallelStrategy,
    ParallelTask,
)
from src.core.exceptions import AgentExecutionError


class MockSuccessAgent(BaseAgent):
    """Mock agent that always succeeds."""

    def __init__(self):
        super().__init__(
            name="SuccessAgent",
            description="Always succeeds",
            capabilities=["test"],
            max_retries=3,
            timeout=30,
        )
        self.process_count = 0

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        self.process_count += 1
        await asyncio.sleep(0.1)  # Simulate work
        return AgentResponse(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            result={"success": True, "value": message.payload.get("value", 42)},
        )


class MockFailAgent(BaseAgent):
    """Mock agent that always fails."""

    def __init__(self):
        super().__init__(
            name="FailAgent",
            description="Always fails",
            capabilities=["test"],
            max_retries=3,
            timeout=30,
        )

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        raise AgentExecutionError("Intentional failure for testing")


class MockSlowAgent(BaseAgent):
    """Mock agent that is slow."""

    def __init__(self):
        super().__init__(
            name="SlowAgent",
            description="Slow agent",
            capabilities=["test"],
            max_retries=3,
            timeout=30,
        )

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        await asyncio.sleep(2.0)  # Very slow
        return AgentResponse(
            agent_name=self.name, status=AgentStatus.COMPLETED, result={"slow": True}
        )


@pytest.fixture
def parallel_processor():
    """Create a parallel processor for testing."""
    return ParallelAgentProcessor(
        max_concurrent=3,
        default_timeout=1.0,
        enable_pooling=False,  # Disable pooling for simpler tests
    )


@pytest.fixture
def agent_context():
    """Create agent context for testing."""
    return AgentContext(
        investigation_id="test-parallel-123",
        user_id="test_user",
        session_id="test_session",
    )


@pytest.fixture
def sample_tasks():
    """Create sample tasks for testing."""
    return [
        ParallelTask(
            agent_type=MockSuccessAgent,
            message=AgentMessage(
                sender="test",
                recipient="SuccessAgent",
                action="test",
                payload={"value": 1},
            ),
        ),
        ParallelTask(
            agent_type=MockSuccessAgent,
            message=AgentMessage(
                sender="test",
                recipient="SuccessAgent",
                action="test",
                payload={"value": 2},
            ),
        ),
        ParallelTask(
            agent_type=MockSuccessAgent,
            message=AgentMessage(
                sender="test",
                recipient="SuccessAgent",
                action="test",
                payload={"value": 3},
            ),
        ),
    ]


class TestParallelAgentProcessor:
    """Test ParallelAgentProcessor class."""

    @pytest.mark.unit
    def test_processor_initialization(self):
        """Test processor initialization."""
        processor = ParallelAgentProcessor(
            max_concurrent=5, default_timeout=10.0, enable_pooling=True
        )

        assert processor.max_concurrent == 5
        assert processor.default_timeout == 10.0
        assert processor.enable_pooling == True
        assert processor._stats["total_tasks"] == 0

    @pytest.mark.unit
    async def test_execute_parallel_all_succeed(
        self, parallel_processor, agent_context, sample_tasks
    ):
        """Test parallel execution with all tasks succeeding."""
        results = await parallel_processor.execute_parallel(
            tasks=sample_tasks,
            context=agent_context,
            strategy=ParallelStrategy.ALL_SUCCEED,
        )

        assert len(results) == 3
        assert all(r.success for r in results)
        assert all(r.result.status == AgentStatus.COMPLETED for r in results)

        # Check statistics
        assert parallel_processor._stats["total_tasks"] == 3
        assert parallel_processor._stats["successful_tasks"] == 3
        assert parallel_processor._stats["failed_tasks"] == 0

    @pytest.mark.unit
    async def test_execute_parallel_best_effort(
        self, parallel_processor, agent_context
    ):
        """Test best effort strategy with some failures."""
        tasks = [
            ParallelTask(
                agent_type=MockSuccessAgent,
                message=AgentMessage(
                    sender="test", recipient="test", action="test", payload={}
                ),
            ),
            ParallelTask(
                agent_type=MockFailAgent,
                message=AgentMessage(
                    sender="test", recipient="test", action="test", payload={}
                ),
            ),
            ParallelTask(
                agent_type=MockSuccessAgent,
                message=AgentMessage(
                    sender="test", recipient="test", action="test", payload={}
                ),
            ),
        ]

        results = await parallel_processor.execute_parallel(
            tasks=tasks, context=agent_context, strategy=ParallelStrategy.BEST_EFFORT
        )

        assert len(results) == 3
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        assert len(successful) == 2
        assert len(failed) == 1
        assert failed[0].error is not None

    @pytest.mark.unit
    async def test_execute_parallel_first_success(
        self, parallel_processor, agent_context
    ):
        """Test first success strategy."""
        tasks = [
            ParallelTask(
                agent_type=MockSlowAgent,
                message=AgentMessage(
                    sender="test", recipient="test", action="test", payload={}
                ),
            ),
            ParallelTask(
                agent_type=MockSuccessAgent,
                message=AgentMessage(
                    sender="test",
                    recipient="test",
                    action="test",
                    payload={"fast": True},
                ),
            ),
            ParallelTask(
                agent_type=MockSlowAgent,
                message=AgentMessage(
                    sender="test", recipient="test", action="test", payload={}
                ),
            ),
        ]

        results = await parallel_processor.execute_parallel(
            tasks=tasks, context=agent_context, strategy=ParallelStrategy.FIRST_SUCCESS
        )

        # Should have result from the fast success agent
        assert len(results) >= 1
        success_results = [r for r in results if r.success]
        assert len(success_results) >= 1
        assert success_results[0].agent_name == "SuccessAgent"

    @pytest.mark.unit
    async def test_execute_parallel_with_timeout(
        self, parallel_processor, agent_context
    ):
        """Test task timeout handling."""
        # Set very short timeout
        parallel_processor.default_timeout = 0.1

        tasks = [
            ParallelTask(
                agent_type=MockSlowAgent,
                message=AgentMessage(
                    sender="test", recipient="test", action="test", payload={}
                ),
                timeout=0.1,  # Will timeout
            )
        ]

        results = await parallel_processor.execute_parallel(
            tasks=tasks, context=agent_context, strategy=ParallelStrategy.BEST_EFFORT
        )

        assert len(results) == 1
        assert not results[0].success
        assert (
            "timeout" in results[0].error.lower()
            or "timed out" in results[0].error.lower()
        )

    @pytest.mark.unit
    async def test_execute_parallel_with_fallback(
        self, parallel_processor, agent_context
    ):
        """Test fallback execution."""
        fallback_called = False

        async def fallback_func():
            nonlocal fallback_called
            fallback_called = True
            return AgentResponse(
                agent_name="fallback",
                status=AgentStatus.COMPLETED,
                result={"fallback": True},
            )

        tasks = [
            ParallelTask(
                agent_type=MockFailAgent,
                message=AgentMessage(
                    sender="test", recipient="test", action="test", payload={}
                ),
                fallback=fallback_func,
            )
        ]

        results = await parallel_processor.execute_parallel(
            tasks=tasks, context=agent_context, strategy=ParallelStrategy.BEST_EFFORT
        )

        assert len(results) == 1
        assert results[0].success
        assert results[0].agent_name == "fallback"
        assert fallback_called
        assert results[0].metadata.get("used_fallback") == True

    @pytest.mark.unit
    async def test_max_concurrent_limit(self, agent_context):
        """Test max concurrent execution limit."""
        processor = ParallelAgentProcessor(
            max_concurrent=2, default_timeout=5.0, enable_pooling=False
        )

        # Track concurrent executions
        concurrent_count = 0
        max_concurrent_observed = 0
        lock = asyncio.Lock()

        class ConcurrentTrackingAgent(BaseAgent):
            def __init__(self):
                super().__init__(
                    name="ConcurrentAgent",
                    description="Tracks concurrency",
                    capabilities=["test"],
                )

            async def initialize(self) -> None:
                pass

            async def shutdown(self) -> None:
                pass

            async def process(
                self, message: AgentMessage, context: AgentContext
            ) -> AgentResponse:
                nonlocal concurrent_count, max_concurrent_observed

                async with lock:
                    concurrent_count += 1
                    max_concurrent_observed = max(
                        max_concurrent_observed, concurrent_count
                    )

                await asyncio.sleep(0.1)  # Hold the slot

                async with lock:
                    concurrent_count -= 1

                return AgentResponse(
                    agent_name=self.name,
                    status=AgentStatus.COMPLETED,
                    result={"done": True},
                )

        # Create many tasks
        tasks = [
            ParallelTask(
                agent_type=ConcurrentTrackingAgent,
                message=AgentMessage(
                    sender="test", recipient="test", action="test", payload={}
                ),
            )
            for _ in range(5)
        ]

        await processor.execute_parallel(
            tasks=tasks, context=agent_context, strategy=ParallelStrategy.BEST_EFFORT
        )

        # Should never exceed max_concurrent
        assert max_concurrent_observed <= 2

    @pytest.mark.unit
    async def test_with_agent_pooling(self, agent_context):
        """Test parallel execution with agent pooling enabled."""
        processor = ParallelAgentProcessor(
            max_concurrent=3, default_timeout=1.0, enable_pooling=True
        )

        # Mock the agent pool
        mock_pool = AsyncMock()
        mock_agent = MockSuccessAgent()

        @asynccontextmanager
        async def mock_acquire(agent_type, context):
            yield mock_agent

        mock_pool.acquire = mock_acquire

        with patch(
            "src.agents.parallel_processor.get_agent_pool", return_value=mock_pool
        ):
            tasks = [
                ParallelTask(
                    agent_type=MockSuccessAgent,
                    message=AgentMessage(
                        sender="test", recipient="test", action="test", payload={}
                    ),
                )
                for _ in range(3)
            ]

            results = await processor.execute_parallel(
                tasks=tasks,
                context=agent_context,
                strategy=ParallelStrategy.ALL_SUCCEED,
            )

            assert len(results) == 3
            assert all(r.success for r in results)

    @pytest.mark.unit
    async def test_get_stats(self, parallel_processor, agent_context, sample_tasks):
        """Test statistics collection."""
        # Execute some tasks
        await parallel_processor.execute_parallel(
            tasks=sample_tasks, context=agent_context
        )

        stats = parallel_processor.get_stats()

        assert stats["total_tasks"] == 3
        assert stats["successful_tasks"] == 3
        assert stats["failed_tasks"] == 0
        assert stats["total_time"] > 0
        assert "avg_success_rate" in stats
        assert stats["avg_success_rate"] == 1.0  # All succeeded
        assert "avg_execution_time" in stats
        assert stats["avg_execution_time"] > 0

    @pytest.mark.unit
    async def test_aggregate_results(self, parallel_processor):
        """Test aggregating results from multiple agents."""
        results = [
            ParallelResult(
                task_id="1",
                agent_name="Agent1",
                success=True,
                result=AgentResponse(
                    agent_name="Agent1",
                    status=AgentStatus.COMPLETED,
                    result={"findings": ["anomaly1", "anomaly2"], "score": 0.9},
                ),
                execution_time=0.5,
            ),
            ParallelResult(
                task_id="2",
                agent_name="Agent2",
                success=True,
                result=AgentResponse(
                    agent_name="Agent2",
                    status=AgentStatus.COMPLETED,
                    result={"findings": ["anomaly3"], "score": 0.8},
                ),
                execution_time=0.6,
            ),
            ParallelResult(
                task_id="3",
                agent_name="Agent1",  # Same agent, different task
                success=True,
                result=AgentResponse(
                    agent_name="Agent1",
                    status=AgentStatus.COMPLETED,
                    result={"findings": ["anomaly4"], "score": 0.85},
                ),
                execution_time=0.4,
            ),
        ]

        aggregated = parallel_processor.aggregate_results(
            results, aggregation_key="findings"
        )

        assert aggregated["total_tasks"] == 3
        assert aggregated["successful_tasks"] == 3
        assert aggregated["failed_tasks"] == 0
        assert aggregated["total_execution_time"] == pytest.approx(1.5, rel=0.01)
        assert "results_by_agent" in aggregated
        assert len(aggregated["results_by_agent"]["Agent1"]) == 2
        assert len(aggregated["results_by_agent"]["Agent2"]) == 1
        assert len(aggregated["findings"]) == 4  # All findings aggregated

    @pytest.mark.unit
    async def test_majority_vote_strategy(self, parallel_processor, agent_context):
        """Test majority vote strategy."""
        # Create tasks where 2/3 will succeed
        tasks = [
            ParallelTask(
                agent_type=MockSuccessAgent,
                message=AgentMessage(
                    sender="test", recipient="test", action="test", payload={}
                ),
            ),
            ParallelTask(
                agent_type=MockSuccessAgent,
                message=AgentMessage(
                    sender="test", recipient="test", action="test", payload={}
                ),
            ),
            ParallelTask(
                agent_type=MockFailAgent,
                message=AgentMessage(
                    sender="test", recipient="test", action="test", payload={}
                ),
            ),
        ]

        results = await parallel_processor.execute_parallel(
            tasks=tasks, context=agent_context, strategy=ParallelStrategy.MAJORITY_VOTE
        )

        # Majority succeeded, so should return successful results
        assert len(results) == 3
        successful = [r for r in results if r.success]
        assert len(successful) >= 2  # At least majority succeeded


from contextlib import asynccontextmanager


@asynccontextmanager
async def mock_acquire(agent_type, context):
    """Mock context manager for agent pool acquire."""
    yield MockSuccessAgent()
