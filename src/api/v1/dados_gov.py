"""
API routes for dados.gov.br integration.

This module exposes endpoints for searching and retrieving
data from the Brazilian Open Data Portal.
"""

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field

from src.api.auth import get_current_user
from src.services.dados_gov_service import DadosGovService
from src.tools.dados_gov_api import DadosGovAPIError
from src.tools.dados_gov_models import Dataset, DatasetSearchResult, Organization

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dados-gov")


class DatasetSearchRequest(BaseModel):
    """Request model for dataset search"""

    keywords: Optional[list[str]] = Field(
        None,
        description="Keywords to search for",
        example=["transparência", "gastos", "contratos"],
    )
    organization: Optional[str] = Field(
        None,
        description="Filter by organization",
        example="ministerio-da-saude",
    )
    data_format: Optional[str] = Field(
        None,
        description="Preferred data format",
        example="csv",
    )
    limit: int = Field(
        20,
        ge=1,
        le=100,
        description="Maximum number of results",
    )


class DataAvailabilityResponse(BaseModel):
    """Response model for data availability analysis"""

    topic: str
    total_datasets: int
    analyzed_datasets: int
    organizations: dict[str, int]
    formats: dict[str, int]
    years_covered: list[str]
    geographic_coverage: dict[str, int]
    update_frequency: dict[str, int]


@router.get(
    "/search",
    response_model=DatasetSearchResult,
    summary="Search datasets",
    description="Search for datasets in the Brazilian Open Data Portal",
)
async def search_datasets(
    query: Optional[str] = Query(
        None,
        description="Search query",
        example="educação básica",
    ),
    organization: Optional[str] = Query(
        None,
        description="Filter by organization",
        example="inep",
    ),
    tags: Optional[list[str]] = Query(
        None,
        description="Filter by tags",
        example=["educação", "censo"],
    ),
    format: Optional[str] = Query(
        None,
        description="Filter by data format",
        example="csv",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of results per page",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Pagination offset",
    ),
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Search for datasets in dados.gov.br.

    This endpoint allows searching the Brazilian Open Data Portal
    for datasets matching specific criteria.
    """
    service = DadosGovService()

    try:
        # Use the service to search
        if query or tags:
            keywords = []
            if query:
                keywords.append(query)
            if tags:
                keywords.extend(tags)

            result = await service.search_transparency_datasets(
                keywords=keywords,
                organization=organization,
                data_format=format,
                limit=limit,
            )
        else:
            # Direct API call for browsing without keywords
            client = service.client
            api_result = await client.search_datasets(
                organization=organization,
                format=format,
                limit=limit,
                offset=offset,
            )

            result = DatasetSearchResult(
                count=api_result.get("count", 0),
                results=[Dataset(**ds) for ds in api_result.get("results", [])],
            )

        return result

    except DadosGovAPIError as e:
        logger.error(f"API error: {e}")
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error searching datasets",
        )
    finally:
        await service.close()


@router.get(
    "/dataset/{dataset_id}",
    response_model=Dataset,
    summary="Get dataset details",
    description="Get complete information about a specific dataset",
)
async def get_dataset(
    dataset_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Get detailed information about a dataset.

    Returns complete dataset information including all resources
    and metadata.
    """
    service = DadosGovService()

    try:
        dataset = await service.get_dataset_with_resources(dataset_id)
        return dataset

    except DadosGovAPIError as e:
        logger.error(f"API error: {e}")
        if e.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset '{dataset_id}' not found",
            )
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving dataset",
        )
    finally:
        await service.close()


