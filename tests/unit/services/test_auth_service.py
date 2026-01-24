"""Tests for authentication service."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from src.core.exceptions import AuthenticationError, ValidationError
from src.services.auth_service import AuthService, auth_service


class TestAuthServiceInitialization:
    """Tests for AuthService initialization."""

    def test_initialization(self):
        """Test auth service initialization."""
        service = AuthService()

        assert service.algorithm == "HS256"
        assert service.access_token_expire == timedelta(minutes=30)
        assert service.refresh_token_expire == timedelta(days=7)
        assert service._pool is None

    def test_singleton_instance(self):
        """Test singleton auth_service exists."""
        assert auth_service is not None
        assert isinstance(auth_service, AuthService)


class TestGetPool:
    """Tests for get_pool method."""

    @pytest.fixture
    def service(self):
        """Create auth service for testing."""
        return AuthService()

    @pytest.mark.asyncio
    async def test_get_pool_creates_pool(self, service):
        """Test pool creation."""
        mock_pool = AsyncMock()

        with patch(
            "src.services.auth_service.get_db_pool", return_value=mock_pool
        ):
            pool = await service.get_pool()

            assert pool is mock_pool
            assert service._pool is mock_pool

    @pytest.mark.asyncio
    async def test_get_pool_returns_cached(self, service):
        """Test pool is reused."""
        mock_pool = AsyncMock()
        service._pool = mock_pool

        with patch("src.services.auth_service.get_db_pool") as mock_get:
            pool = await service.get_pool()

            assert pool is mock_pool
            mock_get.assert_not_called()


class TestCreateUser:
    """Tests for create_user method."""

    @pytest.fixture
    def service(self):
        """Create auth service for testing."""
        return AuthService()

    @pytest.mark.asyncio
    async def test_create_user_success(self, service):
        """Test successful user creation."""
        user_id = uuid4()
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(
            side_effect=[
                None,  # Check existing user
                {
                    "id": user_id,
                    "username": "testuser",
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "is_active": True,
                    "is_admin": False,
                    "created_at": datetime.now(UTC),
                },
            ]
        )

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock())
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch.object(service, "get_pool", return_value=mock_pool):
            result = await service.create_user(
                username="testuser",
                email="test@example.com",
                password="securepassword123",
                full_name="Test User",
            )

            assert result["username"] == "testuser"
            assert result["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_create_user_weak_password(self, service):
        """Test password validation."""
        with pytest.raises(ValidationError, match="at least 8 characters"):
            await service.create_user(
                username="testuser",
                email="test@example.com",
                password="short",
            )

    @pytest.mark.asyncio
    async def test_create_user_already_exists(self, service):
        """Test user already exists error."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={"id": uuid4()})

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock())
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch.object(service, "get_pool", return_value=mock_pool):
            with pytest.raises(ValidationError, match="already exists"):
                await service.create_user(
                    username="existing",
                    email="existing@example.com",
                    password="securepassword123",
                )


