"""
Module: core.llm_cost_tracker
Description: LLM usage cost tracking and monitoring
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from src.core import get_logger
from src.infrastructure.observability.metrics import metrics_manager

logger = get_logger(__name__)


@dataclass
class LLMUsage:
    """LLM usage tracking for a single request."""

    provider: str  # maritaca, anthropic, groq, together
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    user_id: str | None = None
    agent_name: str | None = None
    request_id: str | None = None


# Cost per 1M tokens (as of 2025-01) - Update quarterly
LLM_COSTS = {
    # Maritaca AI (Brazilian provider) - Prices in BRL converted to USD (~5.5 BRL/USD)
    "maritaca": {
        "sabiazinho-3": {
            "input": 0.18,
            "output": 0.55,
        },  # R$ 1.00/R$ 3.00 per 1M tokens - Fast and economical
        "sabia-3": {
            "input": 0.91,
            "output": 1.82,
        },  # R$ 5.00/R$ 10.00 per 1M tokens - Legacy model
        "sabia-3.1": {
            "input": 0.91,
            "output": 1.82,
        },  # R$ 5.00/R$ 10.00 per 1M tokens - Latest and most advanced (RECOMMENDED)
    },
    # Anthropic Claude
    "anthropic": {
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
        "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
        "claude-3-7-sonnet-20250219": {"input": 3.00, "output": 15.00},
    },
    # Groq (fallback)
    "groq": {
        "mixtral-8x7b-32768": {"input": 0.27, "output": 0.27},
        "llama2-70b-4096": {"input": 0.70, "output": 0.80},
    },
    # Together AI (fallback)
    "together": {
        "mistralai/Mixtral-8x7B-Instruct-v0.1": {"input": 0.60, "output": 0.60},
        "meta-llama/Llama-2-70b-chat-hf": {"input": 0.90, "output": 0.90},
    },
}


class LLMCostTracker:
    """
    Track and monitor LLM usage costs across all providers.

    Features:
    - Real-time cost tracking
    - Per-user cost limits
    - Per-agent cost analytics
    - Daily/monthly budget alerts
    - Prometheus metrics integration
    """

    def __init__(self):
        """Initialize cost tracker."""
        self._usage_history: list[LLMUsage] = []
        self._cost_cache: dict[str, float] = {}  # user_id -> total_cost
        self._lock = asyncio.Lock()

        # Budget limits (USD)
        self.daily_budget_limit = 100.00  # $100/day
        self.monthly_budget_limit = 2000.00  # $2000/month
        self.per_user_daily_limit = 10.00  # $10/user/day

        logger.info("LLM Cost Tracker initialized")

    def calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Calculate cost for an LLM request.

        Args:
            provider: LLM provider name
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        try:
            costs = LLM_COSTS.get(provider, {}).get(model)
            if not costs:
                logger.warning(f"No cost data for {provider}/{model}, using default")
                costs = {"input": 1.00, "output": 1.50}  # Conservative default

            input_cost = (input_tokens / 1_000_000) * costs["input"]
            output_cost = (output_tokens / 1_000_000) * costs["output"]

            return input_cost + output_cost

        except Exception as e:
            logger.error(f"Error calculating cost: {e}")
            return 0.0

    async def track_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        user_id: str | None = None,
        agent_name: str | None = None,
        request_id: str | None = None,
    ) -> LLMUsage:
        """
        Track LLM usage and update metrics.

        Args:
            provider: LLM provider
            model: Model name
            input_tokens: Input token count
            output_tokens: Output token count
            latency_ms: Request latency in milliseconds
            user_id: Optional user ID
            agent_name: Optional agent name
            request_id: Optional request ID

        Returns:
            LLMUsage object with cost information
        """
        # Calculate cost
        total_tokens = input_tokens + output_tokens
        cost_usd = self.calculate_cost(provider, model, input_tokens, output_tokens)

        # Create usage record
        usage = LLMUsage(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            user_id=user_id,
            agent_name=agent_name,
            request_id=request_id,
        )

        # Store usage
        async with self._lock:
            self._usage_history.append(usage)

            # Update cost cache
            if user_id:
                self._cost_cache[user_id] = (
                    self._cost_cache.get(user_id, 0.0) + cost_usd
                )

        # Record Prometheus metrics
        metrics_manager.increment_counter(
            "cidadao_ai_llm_requests_total",
            labels={
                "provider": provider,
                "model": model,
                "agent": agent_name or "unknown",
            },
        )

        metrics_manager.increment_counter(
            "cidadao_ai_llm_tokens_total",
            value=total_tokens,
            labels={
                "provider": provider,
                "model": model,
                "type": "combined",
            },
        )

        metrics_manager.observe_histogram(
            "cidadao_ai_llm_cost_usd",
            cost_usd,
            labels={
                "provider": provider,
                "model": model,
            },
        )

        metrics_manager.observe_histogram(
            "cidadao_ai_llm_latency_ms",
            latency_ms,
            labels={
                "provider": provider,
                "model": model,
            },
        )

        # Check budget limits
        await self._check_budget_limits(cost_usd, user_id)

        logger.debug(
            f"LLM usage tracked: {provider}/{model} - "
            f"{total_tokens} tokens, ${cost_usd:.6f}, {latency_ms:.2f}ms"
        )

        return usage

    async def _check_budget_limits(self, cost: float, user_id: str | None):
        """Check if budget limits are exceeded and log warnings."""
        # Check daily budget
        daily_cost = await self.get_daily_cost()
        if daily_cost > self.daily_budget_limit:
            logger.warning(
                f"Daily budget exceeded: ${daily_cost:.2f} > ${self.daily_budget_limit:.2f}"
            )
            metrics_manager.increment_counter(
                "cidadao_ai_llm_budget_exceeded_total", labels={"period": "daily"}
            )

        # Check per-user daily limit
        if user_id:
            user_daily_cost = await self.get_user_daily_cost(user_id)
            if user_daily_cost > self.per_user_daily_limit:
                logger.warning(
                    f"User {user_id} daily limit exceeded: "
                    f"${user_daily_cost:.2f} > ${self.per_user_daily_limit:.2f}"
                )
                metrics_manager.increment_counter(
                    "cidadao_ai_llm_user_budget_exceeded_total",
                    labels={"user_id": user_id[:8]},  # Anonymize
                )

    async def get_daily_cost(self) -> float:
        """Get total cost for the current day."""
        now = datetime.now(UTC)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

        async with self._lock:
            daily_cost = sum(
                usage.cost_usd
                for usage in self._usage_history
                if usage.timestamp >= start_of_day
            )

        return daily_cost

    async def get_monthly_cost(self) -> float:
        """Get total cost for the current month."""
        now = datetime.now(UTC)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        async with self._lock:
            monthly_cost = sum(
                usage.cost_usd
                for usage in self._usage_history
                if usage.timestamp >= start_of_month
            )

        return monthly_cost

    async def get_user_daily_cost(self, user_id: str) -> float:
        """Get daily cost for a specific user."""
        now = datetime.now(UTC)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

        async with self._lock:
            user_cost = sum(
                usage.cost_usd
                for usage in self._usage_history
                if usage.user_id == user_id and usage.timestamp >= start_of_day
            )

        return user_cost

    async def get_cost_by_agent(self, hours: int = 24) -> dict[str, float]:
        """Get cost breakdown by agent for the last N hours."""
        cutoff = datetime.now(UTC) - timedelta(hours=hours)

        cost_by_agent: dict[str, float] = {}

        async with self._lock:
            for usage in self._usage_history:
                if usage.timestamp >= cutoff and usage.agent_name:
                    agent = usage.agent_name
                    cost_by_agent[agent] = (
                        cost_by_agent.get(agent, 0.0) + usage.cost_usd
                    )

        return cost_by_agent

    async def get_cost_by_provider(self, hours: int = 24) -> dict[str, float]:
        """Get cost breakdown by provider for the last N hours."""
        cutoff = datetime.now(UTC) - timedelta(hours=hours)

        cost_by_provider: dict[str, float] = {}

        async with self._lock:
            for usage in self._usage_history:
                if usage.timestamp >= cutoff:
                    provider = usage.provider
                    cost_by_provider[provider] = (
                        cost_by_provider.get(provider, 0.0) + usage.cost_usd
                    )

        return cost_by_provider

    async def get_summary(self) -> dict[str, Any]:
        """Get comprehensive cost summary."""
        daily_cost = await self.get_daily_cost()
        monthly_cost = await self.get_monthly_cost()
        cost_by_agent = await self.get_cost_by_agent(hours=24)
        cost_by_provider = await self.get_cost_by_provider(hours=24)

        return {
            "daily_cost_usd": round(daily_cost, 4),
            "monthly_cost_usd": round(monthly_cost, 4),
            "daily_budget_limit_usd": self.daily_budget_limit,
            "monthly_budget_limit_usd": self.monthly_budget_limit,
            "daily_budget_remaining_usd": round(
                max(0, self.daily_budget_limit - daily_cost), 4
            ),
            "monthly_budget_remaining_usd": round(
                max(0, self.monthly_budget_limit - monthly_cost), 4
            ),
            "cost_by_agent_24h": cost_by_agent,
            "cost_by_provider_24h": cost_by_provider,
            "total_requests": len(self._usage_history),
        }

    async def cleanup_old_records(self, days: int = 30):
        """Remove usage records older than N days."""
        cutoff = datetime.now(UTC) - timedelta(days=days)

        async with self._lock:
            original_count = len(self._usage_history)
            self._usage_history = [
                usage for usage in self._usage_history if usage.timestamp >= cutoff
            ]
            removed = original_count - len(self._usage_history)

        if removed > 0:
            logger.info(f"Cleaned up {removed} old LLM usage records")


# Global cost tracker instance
llm_cost_tracker = LLMCostTracker()
