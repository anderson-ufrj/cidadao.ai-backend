"""
Database-backed authentication module for Cidadão.AI
Replaces in-memory storage with PostgreSQL
"""

import os
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.exceptions import AuthenticationError, ValidationError
from src.services.auth_service import auth_service


class User:
    """User model compatible with existing code"""

    def __init__(self, **kwargs):
        self.id = str(kwargs.get("id"))
        self.email = kwargs.get("email")
        self.name = kwargs.get("full_name", kwargs.get("username"))
        self.username = kwargs.get("username")
        self.role = "admin" if kwargs.get("is_admin") else "analyst"
        self.is_active = kwargs.get("is_active", True)
        self.created_at = kwargs.get("created_at")
        self.last_login = kwargs.get("last_login")


class AuthManager:
    """Database-backed authentication manager"""

    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY environment variable is required")

        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )
        self.refresh_token_expire_days = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
        )
        self._auth_service = auth_service

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        try:
            user_data = await self._auth_service.authenticate_user(username, password)
            if user_data:
                return User(**user_data)
            return None
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        return self._auth_service.create_access_token({"sub": user.id})

    def create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token"""
        return self._auth_service.create_refresh_token({"sub": user.id})

    async def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            return await self._auth_service.verify_token(token)
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    async def get_current_user(self, token: str) -> User:
        """Get current user from token"""
        try:
            user_data = await self._auth_service.get_current_user(token)
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive",
                )
            return User(**user_data)
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    async def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token"""
        try:
            tokens = await self._auth_service.refresh_access_token(refresh_token)
            return tokens["access_token"]
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    async def register_user(
        self, email: str, password: str, name: str, role: str = "analyst"
    ) -> User:
        """Register new user"""
        try:
            # Use email as username if not provided
            username = email.split("@")[0]
            is_admin = role == "admin"

            user_data = await self._auth_service.create_user(
                username=username, email=email, password=password, full_name=name
            )

            # Update admin status if needed
            if is_admin and user_data:
                # This would need a separate method in auth_service
                # For now, admin users must be set directly in database
                pass

            return User(**user_data)

        except ValidationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        """Change user password"""
        try:
            return await self._auth_service.change_password(
                UUID(user_id), old_password, new_password
            )
        except (ValidationError, AuthenticationError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        # This would need implementation in auth_service
        # For now, return not implemented
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="User deactivation not implemented yet",
        )

    async def get_all_users(self) -> list[User]:
        """Get all users (admin only)"""
        # This would need implementation in auth_service
        # For now, return empty list
        return []

    async def revoke_token(self, token: str, reason: Optional[str] = None):
        """Add token to blacklist"""
        await self._auth_service.revoke_token(token, reason)

    @classmethod
    async def from_vault(cls, vault_enabled: bool = True):
        """Create AuthManager instance - for compatibility"""
        return cls()


# Create async-safe auth manager getter
_auth_manager_instance = None


async def get_auth_manager() -> AuthManager:
    """Get or create auth manager instance"""
    global _auth_manager_instance
    if _auth_manager_instance is None:
        _auth_manager_instance = AuthManager()
    return _auth_manager_instance


# FastAPI dependencies
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """FastAPI dependency to get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    auth = await get_auth_manager()
    return await auth.get_current_user(credentials.credentials)


def require_role(required_role: str):
    """Decorator to require specific role"""

    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role != required_role and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required",
            )
        return user

    return role_checker


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required"
        )
    return user
