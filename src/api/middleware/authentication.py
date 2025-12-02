"""
Module: api.middleware.authentication
Description: Authentication middleware for API endpoints
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer

from src.core import get_logger, settings


class AuthenticationMiddleware:
    """Authentication middleware for API endpoints."""

    def __init__(self):
        """Initialize authentication middleware."""
        self.logger = get_logger(__name__)
        self.security = HTTPBearer(auto_error=False)

    async def __call__(self, request: Request):
        """Authenticate request."""
        # Skip authentication for health check and docs
        if request.url.path in ["/health", "/health/", "/docs", "/openapi.json", "/"]:
            return True

        # Check for API key in headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return await self._validate_api_key(api_key, request)

        # Check for JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            return await self._validate_jwt_token(token, request)

        # For development, allow unauthenticated access
        if settings.app_env == "development":
            self.logger.warning(
                "unauthenticated_request_allowed",
                path=request.url.path,
                method=request.method,
                environment="development",
            )
            return True

        # Production requires authentication
        self.logger.warning(
            "unauthenticated_request_rejected",
            path=request.url.path,
            method=request.method,
        )

        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async def _validate_api_key(self, api_key: str, request: Request) -> bool:
        """Validate API key."""
        # In a real implementation, this would check against a database
        # For now, we'll use a simple validation

        if not api_key or len(api_key) < 32:
            self.logger.warning(
                "invalid_api_key_format",
                api_key_length=len(api_key) if api_key else 0,
                path=request.url.path,
            )
            raise HTTPException(status_code=401, detail="Invalid API key format")

        # TODO: Implement proper API key validation
        # For development, accept any key with correct format
        self.logger.info(
            "api_key_authentication_success",
            path=request.url.path,
            method=request.method,
        )

        return True

    async def _validate_jwt_token(self, token: str, request: Request) -> bool:
        """Validate JWT token."""
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                settings.jwt_secret_key.get_secret_value(),
                algorithms=[settings.jwt_algorithm],
            )

            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.now(UTC).timestamp() > exp:
                raise HTTPException(status_code=401, detail="Token has expired")

            # Store user info in request state
            request.state.user_id = payload.get("sub")
            request.state.user_email = payload.get("email")
            request.state.user_roles = payload.get("roles", [])

            self.logger.info(
                "jwt_authentication_success",
                user_id=request.state.user_id,
                path=request.url.path,
                method=request.method,
            )

            return True

        except jwt.ExpiredSignatureError:
            self.logger.warning(
                "jwt_token_expired",
                path=request.url.path,
            )
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError as e:
            self.logger.warning(
                "jwt_validation_failed",
                error=str(e),
                path=request.url.path,
            )
            raise HTTPException(status_code=401, detail="Invalid token")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    to_encode.update({"exp": expire.timestamp()})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    return encoded_jwt


def get_current_user(request: Request) -> dict:
    """Get current authenticated user."""
    return {
        "user_id": getattr(request.state, "user_id", None),
        "email": getattr(request.state, "user_email", None),
        "roles": getattr(request.state, "user_roles", []),
    }
