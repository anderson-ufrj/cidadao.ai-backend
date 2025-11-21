"""
Authentication and authorization module for Cidadão.AI
Handles JWT tokens, user management, and security
"""

import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Optional

import bcrypt
import jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..core.secret_manager import get_secret_manager


@dataclass
class User:
    """User model"""

    id: str
    email: str
    name: str
    role: str
    is_active: bool = True
    created_at: datetime = None
    last_login: datetime = None


class AuthManager:
    """Handles authentication and JWT token management"""

    def __init__(self):
        # Security: JWT Secret Key is required
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        if not jwt_secret:
            raise ValueError("JWT_SECRET_KEY environment variable is required")

        self.secret_key = jwt_secret
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )
        self.refresh_token_expire_days = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
        )

        # Initialize user database from environment or create empty
        self.users_db = self._initialize_users()

    def _initialize_users(self) -> dict[str, dict[str, Any]]:
        """Initialize users from environment variables or return empty database"""
        users_db = {}

        # Check for admin user from environment
        admin_email = os.getenv("ADMIN_USER_EMAIL")
        admin_password = os.getenv("ADMIN_USER_PASSWORD")

        if admin_email and admin_password:
            users_db[admin_email] = {
                "id": "admin_1",
                "email": admin_email,
                "name": os.getenv("ADMIN_USER_NAME", "Administrador"),
                "password_hash": self._hash_password(admin_password),
                "role": "admin",
                "is_active": True,
                "created_at": datetime.now(UTC),
            }

        # Check for analyst user from environment
        analyst_email = os.getenv("ANALYST_USER_EMAIL")
        analyst_password = os.getenv("ANALYST_USER_PASSWORD")

        if analyst_email and analyst_password:
            users_db[analyst_email] = {
                "id": "analyst_1",
                "email": analyst_email,
                "name": os.getenv("ANALYST_USER_NAME", "Analista"),
                "password_hash": self._hash_password(analyst_password),
                "role": "analyst",
                "is_active": True,
                "created_at": datetime.now(UTC),
            }

        return users_db

    @classmethod
    async def from_vault(cls, vault_enabled: bool = True):
        """Create AuthManager instance with Vault-based user initialization"""
        instance = cls.__new__(cls)  # Create instance without calling __init__

        if vault_enabled:
            try:
                # Get secret manager and user credentials
                secret_manager = await get_secret_manager()
                user_secrets = await secret_manager.get_secrets_schema("users")

                # Initialize JWT secret from Vault
                jwt_result = await secret_manager.get_secret("jwt/secret_key")
                if not jwt_result.found:
                    raise ValueError("JWT_SECRET_KEY not found in Vault or environment")

                instance.secret_key = jwt_result.value
                instance.algorithm = "HS256"
                instance.access_token_expire_minutes = int(
                    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
                )
                instance.refresh_token_expire_days = int(
                    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
                )

                # Initialize users from Vault
                instance.users_db = {}

                if user_secrets:
                    # Admin user
                    if user_secrets.admin_email and user_secrets.admin_password:
                        instance.users_db[user_secrets.admin_email] = {
                            "id": "admin_vault",
                            "email": user_secrets.admin_email,
                            "name": user_secrets.admin_name or "Administrator",
                            "password_hash": instance._hash_password(
                                user_secrets.admin_password.get_secret_value()
                            ),
                            "role": "admin",
                            "is_active": True,
                            "created_at": datetime.now(UTC),
                        }

                    # Analyst user
                    if user_secrets.analyst_email and user_secrets.analyst_password:
                        instance.users_db[user_secrets.analyst_email] = {
                            "id": "analyst_vault",
                            "email": user_secrets.analyst_email,
                            "name": user_secrets.analyst_name or "Analyst",
                            "password_hash": instance._hash_password(
                                user_secrets.analyst_password.get_secret_value()
                            ),
                            "role": "analyst",
                            "is_active": True,
                            "created_at": datetime.now(UTC),
                        }

                return instance

            except Exception as e:
                print(
                    f"Vault initialization failed, falling back to standard init: {e}"
                )
                # Fall back to standard initialization
                return cls()
        else:
            return cls()

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user_data = self.users_db.get(email)
        if not user_data:
            return None

        if not self._verify_password(password, user_data["password_hash"]):
            return None

        if not user_data["is_active"]:
            return None

        # Update last login
        self.users_db[email]["last_login"] = datetime.now(UTC)

        return User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            role=user_data["role"],
            is_active=user_data["is_active"],
            created_at=user_data["created_at"],
            last_login=user_data["last_login"],
        )

    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        expire = datetime.now(UTC) + timedelta(minutes=self.access_token_expire_minutes)

        payload = {
            "sub": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "exp": expire,
            "iat": datetime.now(UTC),
            "type": "access",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token"""
        expire = datetime.now(UTC) + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": user.id,
            "exp": expire,
            "iat": datetime.now(UTC),
            "type": "refresh",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    def get_current_user(self, token: str) -> User:
        """Get current user from token"""
        payload = self.verify_token(token)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        user_email = payload.get("email")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        user_data = self.users_db.get(user_email)
        if not user_data or not user_data["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        return User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            role=user_data["role"],
            is_active=user_data["is_active"],
            created_at=user_data["created_at"],
            last_login=user_data.get("last_login"),
        )

    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token"""
        payload = self.verify_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        # Find user by ID
        user_data = None
        for email, data in self.users_db.items():
            if data["id"] == user_id:
                user_data = data
                break

        if not user_data or not user_data["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        user = User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            role=user_data["role"],
            is_active=user_data["is_active"],
        )

        return self.create_access_token(user)

    def register_user(
        self, email: str, password: str, name: str, role: str = "analyst"
    ) -> User:
        """Register new user"""
        if email in self.users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user_id = f"user_{len(self.users_db) + 1}"
        password_hash = self._hash_password(password)

        user_data = {
            "id": user_id,
            "email": email,
            "name": name,
            "password_hash": password_hash,
            "role": role,
            "is_active": True,
            "created_at": datetime.now(UTC),
        }

        self.users_db[email] = user_data

        return User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            role=user_data["role"],
            is_active=user_data["is_active"],
            created_at=user_data["created_at"],
        )

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        """Change user password"""
        # Find user by ID
        user_data = None
        user_email = None
        for email, data in self.users_db.items():
            if data["id"] == user_id:
                user_data = data
                user_email = email
                break

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not self._verify_password(old_password, user_data["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid current password",
            )

        # Update password
        self.users_db[user_email]["password_hash"] = self._hash_password(new_password)
        return True

    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        for email, data in self.users_db.items():
            if data["id"] == user_id:
                self.users_db[email]["is_active"] = False
                return True

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    def get_all_users(self) -> list[User]:
        """Get all users (admin only)"""
        users = []
        for data in self.users_db.values():
            users.append(
                User(
                    id=data["id"],
                    email=data["email"],
                    name=data["name"],
                    role=data["role"],
                    is_active=data["is_active"],
                    created_at=data["created_at"],
                    last_login=data.get("last_login"),
                )
            )
        return users


# Global auth manager instance
auth_manager = AuthManager()

# FastAPI security scheme
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = None) -> User:
    """FastAPI dependency to get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    return auth_manager.get_current_user(credentials.credentials)


def require_role(required_role: str):
    """Decorator to require specific role"""

    def role_checker(user: User) -> User:
        if user.role != required_role and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required",
            )
        return user

    return role_checker


def require_admin(user: User = None) -> User:
    """Require admin role"""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required"
        )
    return user
