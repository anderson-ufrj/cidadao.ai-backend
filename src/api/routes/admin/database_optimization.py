"""
Module: api.routes.admin.database_optimization
Description: Admin routes for database optimization
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies import get_db, require_admin
from src.core import get_logger
from src.services.database_optimization_service import database_optimization_service

logger = get_logger(__name__)

router = APIRouter(
    prefix="/database-optimization", tags=["Admin - Database Optimization"]
)


@router.get("/analyze-slow-queries")
async def analyze_slow_queries(
    limit: int = Query(default=20, ge=1, le=100),
    admin_user=Depends(require_admin),
    db=Depends(get_db),
):
    """
    Analyze slow queries and get optimization suggestions.

    Requires admin privileges.
    """
    try:
        analyses = await database_optimization_service.analyze_slow_queries(
            session=db, limit=limit
        )

        # Format response
        results = []
        for analysis in analyses:
            results.append(
                {
                    "query": (
                        analysis.query[:200] + "..."
                        if len(analysis.query) > 200
                        else analysis.query
                    ),
                    "execution_time": analysis.execution_time,
                    "calls": analysis.plan.get("calls", 0),
                    "total_time": analysis.plan.get("total_time", 0),
                    "suggestions": analysis.suggestions,
                    "estimated_improvement": analysis.estimated_improvement,
                }
            )

        logger.info(
            "admin_slow_queries_analyzed",
            admin=admin_user.get("email"),
            queries_count=len(results),
        )

        return {
            "slow_queries": results,
            "total": len(results),
            "threshold_seconds": database_optimization_service._slow_query_threshold,
        }

    except Exception as e:
        logger.error("analyze_slow_queries_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze slow queries",
        )


@router.get("/missing-indexes")
async def get_missing_indexes(admin_user=Depends(require_admin), db=Depends(get_db)):
    """
    Get suggestions for missing indexes.

    Requires admin privileges.
    """
    try:
        index_suggestions = await database_optimization_service.create_missing_indexes(
            session=db, dry_run=True  # Don't create, just suggest
        )

        logger.info(
            "admin_missing_indexes_analyzed",
            admin=admin_user.get("email"),
            suggestions_count=len(index_suggestions),
        )

        return {"missing_indexes": index_suggestions, "total": len(index_suggestions)}

    except Exception as e:
        logger.error("missing_indexes_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze missing indexes",
        )


@router.post("/create-indexes")
async def create_missing_indexes(
    dry_run: bool = Query(
        default=True, description="If true, only show what would be created"
    ),
    admin_user=Depends(require_admin),
    db=Depends(get_db),
):
    """
    Create missing indexes based on analysis.

    Requires admin privileges.
    """
    try:
        results = await database_optimization_service.create_missing_indexes(
            session=db, dry_run=dry_run
        )

        created_count = sum(1 for r in results if r.get("status") == "created")

        logger.info(
            "admin_indexes_created",
            admin=admin_user.get("email"),
            dry_run=dry_run,
            created=created_count,
            total=len(results),
        )

        return {
            "dry_run": dry_run,
            "indexes": results,
            "created": created_count,
            "total": len(results),
        }

    except Exception as e:
        logger.error("create_indexes_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create indexes",
        )


@router.post("/optimize-statistics")
async def optimize_table_statistics(
    tables: list[str] | None = None,
    admin_user=Depends(require_admin),
    db=Depends(get_db),
):
    """
    Update table statistics for query planner optimization.

    Requires admin privileges.
    """
    try:
        results = await database_optimization_service.optimize_table_statistics(
            session=db, tables=tables
        )

        logger.info(
            "admin_statistics_optimized",
            admin=admin_user.get("email"),
            analyzed=len(results["analyzed"]),
            vacuumed=len(results["vacuumed"]),
        )

        return results

    except Exception as e:
        logger.error("optimize_statistics_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to optimize statistics",
        )


@router.get("/database-stats")
async def get_database_statistics(
    admin_user=Depends(require_admin), db=Depends(get_db)
):
    """
    Get comprehensive database statistics.

    Requires admin privileges.
    """
    try:
        stats = await database_optimization_service.get_database_stats(db)

        return {
            "database_size": stats.get("database_size"),
            "largest_tables": stats.get("largest_tables", []),
            "least_used_indexes": stats.get("least_used_indexes", []),
            "cache_hit_ratio": stats.get("cache_hit_ratio"),
            "connections": stats.get("connections"),
            "recommendations": generate_recommendations(stats),
        }

    except Exception as e:
        logger.error("database_stats_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get database statistics",
        )


def generate_recommendations(stats: dict[str, Any]) -> list[str]:
    """Generate recommendations based on statistics."""
    recommendations = []

    # Cache hit ratio
    cache_ratio = stats.get("cache_hit_ratio", {}).get("ratio", 0)
    if cache_ratio < 0.90:
        recommendations.append(
            f"Cache hit ratio is {cache_ratio:.1%}. Consider increasing shared_buffers."
        )

    # Unused indexes
    unused_indexes = [
        idx for idx in stats.get("least_used_indexes", []) if idx["scans"] == 0
    ]
    if unused_indexes:
        recommendations.append(
            f"Found {len(unused_indexes)} unused indexes consuming space. Consider dropping them."
        )

    # Connection pooling
    connections = stats.get("connections", {})
    idle_ratio = connections.get("idle", 0) / max(connections.get("total", 1), 1)
    if idle_ratio > 0.8:
        recommendations.append(
            "High idle connection ratio. Consider adjusting connection pool settings."
        )

    # Large tables
    large_tables = stats.get("largest_tables", [])
    if large_tables and large_tables[0]["row_count"] > 10000000:
        recommendations.append(
            "Very large tables detected. Consider partitioning for better performance."
        )

    return recommendations