class TestAuthenticateUser:
    """Tests for authenticate_user method."""

    @pytest.fixture
    def service(self):
        """Create auth service for testing."""
        return AuthService()

    @pytest.mark.asyncio
    async def test_authenticate_success(self, service):
        """Test successful authentication."""
        import bcrypt

        password = "correctpassword"
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        user_data = {
            "id": uuid4(),
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": password_hash.decode(),
            "full_name": "Test User",
            "is_active": True,
            "is_admin": False,
            "failed_login_attempts": 0,
            "locked_until": None,
        }

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=user_data)
        mock_conn.execute = AsyncMock()

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock())
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch.object(service, "get_pool", return_value=mock_pool):
            result = await service.authenticate_user("testuser", password)

            assert result is not None
            assert result["username"] == "testuser"
            assert "password_hash" not in result

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, service):
        """Test authentication with non-existent user."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock())
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch.object(service, "get_pool", return_value=mock_pool):
            result = await service.authenticate_user("nonexistent", "password")

            assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self, service):
        """Test authentication with wrong password."""
        import bcrypt

        correct_hash = bcrypt.hashpw(b"correctpassword", bcrypt.gensalt())

        user_data = {
            "id": uuid4(),
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": correct_hash.decode(),
            "full_name": "Test User",
            "is_active": True,
            "is_admin": False,
            "failed_login_attempts": 0,
            "locked_until": None,
        }

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=user_data)

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock())
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch.object(
            service, "_increment_failed_attempts"
        ) as mock_increment, patch.object(service, "get_pool", return_value=mock_pool):
            mock_increment.return_value = None

            result = await service.authenticate_user("testuser", "wrongpassword")

            assert result is None
            mock_increment.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_locked_account(self, service):
        """Test authentication with locked account."""
        user_data = {
            "id": uuid4(),
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hash",
            "full_name": "Test User",
            "is_active": True,
            "is_admin": False,
            "failed_login_attempts": 5,
            "locked_until": datetime.now(UTC) + timedelta(minutes=30),
        }

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=user_data)

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock())
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch.object(service, "get_pool", return_value=mock_pool):
            with pytest.raises(AuthenticationError, match="locked"):
                await service.authenticate_user("testuser", "password")

    @pytest.mark.asyncio
    async def test_authenticate_inactive_account(self, service):
        """Test authentication with inactive account."""
        user_data = {
            "id": uuid4(),
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hash",
            "full_name": "Test User",
            "is_active": False,
            "is_admin": False,
            "failed_login_attempts": 0,
            "locked_until": None,
        }

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=user_data)

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock())
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch.object(service, "get_pool", return_value=mock_pool):
            with pytest.raises(AuthenticationError, match="deactivated"):
                await service.authenticate_user("testuser", "password")


class TestTokenCreation:
    """Tests for token creation methods."""

    @pytest.fixture
    def service(self):
        """Create auth service for testing."""
        return AuthService()

    def test_create_access_token(self, service):
        """Test access token creation."""
        with patch("src.services.auth_service.settings") as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test-secret-key"

            token = service.create_access_token({"sub": "user123"})

            assert isinstance(token, str)
            assert len(token) > 0

    def test_create_refresh_token(self, service):
        """Test refresh token creation."""
        with patch("src.services.auth_service.settings") as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test-secret-key"

            token = service.create_refresh_token({"sub": "user123"})

            assert isinstance(token, str)
            assert len(token) > 0


class TestTokenVerification:
    """Tests for token verification methods."""

    @pytest.fixture
    def service(self):
        """Create auth service for testing."""
        return AuthService()

    @pytest.mark.asyncio
    async def test_verify_token_valid(self, service):
        """Test verifying valid token."""
        with patch("src.services.auth_service.settings") as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test-secret-key"

            # Create a valid token
            token = service.create_access_token({"sub": "user123"})

            with patch.object(
                service, "_is_token_blacklisted", return_value=False
            ):
                payload = await service.verify_token(token, token_type="access")

                assert payload["sub"] == "user123"
                assert payload["type"] == "access"

    @pytest.mark.asyncio
    async def test_verify_token_wrong_type(self, service):
        """Test verifying token with wrong type."""
        with patch("src.services.auth_service.settings") as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test-secret-key"

            # Create an access token
            token = service.create_access_token({"sub": "user123"})

            with patch.object(
                service, "_is_token_blacklisted", return_value=False
            ):
                with pytest.raises(AuthenticationError, match="Invalid token type"):
                    await service.verify_token(token, token_type="refresh")

    @pytest.mark.asyncio
    async def test_verify_token_blacklisted(self, service):
        """Test verifying blacklisted token."""
        with patch("src.services.auth_service.settings") as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test-secret-key"

            token = service.create_access_token({"sub": "user123"})

            with patch.object(
                service, "_is_token_blacklisted", return_value=True
            ):
                with pytest.raises(AuthenticationError, match="revoked"):
                    await service.verify_token(token)

    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, service):
        """Test verifying invalid token."""
        with pytest.raises(AuthenticationError, match="Invalid token"):
            await service.verify_token("invalid.token.here")


class TestTokenBlacklist:
    """Tests for token blacklist methods."""

    @pytest.fixture
    def service(self):
        """Create auth service for testing."""
        return AuthService()

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_true(self, service):
        """Test checking blacklisted token."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={"id": 1})

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock())
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch.object(service, "get_pool", return_value=mock_pool):
            result = await service._is_token_blacklisted("jti-123")

            assert result is True

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_false(self, service):
        """Test checking non-blacklisted token."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock())
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch.object(service, "get_pool", return_value=mock_pool):
            result = await service._is_token_blacklisted("jti-456")

            assert result is False

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_no_jti(self, service):
        """Test checking without JTI."""
        result = await service._is_token_blacklisted(None)

        assert result is False

    @pytest.mark.asyncio
    async def test_revoke_token(self, service):
        """Test revoking token."""
        with patch("src.services.auth_service.settings") as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test-secret-key"

            token = service.create_access_token({"sub": "user123"})

            mock_conn = AsyncMock()
            mock_conn.execute = AsyncMock()

            mock_pool = AsyncMock()
            mock_pool.acquire = MagicMock(return_value=AsyncMock())
            mock_pool.acquire.return_value.__aenter__ = AsyncMock(
                return_value=mock_conn
            )
            mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

            with patch.object(service, "get_pool", return_value=mock_pool):
                await service.revoke_token(token, "User logout")

                mock_conn.execute.assert_called_once()


class TestGetCurrentUser:
    """Tests for get_current_user method."""

    @pytest.fixture
    def service(self):
        """Create auth service for testing."""
        return AuthService()

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, service):
        """Test getting current user."""
        user_id = uuid4()

        with patch("src.services.auth_service.settings") as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test-secret-key"

            token = service.create_access_token({"sub": str(user_id)})

            user_data = {
                "id": user_id,
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "is_active": True,
                "is_admin": False,
                "created_at": datetime.now(UTC),
            }

            mock_conn = AsyncMock()
            mock_conn.fetchrow = AsyncMock(return_value=user_data)

            mock_pool = AsyncMock()
            mock_pool.acquire = MagicMock(return_value=AsyncMock())
            mock_pool.acquire.return_value.__aenter__ = AsyncMock(
                return_value=mock_conn
            )
            mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

            with patch.object(
                service, "_is_token_blacklisted", return_value=False
            ), patch.object(service, "get_pool", return_value=mock_pool):
                result = await service.get_current_user(token)

                assert result is not None
                assert result["username"] == "testuser"


class TestChangePassword:
    """Tests for change_password method."""

    @pytest.fixture
    def service(self):
        """Create auth service for testing."""
        return AuthService()

    @pytest.mark.asyncio
    async def test_change_password_success(self, service):
        """Test successful password change."""
        import bcrypt

        user_id = uuid4()
        current_password = "oldpassword123"
        current_hash = bcrypt.hashpw(current_password.encode(), bcrypt.gensalt())

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(
            return_value={"password_hash": current_hash.decode()}
        )
        mock_conn.execute = AsyncMock()

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock())
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch.object(service, "get_pool", return_value=mock_pool):
            result = await service.change_password(
                user_id, current_password, "newpassword456"
            )

            assert result is True
            mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_weak_new_password(self, service):
        """Test password change with weak new password."""
        with pytest.raises(ValidationError, match="at least 8 characters"):
            await service.change_password(uuid4(), "oldpassword", "short")

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, service):
        """Test password change with wrong current password."""
        import bcrypt

        user_id = uuid4()
        correct_hash = bcrypt.hashpw(b"correctpassword", bcrypt.gensalt())

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(
            return_value={"password_hash": correct_hash.decode()}
        )

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock())
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch.object(service, "get_pool", return_value=mock_pool):
            with pytest.raises(AuthenticationError, match="incorrect"):
                await service.change_password(
                    user_id, "wrongpassword", "newpassword456"
                )

    @pytest.mark.asyncio
    async def test_change_password_user_not_found(self, service):
        """Test password change for non-existent user."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock())
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch.object(service, "get_pool", return_value=mock_pool):
            result = await service.change_password(
                uuid4(), "oldpassword", "newpassword456"
            )

            assert result is False


