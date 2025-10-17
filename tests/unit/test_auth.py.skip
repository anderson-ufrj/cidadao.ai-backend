"""Unit tests for authentication system."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from jose import jwt

from src.api.auth import (
    AuthManager,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    verify_password,
    verify_token,
)
from src.core.exceptions import UnauthorizedError
from src.models.user import User


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing creates different hash each time."""
        password = "secure_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Different salts
        assert hash1.startswith("$2b$")  # bcrypt format
        assert len(hash1) > 50  # Reasonable hash length

    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "test_password_456"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False


class TestTokenCreation:
    """Test JWT token creation."""

    @pytest.fixture
    def settings(self):
        """Mock settings."""
        settings = MagicMock()
        settings.JWT_SECRET_KEY = "test_secret_key_123"
        settings.JWT_ALGORITHM = "HS256"
        settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        settings.REFRESH_TOKEN_EXPIRE_DAYS = 7
        return settings

    def test_create_access_token(self, settings):
        """Test access token creation."""
        with patch("src.api.auth.get_settings", return_value=settings):
            user_id = "user123"
            email = "test@example.com"
            role = "user"

            token = create_access_token(user_id, email, role)

            # Decode and verify token
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )

            assert payload["sub"] == user_id
            assert payload["email"] == email
            assert payload["role"] == role
            assert payload["type"] == "access"
            assert "exp" in payload
            assert "iat" in payload

    def test_create_refresh_token(self, settings):
        """Test refresh token creation."""
        with patch("src.api.auth.get_settings", return_value=settings):
            user_id = "user456"

            token = create_refresh_token(user_id)

            # Decode and verify token
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )

            assert payload["sub"] == user_id
            assert payload["type"] == "refresh"
            assert "exp" in payload
            assert "iat" in payload

    def test_token_expiration(self, settings):
        """Test token expiration times."""
        with patch("src.api.auth.get_settings", return_value=settings):
            # Create tokens
            access_token = create_access_token("user1", "user@test.com", "user")
            refresh_token = create_refresh_token("user1")

            # Decode tokens
            access_payload = jwt.decode(
                access_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            refresh_payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )

            # Check expiration times
            access_exp = datetime.fromtimestamp(access_payload["exp"])
            refresh_exp = datetime.fromtimestamp(refresh_payload["exp"])
            now = datetime.utcnow()

            # Access token should expire in ~30 minutes
            assert (access_exp - now) < timedelta(minutes=31)
            assert (access_exp - now) > timedelta(minutes=29)

            # Refresh token should expire in ~7 days
            assert (refresh_exp - now) < timedelta(days=7, minutes=1)
            assert (refresh_exp - now) > timedelta(days=6, hours=23)


class TestTokenVerification:
    """Test JWT token verification."""

    @pytest.fixture
    def settings(self):
        """Mock settings."""
        settings = MagicMock()
        settings.JWT_SECRET_KEY = "test_secret_key_789"
        settings.JWT_ALGORITHM = "HS256"
        return settings

    @pytest.mark.asyncio
    async def test_verify_valid_token(self, settings):
        """Test verifying valid token."""
        with patch("src.api.auth.get_settings", return_value=settings):
            # Create valid token
            user_id = "valid_user"
            token = create_access_token(user_id, "test@example.com", "user")

            # Verify token
            payload = await verify_token(token)

            assert payload["sub"] == user_id
            assert payload["type"] == "access"

    @pytest.mark.asyncio
    async def test_verify_expired_token(self, settings):
        """Test verifying expired token."""
        with patch("src.api.auth.get_settings", return_value=settings):
            # Create expired token
            payload = {
                "sub": "user123",
                "type": "access",
                "exp": datetime.utcnow() - timedelta(hours=1),
                "iat": datetime.utcnow() - timedelta(hours=2),
            }
            expired_token = jwt.encode(
                payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
            )

            # Should raise UnauthorizedError
            with pytest.raises(UnauthorizedError) as exc_info:
                await verify_token(expired_token)

            assert "Token has expired" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_invalid_token(self, settings):
        """Test verifying invalid token."""
        with patch("src.api.auth.get_settings", return_value=settings):
            invalid_token = "invalid.jwt.token"

            # Should raise UnauthorizedError
            with pytest.raises(UnauthorizedError) as exc_info:
                await verify_token(invalid_token)

            assert "Invalid token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_wrong_secret(self, settings):
        """Test verifying token with wrong secret."""
        # Create token with one secret
        with patch("src.api.auth.get_settings", return_value=settings):
            token = create_access_token("user1", "test@example.com", "user")

        # Try to verify with different secret
        settings.JWT_SECRET_KEY = "different_secret"
        with patch("src.api.auth.get_settings", return_value=settings):
            with pytest.raises(UnauthorizedError) as exc_info:
                await verify_token(token)

            assert "Invalid token" in str(exc_info.value)


