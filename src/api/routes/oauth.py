"""
OAuth2 routes for Cidadão.AI API
Multiple provider authentication endpoints
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from src.core.oauth_config import OAuthProvider
from src.api.oauth import oauth_manager
from src.api.auth import auth_manager, get_current_user, require_admin, User

router = APIRouter(prefix="/auth/oauth", tags=["oauth"])


class OAuthUrlResponse(BaseModel):
    """OAuth authorization URL response."""
    authorization_url: str
    state: str
    provider: str


class OAuthLoginResponse(BaseModel):
    """OAuth login response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict
    is_new_user: bool


@router.get("/providers")
async def list_oauth_providers():
    """List available OAuth providers."""
    providers = []
    
    for provider, config in oauth_manager.config.providers.items():
        if config.enabled:
            providers.append({
                "name": provider.value,
                "display_name": config.name,
                "scopes": [
                    {
                        "name": scope.name,
                        "description": scope.description,
                        "required": scope.required
                    }
                    for scope in config.scopes
                ]
            })
    
    return {"providers": providers}


@router.get("/{provider}/authorize", response_model=OAuthUrlResponse)
async def get_oauth_authorization_url(
    provider: OAuthProvider,
    redirect_url: Optional[str] = Query(None, description="URL to redirect after login")
):
    """Get OAuth authorization URL for provider."""
    
    try:
        authorization_url, state = await oauth_manager.get_authorization_url(
            provider=provider,
            redirect_url=redirect_url
        )
        
        return OAuthUrlResponse(
            authorization_url=authorization_url,
            state=state,
            provider=provider.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate authorization URL: {str(e)}"
        )


@router.get("/{provider}/login")
async def oauth_login_redirect(
    provider: OAuthProvider,
    redirect_url: Optional[str] = Query(None, description="URL to redirect after login")
):
    """Redirect to OAuth provider for authentication."""
    
    try:
        authorization_url, _ = await oauth_manager.get_authorization_url(
            provider=provider,
            redirect_url=redirect_url
        )
        
        return RedirectResponse(url=authorization_url)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to redirect to OAuth provider: {str(e)}"
        )


@router.get("/{provider}/callback", response_model=OAuthLoginResponse)
async def oauth_callback(
    provider: OAuthProvider,
    code: Optional[str] = Query(None, description="Authorization code"),
    state: Optional[str] = Query(None, description="OAuth state"),
    error: Optional[str] = Query(None, description="OAuth error"),
    error_description: Optional[str] = Query(None, description="Error description")
):
    """Handle OAuth callback from provider."""
    
    if error:
        oauth_manager.logger.warning(
            "oauth_callback_error_received",
            provider=provider.value,
            error=error,
            error_description=error_description
        )
        raise HTTPException(
            status_code=400,
            detail=f"OAuth error: {error} - {error_description or 'Unknown error'}"
        )
    
    if not code or not state:
        raise HTTPException(
            status_code=400,
            detail="Missing required OAuth parameters (code, state)"
        )
    
    try:
        # Handle OAuth callback
        user, is_new_user = await oauth_manager.handle_callback(
            provider=provider,
            code=code,
            state=state,
            error=error
        )
        
        # Generate JWT tokens
        access_token = auth_manager.create_access_token(user)
        refresh_token = auth_manager.create_refresh_token(user)
        
        response_data = OAuthLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_manager.access_token_expire_minutes * 60,
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "is_active": user.is_active
            },
            is_new_user=is_new_user
        )
        
        # Check if user needs admin approval
        if not user.is_active and oauth_manager.config.require_admin_approval:
            oauth_manager.logger.info(
                "oauth_user_awaiting_approval",
                provider=provider.value,
                email=user.email
            )
            raise HTTPException(
                status_code=403,
                detail="Account created successfully but requires administrator approval. "
                       "Please wait for approval before accessing the system."
            )
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        oauth_manager.logger.error(
            "oauth_callback_processing_error",
            provider=provider.value,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process OAuth callback: {str(e)}"
        )


