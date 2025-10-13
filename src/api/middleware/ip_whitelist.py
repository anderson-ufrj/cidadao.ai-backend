"""
Module: api.middleware.ip_whitelist
Description: IP whitelist middleware for production environments
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import ipaddress
from typing import Optional

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.core import get_logger
from src.core.config import settings
from src.db.session import get_session
from src.services.ip_whitelist_service import ip_whitelist_service

logger = get_logger(__name__)


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """
    IP whitelist middleware for production environments.

    Features:
    - Environment-based activation
    - Path exclusions
    - Multiple IP extraction methods
    - Performance optimization with caching
    """

    def __init__(
        self,
        app,
        enabled: Optional[bool] = None,
        excluded_paths: Optional[list[str]] = None,
        strict_mode: bool = True,
    ):
        """
        Initialize IP whitelist middleware.

        Args:
            app: FastAPI application
            enabled: Force enable/disable (None = auto based on environment)
            excluded_paths: Paths to exclude from whitelist check
            strict_mode: If True, reject if can't determine IP
        """
        super().__init__(app)

        # Auto-enable in production if not specified
        if enabled is None:
            self.enabled = settings.is_production
        else:
            self.enabled = enabled

        self.excluded_paths = set(excluded_paths or self._get_default_excluded_paths())
        self.strict_mode = strict_mode

        logger.info(
            "ip_whitelist_middleware_initialized",
            enabled=self.enabled,
            environment=settings.app_env,
            strict_mode=self.strict_mode,
        )

    async def dispatch(self, request: Request, call_next):
        """Process request with IP whitelist check."""
        # Skip if disabled
        if not self.enabled:
            return await call_next(request)

        # Skip excluded paths
        if self._should_skip(request.url.path):
            return await call_next(request)

        try:
            # Extract client IP
            client_ip = self._get_client_ip(request)

            if not client_ip:
                if self.strict_mode:
                    logger.warning(
                        "ip_whitelist_no_client_ip",
                        path=request.url.path,
                        headers=dict(request.headers),
                    )
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={
                            "detail": "Client IP could not be determined",
                            "error": "IP_NOT_DETERMINED",
                        },
                    )
                else:
                    # Allow through if can't determine IP
                    logger.debug("ip_whitelist_no_client_ip_allowing")
                    return await call_next(request)

            # Check whitelist
            async with get_session() as session:
                is_whitelisted = await ip_whitelist_service.check_ip(
                    session, client_ip, environment=settings.app_env
                )

            if not is_whitelisted:
                logger.warning(
                    "ip_whitelist_access_denied",
                    client_ip=client_ip,
                    path=request.url.path,
                    method=request.method,
                )

                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": "Access denied: IP not whitelisted",
                        "error": "IP_NOT_WHITELISTED",
                    },
                )

            # IP is whitelisted, proceed
            request.state.client_ip = client_ip
            request.state.ip_whitelisted = True

            return await call_next(request)

        except Exception as e:
            logger.error("ip_whitelist_error", error=str(e), exc_info=True)

            # In case of error, fail open or closed based on strict mode
            if self.strict_mode:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "detail": "IP whitelist check failed",
                        "error": "WHITELIST_CHECK_ERROR",
                    },
                )
            else:
                # Allow through on error
                return await call_next(request)

    def _get_default_excluded_paths(self) -> list[str]:
        """Get default paths to exclude from whitelist."""
        return [
            # Health checks
            "/health",
            "/healthz",
            "/ping",
            "/ready",
            # Documentation
            "/docs",
            "/redoc",
            "/openapi.json",
            # Metrics
            "/metrics",
            # Static assets
            "/static",
            "/favicon.ico",
            "/_next",
            # Public endpoints
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/public",
            # Webhook endpoints (they have their own auth)
            "/api/v1/webhooks/incoming",
        ]

    def _should_skip(self, path: str) -> bool:
        """Check if path should skip whitelist check."""
        # Exact match
        if path in self.excluded_paths:
            return True

        # Prefix match
        for excluded in self.excluded_paths:
            if excluded.endswith("*") and path.startswith(excluded[:-1]):
                return True
            if path.startswith(excluded + "/"):
                return True

        return False

    def _get_client_ip(self, request: Request) -> Optional[str]:
        """
        Extract client IP from request.

        Tries multiple methods in order:
        1. X-Real-IP header
        2. X-Forwarded-For header
        3. CloudFlare headers
        4. Direct client connection
        """
        # Try X-Real-IP first (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip and self._is_valid_ip(real_ip):
            return real_ip

        # Try X-Forwarded-For (proxy chains)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            ips = [ip.strip() for ip in forwarded_for.split(",")]
            for ip in ips:
                if self._is_valid_ip(ip):
                    return ip

        # Try CloudFlare headers
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip and self._is_valid_ip(cf_ip):
            return cf_ip

        # Try True-Client-IP (Akamai, CloudFlare Enterprise)
        true_client_ip = request.headers.get("True-Client-IP")
        if true_client_ip and self._is_valid_ip(true_client_ip):
            return true_client_ip

        # Try Fastly header
        fastly_ip = request.headers.get("Fastly-Client-IP")
        if fastly_ip and self._is_valid_ip(fastly_ip):
            return fastly_ip

        # Fallback to direct connection
        if request.client and request.client.host:
            return request.client.host

        return None

    def _is_valid_ip(self, ip: str) -> bool:
        """Check if string is a valid IP address."""
        if not ip:
            return False

        try:
            # Validate IP
            ipaddress.ip_address(ip)

            # Reject private/local IPs unless in development
            if not settings.is_development:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_private or ip_obj.is_loopback:
                    return False

            return True
        except ValueError:
            return False
