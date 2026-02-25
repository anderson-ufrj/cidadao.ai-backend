"""
API dependencies for dependency injection.
Provides common dependencies used across API routes.
"""

from collections.abc import AsyncGenerator
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.authentication import get_current_user as _get_current_user
from src.core import get_logger
from src.core.config import settings
from src.db.session import get_session as get_db_session

_dep_logger = get_logger(__name__)


def get_current_user(request: Request) -> dict[str, Any]:
    """
    Get current authenticated user from request.
    Returns user information stored in request state.
    """
    return _get_current_user(request)


def get_current_optional_user(request: Request) -> dict[str, Any] | None:
    """
    Get current user if authenticated, None otherwise.
    Extracts JWT from Authorization header directly since the
    AuthenticationMiddleware is not registered as global middleware.
    """
    try:
        # First check if middleware already set it
        if hasattr(request.state, "user_id") and request.state.user_id:
            return get_current_user(request)

        # Extract JWT from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header[7:]

        # Try backend secret first, then Supabase secret
        secrets_to_try = [
            (settings.jwt_secret_key.get_secret_value(), "backend"),
        ]
        if settings.supabase_jwt_secret:
            secrets_to_try.append(
                (settings.supabase_jwt_secret.get_secret_value(), "supabase")
            )

        for secret, source in secrets_to_try:
            try:
                payload = jwt.decode(
                    token,
                    secret,
                    algorithms=[settings.jwt_algorithm],
                    options={"verify_aud": False},
                )
                user_id = payload.get("sub")
                if user_id:
                    # Store in request state for downstream use
                    request.state.user_id = user_id
                    request.state.user_email = payload.get("email")
                    request.state.user_roles = payload.get("roles", [])
                    _dep_logger.debug(
                        "jwt_extracted_from_header",
                        user_id=user_id,
                        source=source,
                        path=request.url.path,
                    )
                    return {
                        "user_id": user_id,
                        "email": payload.get("email"),
                        "roles": payload.get("roles", []),
                    }
            except jwt.ExpiredSignatureError:
                return None
            except jwt.JWTError:
                continue

        return None
    except Exception:
        return None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session.
    Yields an async SQLAlchemy session.
    """
    async with get_db_session() as session:
        yield session


def require_admin(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    """
    Require admin role for access.
    Raises 403 if user is not admin.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    # Check for admin role
    user_role = user.get("role", "").lower()
    is_admin = user.get("is_admin", False)
    is_superuser = user.get("is_superuser", False)

    if user_role != "admin" and not is_admin and not is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )

    return user


# Export commonly used dependencies
__all__ = [
    "get_current_user",
    "get_current_optional_user",
    "get_db",
    "require_admin",
]
