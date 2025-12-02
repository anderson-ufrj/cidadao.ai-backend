"""
API dependencies for dependency injection.
Provides common dependencies used across API routes.
"""

from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.authentication import get_current_user as _get_current_user
from src.db.session import get_session as get_db_session


def get_current_user(request: Request) -> dict[str, Any]:
    """
    Get current authenticated user from request.
    Returns user information stored in request state.
    """
    return _get_current_user(request)


def get_current_optional_user(request: Request) -> dict[str, Any] | None:
    """
    Get current user if authenticated, None otherwise.
    Used for endpoints that support both authenticated and anonymous access.
    """
    try:
        # Check if user is authenticated
        if hasattr(request.state, "user_id") and request.state.user_id:
            return get_current_user(request)
        return None
    except Exception:
        # If any error occurs, treat as anonymous user
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
