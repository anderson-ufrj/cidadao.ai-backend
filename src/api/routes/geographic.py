"""
API routes for geographic data endpoints.
Provides Brazilian geographic data and boundaries for map visualizations.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.lampiao import LampiaoAgent, RegionType
from src.core.auth import get_current_user
from src.core.database import get_db
from src.core.cache import CacheService, CacheKey
from src.core.rate_limit import RateLimiter, rate_limit
from src.core import get_logger
from src.services.agent_lazy_loader import AgentLazyLoader
from src.agents.deodoro import AgentContext, AgentMessage
from src.core.exceptions import NotFoundError


logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/geo", tags=["geographic"])

# Rate limiter for geographic endpoints
geo_rate_limiter = RateLimiter(calls=50, period=60)  # 50 calls per minute

# Cache service
cache_service = CacheService()

# Lazy load agents
agent_loader = AgentLazyLoader()


class BrazilianRegion(BaseModel):
    """Brazilian region model."""
    
    id: str = Field(..., description="Region identifier (e.g., 'SP' for São Paulo)")
    name: str = Field(..., description="Region name")
    type: RegionType = Field(..., description="Region type")
    parent_id: Optional[str] = Field(None, description="Parent region ID")
    geometry: Optional[Dict[str, Any]] = Field(None, description="GeoJSON geometry")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    
    
class GeographicBoundary(BaseModel):
    """Geographic boundary model for map rendering."""
    
    type: str = Field("FeatureCollection", description="GeoJSON type")
    features: List[Dict[str, Any]] = Field(..., description="GeoJSON features")
    bbox: Optional[List[float]] = Field(None, description="Bounding box [min_lng, min_lat, max_lng, max_lat]")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Collection properties")


class RegionalDataPoint(BaseModel):
    """Data point for a specific region."""
    
    region_id: str
    region_name: str
    value: float
    normalized_value: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GeographicDataResponse(BaseModel):
    """Response model for geographic data."""
    
    data_type: str
    region_type: RegionType
    data_points: List[RegionalDataPoint]
    summary_statistics: Dict[str, float]
    timestamp: datetime
    cache_expires: datetime


# Brazilian states GeoJSON (simplified boundaries for demo)
BRAZIL_STATES_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": "SP",
            "properties": {
                "name": "São Paulo",
                "region": "Sudeste",
                "population": 46649132,
                "area_km2": 248219.627,
                "capital": "São Paulo",
                "iso_code": "BR-SP"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-53.089, -25.650],
                    [-53.089, -19.780],
                    [-44.161, -19.780],
                    [-44.161, -25.650],
                    [-53.089, -25.650]
                ]]
            }
        },
        {
            "type": "Feature",
            "id": "RJ",
            "properties": {
                "name": "Rio de Janeiro",
                "region": "Sudeste",
                "population": 17463349,
                "area_km2": 43780.157,
                "capital": "Rio de Janeiro",
                "iso_code": "BR-RJ"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-44.889, -23.369],
                    [-44.889, -20.763],
                    [-40.958, -20.763],
                    [-40.958, -23.369],
                    [-44.889, -23.369]
                ]]
            }
        },
        {
            "type": "Feature",
            "id": "MG",
            "properties": {
                "name": "Minas Gerais",
                "region": "Sudeste",
                "population": 21411923,
                "area_km2": 586521.123,
                "capital": "Belo Horizonte",
                "iso_code": "BR-MG"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-51.046, -22.921],
                    [-51.046, -14.235],
                    [-39.861, -14.235],
                    [-39.861, -22.921],
                    [-51.046, -22.921]
                ]]
            }
        },
        # Add more states as needed...
    ]
}


# Brazilian regions (macro-regions)
BRAZIL_REGIONS = {
    "norte": {
        "name": "Norte",
        "states": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
        "center": {"lat": -3.4168, "lng": -60.0217}
    },
    "nordeste": {
        "name": "Nordeste", 
        "states": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
        "center": {"lat": -12.9718, "lng": -38.5014}
    },
    "centro_oeste": {
        "name": "Centro-Oeste",
        "states": ["DF", "GO", "MT", "MS"],
        "center": {"lat": -15.7801, "lng": -55.9292}
    },
    "sudeste": {
        "name": "Sudeste",
        "states": ["ES", "MG", "RJ", "SP"],
        "center": {"lat": -20.6547, "lng": -43.7662}
    },
    "sul": {
        "name": "Sul",
        "states": ["PR", "RS", "SC"],
        "center": {"lat": -27.5949, "lng": -50.8215}
    }
}


@router.get("/boundaries/{region_type}", response_model=GeographicBoundary)
@rate_limit(geo_rate_limiter)
async def get_geographic_boundaries(
    region_type: RegionType = Path(..., description="Type of region boundaries to retrieve"),
    simplified: bool = Query(True, description="Return simplified boundaries for performance"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get geographic boundaries for Brazilian regions.
    
    Returns GeoJSON data suitable for rendering maps in the frontend.
    Currently supports state-level boundaries with plans to add municipalities.
    """
    try:
        cache_key = CacheKey(
            prefix="geo_boundaries",
            params={"region_type": region_type.value, "simplified": simplified}
        )
        
        # Try to get from cache
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            logger.info("Returning cached geographic boundaries", region_type=region_type.value)
            return GeographicBoundary(**cached_data)
        
        # Generate boundaries based on region type
        if region_type == RegionType.STATE:
            boundaries = BRAZIL_STATES_GEOJSON
            
        elif region_type == RegionType.MACRO_REGION:
            # Generate macro-region boundaries by combining states
            features = []
            for region_id, region_info in BRAZIL_REGIONS.items():
                features.append({
                    "type": "Feature",
                    "id": region_id,
                    "properties": {
                        "name": region_info["name"],
                        "states": region_info["states"],
                        "center": region_info["center"]
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]  # Placeholder
                    }
                })
            
            boundaries = {
                "type": "FeatureCollection",
                "features": features
            }
            
        else:
            raise HTTPException(
                status_code=501,
                detail=f"Boundaries for {region_type.value} not yet implemented"
            )
        
        # Calculate bounding box for Brazil
        boundaries["bbox"] = [-73.9872, -33.7506, -34.7299, 5.2718]
        
        result = GeographicBoundary(
            type=boundaries["type"],
            features=boundaries["features"],
            bbox=boundaries.get("bbox"),
            properties={
                "region_type": region_type.value,
                "simplified": simplified,
                "total_features": len(boundaries["features"])
            }
        )
        
        # Cache the result
        await cache_service.set(cache_key, result.dict(), expire=86400)  # 24 hours
        
        return result
        
    except Exception as e:
        logger.error(
            "Failed to retrieve geographic boundaries",
            region_type=region_type.value,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to retrieve boundaries: {str(e)}")


@router.get("/regions", response_model=List[BrazilianRegion])
@rate_limit(geo_rate_limiter)
async def list_regions(
    region_type: RegionType = Query(RegionType.STATE, description="Type of regions to list"),
    parent_id: Optional[str] = Query(None, description="Filter by parent region"),
    search: Optional[str] = Query(None, description="Search regions by name"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    List Brazilian regions with their metadata.
    
    Useful for populating dropdown menus and region selectors in the frontend.
    """
    try:
        # Get Lampião agent for region data
        lampiao_agent = await agent_loader.get_agent("lampiao")
        if not lampiao_agent:
            lampiao_agent = LampiaoAgent()
            await lampiao_agent.initialize()
        
        regions = []
        
        if region_type == RegionType.STATE:
            # Get all states from Lampião
            for state_id, state_info in lampiao_agent.brazil_regions.items():
                if search and search.lower() not in state_info["name"].lower():
                    continue
                    
                regions.append(BrazilianRegion(
                    id=state_id,
                    name=state_info["name"],
                    type=RegionType.STATE,
                    parent_id=None,
                    properties={
                        "region": state_info["region"],
                        "capital": state_info["capital"],
                        "area_km2": state_info["area"]
                    }
                ))
                
        elif region_type == RegionType.MACRO_REGION:
            # Get macro regions
            for region_id, region_info in BRAZIL_REGIONS.items():
                if search and search.lower() not in region_info["name"].lower():
                    continue
                    
                regions.append(BrazilianRegion(
                    id=region_id,
                    name=region_info["name"],
                    type=RegionType.MACRO_REGION,
                    parent_id=None,
                    properties={
                        "states": region_info["states"],
                        "center": region_info["center"]
                    }
                ))
        
        # Sort by name
        regions.sort(key=lambda r: r.name)
        
        return regions
        
    except Exception as e:
        logger.error(
            "Failed to list regions",
            region_type=region_type.value,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to list regions: {str(e)}")


@router.get("/regions/{region_id}", response_model=BrazilianRegion)
@rate_limit(geo_rate_limiter)
async def get_region_details(
    region_id: str = Path(..., description="Region identifier"),
    include_geometry: bool = Query(False, description="Include GeoJSON geometry"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get detailed information about a specific region.
    
    Includes metadata and optionally the geographic boundary geometry.
    """
    try:
        # Get Lampião agent
        lampiao_agent = await agent_loader.get_agent("lampiao")
        if not lampiao_agent:
            lampiao_agent = LampiaoAgent()
            await lampiao_agent.initialize()
        
        # Check if it's a state
        if region_id in lampiao_agent.brazil_regions:
            state_info = lampiao_agent.brazil_regions[region_id]
            
            geometry = None
            if include_geometry:
                # Find geometry in GeoJSON
                for feature in BRAZIL_STATES_GEOJSON["features"]:
                    if feature["id"] == region_id:
                        geometry = feature["geometry"]
                        break
            
            return BrazilianRegion(
                id=region_id,
                name=state_info["name"],
                type=RegionType.STATE,
                parent_id=None,
                geometry=geometry,
                properties={
                    "region": state_info["region"],
                    "capital": state_info["capital"],
                    "area_km2": state_info["area"],
                    "iso_code": f"BR-{region_id}"
                }
            )
            
        # Check if it's a macro region
        elif region_id in BRAZIL_REGIONS:
            region_info = BRAZIL_REGIONS[region_id]
            
            return BrazilianRegion(
                id=region_id,
                name=region_info["name"],
                type=RegionType.MACRO_REGION,
                parent_id=None,
                geometry=None,  # TODO: Implement combined geometry
                properties={
                    "states": region_info["states"],
                    "center": region_info["center"],
                    "state_count": len(region_info["states"])
                }
            )
            
        else:
            raise NotFoundError(f"Region '{region_id}' not found")
            
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Region '{region_id}' not found")
    except Exception as e:
        logger.error(
            "Failed to get region details",
            region_id=region_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to get region details: {str(e)}")


@router.get("/data/{metric}", response_model=GeographicDataResponse)
@rate_limit(geo_rate_limiter)
async def get_geographic_data(
    metric: str = Path(..., description="Metric to retrieve (e.g., contracts, spending)"),
    region_type: RegionType = Query(RegionType.STATE, description="Geographic aggregation level"),
    normalize: bool = Query(False, description="Normalize by population or area"),
    time_range: str = Query("30d", description="Time range: 7d, 30d, 90d, 1y"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get data aggregated by geographic regions.
    
    This endpoint aggregates various metrics by geographic regions,
    perfect for creating choropleth maps and regional comparisons.
    """
    try:
        logger.info(
            "Retrieving geographic data",
            metric=metric,
            region_type=region_type.value,
            normalize=normalize,
        )
        
        # Get Lampião agent for regional analysis
        lampiao_agent = await agent_loader.get_agent("lampiao")
        if not lampiao_agent:
            lampiao_agent = LampiaoAgent()
            await lampiao_agent.initialize()
        
        # Create context
        context = AgentContext(
            investigation_id=f"geo_data_{datetime.utcnow().timestamp()}",
            user_id=current_user["id"],
            session_id=current_user.get("session_id", "default"),
            metadata={
                "metric": metric,
                "region_type": region_type.value,
                "time_range": time_range
            }
        )
        
        # Request regional analysis
        message = AgentMessage(
            role="user",
            content=f"Analyze {metric} by region",
            data={
                "metric": metric,
                "region_type": region_type.value,
                "normalize": normalize,
                "time_range": time_range
            }
        )
        
        response = await lampiao_agent.process(message, context)
        
        if not response.success:
            raise HTTPException(status_code=500, detail="Regional analysis failed")
        
        regional_data = response.data
        
        # Convert to API response format
        data_points = []
        for metric_data in regional_data.metrics:
            data_points.append(RegionalDataPoint(
                region_id=metric_data.region_id,
                region_name=metric_data.region_name,
                value=metric_data.value,
                normalized_value=metric_data.normalized_value if normalize else None,
                metadata={
                    "rank": metric_data.rank,
                    "percentile": metric_data.percentile,
                    **metric_data.metadata
                }
            ))
        
        cache_ttl = 3600  # 1 hour
        
        return GeographicDataResponse(
            data_type=metric,
            region_type=region_type,
            data_points=data_points,
            summary_statistics=regional_data.statistics,
            timestamp=datetime.utcnow(),
            cache_expires=datetime.utcnow() + timedelta(seconds=cache_ttl)
        )
        
    except Exception as e:
        logger.error(
            "Failed to retrieve geographic data",
            metric=metric,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to retrieve geographic data: {str(e)}")


@router.get("/coordinates/{region_id}")
@rate_limit(geo_rate_limiter)
async def get_region_coordinates(
    region_id: str = Path(..., description="Region identifier"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get center coordinates for a region.
    
    Useful for placing markers or centering maps on specific regions.
    """
    try:
        # Predefined coordinates for major cities/states
        coordinates = {
            # State capitals
            "SP": {"lat": -23.5505, "lng": -46.6333, "name": "São Paulo"},
            "RJ": {"lat": -22.9068, "lng": -43.1729, "name": "Rio de Janeiro"},
            "MG": {"lat": -19.9167, "lng": -43.9345, "name": "Belo Horizonte"},
            "BA": {"lat": -12.9714, "lng": -38.5014, "name": "Salvador"},
            "RS": {"lat": -30.0346, "lng": -51.2177, "name": "Porto Alegre"},
            "PR": {"lat": -25.4290, "lng": -49.2710, "name": "Curitiba"},
            "PE": {"lat": -8.0476, "lng": -34.8770, "name": "Recife"},
            "CE": {"lat": -3.7172, "lng": -38.5433, "name": "Fortaleza"},
            "PA": {"lat": -1.4558, "lng": -48.4902, "name": "Belém"},
            "MA": {"lat": -2.5307, "lng": -44.3068, "name": "São Luís"},
            "GO": {"lat": -16.6869, "lng": -49.2648, "name": "Goiânia"},
            "DF": {"lat": -15.7801, "lng": -47.9292, "name": "Brasília"},
            # Add more as needed...
        }
        
        # Check macro regions
        if region_id in BRAZIL_REGIONS:
            region = BRAZIL_REGIONS[region_id]
            return {
                "region_id": region_id,
                "name": region["name"],
                "coordinates": region["center"],
                "type": "macro_region"
            }
        
        # Check states
        if region_id in coordinates:
            coord = coordinates[region_id]
            return {
                "region_id": region_id,
                "name": coord["name"],
                "coordinates": {"lat": coord["lat"], "lng": coord["lng"]},
                "type": "state_capital"
            }
        
        raise HTTPException(status_code=404, detail=f"Coordinates not found for region '{region_id}'")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get region coordinates",
            region_id=region_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to get coordinates: {str(e)}")