class TestCleanupExpiredTokens:
    """Tests for cleanup_expired_tokens method."""

    @pytest.fixture
    def service(self):
        """Create auth service for testing."""
        return AuthService()

    @pytest.mark.asyncio
    async def test_cleanup_expired_tokens(self, service):
        """Test cleaning up expired tokens."""
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock())
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch.object(service, "get_pool", return_value=mock_pool):
            await service.cleanup_expired_tokens()

            mock_conn.execute.assert_called_once()


class TestRefreshAccessToken:
    """Tests for refresh_access_token method."""

    @pytest.fixture
    def service(self):
        """Create auth service for testing."""
        return AuthService()

    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, service):
        """Test successful token refresh."""
        user_id = uuid4()

        with patch("src.services.auth_service.settings") as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test-secret-key"

            refresh_token = service.create_refresh_token({"sub": str(user_id)})

            user_data = {
                "id": user_id,
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "is_active": True,
                "is_admin": False,
                "created_at": datetime.now(UTC),
            }

            with patch.object(
                service, "_is_token_blacklisted", return_value=False
            ), patch.object(service, "get_current_user", return_value=user_data), patch.object(
                service, "revoke_token"
            ) as mock_revoke:
                result = await service.refresh_access_token(refresh_token)

                assert "access_token" in result
                assert "refresh_token" in result
                assert result["token_type"] == "bearer"
                mock_revoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_access_token_user_not_found(self, service):
        """Test token refresh when user not found."""
        user_id = uuid4()

        with patch("src.services.auth_service.settings") as mock_settings:
            mock_settings.JWT_SECRET_KEY = "test-secret-key"

            refresh_token = service.create_refresh_token({"sub": str(user_id)})

            with patch.object(
                service, "_is_token_blacklisted", return_value=False
            ), patch.object(service, "get_current_user", return_value=None):
                with pytest.raises(AuthenticationError, match="not found"):
                    await service.refresh_access_token(refresh_token)


class TestIncrementFailedAttempts:
    """Tests for _increment_failed_attempts method."""

    @pytest.fixture
    def service(self):
        """Create auth service for testing."""
        return AuthService()

    @pytest.mark.asyncio
    async def test_increment_below_threshold(self, service):
        """Test incrementing failed attempts below threshold."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={"failed_login_attempts": 3})

        await service._increment_failed_attempts(mock_conn, uuid4())

        # Should not call execute to lock (only fetchrow for update)
        mock_conn.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_increment_locks_at_threshold(self, service):
        """Test account lock at 5 failed attempts."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={"failed_login_attempts": 5})
        mock_conn.execute = AsyncMock()

        await service._increment_failed_attempts(mock_conn, uuid4())

        # Should call execute to set locked_until
        mock_conn.execute.assert_called_once()
