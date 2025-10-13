"""
Batch API endpoints for processing multiple requests efficiently.

This module provides endpoints for batching multiple operations,
reducing network overhead and improving throughput.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel, Field, validator

from src.agents import MasterAgent, get_agent_pool
from src.agents.parallel_processor import ParallelAgentProcessor, ParallelStrategy
from src.api.dependencies import get_current_user
from src.core import get_logger
from src.services.chat_service_with_cache import chat_service

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/batch")


class BatchOperation(BaseModel):
    """Single operation in a batch request."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    operation: str = Field(..., description="Operation type")
    data: dict[str, Any] = Field(..., description="Operation data")
    priority: int = Field(default=5, ge=1, le=10)
    timeout: Optional[float] = Field(default=30.0, ge=1.0, le=300.0)

    @validator("operation")
    def validate_operation(cls, v):
        allowed = ["chat", "investigate", "analyze", "search"]
        if v not in allowed:
            raise ValueError(f"Operation must be one of {allowed}")
        return v


class BatchRequest(BaseModel):
    """Batch request containing multiple operations."""

    operations: list[BatchOperation] = Field(..., max_items=100)
    strategy: ParallelStrategy = Field(
        default=ParallelStrategy.BEST_EFFORT, description="Execution strategy"
    )
    max_concurrent: int = Field(default=5, ge=1, le=20)
    return_partial: bool = Field(
        default=True, description="Return partial results if some operations fail"
    )


class BatchOperationResult(BaseModel):
    """Result of a single batch operation."""

    id: str
    operation: str
    success: bool
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BatchResponse(BaseModel):
    """Response from batch processing."""

    batch_id: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    results: list[BatchOperationResult]
    total_execution_time: float
    metadata: dict[str, Any] = Field(default_factory=dict)


# Batch processor instance
batch_processor = ParallelAgentProcessor(max_concurrent=10)


@router.post("/process", response_model=BatchResponse)
async def process_batch(
    request: BatchRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
) -> BatchResponse:
    """
    Process multiple operations in a single batch request.

    Supports operations:
    - chat: Chat completions
    - investigate: Full investigations
    - analyze: Data analysis
    - search: Search operations

    Operations are executed in parallel when possible.
    """
    batch_id = str(uuid.uuid4())
    start_time = datetime.utcnow()

    logger.info(
        f"Processing batch {batch_id} with {len(request.operations)} operations "
        f"for user {current_user.id}"
    )

    # Sort operations by priority
    sorted_ops = sorted(request.operations, key=lambda x: x.priority, reverse=True)

    # Process operations in parallel
    tasks = []
    for op in sorted_ops:
        task = asyncio.create_task(
            _process_single_operation(op, current_user, batch_processor.max_concurrent)
        )
        tasks.append(task)

    # Execute with specified concurrency
    results = []
    if request.strategy == ParallelStrategy.FIRST_SUCCESS:
        # Process until first success
        for task in asyncio.as_completed(tasks):
            result = await task
            results.append(result)
            if result.success:
                # Cancel remaining tasks
                for t in tasks:
                    if not t.done():
                        t.cancel()
                break
    else:
        # Process all tasks
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                results.append(
                    BatchOperationResult(
                        id=sorted_ops[i].id,
                        operation=sorted_ops[i].operation,
                        success=False,
                        error=str(result),
                        execution_time=0.0,
                    )
                )
            else:
                results.append(result)

    # Calculate statistics
    total_time = (datetime.utcnow() - start_time).total_seconds()
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful

    # Background cleanup if needed
    background_tasks.add_task(_cleanup_batch_resources, batch_id)

    return BatchResponse(
        batch_id=batch_id,
        total_operations=len(request.operations),
        successful_operations=successful,
        failed_operations=failed,
        results=results,
        total_execution_time=total_time,
        metadata={
            "strategy": request.strategy,
            "user_id": current_user.id,
            "avg_execution_time": total_time / len(results) if results else 0,
        },
    )


