"""
Module: api.routes.webhooks
Description: Webhook endpoints for receiving external events
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from src.api.dependencies import get_current_user
from src.api.middleware.webhook_verification import verify_webhook_signature
from src.core import get_logger
from src.services.webhook_service import WebhookConfig, WebhookEvent, webhook_service

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


class IncomingWebhookPayload(BaseModel):
    """Generic incoming webhook payload."""

    event: str
    timestamp: Optional[datetime] = None
    data: dict[str, Any]
    signature: Optional[str] = None


class WebhookRegistrationRequest(BaseModel):
    """Request to register a new webhook."""

    url: str = Field(..., description="Webhook endpoint URL")
    events: Optional[list[str]] = Field(
        None, description="Events to subscribe to (None = all)"
    )
    secret: Optional[str] = Field(None, description="Webhook secret for HMAC signing")
    headers: Optional[dict[str, str]] = Field(None, description="Custom headers")
    active: bool = Field(True, description="Whether webhook is active")


class WebhookTestRequest(BaseModel):
    """Request to test a webhook."""

    url: str = Field(..., description="Webhook URL to test")
    secret: Optional[str] = Field(None, description="Webhook secret if any")


@router.post("/incoming/github")
async def receive_github_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receive webhooks from GitHub.

    Requires webhook signature verification.
    """
    # Get raw body from request state (set by verification middleware)
    body = getattr(request.state, "webhook_body", None)
    if not body:
        body = await request.body()

    # Parse event type
    event_type = request.headers.get("X-GitHub-Event", "unknown")

    # Parse payload
    try:
        import json

        payload = json.loads(body)
    except Exception as e:
        logger.error("Failed to parse GitHub webhook", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload format"
        )

    # Log webhook received
    logger.info(
        "github_webhook_received",
        event=event_type,
        repository=payload.get("repository", {}).get("full_name"),
        action=payload.get("action"),
    )

    # Process webhook asynchronously
    background_tasks.add_task(process_github_webhook, event_type, payload)

    return {"status": "accepted", "event": event_type}


@router.post("/incoming/generic/{webhook_id}")
async def receive_generic_webhook(
    webhook_id: str,
    request: Request,
    payload: IncomingWebhookPayload,
    background_tasks: BackgroundTasks,
):
    """
    Receive generic webhooks with configurable verification.

    The webhook_id should match a configured incoming webhook.
    """
    # Verify webhook ID exists and get configuration
    # In production, this would look up from database
    webhook_config = get_incoming_webhook_config(webhook_id)

    if not webhook_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook configuration not found: {webhook_id}",
        )

    # Verify signature if secret is configured
    if webhook_config.get("secret"):
        body = await request.body()
        signature = request.headers.get("X-Webhook-Signature")

        if not signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing webhook signature",
            )

        if not verify_webhook_signature(signature, body, webhook_config["secret"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

    # Log webhook
    logger.info(
        "generic_webhook_received",
        webhook_id=webhook_id,
        event=payload.event,
        timestamp=payload.timestamp,
    )

    # Process asynchronously
    background_tasks.add_task(process_generic_webhook, webhook_id, payload)

    return {"status": "accepted", "webhook_id": webhook_id, "event": payload.event}


@router.post("/register")
async def register_webhook(
    request: WebhookRegistrationRequest, current_user=Depends(get_current_user)
):
    """
    Register a new outgoing webhook.

    Requires authentication.
    """
    # Convert string events to enum
    events = None
    if request.events:
        try:
            events = [WebhookEvent(e) for e in request.events]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event type: {e}",
            )

    # Create webhook config
    config = WebhookConfig(
        url=request.url,
        events=events,
        secret=request.secret,
        headers=request.headers,
        active=request.active,
    )

    # Register webhook
    webhook_service.add_webhook(config)

    logger.info(
        "webhook_registered",
        user=current_user.get("email"),
        url=request.url,
        events=request.events,
    )

    return {
        "status": "registered",
        "url": request.url,
        "events": request.events,
        "active": request.active,
    }


@router.delete("/unregister")
async def unregister_webhook(url: str, current_user=Depends(get_current_user)):
    """
    Unregister a webhook.

    Requires authentication.
    """
    removed = webhook_service.remove_webhook(url)

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Webhook not found: {url}"
        )

    logger.info("webhook_unregistered", user=current_user.get("email"), url=url)

    return {"status": "unregistered", "url": url}


