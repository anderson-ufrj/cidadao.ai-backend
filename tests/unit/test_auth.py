"""Unit tests for authentication system."""

from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from src.api.auth import AuthManager, User


class TestPasswordHashing:
    """Test password hashing and verification."""

    @pytest.fixture
    def auth_manager(self):
        """Create AuthManager instance for testing."""
        return AuthManager()

    def test_hash_password(self, auth_manager):
        """Test password hashing creates different hash each time."""
        password = "secure_password_123"
        hash1 = auth_manager._hash_password(password)
        hash2 = auth_manager._hash_password(password)

        assert hash1 != hash2  # Different salts
        assert hash1.startswith("$2b$")  # bcrypt format
        assert len(hash1) > 50  # Reasonable hash length

    def test_verify_password_correct(self, auth_manager):
        """Test verifying correct password."""
        password = "test_password_456"
        hashed = auth_manager._hash_password(password)

        assert auth_manager._verify_password(password, hashed) is True

    def test_verify_password_incorrect(self, auth_manager):
        """Test verifying incorrect password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = auth_manager._hash_password(password)

        assert auth_manager._verify_password(wrong_password, hashed) is False


class TestTokenCreation:
    """Test JWT token creation."""

    @pytest.fixture
    def auth_manager(self):
        """Create AuthManager instance for testing."""
        return AuthManager()

    def test_create_access_token(self, auth_manager):
        """Test access token creation."""
        user = User(
            id="user123",
            email="test@example.com",
            name="Test User",
            role="user",
            is_active=True,
            created_at=datetime.now(UTC),
        )

        token = auth_manager.create_access_token(user)

        # Decode and verify token
        payload = jwt.decode(
            token, auth_manager.secret_key, algorithms=[auth_manager.algorithm]
        )

        assert payload["sub"] == user.id
        assert payload["email"] == user.email
        assert payload["role"] == user.role
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_refresh_token(self, auth_manager):
        """Test refresh token creation."""
        user = User(
            id="user456", email="test@example.com", name="Test User", role="user"
        )

        token = auth_manager.create_refresh_token(user)

        # Decode and verify token
        payload = jwt.decode(
            token, auth_manager.secret_key, algorithms=[auth_manager.algorithm]
        )

        assert payload["sub"] == user.id
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload

    def test_token_expiration(self, auth_manager):
        """Test token expiration times."""
        user = User(id="user1", email="user@test.com", name="Test User", role="user")

        # Create tokens
        access_token = auth_manager.create_access_token(user)
        refresh_token = auth_manager.create_refresh_token(user)

        # Decode tokens
        access_payload = jwt.decode(
            access_token,
            auth_manager.secret_key,
            algorithms=[auth_manager.algorithm],
        )
        refresh_payload = jwt.decode(
            refresh_token,
            auth_manager.secret_key,
            algorithms=[auth_manager.algorithm],
        )

        # Check expiration times
        access_exp = access_payload["exp"]
        refresh_exp = refresh_payload["exp"]
        now = datetime.now(UTC).timestamp()

        # Access token should expire in ~30 minutes (convert to seconds)
        assert (access_exp - now) < 31 * 60  # Less than 31 minutes
        assert (access_exp - now) > 29 * 60  # More than 29 minutes

        # Refresh token should expire in ~7 days (convert to seconds)
        assert (
            refresh_exp - now
        ) < 7 * 24 * 60 * 60 + 60  # Less than 7 days + 1 minute
        assert (
            refresh_exp - now
        ) > 6 * 24 * 60 * 60 + 23 * 60 * 60  # More than 6 days 23 hours


class TestTokenVerification:
    """Test JWT token verification."""

    @pytest.fixture
    def auth_manager(self):
        """Create AuthManager instance for testing."""
        return AuthManager()

    def test_verify_valid_token(self, auth_manager):
        """Test verifying valid token."""
        # Create valid token
        user = User(
            id="valid_user", email="test@example.com", name="Valid User", role="user"
        )
        token = auth_manager.create_access_token(user)

        # Verify token
        payload = auth_manager.verify_token(token)

        assert payload["sub"] == user.id
        assert payload["type"] == "access"

    def test_verify_expired_token(self, auth_manager):
        """Test verifying expired token."""
        from fastapi import HTTPException

        # Create expired token
        payload = {
            "sub": "user123",
            "type": "access",
            "exp": datetime.now(UTC) - timedelta(hours=1),
            "iat": datetime.now(UTC) - timedelta(hours=2),
        }
        expired_token = jwt.encode(
            payload, auth_manager.secret_key, algorithm=auth_manager.algorithm
        )

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            auth_manager.verify_token(expired_token)

        assert exc_info.value.status_code == 401
        assert "Token expired" in exc_info.value.detail

    def test_verify_invalid_token(self, auth_manager):
        """Test verifying invalid token."""
        from fastapi import HTTPException

        invalid_token = "invalid.jwt.token"

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            auth_manager.verify_token(invalid_token)

        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail

    def test_verify_wrong_secret(self):
        """Test verifying token with wrong secret."""
        from fastapi import HTTPException

        # Create token with one secret
        auth_manager1 = AuthManager()
        user = User(id="user1", email="test@example.com", name="Test User", role="user")
        token = auth_manager1.create_access_token(user)

        # Try to verify with different secret (create new instance)
        import os

        # Temporarily change secret
        original = os.environ.get("JWT_SECRET_KEY")
        os.environ["JWT_SECRET_KEY"] = "different_secret"

        try:
            auth_manager2 = AuthManager()
            with pytest.raises(HTTPException) as exc_info:
                auth_manager2.verify_token(token)

            assert exc_info.value.status_code == 401
            assert "Invalid token" in exc_info.value.detail
        finally:
            # Restore original
            if original:
                os.environ["JWT_SECRET_KEY"] = original
            else:
                os.environ.pop("JWT_SECRET_KEY", None)


class TestUserAuthentication:
    """Test user authentication flow."""

    @pytest.fixture
    def auth_manager(self):
        """Create AuthManager instance for testing."""
        return AuthManager()

    def test_authenticate_user_success(self, auth_manager):
        """Test successful user authentication."""
        # Add test user to auth_manager's users_db
        email = "test@example.com"
        password = "secure_password_123"

        # Register user
        auth_manager.register_user(email, password, "Test User", "user")

        # Authenticate
        authenticated_user = auth_manager.authenticate_user(email, password)

        assert authenticated_user is not None
        assert authenticated_user.email == email
        assert authenticated_user.name == "Test User"
        assert authenticated_user.role == "user"

    def test_authenticate_user_wrong_password(self, auth_manager):
        """Test authentication with wrong password."""
        # Add test user to auth_manager's users_db
        email = "test@example.com"
        password = "correct_password"

        # Register user
        auth_manager.register_user(email, password, "Test User", "user")

        # Try to authenticate with wrong password
        authenticated_user = auth_manager.authenticate_user(email, "wrong_password")

        assert authenticated_user is None

    def test_authenticate_user_not_found(self, auth_manager):
        """Test authentication with non-existent user."""
        # Try to authenticate non-existent user
        authenticated_user = auth_manager.authenticate_user(
            "nonexistent@example.com", "any_password"
        )

        assert authenticated_user is None

    def test_authenticate_inactive_user(self, auth_manager):
        """Test authentication with inactive user."""
        # Add test user
        email = "inactive@example.com"
        password = "password123"

        # Register user
        user = auth_manager.register_user(email, password, "Inactive User", "user")

        # Deactivate the user
        auth_manager.deactivate_user(user.id)

        # Try to authenticate
        authenticated_user = auth_manager.authenticate_user(email, password)

        assert authenticated_user is None


class TestGetCurrentUser:
    """Test getting current user from token."""

    @pytest.fixture
    def auth_manager(self):
        """Create AuthManager instance for testing."""
        return AuthManager()

    def test_get_current_user_valid(self, auth_manager):
        """Test getting current user with valid token."""
        # Register a user
        email = "current@example.com"
        password = "password123"
        user = auth_manager.register_user(email, password, "Current User", "user")

        # Create valid token
        token = auth_manager.create_access_token(user)

        # Get current user
        current_user = auth_manager.get_current_user(token)

        assert current_user is not None
        assert current_user.id == user.id
        assert current_user.email == email

    def test_get_current_user_invalid_token(self, auth_manager):
        """Test getting current user with invalid token."""
        from fastapi import HTTPException

        invalid_token = "invalid.token"

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            auth_manager.get_current_user(invalid_token)

        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail

    def test_get_current_user_not_found(self, auth_manager):
        """Test getting current user when user not found in database."""
        from fastapi import HTTPException

        # Create a user object that won't be in the database
        user = User(
            id="ghost_user", email="ghost@example.com", name="Ghost User", role="user"
        )

        # Create token for non-existent user
        token = auth_manager.create_access_token(user)

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            auth_manager.get_current_user(token)

        assert exc_info.value.status_code == 401
        assert "User not found" in exc_info.value.detail

    def test_get_current_user_inactive(self, auth_manager):
        """Test getting current user when user is inactive."""
        from fastapi import HTTPException

        # Register and deactivate user
        email = "inactive@example.com"
        password = "password123"
        user = auth_manager.register_user(email, password, "Inactive User", "user")
        auth_manager.deactivate_user(user.id)

        # Create token for inactive user
        token = auth_manager.create_access_token(user)

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            auth_manager.get_current_user(token)

        assert exc_info.value.status_code == 401
        assert "inactive" in exc_info.value.detail.lower()


class TestAuthManager:
    """Test AuthManager class methods."""

    @pytest.fixture
    def auth_manager(self):
        """Create AuthManager instance for testing."""
        return AuthManager()

    def test_auth_manager_register_user(self, auth_manager):
        """Test AuthManager register user method."""
        email = "newuser@example.com"
        password = "password123"
        name = "New User"
        role = "user"

        user = auth_manager.register_user(email, password, name, role)

        assert user is not None
        assert user.email == email
        assert user.name == name
        assert user.role == role
        assert user.is_active is True

    def test_auth_manager_register_duplicate_user(self, auth_manager):
        """Test registering duplicate user raises exception."""
        from fastapi import HTTPException

        email = "duplicate@example.com"
        password = "password123"

        # Register first user
        auth_manager.register_user(email, password, "First User", "user")

        # Try to register duplicate
        with pytest.raises(HTTPException) as exc_info:
            auth_manager.register_user(email, password, "Second User", "user")

        assert exc_info.value.status_code == 400
        assert "already registered" in exc_info.value.detail

    def test_auth_manager_change_password(self, auth_manager):
        """Test changing user password."""
        email = "user@example.com"
        old_password = "old_password"
        new_password = "new_password"

        # Register user
        user = auth_manager.register_user(email, old_password, "Test User", "user")

        # Change password
        result = auth_manager.change_password(user.id, old_password, new_password)
        assert result is True

        # Verify old password doesn't work
        assert auth_manager.authenticate_user(email, old_password) is None

        # Verify new password works
        assert auth_manager.authenticate_user(email, new_password) is not None

    def test_auth_manager_refresh_token(self, auth_manager):
        """Test refreshing access token."""

        # Register user
        email = "refresh@example.com"
        user = auth_manager.register_user(email, "password", "Refresh User", "user")

        # Create refresh token
        refresh_token = auth_manager.create_refresh_token(user)

        # Refresh access token
        new_access_token = auth_manager.refresh_access_token(refresh_token)

        assert new_access_token is not None
        assert isinstance(new_access_token, str)

        # Verify new token works
        payload = auth_manager.verify_token(new_access_token)
        assert payload["sub"] == user.id

    def test_auth_manager_get_all_users(self, auth_manager):
        """Test getting all users."""
        # Register multiple users
        auth_manager.register_user("user1@example.com", "pass1", "User 1", "user")
        auth_manager.register_user("user2@example.com", "pass2", "User 2", "admin")
        auth_manager.register_user("user3@example.com", "pass3", "User 3", "analyst")

        # Get all users
        users = auth_manager.get_all_users()

        # Should have at least 3 users (may have defaults from env)
        assert len(users) >= 3

        # Check that our users are in the list
        emails = [u.email for u in users]
        assert "user1@example.com" in emails
        assert "user2@example.com" in emails
        assert "user3@example.com" in emails