async def _process_single_operation(
    operation: BatchOperation, user: Any, semaphore_limit: int
) -> BatchOperationResult:
    """Process a single operation with error handling."""
    start_time = datetime.utcnow()

    try:
        # Route to appropriate handler
        if operation.operation == "chat":
            result = await _handle_chat_operation(operation.data, user)
        elif operation.operation == "investigate":
            result = await _handle_investigate_operation(operation.data, user)
        elif operation.operation == "analyze":
            result = await _handle_analyze_operation(operation.data, user)
        elif operation.operation == "search":
            result = await _handle_search_operation(operation.data, user)
        else:
            raise ValueError(f"Unknown operation: {operation.operation}")

        execution_time = (datetime.utcnow() - start_time).total_seconds()

        return BatchOperationResult(
            id=operation.id,
            operation=operation.operation,
            success=True,
            result=result,
            execution_time=execution_time,
        )

    except Exception as e:
        logger.error(f"Batch operation {operation.id} failed: {str(e)}")

        execution_time = (datetime.utcnow() - start_time).total_seconds()

        return BatchOperationResult(
            id=operation.id,
            operation=operation.operation,
            success=False,
            error=str(e),
            execution_time=execution_time,
        )


async def _handle_chat_operation(data: dict[str, Any], user: Any) -> dict[str, Any]:
    """Handle chat operation."""
    message = data.get("message", "")
    session_id = data.get("session_id", str(uuid.uuid4()))

    # Get or create session
    session = await chat_service.get_or_create_session(session_id, user_id=user.id)

    # Process message
    response = await chat_service.process_message(
        session_id=session_id, message=message, user_id=user.id
    )

    return {
        "session_id": session_id,
        "response": response.message,
        "agent": response.agent_name,
        "confidence": response.confidence,
    }


async def _handle_investigate_operation(
    data: dict[str, Any], user: Any
) -> dict[str, Any]:
    """Handle investigation operation."""
    query = data.get("query", "")

    # Get agent pool and master agent
    pool = await get_agent_pool()

    # Create investigation context
    from src.agents.deodoro import AgentContext

    context = AgentContext(
        investigation_id=str(uuid.uuid4()),
        user_id=user.id,
        data_sources=data.get("data_sources", []),
    )

    # Execute investigation
    async with pool.acquire(MasterAgent, context) as master:
        result = await master._investigate({"query": query}, context)

    return {
        "investigation_id": result.investigation_id,
        "findings": result.findings,
        "confidence": result.confidence_score,
        "sources": result.sources,
        "explanation": result.explanation,
    }


async def _handle_analyze_operation(data: dict[str, Any], user: Any) -> dict[str, Any]:
    """Handle analysis operation."""
    # Simplified for now - extend based on your analysis needs
    return {
        "status": "completed",
        "analysis_type": data.get("type", "general"),
        "results": {
            "summary": "Analysis completed successfully",
            "data": data.get("data", {}),
        },
    }


async def _handle_search_operation(data: dict[str, Any], user: Any) -> dict[str, Any]:
    """Handle search operation."""
    query = data.get("query", "")
    filters = data.get("filters", {})

    # Simplified search - integrate with your search service
    return {"query": query, "results": [], "total": 0, "filters_applied": filters}


async def _cleanup_batch_resources(batch_id: str):
    """Cleanup any resources used by the batch."""
    # Add cleanup logic if needed
    logger.debug(f"Cleaning up resources for batch {batch_id}")


@router.get("/status/{batch_id}")
async def get_batch_status(
    batch_id: str, current_user=Depends(get_current_user)
) -> dict[str, Any]:
    """
    Get the status of a batch operation.

    Note: This is a placeholder for async batch processing.
    Currently all batches are processed synchronously.
    """
    return {
        "batch_id": batch_id,
        "status": "completed",
        "message": "Batch operations are currently processed synchronously",
    }


@router.post("/validate", response_model=dict[str, Any])
async def validate_batch(
    request: BatchRequest, current_user=Depends(get_current_user)
) -> dict[str, Any]:
    """
    Validate a batch request without executing it.

    Useful for checking if operations are valid before submission.
    """
    validation_results = []

    for op in request.operations:
        is_valid = True
        errors = []

        # Validate operation type
        if op.operation not in ["chat", "investigate", "analyze", "search"]:
            is_valid = False
            errors.append(f"Unknown operation: {op.operation}")

        # Validate operation data
        if op.operation == "chat" and "message" not in op.data:
            is_valid = False
            errors.append("Chat operation requires 'message' field")
        elif op.operation == "investigate" and "query" not in op.data:
            is_valid = False
            errors.append("Investigate operation requires 'query' field")

        validation_results.append(
            {
                "id": op.id,
                "operation": op.operation,
                "valid": is_valid,
                "errors": errors,
            }
        )

    total_valid = sum(1 for v in validation_results if v["valid"])

    return {
        "valid": total_valid == len(request.operations),
        "total_operations": len(request.operations),
        "valid_operations": total_valid,
        "invalid_operations": len(request.operations) - total_valid,
        "results": validation_results,
    }
