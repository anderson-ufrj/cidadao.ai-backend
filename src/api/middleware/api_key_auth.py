"""
Module: api.middleware.api_key_auth
Description: API key authentication middleware
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from datetime import UTC, datetime
from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param

from src.core import get_logger
from src.core.dependencies import get_db_session
from src.core.exceptions import AuthenticationError
from src.models.api_key import APIKey
from src.services.api_key_service import APIKeyService

logger = get_logger(__name__)


class APIKeyAuth(HTTPBearer):
    """API Key authentication handler."""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[APIKey]:
        """
        Extract and validate API key from request.

        Supports:
        - Authorization: Bearer <api_key>
        - X-API-Key: <api_key>
        """
        # Try Authorization header first
        authorization = request.headers.get("Authorization")
        api_key = None

        if authorization:
            scheme, credentials = get_authorization_scheme_param(authorization)
            if scheme.lower() == "bearer":
                api_key = credentials

        # Try X-API-Key header
        if not api_key:
            api_key = request.headers.get("X-API-Key")

        # Check query parameter as last resort (not recommended)
        if not api_key and hasattr(request, "query_params"):
            api_key = request.query_params.get("api_key")

        if not api_key:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key required",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None

        # Get client info for validation
        client_ip = request.client.host if request.client else None
        origin = request.headers.get("Origin")

        # Determine required scope from endpoint
        scope = self._get_required_scope(request)

        # Validate API key
        async with get_db_session() as db:
            service = APIKeyService(db)

            try:
                api_key_obj = await service.validate_api_key(
                    key=api_key, ip=client_ip, origin=origin, scope=scope
                )

                # Store API key in request state for logging
                request.state.api_key = api_key_obj
                request.state.api_key_id = str(api_key_obj.id)

                return api_key_obj

            except AuthenticationError as e:
                logger.warning(
                    "api_key_auth_failed", reason=str(e), ip=client_ip, origin=origin
                )

                if self.auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=str(e),
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                return None
            except Exception as e:
                logger.error("api_key_auth_error", error=str(e), exc_info=True)

                if self.auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Authentication error",
                    )
                return None

    def _get_required_scope(self, request: Request) -> Optional[str]:
        """Determine required scope based on endpoint."""
        path = request.url.path
        method = request.method

        # Define scope mappings
        scope_mappings = {
            # Read operations
            ("GET", "/api/v1/investigations"): "investigations:read",
            ("GET", "/api/v1/data"): "data:read",
            ("GET", "/api/v1/agents"): "agents:read",
            ("GET", "/api/v1/reports"): "reports:read",
            # Write operations
            ("POST", "/api/v1/investigations"): "investigations:write",
            ("POST", "/api/v1/reports"): "reports:write",
            # Admin operations
            ("POST", "/api/v1/api-keys"): "admin:api_keys",
            ("DELETE", "/api/v1"): "admin:delete",
        }

        # Check exact matches
        for (scope_method, scope_path), scope in scope_mappings.items():
            if method == scope_method and path.startswith(scope_path):
                return scope

        # Default scopes by method
        if method == "GET":
            return "read"
        elif method in ["POST", "PUT", "PATCH"]:
            return "write"
        elif method == "DELETE":
            return "delete"

        return None


class RateLimitMiddleware:
    """Rate limiting middleware for API keys."""

    def __init__(self, app):
        self.app = app
        self.rate_limiter = None  # Initialize with your rate limiter

    async def __call__(self, request: Request, call_next):
        """Check rate limits for API key requests."""
        # Get API key from request state
        api_key = getattr(request.state, "api_key", None)

        if api_key and isinstance(api_key, APIKey):
            # Get rate limits
            limits = api_key.get_rate_limits()

            # Check each limit
            for window, limit in limits.items():
                if limit is not None:
                    # This would integrate with your rate limiting service
                    # For now, we'll use a simple example
                    cache_key = f"rate_limit:{api_key.id}:{window}"

                    # Check if limit exceeded
                    # (Implementation depends on your rate limiting backend)

            # Update request count
            api_key.total_requests += 1

        # Process request
        try:
            response = await call_next(request)
            return response
        except Exception:
            # Update error count if API key is present
            if api_key and isinstance(api_key, APIKey):
                api_key.total_errors += 1
                api_key.last_error_at = datetime.now(UTC)
            raise


def get_api_key_auth(
    required_scopes: Optional[list] = None, auto_error: bool = True
) -> APIKeyAuth:
    """
    Get API key auth dependency with optional scope requirements.

    Args:
        required_scopes: List of required scopes
        auto_error: Raise exception on auth failure

    Returns:
        APIKeyAuth instance
    """
    auth = APIKeyAuth(auto_error=auto_error)

    # Add scope validation if needed
    if required_scopes:
        original_call = auth.__call__

        async def scoped_call(request: Request) -> Optional[APIKey]:
            api_key = await original_call(request)

            if api_key and required_scopes:
                for scope in required_scopes:
                    if not api_key.check_scope_allowed(scope):
                        if auto_error:
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Missing required scope: {scope}",
                            )
                        return None

            return api_key

        auth.__call__ = scoped_call

    return auth


# Convenience instances
api_key_auth = APIKeyAuth()
api_key_auth_optional = APIKeyAuth(auto_error=False)
