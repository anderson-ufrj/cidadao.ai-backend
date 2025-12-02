"""
Module: core.oauth_config
Description: OAuth2 configuration for multiple providers
Author: Anderson H. Silva
Date: 2025-01-15
License: Proprietary - All rights reserved
"""

from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class OAuthProvider(str, Enum):
    """Supported OAuth providers."""

    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"
    GOV_BR = "gov_br"  # Login Único do Governo Federal


class OAuthScope(BaseModel):
    """OAuth scope configuration."""

    name: str
    description: str
    required: bool = False


class OAuthProviderConfig(BaseModel):
    """OAuth provider configuration."""

    name: str = Field(..., description="Provider name")
    client_id: str = Field(..., description="OAuth client ID")
    client_secret: str = Field(..., description="OAuth client secret", repr=False)
    authorization_url: HttpUrl = Field(..., description="Authorization endpoint")
    token_url: HttpUrl = Field(..., description="Token endpoint")
    userinfo_url: HttpUrl = Field(..., description="User info endpoint")
    scopes: list[OAuthScope] = Field(
        default_factory=list, description="Available scopes"
    )
    redirect_uri: str = Field(..., description="Redirect URI")
    enabled: bool = Field(default=True, description="Provider enabled")

    # Provider-specific settings
    pkce_enabled: bool = Field(default=True, description="PKCE enabled")
    state_verification: bool = Field(default=True, description="State verification")
    nonce_verification: bool = Field(default=True, description="Nonce verification")

    # User mapping
    user_id_field: str = Field(default="id", description="User ID field mapping")
    email_field: str = Field(default="email", description="Email field mapping")
    name_field: str = Field(default="name", description="Name field mapping")
    avatar_field: str = Field(default="avatar_url", description="Avatar field mapping")

    # Additional validation
    email_verification_required: bool = Field(
        default=True, description="Require verified email"
    )
    allowed_domains: list[str] | None = Field(
        default=None, description="Allowed email domains"
    )


class OAuthConfig(BaseModel):
    """Complete OAuth configuration."""

    providers: dict[OAuthProvider, OAuthProviderConfig] = Field(
        default_factory=dict, description="OAuth provider configurations"
    )

    # Global settings
    session_timeout_minutes: int = Field(
        default=60, description="OAuth session timeout"
    )
    state_lifetime_minutes: int = Field(
        default=10, description="State parameter lifetime"
    )
    nonce_lifetime_minutes: int = Field(
        default=10, description="Nonce parameter lifetime"
    )

    # Security settings
    secure_cookies: bool = Field(default=True, description="Use secure cookies")
    same_site_policy: str = Field(default="Lax", description="SameSite cookie policy")
    csrf_protection: bool = Field(default=True, description="CSRF protection enabled")

    # Auto-registration settings
    auto_register_enabled: bool = Field(
        default=True, description="Auto-register new users"
    )
    default_role: str = Field(
        default="analyst", description="Default role for new users"
    )
    require_admin_approval: bool = Field(
        default=False, description="Require admin approval"
    )


def get_oauth_providers_config() -> OAuthConfig:
    """Get OAuth providers configuration."""

    google_config = OAuthProviderConfig(
        name="Google",
        client_id="${GOOGLE_CLIENT_ID}",
        client_secret="${GOOGLE_CLIENT_SECRET}",
        authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        userinfo_url="https://www.googleapis.com/oauth2/v2/userinfo",
        scopes=[
            OAuthScope(name="openid", description="OpenID Connect", required=True),
            OAuthScope(name="email", description="Email address", required=True),
            OAuthScope(name="profile", description="Basic profile", required=True),
        ],
        redirect_uri="${BASE_URL}/auth/oauth/google/callback",
        user_id_field="id",
        email_field="email",
        name_field="name",
        avatar_field="picture",
    )

    github_config = OAuthProviderConfig(
        name="GitHub",
        client_id="${GITHUB_CLIENT_ID}",
        client_secret="${GITHUB_CLIENT_SECRET}",
        authorization_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        userinfo_url="https://api.github.com/user",
        scopes=[
            OAuthScope(name="user:email", description="Email addresses", required=True),
            OAuthScope(name="read:user", description="User profile", required=True),
        ],
        redirect_uri="${BASE_URL}/auth/oauth/github/callback",
        user_id_field="id",
        email_field="email",
        name_field="name",
        avatar_field="avatar_url",
    )

    microsoft_config = OAuthProviderConfig(
        name="Microsoft",
        client_id="${MICROSOFT_CLIENT_ID}",
        client_secret="${MICROSOFT_CLIENT_SECRET}",
        authorization_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        userinfo_url="https://graph.microsoft.com/v1.0/me",
        scopes=[
            OAuthScope(name="openid", description="OpenID Connect", required=True),
            OAuthScope(name="email", description="Email address", required=True),
            OAuthScope(name="profile", description="Basic profile", required=True),
        ],
        redirect_uri="${BASE_URL}/auth/oauth/microsoft/callback",
        user_id_field="id",
        email_field="mail",
        name_field="displayName",
        avatar_field="photo",
        email_verification_required=False,  # Microsoft handles verification
    )

    gov_br_config = OAuthProviderConfig(
        name="Login Único - Gov.br",
        client_id="${GOV_BR_CLIENT_ID}",
        client_secret="${GOV_BR_CLIENT_SECRET}",
        authorization_url="https://sso.staging.acesso.gov.br/authorize",
        token_url="https://sso.staging.acesso.gov.br/token",
        userinfo_url="https://sso.staging.acesso.gov.br/userinfo",
        scopes=[
            OAuthScope(name="openid", description="OpenID Connect", required=True),
            OAuthScope(name="email", description="Email address", required=True),
            OAuthScope(name="profile", description="Basic profile", required=True),
            OAuthScope(name="govbr_cpf", description="CPF do usuário", required=False),
            OAuthScope(name="govbr_nome", description="Nome completo", required=False),
        ],
        redirect_uri="${BASE_URL}/auth/oauth/govbr/callback",
        user_id_field="sub",
        email_field="email",
        name_field="name",
        avatar_field="picture",
        email_verification_required=True,
        # Only allow government domains
        allowed_domains=[
            "gov.br",
            "fazenda.gov.br",
            "cgu.gov.br",
            "tcu.gov.br",
            "mpf.mp.br",
            "camara.leg.br",
            "senado.leg.br",
        ],
    )

    return OAuthConfig(
        providers={
            OAuthProvider.GOOGLE: google_config,
            OAuthProvider.GITHUB: github_config,
            OAuthProvider.MICROSOFT: microsoft_config,
            OAuthProvider.GOV_BR: gov_br_config,
        },
        auto_register_enabled=True,
        default_role="analyst",
        require_admin_approval=False,
    )
