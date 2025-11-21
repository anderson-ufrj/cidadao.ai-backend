"""
Transparency Coverage Map Tasks

Celery tasks for updating and maintaining transparency API coverage snapshots.
Updates every 6 hours to provide fresh data for the Brazil transparency map.

Author: Anderson Henrique da Silva
Created: 2025-10-23
"""

import logging
import os
from datetime import UTC, datetime
from typing import Optional

from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.models.transparency_coverage import TransparencyCoverageSnapshot
from src.services.transparency_apis.health_check import HealthMonitor

logger = logging.getLogger(__name__)

# Create synchronous database session for Celery tasks
# Celery tasks are synchronous, so we need a sync engine (not async)
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL.startswith("postgresql+asyncpg"):
    # Convert async URL to sync URL for synchronous Celery tasks
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
elif not DATABASE_URL:
    # Default to SQLite if no DATABASE_URL (development)
    DATABASE_URL = "sqlite:///./cidadao_ai_dev.db"

# Create sync engine and session factory for Celery
sync_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# State names mapping (Portuguese)
STATE_NAMES = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
    "BR": "Federal",  # Para Portal da Transparência Federal
}

# API to State mapping
API_TO_STATE = {
    "SP-tce": "SP",
    "SP-ckan": "SP",
    "RJ-tce": "RJ",
    "RJ-ckan": "RJ",
    "MG-tce": "MG",
    "RS-ckan": "RS",
    "SC-ckan": "SC",
    "BA-tce": "BA",
    "BA-ckan": "BA",
    "PE-tce": "PE",
    "PE-ckan": "PE",  # New: Pernambuco state CKAN
    "CE-tce": "CE",
    "RO-cge": "RO",  # Rondônia CGE (replaced RO-state)
    "GO-ckan": "GO",  # New: Goiás
    "ES-ckan": "ES",  # New: Espírito Santo
    "DF-ckan": "DF",  # New: Distrito Federal
    "AC-ckan": "AC",  # New: Acre
    "RN-ckan": "RN",  # New: Rio Grande do Norte
    "FEDERAL-portal": "BR",
}


@shared_task(name="update_transparency_coverage", bind=True)
def update_transparency_coverage(self):
    """
    Update transparency coverage map snapshot.

    Runs every 6 hours via Celery Beat to update API coverage status
    for all Brazilian states.

    Returns:
        dict: Summary of the update operation
    """
    import asyncio

    try:
        logger.info("🗺️  Starting transparency coverage update...")

        # Create database session
        db: Session = SessionLocal()

        try:
            # Run comprehensive health check on all APIs (async call in sync context)
            health_monitor = HealthMonitor()

            # Create event loop for async call (Celery tasks are synchronous)
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            health_report = loop.run_until_complete(health_monitor.generate_report())

            logger.info(
                f"Health check completed: {health_report.get('overall_status')} - "
                f"{health_report.get('metadata', {}).get('healthy_count', 0)} healthy APIs"
            )

            # Transform health report into map-friendly format
            coverage_data = transform_to_map_format(health_report)

            # Create main snapshot entry
            main_snapshot = TransparencyCoverageSnapshot(
                snapshot_date=datetime.now(UTC),
                coverage_data=coverage_data,
                summary_stats=coverage_data["summary"],
                state_code=None,  # Main snapshot
                state_status=None,
                coverage_percentage=coverage_data["summary"][
                    "overall_coverage_percentage"
                ],
            )
            db.add(main_snapshot)

            # Create per-state entries for faster queries
            for state_code, state_info in coverage_data["states"].items():
                state_snapshot = TransparencyCoverageSnapshot(
                    snapshot_date=datetime.now(UTC),
                    coverage_data={"state": state_info},
                    summary_stats={
                        "overall_status": state_info["overall_status"],
                        "coverage_percentage": state_info["coverage_percentage"],
                        "api_count": len(state_info["apis"]),
                    },
                    state_code=state_code,
                    state_status=state_info["overall_status"],
                    coverage_percentage=state_info["coverage_percentage"],
                )
                db.add(state_snapshot)

            db.commit()

            logger.info(
                f"✅ Coverage map updated successfully! "
                f"States with APIs: {coverage_data['summary']['states_with_apis']}/27, "
                f"Working: {coverage_data['summary']['states_working']}, "
                f"Overall coverage: {coverage_data['summary']['overall_coverage_percentage']:.1f}%"
            )

            return {
                "status": "success",
                "timestamp": datetime.now(UTC).isoformat(),
                "summary": coverage_data["summary"],
            }

        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error updating coverage map: {str(e)}", exc_info=True)
            raise
        finally:
            db.close()

    except Exception as e:
        logger.error(f"❌ Fatal error in coverage update task: {str(e)}", exc_info=True)
        # Celery will retry automatically based on retry policy
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes


