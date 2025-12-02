"""
Parallel processing utilities for multi-agent system.

This module provides utilities for executing multiple agent tasks
in parallel, significantly improving investigation speed.
"""

import asyncio
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse, BaseAgent
from src.agents.simple_agent_pool import get_agent_pool
from src.core import AgentStatus, get_logger

logger = get_logger(__name__)


class ParallelStrategy(str, Enum):
    """Strategies for parallel execution."""

    ALL_SUCCEED = "all_succeed"  # All tasks must succeed
    BEST_EFFORT = "best_effort"  # Continue even if some fail
    FIRST_SUCCESS = "first_success"  # Stop after first success
    MAJORITY_VOTE = "majority_vote"  # Majority must succeed


@dataclass
class ParallelTask:
    """Task to be executed in parallel."""

    agent_type: type[BaseAgent]
    message: AgentMessage
    timeout: float | None = None
    weight: float = 1.0  # For weighted results
    fallback: Callable | None = None


@dataclass
class ParallelResult:
    """Result from parallel execution."""

    task_id: str
    agent_name: str
    success: bool
    result: AgentResponse | None = None
    error: str | None = None
    execution_time: float = 0.0
    metadata: dict[str, Any] | None = None


class ParallelAgentProcessor:
    """
    Processor for executing multiple agent tasks in parallel.

    Features:
    - Concurrent execution with configurable strategies
    - Automatic retry and fallback handling
    - Performance monitoring and optimization
    - Result aggregation and voting
    """

    def __init__(
        self,
        max_concurrent: int = 5,
        default_timeout: float = 30.0,
        enable_pooling: bool = True,
    ) -> None:
        """
        Initialize parallel processor.

        Args:
            max_concurrent: Maximum concurrent tasks
            default_timeout: Default timeout per task
            enable_pooling: Use agent pooling
        """
        self.max_concurrent = max_concurrent
        self.default_timeout = default_timeout
        self.enable_pooling = enable_pooling
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "total_time": 0.0,
        }

    async def execute_parallel(
        self,
        tasks: list[ParallelTask],
        context: AgentContext,
        strategy: ParallelStrategy = ParallelStrategy.BEST_EFFORT,
    ) -> list[ParallelResult]:
        """
        Execute multiple agent tasks in parallel.

        Args:
            tasks: List of tasks to execute
            context: Agent execution context
            strategy: Execution strategy

        Returns:
            List of results
        """
        start_time = datetime.now()
        self._stats["total_tasks"] += len(tasks)

        logger.info(
            f"Starting parallel execution of {len(tasks)} tasks with strategy {strategy}"
        )

        # Create coroutines for all tasks
        coroutines = []
        for i, task in enumerate(tasks):
            task_id = f"{context.investigation_id}_{i}"
            coro = self._execute_single_task(task_id, task, context)
            coroutines.append(coro)

        # Execute based on strategy
        if strategy == ParallelStrategy.FIRST_SUCCESS:
            results = await self._execute_first_success(coroutines)
        else:
            results = await self._execute_all_tasks(coroutines)

        # Process results based on strategy
        final_results = self._process_results(results, strategy)

        # Update statistics
        execution_time = (datetime.now() - start_time).total_seconds()
        self._stats["total_time"] += execution_time
        self._stats["successful_tasks"] += sum(1 for r in final_results if r.success)
        self._stats["failed_tasks"] += sum(1 for r in final_results if not r.success)

        logger.info(
            f"Parallel execution completed: {len(final_results)} results, "
            f"{sum(1 for r in final_results if r.success)} successful, "
            f"time: {execution_time:.2f}s"
        )

        return final_results

    async def _execute_single_task(
        self, task_id: str, task: ParallelTask, context: AgentContext
    ) -> ParallelResult:
        """Execute a single task with error handling."""
        async with self._semaphore:  # Limit concurrency
            start_time = datetime.now()

            try:
                # Get agent from pool or create new
                if self.enable_pooling:
                    pool = await get_agent_pool()
                    async with pool.acquire(task.agent_type, context) as agent:
                        result = await self._run_agent_task(agent, task, context)
                else:
                    agent = task.agent_type()
                    result = await self._run_agent_task(agent, task, context)

                execution_time = (datetime.now() - start_time).total_seconds()

                # Extract error message if agent returned ERROR status
                error_msg = None
                if (
                    result.status == AgentStatus.ERROR
                    and hasattr(result, "error")
                    and result.error
                ):
                    error_msg = result.error

                return ParallelResult(
                    task_id=task_id,
                    agent_name=agent.name,
                    success=result.status == AgentStatus.COMPLETED,
                    result=result,
                    error=error_msg,
                    execution_time=execution_time,
                    metadata={"task_type": task.agent_type.__name__},
                )

            except Exception as e:
                logger.error(
                    f"Task {task_id} failed: {str(e)}\n{traceback.format_exc()}"
                )

                # Try fallback if available
                if task.fallback:
                    try:
                        fallback_result = await task.fallback()
                        return ParallelResult(
                            task_id=task_id,
                            agent_name="fallback",
                            success=True,
                            result=fallback_result,
                            execution_time=(
                                datetime.now() - start_time
                            ).total_seconds(),
                            metadata={"used_fallback": True},
                        )
                    except Exception as fb_error:
                        logger.error(f"Fallback also failed: {fb_error}")

                return ParallelResult(
                    task_id=task_id,
                    agent_name=task.agent_type.__name__,
                    success=False,
                    error=str(e),
                    execution_time=(datetime.now() - start_time).total_seconds(),
                )

    async def _run_agent_task(
        self, agent: BaseAgent, task: ParallelTask, context: AgentContext
    ) -> AgentResponse:
        """Run agent task with timeout."""
        timeout = task.timeout or self.default_timeout

        try:
            return await asyncio.wait_for(
                agent.process(task.message, context), timeout=timeout
            )
        except TimeoutError:
            logger.error(f"Agent {agent.name} timed out after {timeout}s")
            return AgentResponse(
                agent_name=agent.name,
                status=AgentStatus.ERROR,
                error=f"Timeout after {timeout} seconds",
            )

    async def _execute_all_tasks(
        self, coroutines: list[asyncio.Task]
    ) -> list[ParallelResult]:
        """Execute all tasks and gather results."""
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # Convert exceptions to ParallelResult
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(
                    ParallelResult(
                        task_id=f"task_{i}",
                        agent_name="unknown",
                        success=False,
                        error=str(result),
                    )
                )
            else:
                final_results.append(result)

        return final_results

    async def _execute_first_success(
        self, coroutines: list[asyncio.Task]
    ) -> list[ParallelResult]:
        """Execute tasks until first success."""
        # Convert coroutines to tasks for asyncio.wait() (required in Python 3.11+)
        tasks = [asyncio.create_task(coro) for coro in coroutines]
        pending = set(tasks)
        results = []

        while pending:
            done, pending = await asyncio.wait(
                pending, return_when=asyncio.FIRST_COMPLETED
            )

            for task in done:
                try:
                    result = await task
                    results.append(result)

                    if result.success:
                        # Cancel remaining tasks
                        for p in pending:
                            p.cancel()
                        return results
                except Exception as e:
                    logger.error(f"Task failed: {e}")

        return results

    def _process_results(
        self, results: list[ParallelResult], strategy: ParallelStrategy
    ) -> list[ParallelResult]:
        """Process results based on strategy."""
        if strategy == ParallelStrategy.ALL_SUCCEED:
            # Check if all succeeded
            if not all(r.success for r in results):
                logger.warning("Not all tasks succeeded with ALL_SUCCEED strategy")

        elif strategy == ParallelStrategy.MAJORITY_VOTE:
            # Count successes
            successes = sum(1 for r in results if r.success)
            if successes < len(results) / 2:
                logger.warning("Majority vote failed")

        return results

    def aggregate_results(
        self, results: list[ParallelResult], aggregation_key: str = "findings"
    ) -> dict[str, Any]:
        """
        Aggregate results from multiple agents.

        Args:
            results: List of parallel results
            aggregation_key: Key to aggregate from results

        Returns:
            Aggregated data
        """
        aggregated = {
            "total_tasks": len(results),
            "successful_tasks": sum(1 for r in results if r.success),
            "failed_tasks": sum(1 for r in results if not r.success),
            "total_execution_time": sum(r.execution_time for r in results),
            "results_by_agent": {},
            aggregation_key: [],
        }

        # Aggregate data from successful results
        for result in results:
            if result.success and result.result:
                agent_name = result.agent_name

                # Store by agent
                if agent_name not in aggregated["results_by_agent"]:
                    aggregated["results_by_agent"][agent_name] = []

                aggregated["results_by_agent"][agent_name].append(result.result)

                # Aggregate specific key
                if hasattr(result.result, "result") and isinstance(
                    result.result.result, dict
                ):
                    data = result.result.result.get(aggregation_key, [])
                    if isinstance(data, list):
                        aggregated[aggregation_key].extend(data)
                    else:
                        aggregated[aggregation_key].append(data)

        return aggregated

    def get_stats(self) -> dict[str, Any]:
        """Get processor statistics."""
        return {
            **self._stats,
            "avg_success_rate": (
                self._stats["successful_tasks"] / self._stats["total_tasks"]
                if self._stats["total_tasks"] > 0
                else 0
            ),
            "avg_execution_time": (
                self._stats["total_time"] / self._stats["total_tasks"]
                if self._stats["total_tasks"] > 0
                else 0
            ),
        }


# Global processor instance
parallel_processor = ParallelAgentProcessor()