@router.get("/list")
async def list_webhooks(current_user=Depends(get_current_user)):
    """
    List all registered outgoing webhooks.

    Requires authentication.
    """
    webhooks = webhook_service.list_webhooks()

    return {
        "webhooks": [
            {
                "url": str(w.url),
                "events": [e.value for e in w.events] if w.events else None,
                "active": w.active,
                "has_secret": bool(w.secret),
            }
            for w in webhooks
        ],
        "total": len(webhooks),
    }


@router.post("/test")
async def test_webhook(
    request: WebhookTestRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    """
    Test a webhook endpoint.

    Sends a test payload to verify webhook is working.
    """
    # Create temporary webhook config
    config = WebhookConfig(
        url=request.url, secret=request.secret, max_retries=1, timeout=10
    )

    # Test webhook
    delivery = await webhook_service.test_webhook(config)

    logger.info(
        "webhook_tested",
        user=current_user.get("email"),
        url=request.url,
        success=delivery.success,
        status_code=delivery.status_code,
    )

    return {
        "url": request.url,
        "success": delivery.success,
        "status_code": delivery.status_code,
        "response": delivery.response_body,
        "error": delivery.error,
        "duration_ms": delivery.duration_ms,
    }


@router.get("/history")
async def get_webhook_history(
    event: Optional[str] = None,
    url: Optional[str] = None,
    success: Optional[bool] = None,
    limit: int = 100,
    current_user=Depends(get_current_user),
):
    """
    Get webhook delivery history.

    Requires authentication.
    """
    # Convert event string to enum if provided
    event_enum = None
    if event:
        try:
            event_enum = WebhookEvent(event)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event type: {event}",
            )

    history = webhook_service.get_delivery_history(
        event=event_enum, url=url, success=success, limit=limit
    )

    return {
        "deliveries": [
            {
                "webhook_url": d.webhook_url,
                "event": d.event.value,
                "timestamp": d.timestamp.isoformat(),
                "success": d.success,
                "status_code": d.status_code,
                "error": d.error,
                "attempts": d.attempts,
                "duration_ms": d.duration_ms,
            }
            for d in history
        ],
        "total": len(history),
    }


# Helper functions


def get_incoming_webhook_config(webhook_id: str) -> Optional[dict[str, Any]]:
    """Get configuration for incoming webhook."""
    # In production, this would be from database
    # For now, return mock config
    configs = {
        "test": {"secret": "test-secret", "active": True},
        "monitoring": {"secret": "monitoring-secret", "active": True},
    }

    return configs.get(webhook_id)


async def process_github_webhook(event_type: str, payload: dict[str, Any]):
    """Process GitHub webhook asynchronously."""
    try:
        # Handle different GitHub events
        if event_type == "push":
            # Handle code push
            logger.info("Processing GitHub push event")
        elif event_type == "pull_request":
            # Handle pull request
            logger.info("Processing GitHub pull request event")
        elif event_type == "issues":
            # Handle issues
            logger.info("Processing GitHub issues event")
        # Add more event handlers as needed

    except Exception as e:
        logger.error(
            "Failed to process GitHub webhook",
            event=event_type,
            error=str(e),
            exc_info=True,
        )


async def process_generic_webhook(webhook_id: str, payload: IncomingWebhookPayload):
    """Process generic webhook asynchronously."""
    try:
        # Route to appropriate handler based on webhook_id
        logger.info(
            "Processing generic webhook", webhook_id=webhook_id, event=payload.event
        )

        # Add specific processing logic here

    except Exception as e:
        logger.error(
            "Failed to process generic webhook",
            webhook_id=webhook_id,
            error=str(e),
            exc_info=True,
        )
