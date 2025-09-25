"""
Module: services.api_key_service
Description: Service for API key management and rotation
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from src.core import get_logger
from src.models.api_key import APIKey, APIKeyRotation, APIKeyStatus, APIKeyTier
from src.core.exceptions import ValidationError, NotFoundError, AuthenticationError
from src.core.cache import CacheService
from src.services.notification_service import NotificationService

logger = get_logger(__name__)


class APIKeyService:
    """Service for managing API keys and rotation."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize API key service."""
        self.db = db_session
        self.cache = CacheService()
        self.notification_service = NotificationService()
        
    async def create_api_key(
        self,
        name: str,
        client_id: str,
        client_name: Optional[str] = None,
        client_email: Optional[str] = None,
        tier: APIKeyTier = APIKeyTier.FREE,
        expires_in_days: Optional[int] = None,
        rotation_period_days: int = 90,
        allowed_ips: Optional[List[str]] = None,
        allowed_origins: Optional[List[str]] = None,
        scopes: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[APIKey, str]:
        """
        Create a new API key.
        
        Args:
            name: Key name/description
            client_id: External client identifier
            client_name: Client display name
            client_email: Client email for notifications
            tier: API key tier
            expires_in_days: Days until expiration (None = no expiration)
            rotation_period_days: Days between rotations (0 = no rotation)
            allowed_ips: List of allowed IP addresses
            allowed_origins: List of allowed CORS origins
            scopes: List of API scopes/permissions
            metadata: Additional metadata
            
        Returns:
            Tuple of (APIKey object, plain text key)
        """
        # Generate key
        prefix = "cid"
        full_key, key_hash = APIKey.generate_key(prefix)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create API key record
        api_key = APIKey(
            name=name,
            key_prefix=prefix,
            key_hash=key_hash,
            client_id=client_id,
            client_name=client_name,
            client_email=client_email,
            tier=tier,
            expires_at=expires_at,
            rotation_period_days=rotation_period_days,
            allowed_ips=allowed_ips or [],
            allowed_origins=allowed_origins or [],
            scopes=scopes or [],
            metadata=metadata or {}
        )
        
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        
        logger.info(
            "api_key_created",
            api_key_id=str(api_key.id),
            client_id=client_id,
            tier=tier
        )
        
        # Send notification if email provided
        if client_email:
            await self._send_key_created_notification(api_key, client_email)
        
        return api_key, full_key
    
    async def validate_api_key(
        self,
        key: str,
        ip: Optional[str] = None,
        origin: Optional[str] = None,
        scope: Optional[str] = None
    ) -> APIKey:
        """
        Validate an API key and check permissions.
        
        Args:
            key: The API key to validate
            ip: Client IP address
            origin: Request origin
            scope: Required scope
            
        Returns:
            APIKey object if valid
            
        Raises:
            AuthenticationError: If key is invalid or unauthorized
        """
        # Check cache first
        cache_key = f"api_key:{key[:10]}"  # Use prefix for cache key
        cached_data = await self.cache.get(cache_key)
        
        if cached_data:
            api_key_id = cached_data.get("api_key_id")
            api_key = await self.get_by_id(api_key_id)
        else:
            # Hash the key and find in database
            key_hash = APIKey.hash_key(key)
            
            result = await self.db.execute(
                select(APIKey).where(APIKey.key_hash == key_hash)
            )
            api_key = result.scalar_one_or_none()
            
            if not api_key:
                raise AuthenticationError("Invalid API key")
            
            # Cache for 5 minutes
            await self.cache.set(
                cache_key,
                {"api_key_id": str(api_key.id)},
                ttl=300
            )
        
        # Check if active
        if not api_key.is_active:
            raise AuthenticationError(f"API key is {api_key.status}")
        
        # Check IP restriction
        if ip and not api_key.check_ip_allowed(ip):
            raise AuthenticationError(f"IP {ip} not allowed")
        
        # Check origin restriction
        if origin and not api_key.check_origin_allowed(origin):
            raise AuthenticationError(f"Origin {origin} not allowed")
        
        # Check scope
        if scope and not api_key.check_scope_allowed(scope):
            raise AuthenticationError(f"Scope {scope} not allowed")
        
        # Update last used
        api_key.last_used_at = datetime.utcnow()
        api_key.total_requests += 1
        await self.db.commit()
        
        return api_key
    
    async def rotate_api_key(
        self,
        api_key_id: str,
        reason: str = "scheduled_rotation",
        initiated_by: str = "system",
        grace_period_hours: int = 24
    ) -> Tuple[APIKey, str]:
        """
        Rotate an API key.
        
        Args:
            api_key_id: ID of key to rotate
            reason: Rotation reason
            initiated_by: Who initiated rotation
            grace_period_hours: Hours before old key expires
            
        Returns:
            Tuple of (updated APIKey, new plain text key)
        """
        # Get existing key
        api_key = await self.get_by_id(api_key_id)
        if not api_key:
            raise NotFoundError(f"API key {api_key_id} not found")
        
        # Mark as rotating
        old_status = api_key.status
        api_key.status = APIKeyStatus.ROTATING
        await self.db.commit()
        
        try:
            # Generate new key
            prefix = api_key.key_prefix
            new_full_key, new_key_hash = APIKey.generate_key(prefix)
            
            # Create rotation record
            rotation = APIKeyRotation(
                api_key_id=api_key_id,
                old_key_hash=api_key.key_hash,
                new_key_hash=new_key_hash,
                rotation_reason=reason,
                initiated_by=initiated_by,
                grace_period_hours=grace_period_hours,
                old_key_expires_at=datetime.utcnow() + timedelta(hours=grace_period_hours)
            )
            
            # Update API key
            api_key.key_hash = new_key_hash
            api_key.last_rotated_at = datetime.utcnow()
            api_key.status = old_status
            
            self.db.add(rotation)
            await self.db.commit()
            await self.db.refresh(api_key)
            
            logger.info(
                "api_key_rotated",
                api_key_id=api_key_id,
                reason=reason,
                grace_period_hours=grace_period_hours
            )
            
            # Clear cache
            await self.cache.delete(f"api_key:{api_key.key_prefix}*")
            
            # Send notification
            if api_key.client_email:
                await self._send_key_rotation_notification(
                    api_key,
                    api_key.client_email,
                    grace_period_hours
                )
            
            return api_key, new_full_key
            
        except Exception as e:
            # Restore original status on error
            api_key.status = old_status
            await self.db.commit()
            raise
    
    async def check_and_rotate_keys(self) -> List[str]:
        """
        Check all keys and rotate those that need it.
        
        Returns:
            List of rotated key IDs
        """
        # Find keys that need rotation
        result = await self.db.execute(
            select(APIKey).where(
                and_(
                    APIKey.status == APIKeyStatus.ACTIVE,
                    APIKey.rotation_period_days > 0
                )
            )
        )
        api_keys = result.scalars().all()
        
        rotated_keys = []
        
        for api_key in api_keys:
            if api_key.needs_rotation:
                try:
                    await self.rotate_api_key(
                        str(api_key.id),
                        reason="scheduled_rotation",
                        initiated_by="system"
                    )
                    rotated_keys.append(str(api_key.id))
                except Exception as e:
                    logger.error(
                        "key_rotation_failed",
                        api_key_id=str(api_key.id),
                        error=str(e)
                    )
        
        logger.info(
            "key_rotation_check_completed",
            checked=len(api_keys),
            rotated=len(rotated_keys)
        )
        
        return rotated_keys
    
    async def revoke_api_key(
        self,
        api_key_id: str,
        reason: str,
        revoked_by: str
    ) -> APIKey:
        """
        Revoke an API key.
        
        Args:
            api_key_id: ID of key to revoke
            reason: Revocation reason
            revoked_by: Who revoked the key
            
        Returns:
            Updated APIKey
        """
        api_key = await self.get_by_id(api_key_id)
        if not api_key:
            raise NotFoundError(f"API key {api_key_id} not found")
        
        api_key.status = APIKeyStatus.REVOKED
        api_key.metadata["revocation"] = {
            "reason": reason,
            "revoked_by": revoked_by,
            "revoked_at": datetime.utcnow().isoformat()
        }
        
        await self.db.commit()
        await self.db.refresh(api_key)
        
        # Clear cache
        await self.cache.delete(f"api_key:{api_key.key_prefix}*")
        
        logger.warning(
            "api_key_revoked",
            api_key_id=api_key_id,
            reason=reason,
            revoked_by=revoked_by
        )
        
        # Send notification
        if api_key.client_email:
            await self._send_key_revoked_notification(
                api_key,
                api_key.client_email,
                reason
            )
        
        return api_key
    
    async def get_by_id(self, api_key_id: str) -> Optional[APIKey]:
        """Get API key by ID."""
        result = await self.db.execute(
            select(APIKey)
            .where(APIKey.id == api_key_id)
            .options(selectinload(APIKey.rotations))
        )
        return result.scalar_one_or_none()
    
    async def get_by_client(
        self,
        client_id: str,
        include_inactive: bool = False
    ) -> List[APIKey]:
        """Get all API keys for a client."""
        query = select(APIKey).where(APIKey.client_id == client_id)
        
        if not include_inactive:
            query = query.where(APIKey.status == APIKeyStatus.ACTIVE)
        
        result = await self.db.execute(query.order_by(APIKey.created_at.desc()))
        return result.scalars().all()
    
    async def update_rate_limits(
        self,
        api_key_id: str,
        per_minute: Optional[int] = None,
        per_hour: Optional[int] = None,
        per_day: Optional[int] = None
    ) -> APIKey:
        """Update custom rate limits for a key."""
        api_key = await self.get_by_id(api_key_id)
        if not api_key:
            raise NotFoundError(f"API key {api_key_id} not found")
        
        if per_minute is not None:
            api_key.rate_limit_per_minute = per_minute
        if per_hour is not None:
            api_key.rate_limit_per_hour = per_hour
        if per_day is not None:
            api_key.rate_limit_per_day = per_day
        
        await self.db.commit()
        await self.db.refresh(api_key)
        
        return api_key
    
    async def get_usage_stats(
        self,
        api_key_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get usage statistics for an API key."""
        api_key = await self.get_by_id(api_key_id)
        if not api_key:
            raise NotFoundError(f"API key {api_key_id} not found")
        
        # This would integrate with your metrics system
        # For now, return basic stats
        return {
            "api_key_id": api_key_id,
            "total_requests": api_key.total_requests,
            "total_errors": api_key.total_errors,
            "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
            "error_rate": (
                api_key.total_errors / api_key.total_requests
                if api_key.total_requests > 0 else 0
            )
        }
    
    async def cleanup_expired_keys(self) -> int:
        """Clean up expired API keys."""
        # Find expired keys
        result = await self.db.execute(
            select(APIKey).where(
                and_(
                    APIKey.expires_at.isnot(None),
                    APIKey.expires_at < datetime.utcnow(),
                    APIKey.status == APIKeyStatus.ACTIVE
                )
            )
        )
        expired_keys = result.scalars().all()
        
        # Mark as expired
        for api_key in expired_keys:
            api_key.status = APIKeyStatus.EXPIRED
        
        await self.db.commit()
        
        logger.info(
            "expired_keys_cleanup",
            count=len(expired_keys)
        )
        
        return len(expired_keys)
    
    async def _send_key_created_notification(
        self,
        api_key: APIKey,
        email: str
    ):
        """Send API key creation notification."""
        try:
            await self.notification_service.send_notification(
                type="email",
                recipients=[email],
                template="api_key_created",
                data={
                    "client_name": api_key.client_name or "Client",
                    "key_name": api_key.name,
                    "tier": api_key.tier,
                    "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else "Never",
                    "rate_limits": api_key.get_rate_limits()
                }
            )
        except Exception as e:
            logger.error(
                "notification_failed",
                type="api_key_created",
                error=str(e)
            )
    
    async def _send_key_rotation_notification(
        self,
        api_key: APIKey,
        email: str,
        grace_period_hours: int
    ):
        """Send API key rotation notification."""
        try:
            await self.notification_service.send_notification(
                type="email",
                recipients=[email],
                template="api_key_rotated",
                data={
                    "client_name": api_key.client_name or "Client",
                    "key_name": api_key.name,
                    "grace_period_hours": grace_period_hours,
                    "old_key_expires_at": (
                        datetime.utcnow() + timedelta(hours=grace_period_hours)
                    ).isoformat()
                }
            )
        except Exception as e:
            logger.error(
                "notification_failed",
                type="api_key_rotated",
                error=str(e)
            )
    
    async def _send_key_revoked_notification(
        self,
        api_key: APIKey,
        email: str,
        reason: str
    ):
        """Send API key revocation notification."""
        try:
            await self.notification_service.send_notification(
                type="email",
                recipients=[email],
                template="api_key_revoked",
                data={
                    "client_name": api_key.client_name or "Client",
                    "key_name": api_key.name,
                    "reason": reason,
                    "revoked_at": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(
                "notification_failed",
                type="api_key_revoked",
                error=str(e)
            )