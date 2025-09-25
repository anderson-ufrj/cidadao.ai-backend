"""
Module: api.routes.admin.ip_whitelist
Description: Admin routes for managing IP whitelist
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import ipaddress

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, field_validator

from src.core import get_logger
from src.api.dependencies import require_admin, get_db
from src.services.ip_whitelist_service import ip_whitelist_service, IPWhitelist
from src.core.config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/ip-whitelist", tags=["Admin - IP Whitelist"])


class IPWhitelistRequest(BaseModel):
    """Request to add IP to whitelist."""
    ip_address: str = Field(..., description="IP address or CIDR range")
    description: Optional[str] = Field(None, description="Description of the IP")
    environment: str = Field(default="production", description="Environment")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Validate IP address or CIDR."""
        try:
            # Try as single IP
            ipaddress.ip_address(v)
            return v
        except ValueError:
            # Try as CIDR
            try:
                ipaddress.ip_network(v, strict=False)
                return v
            except ValueError:
                raise ValueError(f"Invalid IP address or CIDR: {v}")
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v


class IPWhitelistUpdateRequest(BaseModel):
    """Request to update IP whitelist entry."""
    active: Optional[bool] = None
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class IPWhitelistResponse(BaseModel):
    """IP whitelist entry response."""
    id: str
    ip_address: str
    description: Optional[str]
    environment: str
    active: bool
    is_cidr: bool
    cidr_prefix: Optional[int]
    created_by: str
    created_at: datetime
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]
    is_expired: bool
    
    @classmethod
    def from_model(cls, model: IPWhitelist) -> "IPWhitelistResponse":
        """Create response from model."""
        return cls(
            id=model.id,
            ip_address=model.ip_address,
            description=model.description,
            environment=model.environment,
            active=model.active,
            is_cidr=model.is_cidr,
            cidr_prefix=model.cidr_prefix,
            created_by=model.created_by,
            created_at=model.created_at,
            expires_at=model.expires_at,
            metadata=model.metadata,
            is_expired=model.is_expired()
        )


@router.post("/add", response_model=IPWhitelistResponse)
async def add_ip_to_whitelist(
    request: IPWhitelistRequest,
    admin_user=Depends(require_admin),
    db=Depends(get_db)
):
    """
    Add IP address or CIDR range to whitelist.
    
    Requires admin privileges.
    """
    try:
        is_cidr = "/" in request.ip_address
        
        entry = await ip_whitelist_service.add_ip(
            session=db,
            ip_address=request.ip_address,
            created_by=admin_user.get("email", "admin"),
            description=request.description,
            environment=request.environment,
            expires_at=request.expires_at,
            is_cidr=is_cidr,
            metadata=request.metadata
        )
        
        logger.info(
            "admin_ip_whitelist_added",
            admin=admin_user.get("email"),
            ip=request.ip_address,
            environment=request.environment
        )
        
        return IPWhitelistResponse.from_model(entry)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "admin_ip_whitelist_add_error",
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add IP to whitelist"
        )


@router.delete("/remove/{ip_address}")
async def remove_ip_from_whitelist(
    ip_address: str,
    environment: str = Query(default="production"),
    admin_user=Depends(require_admin),
    db=Depends(get_db)
):
    """
    Remove IP from whitelist.
    
    Requires admin privileges.
    """
    removed = await ip_whitelist_service.remove_ip(
        session=db,
        ip_address=ip_address,
        environment=environment
    )
    
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP not found in whitelist: {ip_address}"
        )
    
    logger.info(
        "admin_ip_whitelist_removed",
        admin=admin_user.get("email"),
        ip=ip_address,
        environment=environment
    )
    
    return {"status": "removed", "ip_address": ip_address}


@router.get("/list", response_model=List[IPWhitelistResponse])
async def list_whitelisted_ips(
    environment: str = Query(default="production"),
    include_expired: bool = Query(default=False),
    admin_user=Depends(require_admin),
    db=Depends(get_db)
):
    """
    List all whitelisted IPs.
    
    Requires admin privileges.
    """
    entries = await ip_whitelist_service.list_ips(
        session=db,
        environment=environment,
        include_expired=include_expired
    )
    
    return [IPWhitelistResponse.from_model(entry) for entry in entries]


