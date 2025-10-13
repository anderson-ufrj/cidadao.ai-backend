"""
Federal APIs REST Endpoints

Exposes Brazilian government APIs as REST endpoints.
Generates Prometheus metrics automatically on each call.

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brasil
Date: 2025-10-13
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.transparency_apis.federal_apis.datasus_client import DataSUSClient
from src.services.transparency_apis.federal_apis.ibge_client import IBGEClient
from src.services.transparency_apis.federal_apis.inep_client import INEPClient

router = APIRouter(prefix="/api/v1/federal", tags=["Federal APIs"])


# ==================== REQUEST MODELS ====================


class IBGEMunicipalitiesRequest(BaseModel):
    """Request model for IBGE municipalities."""

    state_code: str = Field(..., description="State code (2 digits)", example="33")


class IBGEPopulationRequest(BaseModel):
    """Request model for IBGE population data."""

    state_code: str | None = Field(
        None, description="State code (2 digits)", example="33"
    )
    municipality_code: str | None = Field(
        None, description="Municipality code", example="3304557"
    )


class DataSUSSearchRequest(BaseModel):
    """Request model for DataSUS search."""

    query: str = Field(..., description="Search query", example="saúde")
    limit: int = Field(10, ge=1, le=100, description="Max results")


class DataSUSIndicatorsRequest(BaseModel):
    """Request model for DataSUS health indicators."""

    state_code: str | None = Field(None, description="State code (UF)", example="RJ")


class INEPSearchRequest(BaseModel):
    """Request model for INEP institution search."""

    state: str | None = Field(None, description="State code (UF)", example="RJ")
    city: str | None = Field(None, description="City name", example="Rio de Janeiro")
    name: str | None = Field(None, description="Institution name", example="UFRJ")
    limit: int = Field(20, ge=1, le=100, description="Max results")
    page: int = Field(1, ge=1, description="Page number")


class INEPIndicatorsRequest(BaseModel):
    """Request model for INEP education indicators."""

    state: str | None = Field(None, description="State code (UF)", example="RJ")
    year: int | None = Field(None, description="Year", example=2023)


# ==================== IBGE ENDPOINTS ====================


@router.get(
    "/ibge/states",
    summary="Get Brazilian States",
    description="Retrieve all Brazilian states from IBGE API",
)
async def get_ibge_states() -> dict[str, Any]:
    """Get all Brazilian states."""
    try:
        async with IBGEClient() as client:
            states = await client.get_states()
            return {"success": True, "total": len(states), "data": states}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/ibge/municipalities",
    summary="Get Municipalities by State",
    description="Retrieve municipalities for a specific state",
)
async def get_ibge_municipalities(request: IBGEMunicipalitiesRequest) -> dict[str, Any]:
    """Get municipalities for a state."""
    try:
        async with IBGEClient() as client:
            municipalities = await client.get_municipalities(
                state_id=request.state_code
            )
            return {
                "success": True,
                "state_code": request.state_code,
                "total": len(municipalities),
                "data": municipalities,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/ibge/population",
    summary="Get Population Data",
    description="Retrieve population data from IBGE",
)
async def get_ibge_population(request: IBGEPopulationRequest) -> dict[str, Any]:
    """Get population data."""
    try:
        async with IBGEClient() as client:
            population = await client.get_population(
                state_code=request.state_code,
                municipality_code=request.municipality_code,
            )
            return {
                "success": True,
                "state_code": request.state_code,
                "municipality_code": request.municipality_code,
                "data": population,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== DATASUS ENDPOINTS ====================


@router.post(
    "/datasus/search",
    summary="Search DataSUS Datasets",
    description="Search health datasets in DataSUS",
)
async def search_datasus_datasets(request: DataSUSSearchRequest) -> dict[str, Any]:
    """Search DataSUS datasets."""
    try:
        async with DataSUSClient() as client:
            results = await client.search_datasets(
                query=request.query, limit=request.limit
            )
            return {"success": True, "query": request.query, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/datasus/indicators",
    summary="Get Health Indicators",
    description="Retrieve health indicators from DataSUS",
)
async def get_datasus_indicators(request: DataSUSIndicatorsRequest) -> dict[str, Any]:
    """Get health indicators."""
    try:
        async with DataSUSClient() as client:
            indicators = await client.get_health_indicators(
                state_code=request.state_code
            )
            return {
                "success": True,
                "state_code": request.state_code,
                "data": indicators,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== INEP ENDPOINTS ====================


@router.post(
    "/inep/search-institutions",
    summary="Search Educational Institutions",
    description="Search institutions in INEP database",
)
async def search_inep_institutions(request: INEPSearchRequest) -> dict[str, Any]:
    """Search educational institutions."""
    try:
        async with INEPClient() as client:
            results = await client.search_institutions(
                state=request.state,
                city=request.city,
                name=request.name,
                limit=request.limit,
                page=request.page,
            )
            return {
                "success": True,
                "filters": {
                    "state": request.state,
                    "city": request.city,
                    "name": request.name,
                },
                "pagination": {"page": request.page, "limit": request.limit},
                "data": results,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/inep/indicators",
    summary="Get Education Indicators",
    description="Retrieve education indicators from INEP",
)
async def get_inep_indicators(request: INEPIndicatorsRequest) -> dict[str, Any]:
    """Get education indicators."""
    try:
        async with INEPClient() as client:
            indicators = await client.get_education_indicators(
                state=request.state, year=request.year
            )
            return {
                "success": True,
                "state": request.state,
                "year": request.year,
                "data": indicators,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
