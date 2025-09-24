"""Notification API endpoints."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr, HttpUrl

from src.services.notification_service import (
    notification_service,
    NotificationType,
    NotificationLevel,
    Notification
)
from src.services.webhook_service import webhook_service, WebhookConfig
from src.models.notification_models import NotificationPreference
from src.api.dependencies import get_current_user
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    """Notification response model."""
    id: str
    type: str
    level: str
    title: str
    message: str
    timestamp: str
    read: bool
    channels_sent: List[str]
    metadata: Optional[Dict[str, Any]] = None


class NotificationPreferencesUpdate(BaseModel):
    """Update notification preferences."""
    enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    webhook_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    frequency: Optional[str] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None
    type_preferences: Optional[Dict[str, Dict[str, Any]]] = None


class WebhookConfigRequest(BaseModel):
    """Webhook configuration request."""
    url: HttpUrl
    events: Optional[List[str]] = None
    secret: Optional[str] = None
    description: Optional[str] = None
    headers: Optional[Dict[str, str]] = None


class TestNotificationRequest(BaseModel):
    """Test notification request."""
    type: NotificationType = NotificationType.SYSTEM_ALERT
    level: NotificationLevel = NotificationLevel.INFO
    title: str = "Test Notification"
    message: str = "This is a test notification from Cidadão.AI"
    channels: Optional[List[str]] = None


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = Query(False, description="Filter unread notifications only"),
    type: Optional[str] = Query(None, description="Filter by notification type"),
    level: Optional[str] = Query(None, description="Filter by notification level"),
    limit: int = Query(100, ge=1, le=500, description="Maximum notifications to return"),
    current_user: dict = Depends(get_current_user)
) -> List[NotificationResponse]:
    """Get user notifications with filtering options."""
    try:
        # Parse filters
        notification_type = NotificationType(type) if type else None
        notification_level = NotificationLevel(level) if level else None
        
        # Get notifications
        notifications = notification_service.get_notifications(
            user_id=current_user["id"],
            unread_only=unread_only,
            type=notification_type,
            level=notification_level,
            limit=limit
        )
        
        # Convert to response format
        return [
            NotificationResponse(
                id=n.id,
                type=n.type.value,
                level=n.level.value,
                title=n.title,
                message=n.message,
                timestamp=n.timestamp.isoformat(),
                read=n.read,
                channels_sent=n.channels_sent,
                metadata=n.metadata
            )
            for n in notifications
        ]
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid filter parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notifications"
        )


@router.get("/unread-count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, int]:
    """Get count of unread notifications."""
    notifications = notification_service.get_notifications(
        user_id=current_user["id"],
        unread_only=True
    )
    return {"unread_count": len(notifications)}


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, bool]:
    """Mark a notification as read."""
    success = notification_service.mark_as_read(notification_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
        
    return {"success": True}


@router.post("/mark-all-read")
async def mark_all_as_read(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Mark all notifications as read."""
    count = notification_service.mark_all_as_read(current_user["id"])
    return {"success": True, "marked_count": count}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, bool]:
    """Delete a notification."""
    success = notification_service.delete_notification(notification_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
        
    return {"success": True}


# Preferences endpoints
@router.get("/preferences", response_model=Dict[str, Any])
async def get_preferences(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get user notification preferences."""
    preferences = notification_service.get_user_preferences(current_user["id"])
    
    # Return default preferences if none exist
    if not preferences:
        preferences = {
            "enabled": True,
            "email_enabled": True,
            "webhook_enabled": False,
            "push_enabled": False,
            "frequency": "immediate",
            "type_preferences": {}
        }
        
    return preferences


@router.put("/preferences")
async def update_preferences(
    preferences: NotificationPreferencesUpdate,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update user notification preferences."""
    try:
        # Get current preferences
        current_prefs = notification_service.get_user_preferences(current_user["id"]) or {}
        
        # Update with new values
        update_dict = preferences.dict(exclude_unset=True)
        current_prefs.update(update_dict)
        
        # Save preferences
        await notification_service.set_user_preferences(
            current_user["id"],
            current_prefs
        )
        
        return {"success": True, "preferences": current_prefs}
        
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )


# Webhook endpoints
@router.get("/webhooks", response_model=List[Dict[str, Any]])
async def get_webhooks(
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get user's webhook configurations."""
    webhooks = webhook_service.list_webhooks()
    
    # Filter by user (in production, this would be from database)
    return [
        {
            "url": str(w.url),
            "events": w.events,
            "active": w.active,
            "max_retries": w.max_retries,
            "timeout": w.timeout
        }
        for w in webhooks
    ]


@router.post("/webhooks")
async def add_webhook(
    webhook: WebhookConfigRequest,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Add a new webhook configuration."""
    try:
        config = WebhookConfig(
            url=str(webhook.url),
            events=webhook.events,
            secret=webhook.secret,
            headers=webhook.headers
        )
        
        webhook_service.add_webhook(config)
        
        return {
            "success": True,
            "webhook": {
                "url": str(config.url),
                "events": config.events,
                "active": config.active
            }
        }
        
    except Exception as e:
        logger.error(f"Error adding webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add webhook"
        )


@router.delete("/webhooks")
async def remove_webhook(
    url: str = Query(..., description="Webhook URL to remove"),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, bool]:
    """Remove a webhook configuration."""
    success = webhook_service.remove_webhook(url)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
        
    return {"success": True}


@router.post("/webhooks/test")
async def test_webhook(
    webhook: WebhookConfigRequest,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Test a webhook configuration."""
    try:
        config = WebhookConfig(
            url=str(webhook.url),
            secret=webhook.secret,
            headers=webhook.headers
        )
        
        delivery = await webhook_service.test_webhook(config)
        
        return {
            "success": delivery.success,
            "status_code": delivery.status_code,
            "duration_ms": delivery.duration_ms,
            "error": delivery.error
        }
        
    except Exception as e:
        logger.error(f"Error testing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test webhook: {str(e)}"
        )


# Test endpoints
@router.post("/test")
async def send_test_notification(
    request: TestNotificationRequest,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Send a test notification to the current user."""
    try:
        notification = await notification_service.send_notification(
            user_id=current_user["id"],
            type=request.type,
            title=request.title,
            message=request.message,
            level=request.level,
            channels=request.channels,
            metadata={"test": True}
        )
        
        return {
            "success": True,
            "notification_id": notification.id,
            "channels_sent": notification.channels_sent
        }
        
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test notification: {str(e)}"
        )