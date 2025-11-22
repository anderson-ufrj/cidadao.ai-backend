"""
Module: services.ip_whitelist_service
Description: IP whitelist management for production environments
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import ipaddress
from datetime import UTC, datetime
from typing import Any, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_logger
from src.core.config import settings
from src.models.base import BaseModel
from src.services.cache_service import cache_service

logger = get_logger(__name__)


class IPWhitelist(BaseModel):
    """IP whitelist entry model."""

    __tablename__ = "ip_whitelists"

    id = Column(String(64), primary_key=True)
    ip_address = Column(String(45), nullable=False, unique=True)  # IPv4 or IPv6
    description = Column(String(255))
    environment = Column(String(20), nullable=False, default="production")
    active = Column(Boolean, default=True)
    created_by = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    expires_at = Column(DateTime(timezone=True), nullable=True)
    meta_info = Column(JSON, default=dict)

    # CIDR support
    is_cidr = Column(Boolean, default=False)
    cidr_prefix = Column(Integer, nullable=True)

    def is_expired(self) -> bool:
        """Check if whitelist entry is expired."""
        if not self.expires_at:
            return False
        return datetime.now(UTC) > self.expires_at

    def matches(self, ip: str) -> bool:
        """Check if IP matches this whitelist entry."""
        if not self.active or self.is_expired():
            return False

        try:
            if self.is_cidr:
                # CIDR range check
                network = ipaddress.ip_network(f"{self.ip_address}/{self.cidr_prefix}")
                return ipaddress.ip_address(ip) in network
            else:
                # Exact match
                return self.ip_address == ip
        except ValueError:
            logger.error(f"Invalid IP address format: {ip}")
            return False


class IPWhitelistService:
    """Service for managing IP whitelists."""

    def __init__(self):
        """Initialize IP whitelist service."""
        self._cache_key_prefix = "ip_whitelist"
        self._cache_ttl = 300  # 5 minutes
        self._whitelist_cache: Optional[set[str]] = None
        self._cidr_cache: Optional[list[tuple]] = None
        self._last_cache_update: Optional[datetime] = None

    async def add_ip(
        self,
        session: AsyncSession,
        ip_address: str,
        created_by: str,
        description: Optional[str] = None,
        environment: str = "production",
        expires_at: Optional[datetime] = None,
        is_cidr: bool = False,
        meta_info: Optional[dict[str, Any]] = None,
    ) -> IPWhitelist:
        """Add IP address or CIDR range to whitelist."""
        try:
            # Parse and validate IP/CIDR
            if is_cidr or "/" in ip_address:
                network = ipaddress.ip_network(ip_address, strict=False)
                ip_str = str(network.network_address)
                cidr_prefix = network.prefixlen
                is_cidr = True
            else:
                # Validate single IP
                ip_obj = ipaddress.ip_address(ip_address)
                ip_str = str(ip_obj)
                cidr_prefix = None
                is_cidr = False

        except ValueError as e:
            logger.error(f"Invalid IP address format: {ip_address}")
            raise ValueError(f"Invalid IP address format: {ip_address}") from e

        # Check if already exists
        existing = await session.execute(
            select(IPWhitelist).where(
                IPWhitelist.ip_address == ip_str, IPWhitelist.environment == environment
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"IP address already whitelisted: {ip_str}")

        # Create whitelist entry
        entry = IPWhitelist(
            id=f"{environment}:{ip_str}",
            ip_address=ip_str,
            description=description,
            environment=environment,
            created_by=created_by,
            expires_at=expires_at,
            is_cidr=is_cidr,
            cidr_prefix=cidr_prefix,
            meta_info=meta_info or {},
            active=True,  # Explicitly set default for testing
        )

        session.add(entry)
        await session.commit()

        # Invalidate cache
        await self._invalidate_cache()

        logger.info(
            "ip_whitelist_added",
            ip=ip_str,
            environment=environment,
            is_cidr=is_cidr,
            created_by=created_by,
        )

        return entry

    async def remove_ip(
        self, session: AsyncSession, ip_address: str, environment: str = "production"
    ) -> bool:
        """Remove IP from whitelist."""
        result = await session.execute(
            delete(IPWhitelist).where(
                IPWhitelist.ip_address == ip_address,
                IPWhitelist.environment == environment,
            )
        )
        await session.commit()

        if result.rowcount > 0:
            await self._invalidate_cache()
            logger.info("ip_whitelist_removed", ip=ip_address, environment=environment)
            return True

        return False

    async def check_ip(
        self, session: AsyncSession, ip_address: str, environment: str = "production"
    ) -> bool:
        """Check if IP is whitelisted."""
        # Check cache first
        cache_key = f"{self._cache_key_prefix}:{environment}:check:{ip_address}"
        cached = await cache_service.get(cache_key)
        if cached is not None:
            return cached

        # Load whitelist if needed
        await self._ensure_cache_loaded(session, environment)

        # Check exact matches first
        if self._whitelist_cache and ip_address in self._whitelist_cache:
            await cache_service.set(cache_key, True, ttl=self._cache_ttl)
            return True

        # Check CIDR ranges
        if self._cidr_cache:
            for cidr_ip, prefix, expires_at in self._cidr_cache:
                if expires_at and datetime.now(UTC) > expires_at:
                    continue

                try:
                    network = ipaddress.ip_network(f"{cidr_ip}/{prefix}")
                    if ipaddress.ip_address(ip_address) in network:
                        await cache_service.set(cache_key, True, ttl=self._cache_ttl)
                        return True
                except ValueError:
                    continue

        # Not whitelisted
        await cache_service.set(cache_key, False, ttl=self._cache_ttl)
        return False

    async def list_ips(
        self,
        session: AsyncSession,
        environment: str = "production",
        include_expired: bool = False,
    ) -> list[IPWhitelist]:
        """List all whitelisted IPs."""
        query = select(IPWhitelist).where(IPWhitelist.environment == environment)

        if not include_expired:
            now = datetime.now(UTC)
            query = query.where(
                (IPWhitelist.expires_at.is_(None)) | (IPWhitelist.expires_at > now)
            )

        result = await session.execute(query)
        return list(result.scalars().all())

    async def update_ip(
        self,
        session: AsyncSession,
        ip_address: str,
        environment: str = "production",
        active: Optional[bool] = None,
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        meta_info: Optional[dict[str, Any]] = None,
    ) -> Optional[IPWhitelist]:
        """Update whitelist entry."""
        result = await session.execute(
            select(IPWhitelist).where(
                IPWhitelist.ip_address == ip_address,
                IPWhitelist.environment == environment,
            )
        )
        entry = result.scalar_one_or_none()

        if not entry:
            return None

        if active is not None:
            entry.active = active
        if description is not None:
            entry.description = description
        if expires_at is not None:
            entry.expires_at = expires_at
        if meta_info is not None:
            entry.meta_info = meta_info

        await session.commit()
        await self._invalidate_cache()

        logger.info(
            "ip_whitelist_updated",
            ip=ip_address,
            environment=environment,
            active=entry.active,
        )

        return entry

    async def cleanup_expired(
        self, session: AsyncSession, environment: Optional[str] = None
    ) -> int:
        """Remove expired whitelist entries."""
        query = delete(IPWhitelist).where(IPWhitelist.expires_at < datetime.now(UTC))

        if environment:
            query = query.where(IPWhitelist.environment == environment)

        result = await session.execute(query)
        await session.commit()

        if result.rowcount > 0:
            await self._invalidate_cache()
            logger.info(
                "ip_whitelist_cleanup", removed=result.rowcount, environment=environment
            )

        return result.rowcount

    async def _ensure_cache_loaded(
        self, session: AsyncSession, environment: str
    ) -> None:
        """Ensure whitelist is loaded in cache."""
        # Check if cache is still valid
        if (
            self._last_cache_update
            and (datetime.now(UTC) - self._last_cache_update).total_seconds()
            < self._cache_ttl
        ):
            return

        # Load from database
        now = datetime.now(UTC)
        result = await session.execute(
            select(IPWhitelist).where(
                IPWhitelist.environment == environment,
                IPWhitelist.active == True,
                (IPWhitelist.expires_at.is_(None)) | (IPWhitelist.expires_at > now),
            )
        )

        entries = result.scalars().all()

        # Separate exact IPs and CIDR ranges
        self._whitelist_cache = set()
        self._cidr_cache = []

        for entry in entries:
            if entry.is_cidr:
                self._cidr_cache.append(
                    (entry.ip_address, entry.cidr_prefix, entry.expires_at)
                )
            else:
                self._whitelist_cache.add(entry.ip_address)

        self._last_cache_update = datetime.now(UTC)

        logger.debug(
            "ip_whitelist_cache_loaded",
            environment=environment,
            exact_ips=len(self._whitelist_cache),
            cidr_ranges=len(self._cidr_cache),
        )

    async def _invalidate_cache(self) -> None:
        """Invalidate the whitelist cache."""
        self._whitelist_cache = None
        self._cidr_cache = None
        self._last_cache_update = None

        # Clear Redis cache patterns
        pattern = f"{self._cache_key_prefix}:*"
        await cache_service.delete_pattern(pattern)

    def get_default_whitelist(self) -> list[str]:
        """Get default whitelist based on environment."""
        defaults = []

        # Always allow localhost
        defaults.extend(["127.0.0.1", "::1", "localhost"])

        # Development environment
        if settings.is_development:
            defaults.extend(
                [
                    "10.0.0.0/8",  # Private network
                    "172.16.0.0/12",  # Private network
                    "192.168.0.0/16",  # Private network
                ]
            )

        # Production environment - add known services
        if settings.is_production:
            # Vercel IPs (example - would need real ranges)
            defaults.extend(
                [
                    "76.76.21.0/24",  # Vercel edge network (example)
                    "76.223.0.0/16",  # Vercel edge network (example)
                ]
            )

            # HuggingFace Spaces IPs (example - would need real ranges)
            defaults.extend(
                [
                    "34.0.0.0/8",  # Google Cloud (where HF runs)
                    "35.0.0.0/8",  # Google Cloud
                ]
            )

            # Monitoring services
            defaults.extend(["52.0.0.0/8"])  # AWS (for monitoring)

        return defaults

    async def initialize_defaults(
        self, session: AsyncSession, created_by: str = "system"
    ) -> int:
        """Initialize default whitelist entries."""
        defaults = self.get_default_whitelist()
        count = 0

        for ip in defaults:
            try:
                is_cidr = "/" in ip
                await self.add_ip(
                    session=session,
                    ip_address=ip,
                    created_by=created_by,
                    description="Default whitelist entry",
                    environment=settings.app_env,
                    is_cidr=is_cidr,
                )
                count += 1
            except ValueError:
                # Already exists or invalid
                continue

        logger.info(
            "ip_whitelist_defaults_initialized",
            count=count,
            environment=settings.app_env,
        )

        return count


# Global instance
ip_whitelist_service = IPWhitelistService()
