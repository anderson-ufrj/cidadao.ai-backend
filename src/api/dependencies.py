"""
API dependencies for dependency injection.
Provides common dependencies used across API routes.
"""
from typing import Optional, Dict, Any
from fastapi import Request, Depends

from src.api.middleware.authentication import get_current_user as _get_current_user


def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Get current authenticated user from request.
    Returns user information stored in request state.
    """
    return _get_current_user(request)


def get_current_optional_user(request: Request) -> Optional[Dict[str, Any]]:
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


# Export commonly used dependencies
__all__ = [
    "get_current_user",
    "get_current_optional_user",
]