class TestUserAuthentication:
    """Test user authentication flow."""

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, async_session):
        """Test successful user authentication."""
        # Create test user
        password = "secure_password_123"
        hashed = hash_password(password)

        user = User(email="test@example.com", hashed_password=hashed, is_active=True)
        async_session.add(user)
        await async_session.commit()

        # Mock the database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        async_session.execute.return_value = mock_result

        # Authenticate
        authenticated_user = await authenticate_user(
            async_session, "test@example.com", password
        )

        assert authenticated_user is not None
        assert authenticated_user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, async_session):
        """Test authentication with wrong password."""
        # Create test user
        password = "correct_password"
        hashed = hash_password(password)

        user = User(email="test@example.com", hashed_password=hashed, is_active=True)

        # Mock the database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        async_session.execute.return_value = mock_result

        # Try to authenticate with wrong password
        authenticated_user = await authenticate_user(
            async_session, "test@example.com", "wrong_password"
        )

        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, async_session):
        """Test authentication with non-existent user."""
        # Mock the database query to return None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        async_session.execute.return_value = mock_result

        # Try to authenticate
        authenticated_user = await authenticate_user(
            async_session, "nonexistent@example.com", "any_password"
        )

        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, async_session):
        """Test authentication with inactive user."""
        # Create inactive user
        password = "password123"
        hashed = hash_password(password)

        user = User(
            email="inactive@example.com", hashed_password=hashed, is_active=False
        )

        # Mock the database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        async_session.execute.return_value = mock_result

        # Try to authenticate
        authenticated_user = await authenticate_user(
            async_session, "inactive@example.com", password
        )

        assert authenticated_user is None


class TestGetCurrentUser:
    """Test getting current user from token."""

    @pytest.fixture
    def settings(self):
        """Mock settings."""
        settings = MagicMock()
        settings.JWT_SECRET_KEY = "test_secret"
        settings.JWT_ALGORITHM = "HS256"
        return settings

    @pytest.mark.asyncio
    async def test_get_current_user_valid(self, async_session, settings):
        """Test getting current user with valid token."""
        with patch("src.api.auth.get_settings", return_value=settings):
            # Create test user
            user = User(id="user123", email="current@example.com", is_active=True)

            # Create valid token
            token = create_access_token(user.id, user.email, "user")

            # Mock the database query
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = user
            async_session.execute.return_value = mock_result

            # Get current user
            current_user = await get_current_user(token, async_session)

            assert current_user is not None
            assert current_user.id == "user123"
            assert current_user.email == "current@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, async_session, settings):
        """Test getting current user with invalid token."""
        with patch("src.api.auth.get_settings", return_value=settings):
            invalid_token = "invalid.token"

            # Should raise UnauthorizedError
            with pytest.raises(UnauthorizedError):
                await get_current_user(invalid_token, async_session)

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self, async_session, settings):
        """Test getting current user when user not found in database."""
        with patch("src.api.auth.get_settings", return_value=settings):
            # Create token for non-existent user
            token = create_access_token("ghost_user", "ghost@example.com", "user")

            # Mock the database query to return None
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            async_session.execute.return_value = mock_result

            # Should raise UnauthorizedError
            with pytest.raises(UnauthorizedError) as exc_info:
                await get_current_user(token, async_session)

            assert "User not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_current_user_inactive(self, async_session, settings):
        """Test getting current user when user is inactive."""
        with patch("src.api.auth.get_settings", return_value=settings):
            # Create inactive user
            user = User(id="inactive123", email="inactive@example.com", is_active=False)

            # Create token
            token = create_access_token(user.id, user.email, "user")

            # Mock the database query
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = user
            async_session.execute.return_value = mock_result

            # Should raise UnauthorizedError
            with pytest.raises(UnauthorizedError) as exc_info:
                await get_current_user(token, async_session)

            assert "User is inactive" in str(exc_info.value)


class TestAuthManager:
    """Test AuthManager class methods."""

    @pytest.mark.asyncio
    async def test_auth_service_login(self, async_session):
        """Test AuthService login method."""
        # Create test user
        password = "test_password"
        hashed = hash_password(password)

        user = User(
            id="service_user",
            email="service@example.com",
            hashed_password=hashed,
            is_active=True,
            role="admin",
        )

        # Mock database
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        async_session.execute.return_value = mock_result

        # Test login
        auth_service = AuthManager(async_session)
        tokens = await auth_service.login("service@example.com", password)

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert tokens["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_auth_service_login_failed(self, async_session):
        """Test AuthService login with invalid credentials."""
        # Mock database to return None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        async_session.execute.return_value = mock_result

        # Test login
        auth_service = AuthManager(async_session)

        with pytest.raises(UnauthorizedError) as exc_info:
            await auth_service.login("wrong@example.com", "wrong_password")

        assert "Invalid email or password" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_auth_service_refresh_token(self, async_session):
        """Test AuthService refresh token method."""
        settings = MagicMock()
        settings.JWT_SECRET_KEY = "test_secret"
        settings.JWT_ALGORITHM = "HS256"

        with patch("src.api.auth.get_settings", return_value=settings):
            # Create test user
            user = User(
                id="refresh_user",
                email="refresh@example.com",
                is_active=True,
                role="user",
            )

            # Create refresh token
            refresh_token = create_refresh_token(user.id)

            # Mock database
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = user
            async_session.execute.return_value = mock_result

            # Test refresh
            auth_service = AuthManager(async_session)
            new_tokens = await auth_service.refresh_token(refresh_token)

            assert "access_token" in new_tokens
            assert "refresh_token" in new_tokens
            assert new_tokens["access_token"] != refresh_token
