"""
Module: api.routes.llm_costs
Description: LLM cost tracking and analytics endpoints
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.core import get_logger
from src.core.llm_cost_tracker import llm_cost_tracker

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/llm-costs", tags=["LLM Cost Tracking"])


class CostSummaryResponse(BaseModel):
    """LLM cost summary response."""

    daily_cost_usd: float = Field(description="Total cost for current day")
    monthly_cost_usd: float = Field(description="Total cost for current month")
    daily_budget_limit_usd: float = Field(description="Daily budget limit")
    monthly_budget_limit_usd: float = Field(description="Monthly budget limit")
    daily_budget_remaining_usd: float = Field(description="Remaining daily budget")
    monthly_budget_remaining_usd: float = Field(description="Remaining monthly budget")
    cost_by_agent_24h: dict[str, float] = Field(description="Cost breakdown by agent")
    cost_by_provider_24h: dict[str, float] = Field(
        description="Cost breakdown by provider"
    )
    total_requests: int = Field(description="Total number of LLM requests tracked")


class CostByAgentResponse(BaseModel):
    """Cost breakdown by agent."""

    timeframe_hours: int = Field(description="Timeframe in hours")
    costs: dict[str, float] = Field(description="Agent name to cost mapping")
    total_cost_usd: float = Field(description="Total cost across all agents")


class CostByProviderResponse(BaseModel):
    """Cost breakdown by provider."""

    timeframe_hours: int = Field(description="Timeframe in hours")
    costs: dict[str, float] = Field(description="Provider name to cost mapping")
    total_cost_usd: float = Field(description="Total cost across all providers")


@router.get(
    "/summary",
    response_model=CostSummaryResponse,
    summary="Get comprehensive cost summary",
    description="Returns a comprehensive summary of LLM costs including daily/monthly totals, budget limits, and breakdowns by agent and provider.",
)
async def get_cost_summary() -> CostSummaryResponse:
    """
    Get comprehensive LLM cost summary.

    This endpoint provides:
    - Daily and monthly cost totals
    - Budget limits and remaining budget
    - Cost breakdowns by agent (last 24h)
    - Cost breakdowns by provider (last 24h)
    - Total number of requests tracked

    Returns:
        CostSummaryResponse with all cost metrics
    """
    try:
        summary = await llm_cost_tracker.get_summary()
        return CostSummaryResponse(**summary)
    except Exception as e:
        logger.error(f"Error getting cost summary: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve cost summary: {str(e)}"
        ) from e


@router.get(
    "/by-agent",
    response_model=CostByAgentResponse,
    summary="Get cost breakdown by agent",
    description="Returns LLM costs grouped by agent for a specified time window.",
)
async def get_cost_by_agent(
    hours: int = Query(24, ge=1, le=720, description="Hours to look back (max 30 days)")
) -> CostByAgentResponse:
    """
    Get cost breakdown by agent for the last N hours.

    Args:
        hours: Number of hours to look back (1-720, default 24)

    Returns:
        Cost breakdown by agent name

    Example:
        GET /api/v1/llm-costs/by-agent?hours=48
    """
    try:
        costs = await llm_cost_tracker.get_cost_by_agent(hours=hours)
        total = sum(costs.values())

        return CostByAgentResponse(
            timeframe_hours=hours,
            costs=costs,
            total_cost_usd=round(total, 4),
        )
    except Exception as e:
        logger.error(f"Error getting cost by agent: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve agent costs: {str(e)}"
        ) from e


@router.get(
    "/by-provider",
    response_model=CostByProviderResponse,
    summary="Get cost breakdown by LLM provider",
    description="Returns LLM costs grouped by provider (Maritaca, Anthropic, etc.) for a specified time window.",
)
async def get_cost_by_provider(
    hours: int = Query(24, ge=1, le=720, description="Hours to look back (max 30 days)")
) -> CostByProviderResponse:
    """
    Get cost breakdown by LLM provider for the last N hours.

    Supported providers:
    - maritaca (primary - Brazilian Portuguese models)
    - anthropic (Claude Sonnet 4 backup)
    - groq (fallback)
    - together (fallback)

    Args:
        hours: Number of hours to look back (1-720, default 24)

    Returns:
        Cost breakdown by provider name

    Example:
        GET /api/v1/llm-costs/by-provider?hours=168  # Last week
    """
    try:
        costs = await llm_cost_tracker.get_cost_by_provider(hours=hours)
        total = sum(costs.values())

        return CostByProviderResponse(
            timeframe_hours=hours,
            costs=costs,
            total_cost_usd=round(total, 4),
        )
    except Exception as e:
        logger.error(f"Error getting cost by provider: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve provider costs: {str(e)}"
        ) from e


@router.get(
    "/daily",
    summary="Get today's total cost",
    description="Returns the total LLM cost for the current day.",
)
async def get_daily_cost() -> dict[str, Any]:
    """
    Get total LLM cost for the current day.

    Returns:
        Dictionary with daily_cost_usd and budget information

    Example:
        GET /api/v1/llm-costs/daily
        Response: {"daily_cost_usd": 12.45, "budget_limit_usd": 100.00, "remaining_usd": 87.55}
    """
    try:
        daily_cost = await llm_cost_tracker.get_daily_cost()
        budget_limit = llm_cost_tracker.daily_budget_limit
        remaining = max(0, budget_limit - daily_cost)

        return {
            "daily_cost_usd": round(daily_cost, 4),
            "budget_limit_usd": budget_limit,
            "remaining_usd": round(remaining, 4),
            "budget_exceeded": daily_cost > budget_limit,
            "utilization_percent": (
                round((daily_cost / budget_limit) * 100, 2) if budget_limit > 0 else 0
            ),
        }
    except Exception as e:
        logger.error(f"Error getting daily cost: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve daily cost: {str(e)}"
        ) from e


@router.get(
    "/monthly",
    summary="Get this month's total cost",
    description="Returns the total LLM cost for the current month.",
)
async def get_monthly_cost() -> dict[str, Any]:
    """
    Get total LLM cost for the current month.

    Returns:
        Dictionary with monthly_cost_usd and budget information

    Example:
        GET /api/v1/llm-costs/monthly
        Response: {"monthly_cost_usd": 456.78, "budget_limit_usd": 2000.00, "remaining_usd": 1543.22}
    """
    try:
        monthly_cost = await llm_cost_tracker.get_monthly_cost()
        budget_limit = llm_cost_tracker.monthly_budget_limit
        remaining = max(0, budget_limit - monthly_cost)

        return {
            "monthly_cost_usd": round(monthly_cost, 4),
            "budget_limit_usd": budget_limit,
            "remaining_usd": round(remaining, 4),
            "budget_exceeded": monthly_cost > budget_limit,
            "utilization_percent": (
                round((monthly_cost / budget_limit) * 100, 2) if budget_limit > 0 else 0
            ),
        }
    except Exception as e:
        logger.error(f"Error getting monthly cost: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve monthly cost: {str(e)}"
        ) from e


@router.get(
    "/user/{user_id}/daily",
    summary="Get daily cost for specific user",
    description="Returns the total LLM cost for a specific user for the current day.",
)
async def get_user_daily_cost(user_id: str) -> dict[str, Any]:
    """
    Get daily LLM cost for a specific user.

    Args:
        user_id: User identifier

    Returns:
        Dictionary with user's daily cost and limit information

    Example:
        GET /api/v1/llm-costs/user/abc123/daily
        Response: {"user_id": "abc123", "daily_cost_usd": 3.45, "limit_usd": 10.00, "remaining_usd": 6.55}
    """
    try:
        user_cost = await llm_cost_tracker.get_user_daily_cost(user_id)
        limit = llm_cost_tracker.per_user_daily_limit
        remaining = max(0, limit - user_cost)

        return {
            "user_id": user_id,
            "daily_cost_usd": round(user_cost, 4),
            "limit_usd": limit,
            "remaining_usd": round(remaining, 4),
            "limit_exceeded": user_cost > limit,
            "utilization_percent": (
                round((user_cost / limit) * 100, 2) if limit > 0 else 0
            ),
        }
    except Exception as e:
        logger.error(f"Error getting user daily cost: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve user cost: {str(e)}"
        ) from e


@router.post(
    "/cleanup",
    summary="Cleanup old cost records",
    description="Remove LLM cost records older than specified days (admin only).",
)
async def cleanup_old_records(days: int = Query(30, ge=7, le=365)) -> dict[str, Any]:
    """
    Cleanup old LLM cost records.

    Args:
        days: Remove records older than this many days (7-365, default 30)

    Returns:
        Cleanup summary

    Example:
        POST /api/v1/llm-costs/cleanup?days=90
    """
    try:
        await llm_cost_tracker.cleanup_old_records(days=days)
        summary = await llm_cost_tracker.get_summary()

        return {
            "status": "success",
            "cleanup_days": days,
            "remaining_records": summary["total_requests"],
            "message": f"Records older than {days} days have been removed",
        }
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to cleanup records: {str(e)}"
        ) from e