@router.get("/check/{ip_address}")
async def check_ip_whitelist(
    ip_address: str,
    environment: str = Query(default="production"),
    admin_user=Depends(require_admin),
    db=Depends(get_db)
):
    """
    Check if IP is whitelisted.
    
    Requires admin privileges.
    """
    try:
        # Validate IP
        ipaddress.ip_address(ip_address)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid IP address format"
        )
    
    is_whitelisted = await ip_whitelist_service.check_ip(
        session=db,
        ip_address=ip_address,
        environment=environment
    )
    
    return {
        "ip_address": ip_address,
        "environment": environment,
        "is_whitelisted": is_whitelisted
    }


@router.put("/update/{ip_address}", response_model=IPWhitelistResponse)
async def update_whitelist_entry(
    ip_address: str,
    request: IPWhitelistUpdateRequest,
    environment: str = Query(default="production"),
    admin_user=Depends(require_admin),
    db=Depends(get_db)
):
    """
    Update whitelist entry.
    
    Requires admin privileges.
    """
    entry = await ip_whitelist_service.update_ip(
        session=db,
        ip_address=ip_address,
        environment=environment,
        active=request.active,
        description=request.description,
        expires_at=request.expires_at,
        metadata=request.metadata
    )
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP not found in whitelist: {ip_address}"
        )
    
    logger.info(
        "admin_ip_whitelist_updated",
        admin=admin_user.get("email"),
        ip=ip_address,
        active=entry.active
    )
    
    return IPWhitelistResponse.from_model(entry)


@router.post("/cleanup")
async def cleanup_expired_entries(
    environment: Optional[str] = None,
    admin_user=Depends(require_admin),
    db=Depends(get_db)
):
    """
    Remove expired whitelist entries.
    
    Requires admin privileges.
    """
    count = await ip_whitelist_service.cleanup_expired(
        session=db,
        environment=environment
    )
    
    logger.info(
        "admin_ip_whitelist_cleanup",
        admin=admin_user.get("email"),
        removed=count,
        environment=environment
    )
    
    return {
        "status": "cleaned",
        "removed_count": count,
        "environment": environment
    }


@router.post("/initialize-defaults")
async def initialize_default_whitelist(
    admin_user=Depends(require_admin),
    db=Depends(get_db)
):
    """
    Initialize default whitelist entries for current environment.
    
    Requires admin privileges.
    """
    count = await ip_whitelist_service.initialize_defaults(
        session=db,
        created_by=admin_user.get("email", "admin")
    )
    
    logger.info(
        "admin_ip_whitelist_defaults_initialized",
        admin=admin_user.get("email"),
        count=count,
        environment=settings.app_env
    )
    
    return {
        "status": "initialized",
        "added_count": count,
        "environment": settings.app_env,
        "defaults": ip_whitelist_service.get_default_whitelist()
    }


@router.get("/stats")
async def get_whitelist_stats(
    admin_user=Depends(require_admin),
    db=Depends(get_db)
):
    """
    Get whitelist statistics.
    
    Requires admin privileges.
    """
    environments = ["development", "staging", "production"]
    stats = {}
    
    for env in environments:
        entries = await ip_whitelist_service.list_ips(
            session=db,
            environment=env,
            include_expired=True
        )
        
        active = sum(1 for e in entries if e.active and not e.is_expired())
        expired = sum(1 for e in entries if e.is_expired())
        cidr_ranges = sum(1 for e in entries if e.is_cidr)
        
        stats[env] = {
            "total": len(entries),
            "active": active,
            "expired": expired,
            "inactive": sum(1 for e in entries if not e.active),
            "cidr_ranges": cidr_ranges,
            "single_ips": len(entries) - cidr_ranges
        }
    
    return {
        "statistics": stats,
        "current_environment": settings.app_env
    }