@router.post("/users/{user_id}/approve")
async def approve_oauth_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Approve OAuth user account (admin only)."""
    
    require_admin(current_user)
    
    # Find user by ID
    user_data = None
    user_email = None
    for email, data in auth_manager.users_db.items():
        if data['id'] == user_id:
            user_data = data
            user_email = email
            break
    
    if not user_data:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    if user_data['is_active']:
        raise HTTPException(
            status_code=400,
            detail="User is already active"
        )
    
    # Activate user
    auth_manager.users_db[user_email]['is_active'] = True
    
    oauth_manager.logger.info(
        "oauth_user_approved",
        admin_id=current_user.id,
        user_id=user_id,
        user_email=user_email
    )
    
    return {"message": "User approved successfully"}


@router.get("/pending-users")
async def list_pending_oauth_users(
    current_user: User = Depends(get_current_user)
):
    """List users awaiting approval (admin only)."""
    
    require_admin(current_user)
    
    pending_users = []
    for email, data in auth_manager.users_db.items():
        if not data['is_active']:
            pending_users.append({
                "id": data['id'],
                "email": data['email'],
                "name": data['name'],
                "role": data['role'],
                "created_at": data['created_at'].isoformat(),
            })
    
    return {"pending_users": pending_users}


@router.delete("/users/{user_id}/reject")
async def reject_oauth_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Reject and delete OAuth user account (admin only)."""
    
    require_admin(current_user)
    
    # Find user by ID
    user_email = None
    for email, data in auth_manager.users_db.items():
        if data['id'] == user_id:
            user_email = email
            break
    
    if not user_email:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    user_data = auth_manager.users_db[user_email]
    
    if user_data['is_active']:
        raise HTTPException(
            status_code=400,
            detail="Cannot reject active user"
        )
    
    # Delete user
    del auth_manager.users_db[user_email]
    
    oauth_manager.logger.info(
        "oauth_user_rejected",
        admin_id=current_user.id,
        user_id=user_id,
        user_email=user_email
    )
    
    return {"message": "User rejected and deleted successfully"}


@router.get("/config")
async def get_oauth_config(
    current_user: User = Depends(get_current_user)
):
    """Get OAuth configuration (admin only)."""
    
    require_admin(current_user)
    
    config_data = {
        "auto_register_enabled": oauth_manager.config.auto_register_enabled,
        "default_role": oauth_manager.config.default_role,
        "require_admin_approval": oauth_manager.config.require_admin_approval,
        "session_timeout_minutes": oauth_manager.config.session_timeout_minutes,
        "providers": {}
    }
    
    for provider, provider_config in oauth_manager.config.providers.items():
        config_data["providers"][provider.value] = {
            "name": provider_config.name,
            "enabled": provider_config.enabled,
            "scopes": [scope.name for scope in provider_config.scopes],
            "email_verification_required": provider_config.email_verification_required,
            "allowed_domains": provider_config.allowed_domains,
        }
    
    return config_data


@router.put("/config")
async def update_oauth_config(
    config_update: dict,
    current_user: User = Depends(get_current_user)
):
    """Update OAuth configuration (admin only)."""
    
    require_admin(current_user)
    
    # Update global settings
    if "auto_register_enabled" in config_update:
        oauth_manager.config.auto_register_enabled = config_update["auto_register_enabled"]
    
    if "default_role" in config_update:
        oauth_manager.config.default_role = config_update["default_role"]
    
    if "require_admin_approval" in config_update:
        oauth_manager.config.require_admin_approval = config_update["require_admin_approval"]
    
    # Update provider settings
    if "providers" in config_update:
        for provider_name, provider_updates in config_update["providers"].items():
            try:
                provider = OAuthProvider(provider_name)
                if provider in oauth_manager.config.providers:
                    provider_config = oauth_manager.config.providers[provider]
                    
                    if "enabled" in provider_updates:
                        provider_config.enabled = provider_updates["enabled"]
                    
                    if "email_verification_required" in provider_updates:
                        provider_config.email_verification_required = provider_updates["email_verification_required"]
                    
                    if "allowed_domains" in provider_updates:
                        provider_config.allowed_domains = provider_updates["allowed_domains"]
                        
            except ValueError:
                continue  # Skip invalid provider names
    
    oauth_manager.logger.info(
        "oauth_config_updated",
        admin_id=current_user.id,
        updates=config_update
    )
    
    return {"message": "OAuth configuration updated successfully"}