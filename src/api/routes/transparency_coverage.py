"""
Transparency Coverage Map Endpoints

API endpoints for the Brazil transparency map feature.
Provides real-time and cached data about API availability across Brazilian states.

Author: Anderson Henrique da Silva
Created: 2025-10-23
"""

import logging
from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException, Query

from src.services.cache_service import CacheService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transparency", tags=["Transparency Coverage"])

# Cache instance for storing API health checks
cache = CacheService()

# API definitions to test
APIS_TO_TEST = {
    "BR": {
        "name": "Federal",
        "apis": [
            {
                "name": "IBGE - Geografia",
                "url": "https://servicodados.ibge.gov.br/api/v1/localidades/estados",
                "test_path": "",
                "endpoints": 4,
            },
            {
                "name": "CGU e-Aud (Auditoria)",
                "url": "https://eaud.cgu.gov.br/v3/api-docs",
                "test_path": "",
                "endpoints": 378,
            },
            {
                "name": "Portal da Transparência",
                "url": "https://api.portaldatransparencia.gov.br/api-de-dados/acordos-leniencia",
                "test_path": "",
                "endpoints": 3,
            },
            {
                "name": "PNCP - Contratos Públicos",
                "url": "https://pncp.gov.br/api/pncp/v1/orgaos/siafi",
                "test_path": "",
                "endpoints": 5,
            },
        ],
    },
    "SP": {
        "name": "São Paulo",
        "apis": [
            {
                "name": "Dados Abertos SP",
                "url": "https://dados.sp.gov.br/api/3/action/package_list",
                "test_path": "",
                "endpoints": 5,
            },
        ],
    },
    "RJ": {
        "name": "Rio de Janeiro",
        "apis": [
            {
                "name": "Dados Abertos RJ",
                "url": "https://dados.rj.gov.br/api/3/action/package_list",
                "test_path": "",
                "endpoints": 4,
            },
        ],
    },
    "RS": {
        "name": "Rio Grande do Sul",
        "apis": [
            {
                "name": "Dados Abertos RS",
                "url": "https://dados.rs.gov.br/api/3/action/package_list",
                "test_path": "",
                "endpoints": 3,
            },
        ],
    },
    "SC": {
        "name": "Santa Catarina",
        "apis": [
            {
                "name": "Dados Abertos SC",
                "url": "https://dados.sc.gov.br/api/3/action/package_list",
                "test_path": "",
                "endpoints": 3,
            },
        ],
    },
    "BA": {
        "name": "Bahia",
        "apis": [
            {
                "name": "Dados Abertos BA",
                "url": "https://dados.ba.gov.br/api/3/action/package_list",
                "test_path": "",
                "endpoints": 2,
            },
        ],
    },
    "PE": {
        "name": "Pernambuco",
        "apis": [
            {
                "name": "Dados Abertos PE",
                "url": "https://dados.pe.gov.br/api/3/action/package_list",
                "test_path": "",
                "endpoints": 4,
            },
        ],
    },
    "CE": {
        "name": "Ceará",
        "apis": [
            {
                "name": "TCE-CE",
                "url": "https://api.tce.ce.gov.br/",
                "test_path": "",
                "endpoints": 2,
            },
        ],
    },
    "RO": {
        "name": "Rondônia",
        "apis": [
            {
                "name": "CGE-RO",
                "url": "https://transparencia.api.ro.gov.br/api/v1/contratos",
                "test_path": "",
                "endpoints": 8,
            },
        ],
    },
    "AC": {
        "name": "Acre",
        "apis": [
            {
                "name": "Dados Abertos AC",
                "url": "https://dados.ac.gov.br/api/3/action/package_list",
                "test_path": "",
                "endpoints": 1,
            },
        ],
    },
    "RN": {
        "name": "Rio Grande do Norte",
        "apis": [
            {
                "name": "Dados Abertos RN",
                "url": "https://dados.rn.gov.br/api/3/action/package_list",
                "test_path": "",
                "endpoints": 1,
            },
        ],
    },
}


