"""Webhook service for sending notifications to external endpoints.

This service provides async webhook delivery with:
- Retry logic with exponential backoff
- Request signing for security
- Batch webhook sending
- Event filtering
- Delivery status tracking
"""

import asyncio
import hashlib
import hmac
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import httpx
from pydantic import BaseModel, Field, HttpUrl, field_validator
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.core import json_utils
from src.core.logging import get_logger

logger = get_logger(__name__)


class WebhookEvent(str, Enum):
    """Webhook event types."""

    INVESTIGATION_CREATED = "investigation.created"
    INVESTIGATION_COMPLETED = "investigation.completed"
    INVESTIGATION_FAILED = "investigation.failed"

    ANOMALY_DETECTED = "anomaly.detected"
    ANOMALY_RESOLVED = "anomaly.resolved"

    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"

    REPORT_GENERATED = "report.generated"
    EXPORT_COMPLETED = "export.completed"

    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"

    SYSTEM_ALERT = "system.alert"
    SYSTEM_ERROR = "system.error"


class WebhookPayload(BaseModel):
    """Webhook payload model."""

    event: WebhookEvent
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data: dict[str, Any]
    metadata: dict[str, Any] | None = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def ensure_timezone(cls, v):
        """Ensure timestamp has timezone."""
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v


class WebhookConfig(BaseModel):
    """Webhook configuration model."""

    url: HttpUrl
    secret: str | None = None
    events: list[WebhookEvent] | None = None  # None means all events
    headers: dict[str, str] | None = None
    timeout: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    active: bool = Field(default=True)

    def should_send_event(self, event: WebhookEvent) -> bool:
        """Check if webhook should receive this event."""
        if not self.active:
            return False
        if self.events is None:
            return True
        return event in self.events


class WebhookDelivery(BaseModel):
    """Webhook delivery result."""

    webhook_url: str
    event: WebhookEvent
    timestamp: datetime
    status_code: int | None = None
    response_body: str | None = None
    error: str | None = None
    attempts: int = 0
    success: bool = False
    duration_ms: float | None = None


