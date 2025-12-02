"""
Module: api.oauth
Description: OAuth2 implementation with multiple providers
Author: Anderson H. Silva
Date: 2025-01-15
License: Proprietary - All rights reserved
"""

import base64
import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException
from pydantic import BaseModel

from src.api.auth import User, auth_manager
from src.core import get_logger
from src.core.oauth_config import OAuthProvider, get_oauth_providers_config


class OAuthState(BaseModel):
    """OAuth state management."""

    provider: OAuthProvider
    state: str
    nonce: str
    code_verifier: str
    code_challenge: str
    created_at: datetime
    redirect_url: str | None = None


class OAuthUserInfo(BaseModel):
    """OAuth user information."""

    provider: OAuthProvider
    provider_id: str
    email: str
    name: str
    avatar_url: str | None = None
    email_verified: bool = True
    raw_data: dict = {}


class OAuthManager:
    """OAuth2 manager for multiple providers."""

    def __init__(self):
        """Initialize OAuth manager."""
        self.logger = get_logger(__name__)
        self.config = get_oauth_providers_config()
        self.states: dict[str, OAuthState] = {}  # In production, use Redis
        self.http_client = httpx.AsyncClient(timeout=30.0)

    def _generate_pkce_pair(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge."""
        code_verifier = (
            base64.urlsafe_b64encode(secrets.token_bytes(32))
            .decode("utf-8")
            .rstrip("=")
        )
        code_challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode("utf-8")).digest()
            )
            .decode("utf-8")
            .rstrip("=")
        )
        return code_verifier, code_challenge

    def _cleanup_expired_states(self):
        """Clean up expired OAuth states."""
        now = datetime.now(UTC)
        expired_states = [
            state_id
            for state_id, state in self.states.items()
            if now - state.created_at
            > timedelta(minutes=self.config.state_lifetime_minutes)
        ]
        for state_id in expired_states:
            del self.states[state_id]

    async def get_authorization_url(
        self, provider: OAuthProvider, redirect_url: str | None = None
    ) -> tuple[str, str]:
        """Get OAuth authorization URL for provider."""

        if provider not in self.config.providers:
            raise HTTPException(
                status_code=400, detail=f"OAuth provider '{provider}' not configured"
            )

        provider_config = self.config.providers[provider]

        if not provider_config.enabled:
            raise HTTPException(
                status_code=400, detail=f"OAuth provider '{provider}' is disabled"
            )

        # Clean up expired states
        self._cleanup_expired_states()

        # Generate state and PKCE parameters
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        code_verifier, code_challenge = self._generate_pkce_pair()

        # Store OAuth state
        oauth_state = OAuthState(
            provider=provider,
            state=state,
            nonce=nonce,
            code_verifier=code_verifier,
            code_challenge=code_challenge,
            created_at=datetime.now(UTC),
            redirect_url=redirect_url,
        )
        self.states[state] = oauth_state

        # Build authorization URL
        scopes = [scope.name for scope in provider_config.scopes if scope.required]

        auth_params = {
            "client_id": provider_config.client_id,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
            "redirect_uri": provider_config.redirect_uri,
        }

        if provider_config.pkce_enabled:
            auth_params.update(
                {
                    "code_challenge": code_challenge,
                    "code_challenge_method": "S256",
                }
            )

        if provider_config.nonce_verification:
            auth_params["nonce"] = nonce

        # Provider-specific parameters
        if provider == OAuthProvider.MICROSOFT:
            auth_params["response_mode"] = "query"

        elif provider == OAuthProvider.GOV_BR:
            auth_params["acr_values"] = "https://www.gov.br/sso/aal/basic"

        authorization_url = (
            f"{provider_config.authorization_url}?{urlencode(auth_params)}"
        )

        self.logger.info(
            "oauth_authorization_url_generated",
            provider=provider.value,
            state=state,
            scopes=scopes,
        )

        return authorization_url, state

    async def handle_callback(
        self,
        provider: OAuthProvider,
        code: str,
        state: str,
        error: str | None = None,
    ) -> tuple[User, bool]:
        """Handle OAuth callback and return user."""

        if error:
            self.logger.warning(
                "oauth_callback_error",
                provider=provider.value,
                error=error,
                state=state,
            )
            raise HTTPException(status_code=400, detail=f"OAuth error: {error}")

        # Validate state
        if state not in self.states:
            self.logger.warning(
                "oauth_invalid_state", provider=provider.value, state=state
            )
            raise HTTPException(
                status_code=400, detail="Invalid or expired OAuth state"
            )

        oauth_state = self.states[state]

        # Verify provider matches
        if oauth_state.provider != provider:
            self.logger.warning(
                "oauth_provider_mismatch",
                expected=oauth_state.provider.value,
                received=provider.value,
                state=state,
            )
            raise HTTPException(status_code=400, detail="OAuth provider mismatch")

        # Check state expiration
        if datetime.now(UTC) - oauth_state.created_at > timedelta(
            minutes=self.config.state_lifetime_minutes
        ):
            del self.states[state]
            raise HTTPException(status_code=400, detail="OAuth state expired")

        try:
            # Exchange code for tokens
            tokens = await self._exchange_code_for_tokens(provider, code, oauth_state)

            # Get user info
            user_info = await self._get_user_info(provider, tokens["access_token"])

            # Create or get user
            user, is_new_user = await self._create_or_get_user(user_info)

            # Clean up state
            del self.states[state]

            self.logger.info(
                "oauth_login_success",
                provider=provider.value,
                user_id=user.id,
                email=user.email,
                is_new_user=is_new_user,
            )

            return user, is_new_user

        except Exception as e:
            self.logger.error(
                "oauth_callback_error",
                provider=provider.value,
                error=str(e),
                state=state,
            )
            # Clean up state on error
            if state in self.states:
                del self.states[state]
            raise HTTPException(
                status_code=500, detail=f"OAuth authentication failed: {str(e)}"
            )

    async def _exchange_code_for_tokens(
        self, provider: OAuthProvider, code: str, oauth_state: OAuthState
    ) -> dict[str, str]:
        """Exchange authorization code for tokens."""

        provider_config = self.config.providers[provider]

        token_data = {
            "grant_type": "authorization_code",
            "client_id": provider_config.client_id,
            "client_secret": provider_config.client_secret,
            "code": code,
            "redirect_uri": provider_config.redirect_uri,
        }

        if provider_config.pkce_enabled:
            token_data["code_verifier"] = oauth_state.code_verifier

        headers = {"Accept": "application/json"}

        response = await self.http_client.post(
            str(provider_config.token_url), data=token_data, headers=headers
        )

        if response.status_code != 200:
            self.logger.error(
                "oauth_token_exchange_failed",
                provider=provider.value,
                status_code=response.status_code,
                response=response.text,
            )
            raise HTTPException(
                status_code=400, detail="Failed to exchange code for tokens"
            )

        return response.json()

    async def _get_user_info(
        self, provider: OAuthProvider, access_token: str
    ) -> OAuthUserInfo:
        """Get user information from OAuth provider."""

        provider_config = self.config.providers[provider]

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        response = await self.http_client.get(
            str(provider_config.userinfo_url), headers=headers
        )

        if response.status_code != 200:
            self.logger.error(
                "oauth_userinfo_failed",
                provider=provider.value,
                status_code=response.status_code,
            )
            raise HTTPException(
                status_code=400, detail="Failed to get user information"
            )

        user_data = response.json()

        # Map provider fields to our format
        provider_id = str(user_data.get(provider_config.user_id_field))
        email = user_data.get(provider_config.email_field)
        name = user_data.get(provider_config.name_field)
        avatar_url = user_data.get(provider_config.avatar_field)

        # Validate required fields
        if not provider_id or not email:
            raise HTTPException(
                status_code=400,
                detail="Missing required user information from OAuth provider",
            )

        # Check email verification if required
        email_verified = True
        if provider_config.email_verification_required:
            if provider == OAuthProvider.GOOGLE:
                email_verified = user_data.get("email_verified", False)
            elif provider == OAuthProvider.GITHUB:
                # GitHub requires separate API call for email verification
                email_verified = await self._verify_github_email(access_token, email)
            elif provider == OAuthProvider.MICROSOFT:
                # Microsoft emails are pre-verified
                email_verified = True
            elif provider == OAuthProvider.GOV_BR:
                email_verified = user_data.get("email_verified", False)

        # Check allowed domains
        if provider_config.allowed_domains:
            email_domain = email.split("@")[1].lower()
            if not any(
                email_domain.endswith(domain)
                for domain in provider_config.allowed_domains
            ):
                raise HTTPException(
                    status_code=403,
                    detail=f"Email domain not allowed for {provider.value} authentication",
                )

        return OAuthUserInfo(
            provider=provider,
            provider_id=provider_id,
            email=email,
            name=name or email.split("@")[0],
            avatar_url=avatar_url,
            email_verified=email_verified,
            raw_data=user_data,
        )

    async def _verify_github_email(self, access_token: str, email: str) -> bool:
        """Verify GitHub email address."""

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        response = await self.http_client.get(
            "https://api.github.com/user/emails", headers=headers
        )

        if response.status_code != 200:
            return False

        emails = response.json()
        for email_info in emails:
            if email_info.get("email") == email:
                return email_info.get("verified", False)

        return False

    async def _create_or_get_user(self, user_info: OAuthUserInfo) -> tuple[User, bool]:
        """Create new user or get existing user from OAuth info."""

        # Check if email verification is required
        if not user_info.email_verified:
            raise HTTPException(
                status_code=400,
                detail="Email address must be verified to use OAuth authentication",
            )

        # Try to find existing user by email
        existing_user = None
        for email, user_data in auth_manager.users_db.items():
            if email == user_info.email:
                existing_user = User(
                    id=user_data["id"],
                    email=user_data["email"],
                    name=user_data["name"],
                    role=user_data["role"],
                    is_active=user_data["is_active"],
                    created_at=user_data["created_at"],
                    last_login=user_data.get("last_login"),
                )
                break

        if existing_user:
            # Update last login
            auth_manager.users_db[user_info.email]["last_login"] = datetime.now(UTC)
            existing_user.last_login = datetime.now(UTC)
            return existing_user, False

        # Auto-register new user if enabled
        if not self.config.auto_register_enabled:
            raise HTTPException(
                status_code=403,
                detail="Auto-registration is disabled. Please contact an administrator.",
            )

        # Create new user
        new_user = auth_manager.register_user(
            email=user_info.email,
            password=secrets.token_urlsafe(32),  # Random password for OAuth users
            name=user_info.name,
            role=self.config.default_role,
        )

        # Mark as requiring admin approval if configured
        if self.config.require_admin_approval:
            auth_manager.users_db[user_info.email]["is_active"] = False
            new_user.is_active = False

            self.logger.info(
                "oauth_user_pending_approval",
                provider=user_info.provider.value,
                email=user_info.email,
                name=user_info.name,
            )

        return new_user, True


# Global OAuth manager instance
oauth_manager = OAuthManager()