def transform_to_map_format(health_report: dict) -> dict:
    """
    Transform HealthCheckService report into map-friendly format.

    Args:
        health_report: Output from HealthCheckService.generate_report()

    Returns:
        dict: Map-formatted data with states, APIs, and summary
    """
    states_map = {}

    # Process each API from health report
    for api_key, state_code in API_TO_STATE.items():
        # Initialize state if not exists
        if state_code not in states_map:
            states_map[state_code] = {
                "name": STATE_NAMES.get(state_code, state_code),
                "apis": [],
                "overall_status": "unknown",
                "coverage_percentage": 0.0,
                "color": "#94a3b8",  # Default gray
            }

        # Find API details in health report
        api_detail = extract_api_detail(health_report, api_key)
        if api_detail:
            states_map[state_code]["apis"].append(api_detail)

    # Calculate overall status per state
    for state_code, state_info in states_map.items():
        apis = state_info["apis"]
        if not apis:
            state_info["overall_status"] = "no_api"
            state_info["coverage_percentage"] = 0.0
            state_info["color"] = "#6b7280"  # Gray
            continue

        healthy_count = sum(1 for api in apis if api["status"] == "healthy")
        degraded_count = sum(
            1 for api in apis if api["status"] in ["degraded", "timeout"]
        )

        state_info["coverage_percentage"] = (healthy_count / len(apis)) * 100

        if healthy_count == len(apis):
            state_info["overall_status"] = "healthy"
            state_info["color"] = "#22c55e"  # Green
        elif healthy_count > 0 or degraded_count > 0:
            state_info["overall_status"] = "degraded"
            state_info["color"] = "#f59e0b"  # Yellow
        else:
            state_info["overall_status"] = "unhealthy"
            state_info["color"] = "#ef4444"  # Red

    # Calculate summary statistics
    summary = calculate_summary_stats(states_map)

    # Extract known issues
    issues = extract_known_issues(states_map, health_report)

    return {
        "last_update": datetime.now(UTC).isoformat(),
        "states": states_map,
        "summary": summary,
        "issues": issues,
        "call_to_action": {
            "title": "Cobre Transparência do Seu Estado",
            "description": "Seu estado não tem API de transparência? Protocole um pedido via Lei de Acesso à Informação!",
            "guide_url": "https://docs.cidadao.ai/activism/lai-request-guide",
        },
    }


def extract_api_detail(health_report: dict, api_key: str) -> Optional[dict]:
    """
    Extract detailed information for a specific API from health report.

    Args:
        health_report: Health check report from HealthCheckService
        api_key: API identifier (e.g., "SP-tce", "MG-tce")

    Returns:
        dict: API details or None if not found
    """
    # Get API details from health report
    api_details = health_report.get("apis", {}).get("details", {})

    # Check each category
    for category in ["healthy", "degraded", "unhealthy", "unknown"]:
        category_apis = health_report.get("apis", {}).get(category, [])
        if api_key in category_apis:
            detail = api_details.get(api_key, {})

            # Map status
            status_map = {
                "healthy": "healthy",
                "degraded": "degraded",
                "unhealthy": "unhealthy",
                "unknown": "unknown",
            }

            return {
                "id": api_key,
                "name": detail.get("name", api_key),
                "type": detect_api_type(api_key),
                "status": status_map.get(category, "unknown"),
                "response_time_ms": detail.get("response_time_ms"),
                "last_check": detail.get("last_check", datetime.now(UTC).isoformat()),
                "error": detail.get("error"),
                "error_details": detail.get("error_details", {}),
                "coverage": detail.get("coverage", []),
                "action": detail.get("action", ""),
            }

    return None


