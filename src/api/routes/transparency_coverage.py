"""
Transparency Coverage Map Endpoints

API endpoints for the Brazil transparency map feature.
Provides real-time and cached data about API availability across Brazilian states.

Author: Anderson Henrique da Silva
Created: 2025-10-23
"""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.infrastructure.queue.tasks.coverage_tasks import transform_to_map_format
from src.models.transparency_coverage import TransparencyCoverageSnapshot
from src.services.transparency_apis.health_check import HealthMonitor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transparency", tags=["Transparency Coverage"])


@router.get(
    "/coverage/map",
    summary="Get Brazil transparency coverage map",
    description="""
    Get transparency API coverage map for all Brazilian states.

    Returns cached status of all transparency APIs by state, including:
    - Current health status per API
    - Error details and troubleshooting info
    - Legal basis for missing APIs
    - Call-to-action for civic engagement

    **Response Time**: <100ms (cached), 30-60s on first request (cold start)

    **Update Frequency**: Every 6 hours via Celery Beat

    **Cache Info**: Response includes cache metadata (age in minutes)

    **Example Usage**:
    ```bash
    curl https://cidadao-api-production.up.railway.app/api/v1/transparency/coverage/map
    ```
    """,
)
async def get_coverage_map(
    include_history: bool = Query(
        default=False,
        description="Include last 7 days of historical snapshots for trend analysis",
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get transparency API coverage map for Brazil.

    Returns current status of all transparency APIs organized by state,
    with detailed error information and recommended actions.

    Args:
        include_history: If True, includes last 7 days of snapshots
        db: Database session (injected)

    Returns:
        dict: Coverage map data with states, APIs, summary, and issues

    Raises:
        HTTPException: 500 if unable to generate or retrieve coverage data
    """
    try:
        logger.info(
            f"Coverage map endpoint accessed (include_history={include_history})"
        )

        # Query latest main snapshot (state_code=None)
        stmt = (
            select(TransparencyCoverageSnapshot)
            .filter(TransparencyCoverageSnapshot.state_code.is_(None))
            .order_by(TransparencyCoverageSnapshot.snapshot_date.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        latest_snapshot = result.scalar_one_or_none()

        if not latest_snapshot:
            # Cold start: No snapshot exists yet
            # Generate on-demand (this will be slow the first time ~30-60s)
            logger.warning(
                "No coverage snapshot found - generating on-demand (cold start)"
            )

            health_monitor = HealthMonitor()
            health_report = await health_monitor.generate_report()

            coverage_data = transform_to_map_format(health_report)

            # Save for next time
            snapshot = TransparencyCoverageSnapshot(
                snapshot_date=datetime.utcnow(),
                coverage_data=coverage_data,
                summary_stats=coverage_data["summary"],
                state_code=None,  # Main snapshot
                coverage_percentage=coverage_data["summary"][
                    "overall_coverage_percentage"
                ],
            )
            db.add(snapshot)
            await db.commit()

            logger.info(
                f"Coverage map generated on-demand: "
                f"{coverage_data['summary']['states_working']}/{coverage_data['summary']['total_states']} working"
            )

            coverage_data["cache_info"] = {
                "cached": False,
                "last_update": datetime.utcnow().isoformat(),
                "age_minutes": 0,
                "note": "Generated on-demand (first request - future requests will be cached)",
            }
        else:
            # Return cached data
            coverage_data = latest_snapshot.coverage_data
            age_seconds = (
                datetime.utcnow() - latest_snapshot.snapshot_date
            ).total_seconds()
            age_minutes = int(age_seconds / 60)

            coverage_data["cache_info"] = {
                "cached": True,
                "last_update": latest_snapshot.snapshot_date.isoformat(),
                "age_minutes": age_minutes,
                "age_hours": round(age_minutes / 60, 1),
            }

            logger.info(
                f"Coverage map returned from cache (age: {age_minutes}min, "
                f"{coverage_data['summary']['states_working']}/{coverage_data['summary']['total_states']} working)"
            )

        # Include historical data if requested
        if include_history:
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            history_stmt = (
                select(TransparencyCoverageSnapshot)
                .filter(
                    TransparencyCoverageSnapshot.state_code.is_(None),
                    TransparencyCoverageSnapshot.snapshot_date >= seven_days_ago,
                )
                .order_by(TransparencyCoverageSnapshot.snapshot_date.desc())
            )
            history_result = await db.execute(history_stmt)
            history_snapshots = history_result.scalars().all()

            coverage_data["history"] = [
                {
                    "date": snap.snapshot_date.isoformat(),
                    "summary": snap.summary_stats,
                    "overall_coverage": snap.coverage_percentage,
                }
                for snap in history_snapshots
            ]

            logger.info(f"Included {len(history_snapshots)} historical snapshots")

        return coverage_data

    except Exception as e:
        logger.error(f"Coverage map endpoint failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate coverage map: {str(e)}"
        )


@router.get(
    "/coverage/state/{state_code}",
    summary="Get coverage for specific state",
    description="""
    Get detailed coverage information for a specific Brazilian state.

    Returns comprehensive data about all transparency APIs available
    for the specified state, including:
    - Detailed API status and errors
    - Historical trend (last 7 days)
    - Specific issues and recommended actions
    - Legal basis if APIs are missing

    **State Codes**: Use 2-letter codes (SP, MG, RJ, RS, SC, BA, PE, CE, RO, BR for federal)

    **Example**:
    ```bash
    curl https://cidadao-api-production.up.railway.app/api/v1/transparency/coverage/state/SP
    ```
    """,
)
async def get_state_coverage(state_code: str, db: AsyncSession = Depends(get_db)):
    """
    Get detailed coverage information for a specific state.

    Args:
        state_code: Two-letter state code (e.g., "SP", "MG", "RJ")
        db: Database session (injected)

    Returns:
        dict: State-specific coverage data with current status and historical trend

    Raises:
        HTTPException: 404 if state not found, 500 on internal error
    """
    try:
        state_code = state_code.upper()

        logger.info(f"State coverage endpoint accessed for: {state_code}")

        # Get latest state snapshot
        latest_stmt = (
            select(TransparencyCoverageSnapshot)
            .filter(TransparencyCoverageSnapshot.state_code == state_code)
            .order_by(TransparencyCoverageSnapshot.snapshot_date.desc())
            .limit(1)
        )
        latest_result = await db.execute(latest_stmt)
        latest = latest_result.scalar_one_or_none()

        if not latest:
            logger.warning(f"No coverage data found for state: {state_code}")
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "State not found",
                    "state_code": state_code,
                    "message": f"No coverage data available for state {state_code}",
                    "available_states": [
                        "SP",
                        "MG",
                        "RJ",
                        "RS",
                        "SC",
                        "BA",
                        "PE",
                        "CE",
                        "RO",
                        "BR",
                    ],
                },
            )

        # Get historical trend (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        history_stmt = (
            select(TransparencyCoverageSnapshot)
            .filter(
                TransparencyCoverageSnapshot.state_code == state_code,
                TransparencyCoverageSnapshot.snapshot_date >= seven_days_ago,
            )
            .order_by(TransparencyCoverageSnapshot.snapshot_date.desc())
        )
        history_result = await db.execute(history_stmt)
        history = history_result.scalars().all()

        # Analyze trend
        trend = analyze_trend(history)

        logger.info(
            f"State coverage for {state_code}: {latest.state_status}, "
            f"{latest.coverage_percentage:.1f}% coverage, trend: {trend['trend']}"
        )

        return {
            "state_code": state_code,
            "current": {
                "snapshot_date": latest.snapshot_date.isoformat(),
                "status": latest.state_status,
                "coverage_percentage": latest.coverage_percentage,
                "data": latest.coverage_data,
            },
            "history": [
                {
                    "date": snap.snapshot_date.isoformat(),
                    "status": snap.state_status,
                    "coverage_percentage": snap.coverage_percentage,
                }
                for snap in history
            ],
            "trend": trend,
            "cache_info": {
                "age_minutes": int(
                    (datetime.utcnow() - latest.snapshot_date).total_seconds() / 60
                )
            },
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            f"State coverage endpoint failed for {state_code}: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to get state coverage: {str(e)}"
        )


# Constants for trend analysis
MIN_DATA_POINTS_FOR_TREND = 2
COVERAGE_IMPROVEMENT_THRESHOLD = 10  # percentage points
COVERAGE_DEGRADATION_THRESHOLD = -10  # percentage points


def analyze_trend(history: list) -> dict:
    """
    Analyze coverage trend over time.

    Args:
        history: List of TransparencyCoverageSnapshot objects

    Returns:
        dict: Trend analysis with direction and change percentage
    """
    if len(history) < MIN_DATA_POINTS_FOR_TREND:
        return {
            "trend": "insufficient_data",
            "message": "Need at least 2 data points to analyze trend",
        }

    recent = history[0].coverage_percentage or 0
    older = history[-1].coverage_percentage or 0
    change = recent - older

    if change > COVERAGE_IMPROVEMENT_THRESHOLD:
        trend = "improving"
        message = f"Coverage improved by {change:.1f}% in the last 7 days"
    elif change < COVERAGE_DEGRADATION_THRESHOLD:
        trend = "degrading"
        message = f"Coverage degraded by {abs(change):.1f}% in the last 7 days"
    else:
        trend = "stable"
        message = f"Coverage stable (change: {change:+.1f}%)"

    return {
        "trend": trend,
        "change_percentage": round(change, 2),
        "message": message,
        "data_points": len(history),
    }


@router.get(
    "/coverage/stats",
    summary="Get coverage statistics summary",
    description="""
    Get quick statistics about transparency API coverage.

    Returns summary statistics without full state details:
    - Total states
    - States with APIs
    - Working states count
    - Overall coverage percentage
    - Last update timestamp

    **Fast Response**: <10ms (direct query on summary_stats)
    """,
)
async def get_coverage_stats(db: AsyncSession = Depends(get_db)):
    """
    Get quick coverage statistics.

    Returns just the summary without full state details
    for fast dashboard displays.

    Args:
        db: Database session (injected)

    Returns:
        dict: Summary statistics

    Raises:
        HTTPException: 500 if unable to retrieve stats
    """
    try:
        # Query latest main snapshot
        stats_stmt = (
            select(TransparencyCoverageSnapshot)
            .filter(TransparencyCoverageSnapshot.state_code.is_(None))
            .order_by(TransparencyCoverageSnapshot.snapshot_date.desc())
            .limit(1)
        )
        stats_result = await db.execute(stats_stmt)
        latest = stats_result.scalar_one_or_none()

        if not latest:
            logger.warning("No coverage stats available - no snapshots exist")
            raise HTTPException(
                status_code=404,
                detail="No coverage data available - run initial health check",
            )

        age_minutes = int(
            (datetime.utcnow() - latest.snapshot_date).total_seconds() / 60
        )

        logger.info(f"Coverage stats accessed (age: {age_minutes}min)")

        return {
            "summary": latest.summary_stats,
            "last_update": latest.snapshot_date.isoformat(),
            "age_minutes": age_minutes,
            "overall_coverage_percentage": latest.coverage_percentage,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Coverage stats endpoint failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get coverage stats: {str(e)}"
        )
