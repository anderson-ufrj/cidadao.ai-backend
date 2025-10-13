"""Authentication service using PostgreSQL database"""

from datetime import UTC, datetime, timedelta
from typing import Any, Optional
from uuid import UUID, uuid4

import asyncpg
import bcrypt
from asyncpg.pool import Pool
from jose import JWTError, jwt
from pydantic import EmailStr

from src.core.config import settings
from src.core.exceptions import AuthenticationError, ValidationError
from src.infrastructure.database import get_db_pool


class AuthService:
    """Service for handling authentication with PostgreSQL backend"""

    def __init__(self):
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(minutes=30)
        self.refresh_token_expire = timedelta(days=7)
        self._pool: Optional[Pool] = None

    async def get_pool(self) -> Pool:
        """Get database connection pool"""
        if self._pool is None:
            self._pool = await get_db_pool()
        return self._pool

    async def create_user(
        self,
        username: str,
        email: EmailStr,
        password: str,
        full_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new user in the database"""
        # Validate password strength
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")

        # Hash password
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        pool = await self.get_pool()

        try:
            async with pool.acquire() as conn:
                # Check if user already exists
                existing = await conn.fetchrow(
                    "SELECT id FROM users WHERE username = $1 OR email = $2",
                    username,
                    email,
                )
                if existing:
                    raise ValidationError("Username or email already exists")

                # Create user
                user = await conn.fetchrow(
                    """
                    INSERT INTO users (username, email, password_hash, full_name)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id, username, email, full_name, is_active, is_admin, created_at
                """,
                    username,
                    email,
                    password_hash.decode("utf-8"),
                    full_name,
                )

                return dict(user)

        except asyncpg.UniqueViolationError:
            raise ValidationError("Username or email already exists")

    async def authenticate_user(
        self, username: str, password: str
    ) -> Optional[dict[str, Any]]:
        """Authenticate user with username and password"""
        pool = await self.get_pool()

        async with pool.acquire() as conn:
            # Get user by username or email
            user = await conn.fetchrow(
                """
                SELECT id, username, email, password_hash, full_name,
                       is_active, is_admin, failed_login_attempts, locked_until
                FROM users
                WHERE username = $1 OR email = $1
            """,
                username,
            )

            if not user:
                return None

            user_dict = dict(user)

            # Check if account is locked
            if user_dict["locked_until"] and user_dict["locked_until"] > datetime.now(
                UTC
            ):
                raise AuthenticationError("Account is locked. Please try again later.")

            # Check if account is active
            if not user_dict["is_active"]:
                raise AuthenticationError("Account is deactivated")

            # Verify password
            if not bcrypt.checkpw(
                password.encode("utf-8"), user_dict["password_hash"].encode("utf-8")
            ):
                # Increment failed login attempts
                await self._increment_failed_attempts(conn, user_dict["id"])
                return None

            # Reset failed attempts on successful login
            await conn.execute(
                """
                UPDATE users
                SET failed_login_attempts = 0,
                    locked_until = NULL,
                    last_login = $1
                WHERE id = $2
            """,
                datetime.now(UTC),
                user_dict["id"],
            )

            # Remove password hash from return
            user_dict.pop("password_hash")
            return user_dict

    async def _increment_failed_attempts(self, conn: asyncpg.Connection, user_id: UUID):
        """Increment failed login attempts and lock account if necessary"""
        result = await conn.fetchrow(
            """
            UPDATE users
            SET failed_login_attempts = failed_login_attempts + 1
            WHERE id = $1
            RETURNING failed_login_attempts
        """,
            user_id,
        )

        # Lock account after 5 failed attempts
        if result["failed_login_attempts"] >= 5:
            locked_until = datetime.now(UTC) + timedelta(minutes=30)
            await conn.execute(
                """
                UPDATE users
                SET locked_until = $1
                WHERE id = $2
            """,
                locked_until,
                user_id,
            )

    def create_access_token(self, data: dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.now(UTC) + self.access_token_expire
        to_encode.update(
            {
                "exp": expire,
                "type": "access",
                "jti": str(uuid4()),  # JWT ID for blacklisting
            }
        )
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=self.algorithm)

    def create_refresh_token(self, data: dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.now(UTC) + self.refresh_token_expire
        to_encode.update(
            {
                "exp": expire,
                "type": "refresh",
                "jti": str(uuid4()),  # JWT ID for blacklisting
            }
        )
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=self.algorithm)

    async def verify_token(
        self, token: str, token_type: str = "access"
    ) -> dict[str, Any]:
        """Verify JWT token and check blacklist"""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[self.algorithm]
            )

            # Check token type
            if payload.get("type") != token_type:
                raise AuthenticationError("Invalid token type")

            # Check if token is blacklisted
            if await self._is_token_blacklisted(payload.get("jti")):
                raise AuthenticationError("Token has been revoked")

            return payload

        except JWTError:
            raise AuthenticationError("Invalid token")

    async def _is_token_blacklisted(self, jti: Optional[str]) -> bool:
        """Check if token JTI is in blacklist"""
        if not jti:
            return False

        pool = await self.get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT id FROM jwt_blacklist WHERE token_jti = $1", jti
            )
            return result is not None

    async def revoke_token(self, token: str, reason: Optional[str] = None):
        """Add token to blacklist"""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[self.algorithm]
            )
            jti = payload.get("jti")
            if not jti:
                return

            pool = await self.get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO jwt_blacklist (token_jti, user_id, expires_at, reason)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (token_jti) DO NOTHING
                """,
                    jti,
                    payload.get("sub"),
                    datetime.fromtimestamp(payload.get("exp"), tz=UTC),
                    reason,
                )

        except JWTError:
            pass  # Invalid token, ignore

    async def get_current_user(self, token: str) -> Optional[dict[str, Any]]:
        """Get current user from token"""
        payload = await self.verify_token(token)
        user_id = payload.get("sub")

        if not user_id:
            return None

        pool = await self.get_pool()
        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                """
                SELECT id, username, email, full_name, is_active, is_admin, created_at
                FROM users
                WHERE id = $1 AND is_active = true
            """,
                UUID(user_id),
            )

            return dict(user) if user else None

    async def refresh_access_token(self, refresh_token: str) -> dict[str, str]:
        """Create new access token from refresh token"""
        payload = await self.verify_token(refresh_token, token_type="refresh")

        # Get user to ensure they still exist and are active
        user = await self.get_current_user(refresh_token)
        if not user:
            raise AuthenticationError("User not found or inactive")

        # Create new tokens
        access_token = self.create_access_token({"sub": str(user["id"])})
        new_refresh_token = self.create_refresh_token({"sub": str(user["id"])})

        # Revoke old refresh token
        await self.revoke_token(refresh_token, "Token refreshed")

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    async def cleanup_expired_tokens(self):
        """Remove expired tokens from blacklist"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM jwt_blacklist
                WHERE expires_at < $1
            """,
                datetime.now(UTC),
            )

    async def change_password(
        self, user_id: UUID, current_password: str, new_password: str
    ) -> bool:
        """Change user password"""
        if len(new_password) < 8:
            raise ValidationError("Password must be at least 8 characters long")

        pool = await self.get_pool()
        async with pool.acquire() as conn:
            # Get current password hash
            user = await conn.fetchrow(
                "SELECT password_hash FROM users WHERE id = $1", user_id
            )

            if not user:
                return False

            # Verify current password
            if not bcrypt.checkpw(
                current_password.encode("utf-8"), user["password_hash"].encode("utf-8")
            ):
                raise AuthenticationError("Current password is incorrect")

            # Hash new password
            new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())

            # Update password
            await conn.execute(
                """
                UPDATE users
                SET password_hash = $1, updated_at = $2
                WHERE id = $3
            """,
                new_hash.decode("utf-8"),
                datetime.now(UTC),
                user_id,
            )

            return True


# Singleton instance
auth_service = AuthService()
