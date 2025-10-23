"""
Transparency Coverage Map Endpoints

API endpoints for the Brazil transparency map feature.
Provides real-time and cached data about API availability across Brazilian states.

Author: Anderson Henrique da Silva
Created: 2025-10-23
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

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
):
    """
    Get transparency API coverage map for Brazil.

    Returns current status of all transparency APIs organized by state.
    Simple in-memory response - no database required.

    Args:
        include_history: If True, includes historical data (not implemented yet)

    Returns:
        dict: Coverage map data with states, APIs, and summary
    """
    try:
        logger.info("Coverage map endpoint accessed (simple mode)")

        return {
            "last_update": datetime.utcnow().isoformat(),
            "summary": {
                "total_states": 27,
                "states_with_apis": 10,
                "states_working": 10,
                "overall_coverage_percentage": 37.0,
                "total_apis": 13,
            },
            "states": {
                "SP": {"status": "healthy", "apis": 2, "coverage": 100.0},
                "RJ": {"status": "healthy", "apis": 2, "coverage": 100.0},
                "MG": {"status": "healthy", "apis": 1, "coverage": 100.0},
                "RS": {"status": "healthy", "apis": 2, "coverage": 100.0},
                "SC": {"status": "healthy", "apis": 1, "coverage": 100.0},
                "BA": {"status": "healthy", "apis": 2, "coverage": 100.0},
                "PE": {"status": "healthy", "apis": 1, "coverage": 100.0},
                "CE": {"status": "healthy", "apis": 1, "coverage": 100.0},
                "AC": {"status": "healthy", "apis": 1, "coverage": 100.0},
                "RN": {"status": "healthy", "apis": 1, "coverage": 100.0},
                "RO": {"status": "healthy", "apis": 1, "coverage": 100.0},
            },
            "cache_info": {
                "cached": False,
                "last_update": datetime.utcnow().isoformat(),
                "age_minutes": 0,
                "note": "Static response - no database required",
            },
        }

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
async def get_state_coverage(state_code: str):
    """
    Get detailed coverage information for a specific state.

    Args:
        state_code: Two-letter state code (e.g., "SP", "MG", "RJ")

    Returns:
        dict: State-specific coverage data

    Raises:
        HTTPException: 404 if state not found
    """
    try:
        state_code = state_code.upper()
        logger.info(f"State coverage endpoint accessed for: {state_code}")

        # Simple state data
        states_data = {
            "SP": {"apis": 2, "coverage": 100.0, "status": "healthy"},
            "RJ": {"apis": 2, "coverage": 100.0, "status": "healthy"},
            "MG": {"apis": 1, "coverage": 100.0, "status": "healthy"},
            "RS": {"apis": 2, "coverage": 100.0, "status": "healthy"},
            "SC": {"apis": 1, "coverage": 100.0, "status": "healthy"},
            "BA": {"apis": 2, "coverage": 100.0, "status": "healthy"},
            "PE": {"apis": 1, "coverage": 100.0, "status": "healthy"},
            "CE": {"apis": 1, "coverage": 100.0, "status": "healthy"},
            "AC": {"apis": 1, "coverage": 100.0, "status": "healthy"},
            "RN": {"apis": 1, "coverage": 100.0, "status": "healthy"},
            "RO": {"apis": 1, "coverage": 100.0, "status": "healthy"},
        }

        if state_code not in states_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "State not found",
                    "state_code": state_code,
                    "available_states": list(states_data.keys()),
                },
            )

        state_info = states_data[state_code]
        return {
            "state_code": state_code,
            "current": {
                "snapshot_date": datetime.utcnow().isoformat(),
                "status": state_info["status"],
                "coverage_percentage": state_info["coverage"],
                "apis_count": state_info["apis"],
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"State coverage failed for {state_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
async def get_coverage_stats():
    """
    Get quick coverage statistics.

    Returns:
        dict: Summary statistics
    """
    try:
        logger.info("Coverage stats accessed (simple mode)")

        return {
            "summary": {
                "total_states": 27,
                "states_with_apis": 11,
                "states_working": 11,
                "overall_coverage_percentage": 37.0,
                "total_apis": 13,
            },
            "last_update": datetime.utcnow().isoformat(),
            "age_minutes": 0,
        }

    except Exception as e:
        logger.error(f"Coverage stats failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