class WebhookService:
    """Service for managing and sending webhooks."""

    def __init__(self):
        """Initialize webhook service."""
        self._webhooks: list[WebhookConfig] = []
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=False,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )
        self._delivery_history: list[WebhookDelivery] = []
        self._max_history = 1000

    def add_webhook(self, webhook: WebhookConfig) -> None:
        """Add a webhook configuration."""
        self._webhooks.append(webhook)
        logger.info(
            "Webhook added",
            url=str(webhook.url),
            events=webhook.events,
            active=webhook.active,
        )

    def remove_webhook(self, url: str) -> bool:
        """Remove a webhook by URL."""
        initial_count = len(self._webhooks)
        self._webhooks = [w for w in self._webhooks if str(w.url) != url]
        removed = len(self._webhooks) < initial_count

        if removed:
            logger.info("Webhook removed", url=url)

        return removed

    def list_webhooks(self) -> list[WebhookConfig]:
        """List all configured webhooks."""
        return self._webhooks.copy()

    def _generate_signature(self, payload: bytes, secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return f"sha256={signature}"

    def _prepare_request(
        self, webhook: WebhookConfig, payload: WebhookPayload
    ) -> tuple[dict[str, str], bytes]:
        """Prepare webhook request headers and body."""
        # Serialize payload
        body_data = {
            "event": payload.event,
            "timestamp": payload.timestamp.isoformat(),
            "data": payload.data,
        }
        if payload.metadata:
            body_data["metadata"] = payload.metadata

        body = json_utils.dumps(body_data).encode()

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Cidadao.AI/1.0",
            "X-Cidadao-Event": payload.event,
            "X-Cidadao-Timestamp": payload.timestamp.isoformat(),
        }

        # Add signature if secret is configured
        if webhook.secret:
            headers["X-Cidadao-Signature"] = self._generate_signature(
                body, webhook.secret
            )

        # Add custom headers
        if webhook.headers:
            headers.update(webhook.headers)

        return headers, body

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    )
    async def _send_webhook(
        self, webhook: WebhookConfig, payload: WebhookPayload
    ) -> WebhookDelivery:
        """Send a single webhook with retry logic."""
        delivery = WebhookDelivery(
            webhook_url=str(webhook.url),
            event=payload.event,
            timestamp=datetime.now(UTC),
        )

        try:
            # Prepare request
            headers, body = self._prepare_request(webhook, payload)

            # Send request
            start_time = asyncio.get_event_loop().time()
            response = await self._client.post(
                str(webhook.url), headers=headers, content=body, timeout=webhook.timeout
            )
            end_time = asyncio.get_event_loop().time()

            # Update delivery info
            delivery.status_code = response.status_code
            delivery.response_body = response.text[:1000]  # Limit response size
            delivery.success = 200 <= response.status_code < 300
            delivery.duration_ms = (end_time - start_time) * 1000
            delivery.attempts = 1  # Will be updated by retry decorator

            if not delivery.success:
                logger.warning(
                    "Webhook delivery failed",
                    url=str(webhook.url),
                    status_code=response.status_code,
                    response=delivery.response_body,
                )

        except Exception as e:
            delivery.error = str(e)
            delivery.success = False
            logger.error(
                "Webhook delivery error",
                url=str(webhook.url),
                error=str(e),
                exc_info=True,
            )
            raise

        return delivery

    async def send_event(
        self,
        event: WebhookEvent,
        data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> list[WebhookDelivery]:
        """Send an event to all configured webhooks.

        Args:
            event: Event type
            data: Event data
            metadata: Optional metadata

        Returns:
            List of delivery results
        """
        payload = WebhookPayload(event=event, data=data, metadata=metadata)

        # Filter webhooks for this event
        webhooks_to_send = [
            webhook for webhook in self._webhooks if webhook.should_send_event(event)
        ]

        if not webhooks_to_send:
            logger.debug("No webhooks configured for event", event=event)
            return []

        # Send webhooks concurrently
        tasks = [self._send_webhook(webhook, payload) for webhook in webhooks_to_send]

        deliveries = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        results = []
        for delivery in deliveries:
            if isinstance(delivery, Exception):
                # Create failed delivery record
                delivery = WebhookDelivery(
                    webhook_url="unknown",
                    event=event,
                    timestamp=datetime.now(UTC),
                    error=str(delivery),
                    success=False,
                )
            results.append(delivery)

        # Store in history
        self._store_deliveries(results)

        # Log summary
        successful = sum(1 for d in results if d.success)
        logger.info(
            "Webhooks sent",
            event=event,
            total=len(results),
            successful=successful,
            failed=len(results) - successful,
        )

        return results

    def _store_deliveries(self, deliveries: list[WebhookDelivery]) -> None:
        """Store delivery results in history."""
        self._delivery_history.extend(deliveries)

        # Trim history if too large
        if len(self._delivery_history) > self._max_history:
            self._delivery_history = self._delivery_history[-self._max_history :]

    def get_delivery_history(
        self,
        event: WebhookEvent | None = None,
        url: str | None = None,
        success: bool | None = None,
        limit: int = 100,
    ) -> list[WebhookDelivery]:
        """Get webhook delivery history with filtering."""
        history = self._delivery_history.copy()

        # Apply filters
        if event:
            history = [d for d in history if d.event == event]
        if url:
            history = [d for d in history if d.webhook_url == url]
        if success is not None:
            history = [d for d in history if d.success == success]

        # Sort by timestamp (newest first) and limit
        history.sort(key=lambda d: d.timestamp, reverse=True)
        return history[:limit]

    async def test_webhook(self, webhook: WebhookConfig) -> WebhookDelivery:
        """Test a webhook configuration."""
        test_payload = WebhookPayload(
            event=WebhookEvent.SYSTEM_ALERT,
            data={
                "type": "test",
                "message": "This is a test webhook from Cidadão.AI",
                "timestamp": datetime.now(UTC).isoformat(),
            },
            metadata={"test": True},
        )

        return await self._send_webhook(webhook, test_payload)

    async def close(self):
        """Close the webhook service."""
        await self._client.aclose()


# Singleton instance
webhook_service = WebhookService()


# Convenience functions
async def send_webhook_event(
    event: WebhookEvent, data: dict[str, Any], metadata: dict[str, Any] | None = None
) -> list[WebhookDelivery]:
    """Send a webhook event using the default service."""
    return await webhook_service.send_event(event, data, metadata)


async def register_webhook(
    url: str,
    events: list[WebhookEvent] | None = None,
    secret: str | None = None,
    **kwargs,
) -> None:
    """Register a new webhook."""
    config = WebhookConfig(url=url, events=events, secret=secret, **kwargs)
    webhook_service.add_webhook(config)
