"""
Module: api.routes.admin.connection_pools
Description: Admin routes for connection pool management
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import require_admin
from src.core import get_logger
from src.services.connection_pool_service import connection_pool_service

logger = get_logger(__name__)

router = APIRouter(prefix="/connection-pools", tags=["Admin - Connection Pools"])


@router.get("/stats")
async def get_connection_pool_stats(admin_user=Depends(require_admin)):
    """
    Get connection pool statistics.

    Requires admin privileges.
    """
    try:
        stats = await connection_pool_service.get_pool_stats()

        # Add summary
        total_db_connections = sum(
            pool.get("active_connections", 0)
            for pool in stats["database_pools"].values()
        )
        total_redis_connections = sum(
            pool.get("in_use_connections", 0) for pool in stats["redis_pools"].values()
        )

        stats["summary"] = {
            "total_database_connections": total_db_connections,
            "total_redis_connections": total_redis_connections,
            "recommendation_count": len(stats["recommendations"]),
        }

        return stats

    except Exception as e:
        logger.error("connection_pool_stats_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get connection pool statistics",
        )


@router.get("/health")
async def check_connection_pool_health(admin_user=Depends(require_admin)):
    """
    Check health of all connection pools.

    Requires admin privileges.
    """
    try:
        health = await connection_pool_service.health_check()

        logger.info(
            "admin_connection_pool_health_check",
            admin=admin_user.get("email"),
            status=health["status"],
            errors=len(health["errors"]),
        )

        return health

    except Exception as e:
        logger.error("connection_pool_health_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check connection pool health",
        )


@router.get("/optimize")
async def get_optimization_suggestions(admin_user=Depends(require_admin)):
    """
    Get connection pool optimization suggestions.

    Requires admin privileges.
    """
    try:
        optimizations = await connection_pool_service.optimize_pools()

        logger.info(
            "admin_connection_pool_optimization",
            admin=admin_user.get("email"),
            suggestions=len(optimizations["suggested"]),
        )

        return optimizations

    except Exception as e:
        logger.error("connection_pool_optimization_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get optimization suggestions",
        )


@router.get("/config")
async def get_pool_configurations(admin_user=Depends(require_admin)):
    """
    Get current connection pool configurations.

    Requires admin privileges.
    """
    try:
        configs = {
            "database": {
                "main": connection_pool_service.DEFAULT_DB_POOL_CONFIG,
                "active_pools": list(connection_pool_service._engines.keys()),
            },
            "redis": {
                "main": connection_pool_service.DEFAULT_REDIS_POOL_CONFIG,
                "active_pools": list(connection_pool_service._redis_pools.keys()),
            },
        }

        # Add pool-specific configs
        for key, config in connection_pool_service._pool_configs.items():
            if key.startswith("db_"):
                pool_name = key[3:]
                configs["database"][pool_name] = config
            elif key.startswith("redis_"):
                pool_name = key[6:]
                configs["redis"][pool_name] = config

        return configs

    except Exception as e:
        logger.error("connection_pool_config_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pool configurations",
        )


@router.post("/reset-stats")
async def reset_pool_statistics(
    pool_name: str | None = None, admin_user=Depends(require_admin)
):
    """
    Reset connection pool statistics.

    Requires admin privileges.
    """
    try:
        if pool_name:
            # Reset specific pool stats
            if pool_name in connection_pool_service._stats:
                connection_pool_service._stats[pool_name] = type(
                    connection_pool_service._stats[pool_name]
                )()
                logger.info(
                    "admin_pool_stats_reset",
                    admin=admin_user.get("email"),
                    pool=pool_name,
                )
                return {"status": "reset", "pool": pool_name}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pool '{pool_name}' not found",
            )
        # Reset all stats
        for key in connection_pool_service._stats:
            connection_pool_service._stats[key] = type(
                connection_pool_service._stats[key]
            )()

        logger.info("admin_all_pool_stats_reset", admin=admin_user.get("email"))

        return {
            "status": "reset",
            "pools": list(connection_pool_service._stats.keys()),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("pool_stats_reset_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset statistics",
        )


@router.get("/recommendations")
async def get_pool_recommendations(admin_user=Depends(require_admin)):
    """
    Get detailed connection pool recommendations.

    Requires admin privileges.
    """
    try:
        stats = await connection_pool_service.get_pool_stats()
        recommendations = []

        # Analyze database pools
        for name, pool_stats in stats["database_pools"].items():
            # High wait times
            avg_wait = pool_stats.get("average_wait_time", 0)
            if avg_wait > 0.5:
                recommendations.append(
                    {
                        "severity": "high",
                        "pool": name,
                        "type": "database",
                        "issue": f"Average wait time is {avg_wait:.2f}s",
                        "recommendation": "Increase pool_size or max_overflow",
                        "current_config": connection_pool_service._pool_configs.get(
                            f"db_{name}", {}
                        ),
                    }
                )

            # Connection errors
            errors = pool_stats.get("connection_errors", 0)
            if errors > 5:
                recommendations.append(
                    {
                        "severity": "medium",
                        "pool": name,
                        "type": "database",
                        "issue": f"{errors} connection errors detected",
                        "recommendation": "Check database health and network stability",
                    }
                )

            # Low connection reuse
            created = pool_stats.get("connections_created", 0)
            recycled = pool_stats.get("connections_recycled", 0)
            if created > 0 and recycled / created < 0.5:
                recommendations.append(
                    {
                        "severity": "low",
                        "pool": name,
                        "type": "database",
                        "issue": "Low connection reuse rate",
                        "recommendation": "Increase pool_recycle timeout",
                    }
                )

        # Analyze Redis pools
        for name, pool_stats in stats["redis_pools"].items():
            # Near connection limit
            in_use = pool_stats.get("in_use_connections", 0)
            available = pool_stats.get("available_connections", 0)
            total = in_use + available

            if total > 0 and in_use / total > 0.8:
                recommendations.append(
                    {
                        "severity": "high",
                        "pool": name,
                        "type": "redis",
                        "issue": f"Using {in_use}/{total} connections (>80%)",
                        "recommendation": "Increase max_connections",
                    }
                )

        return {
            "recommendations": recommendations,
            "total": len(recommendations),
            "by_severity": {
                "high": sum(1 for r in recommendations if r["severity"] == "high"),
                "medium": sum(1 for r in recommendations if r["severity"] == "medium"),
                "low": sum(1 for r in recommendations if r["severity"] == "low"),
            },
        }

    except Exception as e:
        logger.error("pool_recommendations_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations",
        )
