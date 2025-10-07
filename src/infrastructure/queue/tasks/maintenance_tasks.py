"""
Module: infrastructure.queue.tasks.maintenance_tasks
Description: Celery tasks for system maintenance
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio

from celery import group
from celery.utils.log import get_task_logger

from src.infrastructure.queue.celery_app import celery_app
from src.services.api_key_service import APIKeyService
from src.services.cache_service import CacheService
from src.db.simple_session import get_db_session
from src.core.config import get_settings

logger = get_task_logger(__name__)

settings = get_settings()


@celery_app.task(name="tasks.rotate_api_keys", queue="normal")
def rotate_api_keys() -> Dict[str, Any]:
    """
    Check and rotate API keys that are due.
    
    This task should be run daily.
    
    Returns:
        Rotation results
    """
    logger.info("api_key_rotation_task_started")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_rotate_api_keys_async())
            
            logger.info(
                "api_key_rotation_task_completed",
                rotated_count=result.get("rotated_count", 0)
            )
            
            return result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(
            "api_key_rotation_task_failed",
            error=str(e),
            exc_info=True
        )
        raise


async def _rotate_api_keys_async() -> Dict[str, Any]:
    """Async implementation of API key rotation."""
    async with get_db_session() as db:
        service = APIKeyService(db)
        
        # Check and rotate keys
        rotated_keys = await service.check_and_rotate_keys()
        
        # Clean up expired keys
        cleaned_count = await service.cleanup_expired_keys()
        
        return {
            "task": "api_key_rotation",
            "timestamp": datetime.now().isoformat(),
            "rotated_count": len(rotated_keys),
            "rotated_keys": rotated_keys,
            "cleaned_expired": cleaned_count
        }


@celery_app.task(name="tasks.cleanup_cache", queue="low")
def cleanup_cache(
    older_than_hours: int = 24,
    pattern: str = "*"
) -> Dict[str, Any]:
    """
    Clean up old cache entries.
    
    Args:
        older_than_hours: Remove entries older than this
        pattern: Key pattern to match
        
    Returns:
        Cleanup results
    """
    logger.info(
        "cache_cleanup_started",
        older_than_hours=older_than_hours,
        pattern=pattern
    )
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _cleanup_cache_async(older_than_hours, pattern)
            )
            
            return result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(
            "cache_cleanup_failed",
            error=str(e),
            exc_info=True
        )
        raise


async def _cleanup_cache_async(
    older_than_hours: int,
    pattern: str
) -> Dict[str, Any]:
    """Async cache cleanup implementation."""
    cache_service = CacheService()
    
    # Get cache stats before cleanup
    stats_before = await cache_service.get_stats()
    
    # This would integrate with your cache backend
    # For now, return mock results
    removed_count = 0
    
    # Get cache stats after cleanup
    stats_after = await cache_service.get_stats()
    
    return {
        "task": "cache_cleanup",
        "timestamp": datetime.now().isoformat(),
        "pattern": pattern,
        "older_than_hours": older_than_hours,
        "removed_count": removed_count,
        "stats_before": stats_before,
        "stats_after": stats_after
    }


@celery_app.task(name="tasks.optimize_database", queue="low")
def optimize_database() -> Dict[str, Any]:
    """
    Run database optimization tasks.
    
    This includes:
    - Analyzing tables
    - Updating statistics
    - Cleaning up old data
    
    Returns:
        Optimization results
    """
    logger.info("database_optimization_started")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_optimize_database_async())
            
            return result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(
            "database_optimization_failed",
            error=str(e),
            exc_info=True
        )
        raise


async def _optimize_database_async() -> Dict[str, Any]:
    """Async database optimization implementation."""
    async with get_db_session() as db:
        optimizations = []
        
        # Run ANALYZE on key tables
        tables = [
            "investigations",
            "chat_sessions",
            "api_keys",
            "contracts",
            "anomalies"
        ]
        
        for table in tables:
            try:
                await db.execute(f"ANALYZE {table}")
                optimizations.append({
                    "table": table,
                    "operation": "ANALYZE",
                    "status": "success"
                })
            except Exception as e:
                optimizations.append({
                    "table": table,
                    "operation": "ANALYZE",
                    "status": "failed",
                    "error": str(e)
                })
        
        # Clean up old sessions (older than 30 days)
        try:
            cutoff = datetime.now() - timedelta(days=30)
            result = await db.execute(
                "DELETE FROM chat_sessions WHERE updated_at < :cutoff",
                {"cutoff": cutoff}
            )
            
            optimizations.append({
                "operation": "cleanup_old_sessions",
                "deleted": result.rowcount,
                "status": "success"
            })
        except Exception as e:
            optimizations.append({
                "operation": "cleanup_old_sessions",
                "status": "failed",
                "error": str(e)
            })
        
        await db.commit()
        
        return {
            "task": "database_optimization",
            "timestamp": datetime.now().isoformat(),
            "optimizations": optimizations
        }


@celery_app.task(name="tasks.warm_cache", queue="normal")
def warm_cache() -> Dict[str, Any]:
    """
    Warm up cache with frequently accessed data.
    
    Returns:
        Cache warming results
    """
    logger.info("cache_warming_started")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_warm_cache_async())
            
            return result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(
            "cache_warming_failed",
            error=str(e),
            exc_info=True
        )
        raise


async def _warm_cache_async() -> Dict[str, Any]:
    """Async cache warming implementation."""
    cache_service = CacheService()
    warmed_keys = []
    
    async with get_db_session() as db:
        # Warm frequently accessed data
        
        # 1. Recent investigations
        try:
            result = await db.execute(
                """
                SELECT id, query, status, findings
                FROM investigations
                WHERE created_at > NOW() - INTERVAL '7 days'
                ORDER BY created_at DESC
                LIMIT 20
                """
            )
            investigations = result.fetchall()
            
            for inv in investigations:
                cache_key = f"investigation:{inv.id}"
                await cache_service.set(
                    cache_key,
                    {
                        "id": str(inv.id),
                        "query": inv.query,
                        "status": inv.status,
                        "findings": inv.findings
                    },
                    ttl=3600  # 1 hour
                )
                warmed_keys.append(cache_key)
                
        except Exception as e:
            logger.error("cache_warm_investigations_failed", error=str(e))
        
        # 2. Active API keys
        try:
            result = await db.execute(
                """
                SELECT id, key_prefix, client_id, tier, status
                FROM api_keys
                WHERE status = 'active'
                AND (expires_at IS NULL OR expires_at > NOW())
                """
            )
            api_keys = result.fetchall()
            
            for key in api_keys:
                cache_key = f"api_key:{key.key_prefix}"
                await cache_service.set(
                    cache_key,
                    {
                        "api_key_id": str(key.id),
                        "client_id": key.client_id,
                        "tier": key.tier,
                        "status": key.status
                    },
                    ttl=300  # 5 minutes
                )
                warmed_keys.append(cache_key)
                
        except Exception as e:
            logger.error("cache_warm_api_keys_failed", error=str(e))
        
        # 3. Common query patterns
        common_queries = [
            "contracts last 7 days",
            "anomalies high severity",
            "suppliers top 10"
        ]
        
        for query in common_queries:
            cache_key = f"query_cache:{query}"
            # This would run the actual query
            # For now, just mark as warmed
            warmed_keys.append(cache_key)
    
    return {
        "task": "cache_warming",
        "timestamp": datetime.now().isoformat(),
        "warmed_keys_count": len(warmed_keys),
        "warmed_keys_sample": warmed_keys[:10]  # First 10 as sample
    }


# Add to Celery beat schedule
celery_app.conf.beat_schedule.update({
    "daily-api-key-rotation": {
        "task": "tasks.rotate_api_keys",
        "schedule": timedelta(hours=24),  # Daily at midnight
    },
    "hourly-cache-cleanup": {
        "task": "tasks.cleanup_cache",
        "schedule": timedelta(hours=1),
        "args": (24, "*")  # Clean entries older than 24 hours
    },
    "daily-database-optimization": {
        "task": "tasks.optimize_database",
        "schedule": timedelta(hours=24),
    },
    "periodic-cache-warming": {
        "task": "tasks.warm_cache",
        "schedule": timedelta(minutes=30),  # Every 30 minutes
    }
})