def detect_api_type(api_key: str) -> str:
    """
    Detect API type from key.

    Args:
        api_key: API identifier

    Returns:
        str: API type (tce, ckan, state_portal, federal)
    """
    if "tce" in api_key.lower():
        return "tce"
    elif "ckan" in api_key.lower():
        return "ckan"
    elif "state" in api_key.lower():
        return "state_portal"
    elif "portal" in api_key.lower() or "federal" in api_key.lower():
        return "federal"
    return "unknown"


def calculate_summary_stats(states_map: dict) -> dict:
    """
    Calculate summary statistics from states map.

    Args:
        states_map: Map of state data

    Returns:
        dict: Summary statistics
    """
    total_states = 27  # Brazil has 26 states + 1 DF
    states_with_apis = len([s for s in states_map.values() if s["apis"]])
    states_working = len(
        [s for s in states_map.values() if s["overall_status"] == "healthy"]
    )
    states_degraded = len(
        [s for s in states_map.values() if s["overall_status"] == "degraded"]
    )
    states_no_api = total_states - states_with_apis

    # Calculate overall coverage percentage
    total_apis = sum(len(s["apis"]) for s in states_map.values())
    healthy_apis = sum(
        sum(1 for api in s["apis"] if api["status"] == "healthy")
        for s in states_map.values()
    )
    overall_coverage = (healthy_apis / total_apis * 100) if total_apis > 0 else 0

    # Count APIs by status
    degraded_apis = sum(
        sum(1 for api in s["apis"] if api["status"] in ["degraded", "timeout"])
        for s in states_map.values()
    )
    unhealthy_apis = sum(
        sum(
            1
            for api in s["apis"]
            if api["status"] in ["unhealthy", "blocked", "server_error"]
        )
        for s in states_map.values()
    )

    return {
        "total_states": total_states,
        "states_with_apis": states_with_apis,
        "states_working": states_working,
        "states_degraded": states_degraded,
        "states_no_api": states_no_api,
        "overall_coverage_percentage": round(overall_coverage, 2),
        "api_breakdown": {
            "healthy": healthy_apis,
            "degraded": degraded_apis,
            "unhealthy": unhealthy_apis,
            "total": total_apis,
        },
    }


def extract_known_issues(states_map: dict, health_report: dict) -> list:
    """
    Extract list of known issues for display.

    Args:
        states_map: Map of state data
        health_report: Health check report

    Returns:
        list: List of issue dictionaries
    """
    issues = []

    # Check for TCE-MG specific issue (no API)
    if "MG" in states_map:
        mg_apis = states_map["MG"]["apis"]
        if any(
            api["status"] == "blocked"
            or "firewall" in str(api.get("error", "")).lower()
            for api in mg_apis
        ):
            issues.append(
                {
                    "severity": "critical",
                    "title": "TCE-MG removed API in portal redesign",
                    "description": (
                        "Portal de Dados Abertos do TCE-MG não oferece API REST, apenas visualização web. "
                        "Violação do Decreto Estadual 48.383/2022."
                    ),
                    "affected_states": ["MG"],
                    "action": "Pedido LAI protocolado - Acompanhe: github.com/anderson-ufrj/cidadao.ai/issues/MG-TCE",
                    "legal_basis": "Decreto MG 48.383/2022, Art. 22",
                }
            )

    # Check for multiple infrastructure issues
    unhealthy_states = [
        code
        for code, info in states_map.items()
        if info["overall_status"] in ["unhealthy", "degraded"] and code != "BR"
    ]

    if len(unhealthy_states) >= 3:
        issues.append(
            {
                "severity": "high",
                "title": f"{len(unhealthy_states)} estados com problemas de infraestrutura",
                "description": "Múltiplas APIs estaduais offline ou com timeout extremo",
                "affected_states": unhealthy_states,
                "action": "Monitoramento ativo - Problemas de infraestrutura estadual não fixáveis do nosso lado",
            }
        )

    # Check for Federal Portal demo mode
    if "BR" in states_map:
        br_apis = states_map["BR"]["apis"]
        if any("demo" in str(api.get("error", "")).lower() for api in br_apis):
            issues.append(
                {
                    "severity": "medium",
                    "title": "Portal Federal em modo demonstração",
                    "description": "Portal da Transparência Federal requer chave de API (TRANSPARENCY_API_KEY) para dados reais",
                    "affected_states": ["BR"],
                    "action": "Configure TRANSPARENCY_API_KEY no Railway para habilitar dados federais",
                }
            )

    return issues
