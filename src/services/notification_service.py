"""Notification service for alerts and updates.

This service integrates multiple notification channels:
- In-memory notifications (for UI)
- Email notifications
- Webhook notifications
- Push notifications (future)
"""

import asyncio
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# Optional imports for advanced features
try:
    from src.models.notification_models import (
        NotificationChannel,
        NotificationPreference,
    )
    from src.services.email_service import EmailMessage, email_service
    from src.services.webhook_service import WebhookEvent, webhook_service

    ADVANCED_FEATURES_AVAILABLE = True
except (ImportError, AttributeError):
    # Fallback for environments without email/webhook support
    email_service = None
    webhook_service = None
    EmailMessage = None
    WebhookEvent = None
    NotificationPreference = None
    NotificationChannel = None
    ADVANCED_FEATURES_AVAILABLE = False
from src.core.logging import get_logger

logger = get_logger(__name__)


class NotificationLevel(Enum):
    """Notification severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationType(Enum):
    """Notification types."""

    INVESTIGATION_COMPLETE = "investigation_complete"
    ANOMALY_DETECTED = "anomaly_detected"
    AGENT_ERROR = "agent_error"
    SYSTEM_ALERT = "system_alert"
    REPORT_READY = "report_ready"
    EXPORT_COMPLETE = "export_complete"


class Notification(BaseModel):
    """Notification model."""

    id: str
    type: NotificationType
    level: NotificationLevel
    title: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] | None = None
    read: bool = False
    channels_sent: list[str] = Field(default_factory=list)


class NotificationService:
    """Service for managing notifications across multiple channels."""

    def __init__(self):
        self._notifications: list[Notification] = []
        self._preferences: dict[str, dict[str, Any]] = {}  # user_id -> preferences
        self._max_notifications = 1000

    async def send_notification(
        self,
        user_id: str,
        type: NotificationType,
        title: str,
        message: str,
        level: NotificationLevel = NotificationLevel.INFO,
        metadata: dict[str, Any] | None = None,
        channels: list[str] | None = None,
    ) -> Notification:
        """Send a notification through configured channels.

        Args:
            user_id: User to send notification to
            type: Type of notification
            title: Notification title
            message: Notification message
            level: Severity level
            metadata: Additional data
            channels: Specific channels to use (overrides preferences)

        Returns:
            Created notification
        """
        # Create notification
        notification = Notification(
            id=f"notif_{datetime.now(UTC).timestamp()}_{len(self._notifications)}",
            type=type,
            level=level,
            title=title,
            message=message,
            metadata=metadata or {},
        )

        # Store in-memory
        self._notifications.append(notification)
        self._trim_notifications()

        # Get user preferences or use specified channels
        if channels is None:
            channels = await self._get_user_channels(user_id, type, level)

        # Send through each channel
        tasks = []

        if "email" in channels and ADVANCED_FEATURES_AVAILABLE and email_service:
            tasks.append(self._send_email(user_id, notification))

        if "webhook" in channels and ADVANCED_FEATURES_AVAILABLE and webhook_service:
            tasks.append(self._send_webhook(notification))

        if "push" in channels:
            # TODO: Implement push notifications
            pass

        # Execute all sends concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Track which channels were sent
            for i, channel in enumerate(channels):
                if i < len(results) and not isinstance(results[i], Exception):
                    notification.channels_sent.append(channel)

        logger.info(
            "Notification sent",
            user_id=user_id,
            type=type.value,
            level=level.value,
            channels=notification.channels_sent,
        )

        return notification

    async def send_anomaly_alert(
        self, user_id: str, anomaly_data: dict[str, Any]
    ) -> Notification:
        """Send alert for detected anomaly."""
        severity = anomaly_data.get("severity", "medium")
        level_map = {
            "low": NotificationLevel.INFO,
            "medium": NotificationLevel.WARNING,
            "high": NotificationLevel.ERROR,
            "critical": NotificationLevel.CRITICAL,
        }

        return await self.send_notification(
            user_id=user_id,
            type=NotificationType.ANOMALY_DETECTED,
            title=f"Anomalia Detectada - {severity.upper()}",
            message=anomaly_data.get(
                "description", "Uma anomalia foi detectada no sistema"
            ),
            level=level_map.get(severity, NotificationLevel.WARNING),
            metadata=anomaly_data,
        )

    async def send_investigation_complete(
        self, user_id: str, investigation_id: str, results: dict[str, Any]
    ) -> Notification:
        """Send notification when investigation is complete."""
        anomalies_count = results.get("anomalies_count", 0)
        confidence_score = results.get("confidence_score", 0)

        title = "Investigação Concluída"
        if anomalies_count > 0:
            title += f" - {anomalies_count} Anomalias Encontradas"

        message = f"A investigação {investigation_id} foi concluída com sucesso. "
        message += f"Confiança: {confidence_score:.1f}%"

        return await self.send_notification(
            user_id=user_id,
            type=NotificationType.INVESTIGATION_COMPLETE,
            title=title,
            message=message,
            level=(
                NotificationLevel.INFO
                if anomalies_count == 0
                else NotificationLevel.WARNING
            ),
            metadata={"investigation_id": investigation_id, **results},
        )

    async def send_report_ready(
        self,
        user_id: str,
        report_id: str,
        report_type: str,
        download_url: str | None = None,
    ) -> Notification:
        """Send notification when report is ready."""
        return await self.send_notification(
            user_id=user_id,
            type=NotificationType.REPORT_READY,
            title=f"Relatório {report_type} Pronto",
            message=f"Seu relatório {report_type} está pronto para download",
            level=NotificationLevel.INFO,
            metadata={
                "report_id": report_id,
                "report_type": report_type,
                "download_url": download_url,
            },
        )

    async def _get_user_channels(
        self, user_id: str, type: NotificationType, level: NotificationLevel
    ) -> list[str]:
        """Get notification channels based on user preferences."""
        # Get user preferences (would come from database in production)
        prefs = self._preferences.get(user_id, {})

        # Default channels based on level
        if level == NotificationLevel.CRITICAL:
            return ["email", "webhook", "push"]
        if level == NotificationLevel.ERROR:
            return ["email", "webhook"]
        if level == NotificationLevel.WARNING:
            return ["email"]
        return ["email"]  # INFO level

    async def _send_email(self, user_id: str, notification: Notification) -> bool:
        """Send notification via email."""
        if not ADVANCED_FEATURES_AVAILABLE or not email_service or not EmailMessage:
            return False

        try:
            # Get user email (would come from database)
            user_email = f"{user_id}@example.com"  # Placeholder

            # Map notification type to email template
            template_map = {
                NotificationType.INVESTIGATION_COMPLETE: "investigation_complete",
                NotificationType.ANOMALY_DETECTED: "anomaly_alert",
                NotificationType.REPORT_READY: "notification",
                NotificationType.EXPORT_COMPLETE: "notification",
                NotificationType.AGENT_ERROR: "notification",
                NotificationType.SYSTEM_ALERT: "notification",
            }

            template = template_map.get(notification.type, "notification")

            # Prepare template data
            template_data = {
                "title": notification.title,
                "message": notification.message,
                "severity": notification.level.value,
                **(notification.metadata or {}),
            }

            # Send email
            email = EmailMessage(
                to=[user_email],
                subject=notification.title,
                template=template,
                template_data=template_data,
            )

            return await email_service.send_email(email)

        except Exception as e:
            logger.error(
                "Failed to send email notification",
                user_id=user_id,
                notification_id=notification.id,
                error=str(e),
            )
            return False

    async def _send_webhook(self, notification: Notification) -> bool:
        """Send notification via webhook."""
        if not ADVANCED_FEATURES_AVAILABLE or not webhook_service or not WebhookEvent:
            return False

        try:
            # Map notification type to webhook event
            event_map = {
                NotificationType.INVESTIGATION_COMPLETE: WebhookEvent.INVESTIGATION_COMPLETED,
                NotificationType.ANOMALY_DETECTED: WebhookEvent.ANOMALY_DETECTED,
                NotificationType.REPORT_READY: WebhookEvent.REPORT_GENERATED,
                NotificationType.EXPORT_COMPLETE: WebhookEvent.EXPORT_COMPLETED,
                NotificationType.AGENT_ERROR: WebhookEvent.AGENT_FAILED,
                NotificationType.SYSTEM_ALERT: WebhookEvent.SYSTEM_ALERT,
            }

            event = event_map.get(notification.type, WebhookEvent.SYSTEM_ALERT)

            # Send webhook
            deliveries = await webhook_service.send_event(
                event=event,
                data={
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "level": notification.level.value,
                    "timestamp": notification.timestamp.isoformat(),
                },
                metadata=notification.metadata,
            )

            # Check if any webhook was successful
            return any(d.success for d in deliveries)

        except Exception as e:
            logger.error(
                "Failed to send webhook notification",
                notification_id=notification.id,
                error=str(e),
            )
            return False

    def get_notifications(
        self,
        user_id: str | None = None,
        unread_only: bool = False,
        type: NotificationType | None = None,
        level: NotificationLevel | None = None,
        limit: int = 100,
    ) -> list[Notification]:
        """Get notifications with filtering."""
        notifications = self._notifications.copy()

        # Apply filters
        if unread_only:
            notifications = [n for n in notifications if not n.read]

        if type:
            notifications = [n for n in notifications if n.type == type]

        if level:
            notifications = [n for n in notifications if n.level == level]

        # Sort by timestamp (newest first)
        notifications.sort(key=lambda n: n.timestamp, reverse=True)

        return notifications[:limit]

    def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read."""
        for notification in self._notifications:
            if notification.id == notification_id:
                notification.read = True
                return True
        return False

    def mark_all_as_read(self, user_id: str | None = None) -> int:
        """Mark all notifications as read for a user."""
        count = 0
        for notification in self._notifications:
            if not notification.read:
                notification.read = True
                count += 1
        return count

    def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification."""
        initial_count = len(self._notifications)
        self._notifications = [
            n for n in self._notifications if n.id != notification_id
        ]
        return len(self._notifications) < initial_count

    def _trim_notifications(self):
        """Trim notifications list to max size."""
        if len(self._notifications) > self._max_notifications:
            # Keep only the most recent notifications
            self._notifications = sorted(
                self._notifications, key=lambda n: n.timestamp, reverse=True
            )[: self._max_notifications]

    async def set_user_preferences(
        self, user_id: str, preferences: dict[str, Any]
    ) -> None:
        """Set user notification preferences."""
        self._preferences[user_id] = preferences

    def get_user_preferences(self, user_id: str) -> dict[str, Any]:
        """Get user notification preferences."""
        return self._preferences.get(user_id, {})


# Singleton instance
notification_service = NotificationService()
