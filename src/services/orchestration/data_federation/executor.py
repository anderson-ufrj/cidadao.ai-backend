"""
Data Federation Executor

Executes investigation plans by coordinating multiple API calls.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

import asyncio
import time
from typing import Any

from src.core import get_logger
from src.services.orchestration.api_registry import APIRegistry
from src.services.orchestration.models.api_response import APIResponse, APIStatus
from src.services.orchestration.models.investigation import (
    ExecutionPlan,
    Stage,
    StageResult,
)

logger = get_logger(__name__)


class DataFederationExecutor:
    """
    Executes investigation plans by coordinating API calls.

    Features:
    - Parallel execution of independent stages
    - Dependency management between stages
    - Automatic fallback on API failures
    - Result aggregation from multiple sources
    """

    def __init__(self, api_registry: APIRegistry | None = None) -> None:
        self.registry = api_registry or APIRegistry()
        self.logger = get_logger(__name__)

    async def execute_plan(
        self, plan: ExecutionPlan, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute an investigation plan.

        Args:
            plan: Execution plan with stages
            context: Investigation context with parameters

        Returns:
            Dict with aggregated results from all stages
        """
        self.logger.info(f"Executing plan with {len(plan.stages)} stages")
        start_time = time.time()

        # Results storage
        all_results: dict[str, Any] = {}
        stage_outputs: dict[str, StageResult] = {}

        # Execute stages in order, respecting dependencies
        for stage in plan.stages:
            # Check if dependencies are satisfied
            if not self._can_execute_stage(stage, stage_outputs):
                self.logger.warning(
                    f"Skipping stage {stage.name}: dependencies not met"
                )
                continue

            # Execute stage
            stage_result = await self._execute_stage(stage, context, stage_outputs)
            stage_outputs[stage.name] = stage_result

            # Aggregate results
            if stage_result.data:
                all_results[stage.name] = stage_result.data

        duration = time.time() - start_time
        self.logger.info(f"Plan executed in {duration:.2f}s")

        return {
            "results": all_results,
            "stage_results": stage_outputs,
            "duration_seconds": duration,
            "stages_executed": len(stage_outputs),
            "stages_total": len(plan.stages),
        }

    def _can_execute_stage(
        self, stage: Stage, completed_stages: dict[str, StageResult]
    ) -> bool:
        """Check if stage dependencies are satisfied."""
        if not stage.depends_on:
            return True

        # Check all dependencies are completed
        for dep in stage.depends_on:
            if dep not in completed_stages:
                return False
            if completed_stages[dep].status == "failed":
                return False

        return True

    async def _execute_stage(
        self,
        stage: Stage,
        context: dict[str, Any],
        previous_results: dict[str, StageResult],
    ) -> StageResult:
        """Execute a single stage."""
        self.logger.info(f"Executing stage: {stage.name}")
        start_time = time.time()

        try:
            # If no APIs, this is a synthetic stage (analysis only)
            if not stage.apis:
                return StageResult(
                    stage_name=stage.name,
                    status="success",
                    data={"message": f"Synthetic stage: {stage.reason}"},
                    api_calls=[],
                    duration_seconds=0.0,
                )

            # Execute API calls
            if stage.parallel:
                # Parallel execution
                results = await self._execute_parallel(stage, context)
            else:
                # Sequential execution
                results = await self._execute_sequential(stage, context)

            # Aggregate results
            aggregated_data = self._aggregate_results(results)
            api_calls = [r.api_name for r in results]

            # Determine stage status
            success_count = sum(1 for r in results if r.status == APIStatus.SUCCESS)
            if success_count == 0:
                status = "failed"
            elif success_count < len(results):
                status = "partial_success"
            else:
                status = "success"

            duration = time.time() - start_time

            return StageResult(
                stage_name=stage.name,
                status=status,
                data=aggregated_data,
                api_calls=api_calls,
                duration_seconds=duration,
            )

        except Exception as e:
            self.logger.error(f"Stage {stage.name} failed: {e}")
            return StageResult(
                stage_name=stage.name,
                status="failed",
                data={},
                api_calls=[],
                duration_seconds=time.time() - start_time,
                errors=[str(e)],
            )

    async def _execute_parallel(
        self, stage: Stage, context: dict[str, Any]
    ) -> list[APIResponse]:
        """Execute multiple API calls in parallel."""
        self.logger.debug(f"Parallel execution of {len(stage.apis)} APIs")

        # Create tasks for all APIs
        tasks = []
        for api_name in stage.apis:
            task = self._call_api(api_name, stage.method, context, stage.retry_count)
            tasks.append(task)

        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to failed responses
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    APIResponse(
                        api_name=stage.apis[i],
                        status=APIStatus.FAILED,
                        error=str(result),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    async def _execute_sequential(
        self, stage: Stage, context: dict[str, Any]
    ) -> list[APIResponse]:
        """Execute API calls sequentially."""
        self.logger.debug(f"Sequential execution of {len(stage.apis)} APIs")

        results = []
        for api_name in stage.apis:
            try:
                result = await self._call_api(
                    api_name, stage.method, context, stage.retry_count
                )
                results.append(result)
            except Exception as e:
                self.logger.error(f"API {api_name} failed: {e}")
                results.append(
                    APIResponse(
                        api_name=api_name, status=APIStatus.FAILED, error=str(e)
                    )
                )

        return results

    async def _call_api(
        self, api_name: str, method: str, context: dict[str, Any], retries: int = 3
    ) -> APIResponse:
        """
        Call a specific API with retry logic.

        Args:
            api_name: Name of API to call
            method: Method to call on API
            context: Parameters for the call
            retries: Number of retry attempts

        Returns:
            APIResponse with result
        """
        start_time = time.time()
        last_error = None

        for attempt in range(retries):
            try:
                # Get API client
                client = self.registry.get_client(api_name)

                # Call method dynamically
                if hasattr(client, method):
                    method_func = getattr(client, method)
                    # Try async first, fallback to sync
                    if asyncio.iscoroutinefunction(method_func):
                        data = await method_func(**context)
                    else:
                        data = method_func(**context)

                    duration = time.time() - start_time
                    return APIResponse(
                        api_name=api_name,
                        status=APIStatus.SUCCESS,
                        data=data if isinstance(data, dict) else {"result": data},
                        duration_seconds=duration,
                    )
                # Method not found
                return APIResponse(
                    api_name=api_name,
                    status=APIStatus.FAILED,
                    error=f"Method {method} not found on {api_name}",
                    duration_seconds=time.time() - start_time,
                )

            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    # Wait before retry with exponential backoff
                    wait_time = 2**attempt
                    self.logger.warning(
                        f"API {api_name} attempt {attempt + 1} failed, "
                        f"retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(
                        f"API {api_name} failed after {retries} attempts: {e}"
                    )

        # All retries failed, try fallback
        fallback_api = self.registry.get_fallback_api(api_name)
        if fallback_api:
            self.logger.info(f"Trying fallback API: {fallback_api}")
            return await self._call_api(fallback_api, method, context, retries=1)

        # No fallback or fallback also failed
        return APIResponse(
            api_name=api_name,
            status=APIStatus.FAILED,
            error=str(last_error) if last_error else "Unknown error",
            duration_seconds=time.time() - start_time,
        )

    def _aggregate_results(self, results: list[APIResponse]) -> dict[str, Any]:
        """
        Aggregate results from multiple API calls.

        Combines data from successful calls, logs errors from failed ones.
        """
        aggregated: dict[str, Any] = {}

        for result in results:
            if result.status == APIStatus.SUCCESS:
                # Add data under API name
                aggregated[result.api_name] = result.data
            else:
                # Log failure but don't include in aggregated data
                self.logger.warning(f"API {result.api_name} failed: {result.error}")

        return aggregated