async def test_api_health(url: str, timeout: float = 10.0) -> dict:
    """
    Test if an API endpoint is responding.

    Args:
        url: API URL to test
        timeout: Request timeout in seconds (default 10s)

    Returns:
        dict: Status information
    """
    try:
        # Disable SSL verification for government APIs with certificate issues
        async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
            response = await client.get(url)

            if response.status_code == 200:
                return {
                    "status": "operational",
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                }
            if response.status_code == 403:
                return {
                    "status": "restricted",
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                }
            if response.status_code == 401:
                return {
                    "status": "restricted",
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                    "error": "Requires authentication",
                }
            if response.status_code == 400:
                return {
                    "status": "partial",
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                    "error": "Requires query parameters",
                }
            return {"status": "error", "error": f"HTTP {response.status_code}"}

    except httpx.TimeoutException:
        return {"status": "timeout", "error": "Request timeout"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def generate_coverage_map() -> dict:
    """
    Generate coverage map by testing all APIs.

    Returns:
        dict: Coverage map with real API status
    """
    logger.info("Generating coverage map with real API tests...")

    states_data = {}
    total_apis = 0
    total_endpoints = 0
    working_apis = 0

    for state_code, state_info in APIS_TO_TEST.items():
        state_apis = []

        for api_def in state_info["apis"]:
            total_apis += 1
            total_endpoints += api_def["endpoints"]

            # Test API health
            health = await test_api_health(api_def["url"])

            if health["status"] in ["operational", "restricted", "partial"]:
                working_apis += 1

            state_apis.append(
                {
                    "name": api_def["name"],
                    "url": (
                        api_def["url"].split("/api")[0]
                        if "/api" in api_def["url"]
                        else api_def["url"]
                    ),
                    "endpoints": api_def["endpoints"],
                    "status": health["status"],
                    "response_time_ms": health.get("response_time_ms"),
                    "error": health.get("error"),
                }
            )

        states_data[state_code] = {
            "name": state_info["name"],
            "status": (
                "healthy"
                if any(api["status"] == "operational" for api in state_apis)
                else "degraded"
            ),
            "apis": state_apis,
        }

    coverage_percentage = (
        round((working_apis / total_apis * 100), 1) if total_apis > 0 else 0
    )

    return {
        "last_update": datetime.utcnow().isoformat(),
        "summary": {
            "total_states": 27,
            "states_with_apis": len(APIS_TO_TEST),
            "states_working": sum(
                1 for s in states_data.values() if s["status"] == "healthy"
            ),
            "overall_coverage_percentage": coverage_percentage,
            "total_apis": total_apis,
            "working_apis": working_apis,
            "total_endpoints": total_endpoints,
        },
        "states": states_data,
    }


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
    force_refresh: bool = Query(
        default=False,
        description="Force refresh - bypass cache and test APIs now",
    ),
):
    """
    Get transparency API coverage map for Brazil with REAL-TIME API testing.

    Tests all APIs and returns actual operational status.
    Results cached for 15 minutes for performance.

    Args:
        force_refresh: If True, bypasses cache and tests all APIs now

    Returns:
        dict: Coverage map with real API status, response times, and errors
    """
    try:
        cache_key = "transparency:coverage:map"
        cache_ttl = 900  # 15 minutes

        # Try to get from cache first (unless force_refresh)
        if not force_refresh:
            cached_data = await cache.get(cache_key)
            if cached_data:
                logger.info("Coverage map returned from cache")
                cached_data["cache_info"] = {
                    "cached": True,
                    "note": "Cached data - use ?force_refresh=true to test APIs now",
                }
                return cached_data

        # Generate fresh data by testing all APIs
        logger.info("Testing all APIs for coverage map (this may take 5-10 seconds)...")
        coverage_data = await generate_coverage_map()

        # Save to cache
        await cache.set(cache_key, coverage_data, ttl=cache_ttl)

        coverage_data["cache_info"] = {
            "cached": False,
            "ttl_seconds": cache_ttl,
            "note": "Fresh data from real API tests - will be cached for 15 minutes",
        }

        logger.info(
            f"Coverage map generated: {coverage_data['summary']['working_apis']}/{coverage_data['summary']['total_apis']} APIs operational"
        )

        return coverage_data

    except Exception as e:
        logger.error(f"Coverage map endpoint failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate coverage map: {str(e)}"
        )


@router.get(
    "/coverage/state/{state_code}",
    summary="Get coverage for specific state",
    description="""Get coverage for a specific state""",
)
async def get_state_coverage(state_code: str):
    """Get state coverage - simplified for now."""
    try:
        state_code = state_code.upper()

        # Get from full map
        cache_key = "transparency:coverage:map"
        cached_data = await cache.get(cache_key)

        if not cached_data:
            # Generate if not in cache
            cached_data = await generate_coverage_map()
            await cache.set(cache_key, cached_data, ttl=900)

        if state_code in cached_data.get("states", {}):
            return {
                "state_code": state_code,
                "data": cached_data["states"][state_code],
                "last_update": cached_data["last_update"],
            }

        raise HTTPException(status_code=404, detail=f"State {state_code} not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"State coverage failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/coverage/stats",
    summary="Get coverage stats",
    description="""Get quick coverage statistics""",
)
async def get_coverage_stats():
    """Get coverage stats from cache or generate."""
    try:
        cache_key = "transparency:coverage:map"
        cached_data = await cache.get(cache_key)

        if not cached_data:
            # Generate if not in cache
            cached_data = await generate_coverage_map()
            await cache.set(cache_key, cached_data, ttl=900)

        return {
            "summary": cached_data["summary"],
            "last_update": cached_data["last_update"],
        }

    except Exception as e:
        logger.error(f"Coverage stats failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
