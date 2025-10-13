"""
Module: api.routes.admin.cache_warming
Description: Admin routes for cache warming management
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.dependencies import require_admin
from src.core import get_logger
from src.services.cache_warming_service import (
    CacheWarmingStrategy,
    cache_warming_service,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/cache-warming", tags=["Admin - Cache Warming"])


class CacheWarmingRequest(BaseModel):
    """Request to warm specific cache data."""

    strategies: Optional[list[CacheWarmingStrategy]] = Field(
        None, description="Specific strategies to execute (None = all)"
    )


class SpecificDataWarmingRequest(BaseModel):
    """Request to warm specific data items."""

    data_type: str = Field(..., description="Type of data to warm")
    identifiers: list[str] = Field(..., description="List of identifiers")
    ttl: Optional[int] = Field(None, description="Cache TTL in seconds")


class CacheWarmingStatusResponse(BaseModel):
    """Cache warming status response."""

    last_warming: Optional[datetime]
    query_frequency_tracked: int
    top_queries: list[tuple]
    config: dict[str, Any]


@router.post("/trigger")
async def trigger_cache_warming(
    request: CacheWarmingRequest,
    background_tasks: BackgroundTasks,
    admin_user=Depends(require_admin),
):
    """
    Manually trigger cache warming.

    Requires admin privileges.
    """
    logger.info(
        "admin_cache_warming_triggered",
        admin=admin_user.get("email"),
        strategies=request.strategies,
    )

    # Execute in background
    background_tasks.add_task(
        cache_warming_service.trigger_manual_warming, request.strategies
    )

    return {
        "status": "warming_started",
        "strategies": request.strategies or "all",
        "message": "Cache warming started in background",
    }


@router.post("/warm-specific")
async def warm_specific_data(
    request: SpecificDataWarmingRequest, admin_user=Depends(require_admin)
):
    """
    Warm cache with specific data items.

    Requires admin privileges.
    """
    try:
        results = await cache_warming_service.warm_specific_data(
            data_type=request.data_type,
            identifiers=request.identifiers,
            ttl=request.ttl,
        )

        logger.info(
            "admin_specific_data_warmed",
            admin=admin_user.get("email"),
            data_type=request.data_type,
            warmed_count=len(results["warmed"]),
            failed_count=len(results["failed"]),
        )

        return results

    except Exception as e:
        logger.error("admin_specific_data_warming_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to warm specific data",
        )


@router.get("/status", response_model=CacheWarmingStatusResponse)
async def get_warming_status(admin_user=Depends(require_admin)):
    """
    Get cache warming status.

    Requires admin privileges.
    """
    status = await cache_warming_service.get_warming_status()

    return CacheWarmingStatusResponse(
        last_warming=status["last_warming"],
        query_frequency_tracked=status["query_frequency_tracked"],
        top_queries=status["top_queries"],
        config=status["config"],
    )


@router.post("/strategies/{strategy}")
async def execute_single_strategy(
    strategy: CacheWarmingStrategy,
    background_tasks: BackgroundTasks,
    admin_user=Depends(require_admin),
):
    """
    Execute a single cache warming strategy.

    Requires admin privileges.
    """
    logger.info(
        "admin_single_strategy_warming",
        admin=admin_user.get("email"),
        strategy=strategy,
    )

    # Execute in background
    background_tasks.add_task(cache_warming_service.trigger_manual_warming, [strategy])

    return {
        "status": "strategy_started",
        "strategy": strategy,
        "message": f"Cache warming strategy '{strategy}' started",
    }


@router.get("/strategies")
async def list_available_strategies(admin_user=Depends(require_admin)):
    """
    List available cache warming strategies.

    Requires admin privileges.
    """
    strategies = [
        {"name": strategy.value, "description": get_strategy_description(strategy)}
        for strategy in CacheWarmingStrategy
    ]

    return {"strategies": strategies, "total": len(strategies)}


def get_strategy_description(strategy: CacheWarmingStrategy) -> str:
    """Get human-readable description for strategy."""
    descriptions = {
        CacheWarmingStrategy.POPULAR_DATA: "Warm cache with frequently accessed contracts and data",
        CacheWarmingStrategy.RECENT_INVESTIGATIONS: "Cache recent investigation results",
        CacheWarmingStrategy.FREQUENT_QUERIES: "Cache results of frequently executed queries",
        CacheWarmingStrategy.AGENT_POOLS: "Pre-initialize agent pool connections",
        CacheWarmingStrategy.STATIC_RESOURCES: "Cache static configuration and reference data",
        CacheWarmingStrategy.PREDICTIVE: "Use ML to predict and cache likely needed data",
    }
    return descriptions.get(strategy, "No description available")
