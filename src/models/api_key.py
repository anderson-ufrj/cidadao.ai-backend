"""
Module: models.api_key
Description: API Key model for client authentication and rotation
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
import secrets
import hashlib

from sqlalchemy import (
    Column, String, DateTime, Boolean, Integer, 
    ForeignKey, Index, Text, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from src.models.base import BaseModel


class APIKeyStatus(str, Enum):
    """API key status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ROTATING = "rotating"


class APIKeyTier(str, Enum):
    """API key tier for rate limiting."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class APIKey(BaseModel):
    """
    API Key model for client authentication.
    
    Features:
    - Automatic rotation support
    - Rate limiting by tier
    - Usage tracking
    - IP restrictions
    - Scope limitations
    """
    __tablename__ = "api_keys"
    
    # Basic fields
    name = Column(String(255), nullable=False)
    description = Column(Text)
    key_prefix = Column(String(10), nullable=False)  # e.g., "cid_"
    key_hash = Column(String(128), nullable=False, unique=True)  # SHA-512 hash
    
    # Status and tier
    status = Column(String(20), default=APIKeyStatus.ACTIVE)
    tier = Column(String(20), default=APIKeyTier.FREE)
    
    # Ownership
    client_id = Column(String(255), nullable=False)  # External client ID
    client_name = Column(String(255))
    client_email = Column(String(255))
    
    # Validity
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime)
    last_rotated_at = Column(DateTime)
    rotation_period_days = Column(Integer, default=90)  # 0 = no rotation
    
    # Security
    allowed_ips = Column(JSON, default=list)  # Empty = all IPs allowed
    allowed_origins = Column(JSON, default=list)  # CORS origins
    scopes = Column(JSON, default=list)  # API scopes/permissions
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer)
    rate_limit_per_hour = Column(Integer)
    rate_limit_per_day = Column(Integer)
    
    # Usage tracking
    total_requests = Column(Integer, default=0)
    total_errors = Column(Integer, default=0)
    last_error_at = Column(DateTime)
    
    # Metadata
    meta_info = Column(JSON, default=dict)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_api_keys_client_id', 'client_id'),
        Index('ix_api_keys_status', 'status'),
        Index('ix_api_keys_expires_at', 'expires_at'),
    )
    
    @classmethod
    def generate_key(cls, prefix: str = "cid") -> tuple[str, str]:
        """
        Generate a new API key.
        
        Returns:
            Tuple of (full_key, key_hash)
        """
        # Generate 32 bytes of randomness (256 bits)
        random_bytes = secrets.token_bytes(32)
        
        # Create the key: prefix_base64(random_bytes)
        key_suffix = secrets.token_urlsafe(32)
        full_key = f"{prefix}_{key_suffix}"
        
        # Hash the key for storage
        key_hash = hashlib.sha512(full_key.encode()).hexdigest()
        
        return full_key, key_hash
    
    @classmethod
    def hash_key(cls, key: str) -> str:
        """Hash an API key for comparison."""
        return hashlib.sha512(key.encode()).hexdigest()
    
    @hybrid_property
    def is_active(self) -> bool:
        """Check if key is currently active."""
        if self.status != APIKeyStatus.ACTIVE:
            return False
        
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        
        return True
    
    @hybrid_property
    def needs_rotation(self) -> bool:
        """Check if key needs rotation."""
        if self.rotation_period_days <= 0:
            return False
        
        if not self.last_rotated_at:
            # Never rotated, use creation date
            last_rotation = self.created_at
        else:
            last_rotation = self.last_rotated_at
        
        rotation_due = last_rotation + timedelta(days=self.rotation_period_days)
        return datetime.utcnow() >= rotation_due
    
    def get_rate_limits(self) -> dict:
        """Get rate limits based on tier or custom settings."""
        # Custom limits take precedence
        if any([self.rate_limit_per_minute, self.rate_limit_per_hour, self.rate_limit_per_day]):
            return {
                "per_minute": self.rate_limit_per_minute,
                "per_hour": self.rate_limit_per_hour,
                "per_day": self.rate_limit_per_day
            }
        
        # Default limits by tier
        tier_limits = {
            APIKeyTier.FREE: {
                "per_minute": 10,
                "per_hour": 100,
                "per_day": 1000
            },
            APIKeyTier.BASIC: {
                "per_minute": 30,
                "per_hour": 500,
                "per_day": 5000
            },
            APIKeyTier.PRO: {
                "per_minute": 60,
                "per_hour": 2000,
                "per_day": 20000
            },
            APIKeyTier.ENTERPRISE: {
                "per_minute": 300,
                "per_hour": 10000,
                "per_day": 100000
            }
        }
        
        return tier_limits.get(self.tier, tier_limits[APIKeyTier.FREE])
    
    def check_ip_allowed(self, ip: str) -> bool:
        """Check if IP is allowed for this key."""
        if not self.allowed_ips:
            return True  # No restrictions
        
        return ip in self.allowed_ips
    
    def check_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed for this key."""
        if not self.allowed_origins:
            return True  # No restrictions
        
        return origin in self.allowed_origins
    
    def check_scope_allowed(self, scope: str) -> bool:
        """Check if scope is allowed for this key."""
        if not self.scopes:
            return True  # No restrictions = all scopes
        
        return scope in self.scopes
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert to dictionary."""
        data = {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "tier": self.tier,
            "client_id": self.client_id,
            "client_name": self.client_name,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "is_active": self.is_active,
            "needs_rotation": self.needs_rotation,
            "rate_limits": self.get_rate_limits(),
            "total_requests": self.total_requests,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data.update({
                "allowed_ips": self.allowed_ips,
                "allowed_origins": self.allowed_origins,
                "scopes": self.scopes,
                "metadata": self.meta_info
            })
        
        return data


class APIKeyRotation(BaseModel):
    """Track API key rotation history."""
    __tablename__ = "api_key_rotations"
    
    api_key_id = Column(String(36), ForeignKey("api_keys.id"), nullable=False)
    old_key_hash = Column(String(128), nullable=False)
    new_key_hash = Column(String(128), nullable=False)
    rotation_reason = Column(String(255))
    initiated_by = Column(String(255))  # system, admin, client
    grace_period_hours = Column(Integer, default=24)
    old_key_expires_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    
    # Relationships
    api_key = relationship("APIKey", backref="rotations")