@router.get(
    "/resource/{resource_id}/url",
    response_model=dict[str, str],
    summary="Get resource download URL",
    description="Get the direct download URL for a dataset resource",
)
async def get_resource_url(
    resource_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Get the download URL for a resource.

    Returns the direct URL to download the resource file.
    """
    service = DadosGovService()

    try:
        url = await service.get_resource_download_url(resource_id)
        return {"resource_id": resource_id, "download_url": url}

    except DadosGovAPIError as e:
        logger.error(f"API error: {e}")
        if e.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Resource '{resource_id}' not found",
            )
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving resource",
        )
    finally:
        await service.close()


@router.get(
    "/organizations",
    response_model=list[Organization],
    summary="List organizations",
    description="List all organizations that publish open data",
)
async def list_organizations(
    limit: int = Query(
        50,
        ge=1,
        le=200,
        description="Maximum number of organizations",
    ),
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    List government organizations.

    Returns a list of all organizations that publish datasets
    on the open data portal, sorted by number of datasets.
    """
    service = DadosGovService()

    try:
        organizations = await service.list_government_organizations()
        return organizations[:limit]

    except DadosGovAPIError as e:
        logger.error(f"API error: {e}")
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error listing organizations",
        )
    finally:
        await service.close()


@router.post(
    "/search/transparency",
    response_model=DatasetSearchResult,
    summary="Search transparency datasets",
    description="Search for transparency-related datasets with filters",
)
async def search_transparency_datasets(
    request: DatasetSearchRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Search for transparency-related datasets.

    This endpoint provides a specialized search for datasets
    related to government transparency, spending, and accountability.
    """
    service = DadosGovService()

    try:
        result = await service.search_transparency_datasets(
            keywords=request.keywords,
            organization=request.organization,
            data_format=request.data_format,
            limit=request.limit,
        )
        return result

    except DadosGovAPIError as e:
        logger.error(f"API error: {e}")
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error searching transparency datasets",
        )
    finally:
        await service.close()


@router.get(
    "/analyze/{topic}",
    response_model=DataAvailabilityResponse,
    summary="Analyze data availability",
    description="Analyze what data is available for a specific topic",
)
async def analyze_data_availability(
    topic: str = Path(
        ...,
        description="Topic to analyze",
        example="educação",
    ),
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Analyze data availability for a topic.

    This endpoint analyzes what datasets are available for a specific
    topic, including formats, organizations, and temporal coverage.
    """
    service = DadosGovService()

    try:
        analysis = await service.analyze_data_availability(topic)
        return DataAvailabilityResponse(**analysis)

    except DadosGovAPIError as e:
        logger.error(f"API error: {e}")
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error analyzing data availability",
        )
    finally:
        await service.close()


@router.get(
    "/spending-data",
    response_model=list[Dataset],
    summary="Find government spending data",
    description="Find datasets related to government spending and expenses",
)
async def find_spending_data(
    year: Optional[int] = Query(
        None,
        ge=2000,
        le=2030,
        description="Filter by year",
    ),
    state: Optional[str] = Query(
        None,
        description="Filter by state code",
        example="SP",
    ),
    city: Optional[str] = Query(
        None,
        description="Filter by city name",
        example="São Paulo",
    ),
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Find government spending datasets.

    Search for datasets containing information about government
    expenses, payments, and budget execution.
    """
    service = DadosGovService()

    try:
        datasets = await service.find_government_spending_data(
            year=year,
            state=state,
            city=city,
        )
        return datasets

    except DadosGovAPIError as e:
        logger.error(f"API error: {e}")
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error finding spending data",
        )
    finally:
        await service.close()


@router.get(
    "/procurement-data",
    response_model=list[Dataset],
    summary="Find procurement data",
    description="Find datasets related to public procurement and contracts",
)
async def find_procurement_data(
    organization: Optional[str] = Query(
        None,
        description="Filter by organization",
    ),
    modality: Optional[str] = Query(
        None,
        description="Procurement modality",
        example="pregão",
    ),
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Find procurement-related datasets.

    Search for datasets containing information about public
    tenders, contracts, and procurement processes.
    """
    service = DadosGovService()

    try:
        datasets = await service.find_procurement_data(
            organization=organization,
            modality=modality,
        )
        return datasets

    except DadosGovAPIError as e:
        logger.error(f"API error: {e}")
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error finding procurement data",
        )
    finally:
        await service.close()
