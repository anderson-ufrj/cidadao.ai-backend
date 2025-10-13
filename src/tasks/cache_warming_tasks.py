"""
Module: tasks.cache_warming_tasks
Description: Celery tasks for cache warming
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from datetime import UTC, datetime
from typing import Any, Optional

from celery import shared_task
from celery.utils.log import get_task_logger

from src.services.cache_warming_service import (
    CacheWarmingStrategy,
    cache_warming_service,
)

logger = get_task_logger(__name__)


@shared_task(
    name="cache_warming.warm_all",
    max_retries=3,
    default_retry_delay=300,
    time_limit=600,
    soft_time_limit=540,
)
def warm_all_caches() -> dict[str, Any]:
    """
    Warm all caches using all strategies.

    This task is scheduled to run periodically.
    """
    try:
        logger.info("Starting scheduled cache warming")

        # Execute warming synchronously
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(cache_warming_service.warm_all_caches())

            logger.info("Cache warming completed", result=result)

            return {
                "status": "completed",
                "timestamp": datetime.now(UTC).isoformat(),
                "result": result,
            }

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Cache warming failed: {str(e)}", exc_info=True)
        raise


@shared_task(name="cache_warming.warm_strategy", max_retries=3, default_retry_delay=60)
def warm_specific_strategy(strategy: str) -> dict[str, Any]:
    """
    Warm cache using a specific strategy.

    Args:
        strategy: Name of the warming strategy
    """
    try:
        logger.info(f"Starting cache warming for strategy: {strategy}")

        # Convert string to enum
        strategy_enum = CacheWarmingStrategy(strategy)

        # Execute warming
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                cache_warming_service.trigger_manual_warming([strategy_enum])
            )

            return {
                "status": "completed",
                "strategy": strategy,
                "timestamp": datetime.now(UTC).isoformat(),
                "result": result,
            }

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Strategy warming failed: {str(e)}", exc_info=True)
        raise


@shared_task(
    name="cache_warming.warm_contracts", max_retries=2, default_retry_delay=120
)
def warm_contract_cache(contract_ids: list[str]) -> dict[str, Any]:
    """
    Warm cache for specific contracts.

    Args:
        contract_ids: List of contract IDs to cache
    """
    try:
        logger.info(f"Warming cache for {len(contract_ids)} contracts")

        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                cache_warming_service.warm_specific_data(
                    data_type="contract", identifiers=contract_ids, ttl=3600  # 1 hour
                )
            )

            logger.info(
                f"Contract cache warming completed: "
                f"{len(result['warmed'])} warmed, "
                f"{len(result['failed'])} failed"
            )

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Contract cache warming failed: {str(e)}", exc_info=True)
        raise


@shared_task(
    name="cache_warming.warm_investigations", max_retries=2, default_retry_delay=120
)
def warm_investigation_cache(
    investigation_ids: Optional[list[str]] = None, limit: int = 50
) -> dict[str, Any]:
    """
    Warm cache for investigations.

    Args:
        investigation_ids: Specific IDs or None for recent
        limit: Maximum number to warm if no IDs provided
    """
    try:
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            if investigation_ids:
                # Warm specific investigations
                result = loop.run_until_complete(
                    cache_warming_service.warm_specific_data(
                        data_type="investigation",
                        identifiers=investigation_ids,
                        ttl=1800,  # 30 minutes
                    )
                )
            else:
                # Warm recent investigations
                result = loop.run_until_complete(
                    cache_warming_service.trigger_manual_warming(
                        [CacheWarmingStrategy.RECENT_INVESTIGATIONS]
                    )
                )

            return {
                "status": "completed",
                "timestamp": datetime.now(UTC).isoformat(),
                "result": result,
            }

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Investigation cache warming failed: {str(e)}", exc_info=True)
        raise


@shared_task(name="cache_warming.analyze_patterns", max_retries=1, time_limit=300)
def analyze_cache_patterns() -> dict[str, Any]:
    """
    Analyze cache access patterns for optimization.

    This task collects metrics about cache usage to improve
    warming strategies.
    """
    try:
        logger.info("Analyzing cache access patterns")

        import asyncio

        from src.services.cache_service import cache_service

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Get cache statistics
            stats = loop.run_until_complete(cache_service.get_stats())

            # Get warming status
            warming_status = loop.run_until_complete(
                cache_warming_service.get_warming_status()
            )

            # Analyze patterns
            analysis = {
                "cache_stats": stats,
                "warming_status": warming_status,
                "recommendations": [],
            }

            # Generate recommendations
            if stats.get("hit_rate", 0) < 0.7:
                analysis["recommendations"].append(
                    "Low hit rate detected. Consider warming more frequently accessed data."
                )

            if warming_status["query_frequency_tracked"] > 500:
                analysis["recommendations"].append(
                    "High query diversity. Consider implementing predictive warming."
                )

            logger.info(
                "Cache pattern analysis completed",
                recommendations=len(analysis["recommendations"]),
            )

            return analysis

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Cache pattern analysis failed: {str(e)}", exc_info=True)
        raise


# Celery Beat schedule configuration
from celery.schedules import crontab

beat_schedule = {
    "warm-all-caches": {
        "task": "cache_warming.warm_all",
        "schedule": crontab(minute="*/10"),  # Every 10 minutes
        "options": {"queue": "cache", "priority": 3},
    },
    "warm-popular-data": {
        "task": "cache_warming.warm_strategy",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
        "args": ["popular_data"],
        "options": {"queue": "cache", "priority": 5},
    },
    "warm-static-resources": {
        "task": "cache_warming.warm_strategy",
        "schedule": crontab(hour="*/6"),  # Every 6 hours
        "args": ["static_resources"],
        "options": {"queue": "cache", "priority": 2},
    },
    "analyze-cache-patterns": {
        "task": "cache_warming.analyze_patterns",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
        "options": {"queue": "analytics", "priority": 1},
    },
}
