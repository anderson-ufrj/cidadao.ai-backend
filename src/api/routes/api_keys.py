"""
Module: api.routes.api_keys
Description: API routes for API key management
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field

from src.api.auth import User
from src.api.dependencies import get_db, require_admin
from src.core import get_logger
from src.models.api_key import APIKeyTier
from src.services.api_key_service import APIKeyService

logger = get_logger(__name__)

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


class CreateAPIKeyRequest(BaseModel):
    """Request model for creating API key."""

    name: str = Field(..., description="Key name/description")
    client_id: str = Field(..., description="Client identifier")
    client_name: str | None = Field(None, description="Client display name")
    client_email: EmailStr | None = Field(None, description="Client email")
    tier: APIKeyTier = Field(APIKeyTier.FREE, description="API key tier")
    expires_in_days: int | None = Field(
        None, ge=1, le=365, description="Days until expiration"
    )
    rotation_period_days: int = Field(
        90, ge=0, le=365, description="Rotation period (0=disabled)"
    )
    allowed_ips: list[str] | None = Field(None, description="Allowed IP addresses")
    allowed_origins: list[str] | None = Field(None, description="Allowed CORS origins")
    scopes: list[str] | None = Field(None, description="API scopes/permissions")
    metadata: dict | None = Field(None, description="Additional metadata")


class APIKeyResponse(BaseModel):
    """Response model for API key."""

    id: str
    name: str
    key_prefix: str
    status: str
    tier: str
    client_id: str
    client_name: str | None
    expires_at: datetime | None
    last_used_at: datetime | None
    is_active: bool
    needs_rotation: bool
    rate_limits: dict
    total_requests: int
    created_at: datetime


class APIKeyCreateResponse(APIKeyResponse):
    """Response with the actual key (only shown once)."""

    api_key: str = Field(..., description="The actual API key (save this!)")


class UpdateRateLimitsRequest(BaseModel):
    """Request model for updating rate limits."""

    per_minute: int | None = Field(None, ge=0, description="Requests per minute")
    per_hour: int | None = Field(None, ge=0, description="Requests per hour")
    per_day: int | None = Field(None, ge=0, description="Requests per day")


@router.post("", response_model=APIKeyCreateResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    current_user: User = Depends(require_admin),
) -> APIKeyCreateResponse:
    """
    Create a new API key.

    **Note**: The API key is only shown once. Save it securely!

    Requires admin privileges.
    """
    service = APIKeyService(db)

    try:
        api_key, plain_key = await service.create_api_key(
            name=request.name,
            client_id=request.client_id,
            client_name=request.client_name,
            client_email=request.client_email,
            tier=request.tier,
            expires_in_days=request.expires_in_days,
            rotation_period_days=request.rotation_period_days,
            allowed_ips=request.allowed_ips,
            allowed_origins=request.allowed_origins,
            scopes=request.scopes,
            metadata=request.metadata,
        )

        logger.info(
            "api_key_created_via_api",
            user=current_user.email,
            client_id=request.client_id,
            key_id=str(api_key.id),
        )

        return APIKeyCreateResponse(**api_key.to_dict(), api_key=plain_key)

    except Exception as e:
        logger.error("api_key_creation_failed", user=current_user.email, error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to create API key: {str(e)}"
        )


@router.get("/{api_key_id}", response_model=APIKeyResponse)
async def get_api_key(
    api_key_id: str, db=Depends(get_db), current_user: User = Depends(require_admin)
) -> APIKeyResponse:
    """
    Get API key details.

    Requires admin privileges.
    """
    service = APIKeyService(db)

    api_key = await service.get_by_id(api_key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail=f"API key {api_key_id} not found")

    return APIKeyResponse(**api_key.to_dict())


@router.get("/client/{client_id}", response_model=list[APIKeyResponse])
async def get_client_keys(
    client_id: str,
    include_inactive: bool = Query(False, description="Include inactive keys"),
    db=Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[APIKeyResponse]:
    """
    Get all API keys for a client.

    Requires admin privileges.
    """
    service = APIKeyService(db)

    api_keys = await service.get_by_client(client_id, include_inactive)

    return [APIKeyResponse(**key.to_dict()) for key in api_keys]


@router.post("/{api_key_id}/rotate", response_model=APIKeyCreateResponse)
async def rotate_api_key(
    api_key_id: str,
    background_tasks: BackgroundTasks,
    reason: str = Query(..., description="Rotation reason"),
    grace_period_hours: int = Query(
        24, ge=1, le=168, description="Grace period in hours"
    ),
    db=Depends(get_db),
    current_user: User = Depends(require_admin),
) -> APIKeyCreateResponse:
    """
    Rotate an API key.

    The old key will remain valid for the grace period.

    **Note**: The new API key is only shown once. Save it securely!

    Requires admin privileges.
    """
    service = APIKeyService(db)

    try:
        api_key, new_plain_key = await service.rotate_api_key(
            api_key_id=api_key_id,
            reason=reason,
            initiated_by=current_user.email,
            grace_period_hours=grace_period_hours,
        )

        logger.info(
            "api_key_rotated_via_api",
            user=current_user.email,
            key_id=api_key_id,
            reason=reason,
        )

        return APIKeyCreateResponse(**api_key.to_dict(), api_key=new_plain_key)

    except Exception as e:
        logger.error(
            "api_key_rotation_failed",
            user=current_user.email,
            key_id=api_key_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to rotate API key: {str(e)}"
        )


@router.delete("/{api_key_id}")
async def revoke_api_key(
    api_key_id: str,
    reason: str = Query(..., description="Revocation reason"),
    db=Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """
    Revoke an API key.

    The key will be immediately invalidated.

    Requires admin privileges.
    """
    service = APIKeyService(db)

    try:
        api_key = await service.revoke_api_key(
            api_key_id=api_key_id, reason=reason, revoked_by=current_user.email
        )

        logger.warning(
            "api_key_revoked_via_api",
            user=current_user.email,
            key_id=api_key_id,
            reason=reason,
        )

        return {
            "message": "API key revoked successfully",
            "api_key_id": api_key_id,
            "status": api_key.status,
        }

    except Exception as e:
        logger.error(
            "api_key_revocation_failed",
            user=current_user.email,
            key_id=api_key_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to revoke API key: {str(e)}"
        )


@router.put("/{api_key_id}/rate-limits", response_model=APIKeyResponse)
async def update_rate_limits(
    api_key_id: str,
    request: UpdateRateLimitsRequest,
    db=Depends(get_db),
    current_user: User = Depends(require_admin),
) -> APIKeyResponse:
    """
    Update custom rate limits for an API key.

    Set to null to use tier defaults.

    Requires admin privileges.
    """
    service = APIKeyService(db)

    try:
        api_key = await service.update_rate_limits(
            api_key_id=api_key_id,
            per_minute=request.per_minute,
            per_hour=request.per_hour,
            per_day=request.per_day,
        )

        return APIKeyResponse(**api_key.to_dict())

    except Exception as e:
        logger.error(
            "rate_limit_update_failed",
            user=current_user.email,
            key_id=api_key_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to update rate limits: {str(e)}"
        )


@router.get("/{api_key_id}/usage", response_model=dict)
async def get_usage_stats(
    api_key_id: str,
    days: int = Query(30, ge=1, le=365, description="Days of history"),
    db=Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """
    Get usage statistics for an API key.

    Requires admin privileges.
    """
    service = APIKeyService(db)

    try:
        stats = await service.get_usage_stats(api_key_id, days)
        return stats

    except Exception as e:
        logger.error(
            "usage_stats_failed",
            user=current_user.email,
            key_id=api_key_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to get usage stats: {str(e)}"
        )


@router.post("/rotate-all")
async def rotate_all_due_keys(
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """
    Rotate all API keys that are due for rotation.

    This is typically run as a scheduled job.

    Requires admin privileges.
    """
    service = APIKeyService(db)

    try:
        rotated_keys = await service.check_and_rotate_keys()

        return {
            "message": "Key rotation check completed",
            "rotated_count": len(rotated_keys),
            "rotated_keys": rotated_keys,
        }

    except Exception as e:
        logger.error("bulk_rotation_failed", user=current_user.email, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to rotate keys: {str(e)}")


@router.post("/cleanup-expired")
async def cleanup_expired_keys(
    db=Depends(get_db), current_user: User = Depends(require_admin)
) -> dict:
    """
    Clean up expired API keys.

    This is typically run as a scheduled job.

    Requires admin privileges.
    """
    service = APIKeyService(db)

    try:
        cleaned_count = await service.cleanup_expired_keys()

        return {
            "message": "Expired keys cleanup completed",
            "cleaned_count": cleaned_count,
        }

    except Exception as e:
        logger.error("cleanup_failed", user=current_user.email, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to cleanup keys: {str(e)}")
