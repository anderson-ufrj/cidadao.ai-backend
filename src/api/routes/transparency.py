"""
REST API endpoints for Transparency APIs integration.

Provides access to Brazilian government transparency data from multiple sources
including federal, state, TCE, and CKAN APIs.

Author: Anderson Henrique da Silva
Created: 2025-10-09
License: Proprietary - All rights reserved
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.core import get_logger
from src.services.transparency_apis import (
    get_health_monitor,
    get_transparency_collector,
    registry,
)

logger = get_logger(__name__)
router = APIRouter()


# Response Models
class ContractResponse(BaseModel):
    """Response model for contracts endpoint."""

    contracts: list[dict] = Field(description="List of contracts")
    total: int = Field(description="Total number of contracts")
    sources: list[str] = Field(description="Data sources used")
    errors: list[dict] = Field(description="Errors from failed sources")
    metadata: dict = Field(description="Collection metadata")


class ExpenseResponse(BaseModel):
    """Response model for expenses endpoint."""

    expenses: list[dict] = Field(description="List of expenses")
    total: int = Field(description="Total number of expenses")
    sources: list[str] = Field(description="Data sources used")
    errors: list[dict] = Field(description="Errors from failed sources")
    metadata: dict = Field(description="Collection metadata")


class SupplierResponse(BaseModel):
    """Response model for suppliers endpoint."""

    suppliers: list[dict] = Field(description="List of suppliers")
    total: int = Field(description="Total number of suppliers")
    sources: list[str] = Field(description="Data sources used")
    errors: list[dict] = Field(description="Errors from failed sources")
    metadata: dict = Field(description="Collection metadata")


class AnomalyAnalysisResponse(BaseModel):
    """Response model for anomaly analysis endpoint."""

    summary: dict = Field(description="Analysis summary")
    anomalies: dict = Field(description="Detected anomalies")
    metadata: dict = Field(description="Analysis metadata")


class HealthReportResponse(BaseModel):
    """Response model for health check endpoint."""

    overall_status: str = Field(description="Overall health status")
    overall_health_percentage: float = Field(description="Overall health percentage")
    summary: str = Field(description="Health summary")
    apis: dict = Field(description="Individual API health checks")
    metadata: dict = Field(description="Health check metadata")


class AvailableAPIsResponse(BaseModel):
    """Response model for available APIs list."""

    total: int = Field(description="Total number of APIs")
    apis: list[str] = Field(description="List of available API keys")
    description: str = Field(description="API coverage description")


# Endpoints
@router.get(
    "/contracts",
    response_model=ContractResponse,
    summary="Get contracts from transparency sources",
    description="""
    Fetch government contracts from multiple transparency sources across Brazil.

    **Data Sources:**
    - Federal Portal da Transparência
    - 6 TCE APIs (PE, CE, RJ, SP, MG, BA) - 2500+ municipalities
    - 5 CKAN portals (SP, RJ, RS, SC, BA)
    - 1 State API (RO)

    **Features:**
    - Automatic data validation
    - Multi-source aggregation
    - Intelligent caching
    - Error resilience
    """,
)
async def get_contracts(
    state: Optional[str] = Query(None, description="State code (e.g., PE, CE, RJ)"),
    municipality_code: Optional[str] = Query(
        None, description="IBGE municipality code"
    ),
    year: Optional[int] = Query(None, description="Filter by year"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    validate: bool = Query(True, description="Enable data validation"),
):
    """
    Get contracts from transparency sources.

    Returns contracts from federal, state, and municipal transparency portals
    with automatic validation and error handling.
    """
    try:
        collector = get_transparency_collector()

        result = await collector.collect_contracts(
            state=state,
            municipality_code=municipality_code,
            year=year,
            start_date=start_date,
            end_date=end_date,
            validate=validate,
        )

        logger.info(
            "contracts_endpoint_accessed",
            total=result["total"],
            sources_count=len(result["sources"]),
            state=state,
            municipality_code=municipality_code,
        )

        return ContractResponse(**result)

    except Exception as e:
        logger.error(
            "contracts_endpoint_failed",
            error=str(e),
            state=state,
            municipality_code=municipality_code,
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch contracts: {str(e)}"
        )


@router.get(
    "/expenses",
    response_model=ExpenseResponse,
    summary="Get expenses from transparency sources",
    description="""
    Fetch government expenses from multiple transparency sources.

    Aggregates expense data from federal, state, and municipal APIs with
    automatic validation and caching.
    """,
)
async def get_expenses(
    state: Optional[str] = Query(None, description="State code (e.g., PE, CE, RJ)"),
    municipality_code: Optional[str] = Query(
        None, description="IBGE municipality code"
    ),
    year: Optional[int] = Query(None, description="Filter by year"),
    validate: bool = Query(True, description="Enable data validation"),
):
    """
    Get expenses from transparency sources.

    Returns expenses from multiple government transparency portals
    with validation and error handling.
    """
    try:
        collector = get_transparency_collector()

        result = await collector.collect_expenses(
            state=state,
            municipality_code=municipality_code,
            year=year,
            validate=validate,
        )

        logger.info(
            "expenses_endpoint_accessed",
            total=result["total"],
            sources_count=len(result["sources"]),
            state=state,
            municipality_code=municipality_code,
        )

        return ExpenseResponse(**result)

    except Exception as e:
        logger.error(
            "expenses_endpoint_failed",
            error=str(e),
            state=state,
            municipality_code=municipality_code,
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch expenses: {str(e)}"
        )


@router.get(
    "/suppliers",
    response_model=SupplierResponse,
    summary="Get suppliers from transparency sources",
    description="""
    Fetch government suppliers from multiple transparency sources.

    Returns information about companies and individuals that provide
    goods or services to government entities.
    """,
)
async def get_suppliers(
    state: Optional[str] = Query(None, description="State code (e.g., PE, CE, RJ)"),
    municipality_code: Optional[str] = Query(
        None, description="IBGE municipality code"
    ),
    validate: bool = Query(True, description="Enable data validation"),
):
    """
    Get suppliers from transparency sources.

    Returns supplier information from federal, state, and municipal
    transparency portals with validation.
    """
    try:
        collector = get_transparency_collector()

        result = await collector.collect_suppliers(
            state=state, municipality_code=municipality_code, validate=validate
        )

        logger.info(
            "suppliers_endpoint_accessed",
            total=result["total"],
            sources_count=len(result["sources"]),
            state=state,
            municipality_code=municipality_code,
        )

        return SupplierResponse(**result)

    except Exception as e:
        logger.error(
            "suppliers_endpoint_failed",
            error=str(e),
            state=state,
            municipality_code=municipality_code,
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch suppliers: {str(e)}"
        )


@router.post(
    "/analyze-anomalies",
    response_model=AnomalyAnalysisResponse,
    summary="Analyze contracts for anomalies",
    description="""
    Perform anomaly detection on contract data.

    **Detection Methods:**
    - Value outliers (statistical analysis)
    - Supplier concentration (monopolization detection)
    - Duplicate contracts (similarity matching)

    **Use Cases:**
    - Fraud detection
    - Compliance monitoring
    - Audit support
    """,
)
async def analyze_anomalies(contracts: list[dict]):
    """
    Analyze contracts for anomalies.

    Detects outliers, concentration patterns, and duplicates in contract data
    using statistical and ML-based methods.
    """
    try:
        collector = get_transparency_collector()

        result = await collector.analyze_contracts_for_anomalies(contracts)

        logger.info(
            "anomaly_analysis_endpoint_accessed",
            total_contracts=result["summary"]["total_contracts"],
            risk_score=result["summary"]["risk_score"],
            anomaly_count=result["anomalies"]["outlier_count"],
        )

        return AnomalyAnalysisResponse(**result)

    except Exception as e:
        logger.error(
            "anomaly_analysis_endpoint_failed",
            error=str(e),
            contract_count=len(contracts),
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze anomalies: {str(e)}"
        )


@router.get(
    "/health",
    response_model=HealthReportResponse,
    summary="Check transparency APIs health",
    description="""
    Check health status of all transparency APIs.

    **Monitoring:**
    - Response time tracking
    - Error rate monitoring
    - Availability status
    - Historical performance

    **Use Cases:**
    - System monitoring
    - Incident detection
    - Performance optimization
    """,
)
async def check_health():
    """
    Check health of all transparency APIs.

    Returns comprehensive health status for federal, state, and municipal
    transparency APIs with performance metrics.
    """
    try:
        monitor = get_health_monitor()

        report = await monitor.generate_report()

        logger.info(
            f"Health check endpoint accessed (status: {report.get('overall_status')}, "
            f"healthy: {report.get('healthy_apis', 0)}, total: {report.get('total_apis', 0)})"
        )

        return HealthReportResponse(**report)

    except Exception as e:
        logger.error(f"Health check endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check health: {str(e)}")


@router.get(
    "/apis",
    response_model=AvailableAPIsResponse,
    summary="List available transparency APIs",
    description="""
    List all available transparency APIs in the system.

    **Coverage:**
    - 12 APIs total
    - 6 TCE APIs (state audit courts)
    - 5 CKAN portals (open data)
    - 1 State API (Rondônia)
    - 2500+ municipalities covered
    """,
)
async def list_apis():
    """
    List available transparency APIs.

    Returns all registered transparency APIs with coverage information.
    """
    try:
        apis = registry.list_available_apis()

        logger.info(f"List APIs endpoint accessed (total: {len(apis)})")

        return AvailableAPIsResponse(
            total=len(apis),
            apis=apis,
            description=f"Access to {len(apis)} transparency APIs covering 2500+ Brazilian municipalities",
        )

    except Exception as e:
        logger.error(f"List APIs endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list APIs: {str(e)}")
