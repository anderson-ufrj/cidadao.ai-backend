"""Tests for notification service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from src.services.notification_service import (
    Notification,
    NotificationLevel,
    NotificationService,
    NotificationType,
    notification_service,
)


class TestNotificationLevel:
    """Tests for NotificationLevel enum."""

    def test_notification_levels(self):
        """Test notification level values."""
        assert NotificationLevel.INFO.value == "info"
        assert NotificationLevel.WARNING.value == "warning"
        assert NotificationLevel.ERROR.value == "error"
        assert NotificationLevel.CRITICAL.value == "critical"


class TestNotificationType:
    """Tests for NotificationType enum."""

    def test_notification_types(self):
        """Test notification type values."""
        assert NotificationType.INVESTIGATION_COMPLETE.value == "investigation_complete"
        assert NotificationType.ANOMALY_DETECTED.value == "anomaly_detected"
        assert NotificationType.AGENT_ERROR.value == "agent_error"
        assert NotificationType.SYSTEM_ALERT.value == "system_alert"
        assert NotificationType.REPORT_READY.value == "report_ready"
        assert NotificationType.EXPORT_COMPLETE.value == "export_complete"


class TestNotificationModel:
    """Tests for Notification model."""

    def test_notification_creation(self):
        """Test creating notification."""
        notification = Notification(
            id="test-123",
            type=NotificationType.SYSTEM_ALERT,
            level=NotificationLevel.INFO,
            title="Test Title",
            message="Test message",
        )

        assert notification.id == "test-123"
        assert notification.type == NotificationType.SYSTEM_ALERT
        assert notification.level == NotificationLevel.INFO
        assert notification.title == "Test Title"
        assert notification.message == "Test message"
        assert notification.read is False
        assert notification.channels_sent == []

    def test_notification_with_metadata(self):
        """Test notification with metadata."""
        metadata = {"key": "value", "count": 5}
        notification = Notification(
            id="test-456",
            type=NotificationType.ANOMALY_DETECTED,
            level=NotificationLevel.WARNING,
            title="Anomaly",
            message="Detected",
            metadata=metadata,
        )

        assert notification.metadata == metadata


class TestNotificationServiceInitialization:
    """Tests for NotificationService initialization."""

    def test_initialization(self):
        """Test service initialization."""
        service = NotificationService()

        assert service._notifications == []
        assert service._preferences == {}
        assert service._max_notifications == 1000

    def test_singleton_instance(self):
        """Test singleton notification_service exists."""
        assert notification_service is not None
        assert isinstance(notification_service, NotificationService)


class TestSendNotification:
    """Tests for send_notification method."""

    @pytest.fixture
    def service(self):
        """Create notification service for testing."""
        return NotificationService()

    @pytest.mark.asyncio
    async def test_send_notification_basic(self, service):
        """Test sending basic notification."""
        notification = await service.send_notification(
            user_id="user-123",
            type=NotificationType.SYSTEM_ALERT,
            title="Test Alert",
            message="This is a test",
        )

        assert notification.id is not None
        assert notification.type == NotificationType.SYSTEM_ALERT
        assert notification.title == "Test Alert"
        assert notification.message == "This is a test"
        assert len(service._notifications) == 1

    @pytest.mark.asyncio
    async def test_send_notification_with_level(self, service):
        """Test notification with specific level."""
        notification = await service.send_notification(
            user_id="user-123",
            type=NotificationType.AGENT_ERROR,
            title="Error",
            message="Something went wrong",
            level=NotificationLevel.ERROR,
        )

        assert notification.level == NotificationLevel.ERROR

    @pytest.mark.asyncio
    async def test_send_notification_with_metadata(self, service):
        """Test notification with metadata."""
        metadata = {"investigation_id": "inv-123", "count": 5}
        notification = await service.send_notification(
            user_id="user-123",
            type=NotificationType.INVESTIGATION_COMPLETE,
            title="Complete",
            message="Done",
            metadata=metadata,
        )

        assert notification.metadata == metadata

    @pytest.mark.asyncio
    async def test_send_notification_trims_list(self, service):
        """Test notification list is trimmed to max size."""
        service._max_notifications = 5

        for i in range(10):
            await service.send_notification(
                user_id="user-123",
                type=NotificationType.SYSTEM_ALERT,
                title=f"Alert {i}",
                message=f"Message {i}",
            )

        assert len(service._notifications) == 5


class TestSendAnomalyAlert:
    """Tests for send_anomaly_alert method."""

    @pytest.fixture
    def service(self):
        """Create notification service for testing."""
        return NotificationService()

    @pytest.mark.asyncio
    async def test_send_anomaly_alert_low(self, service):
        """Test low severity anomaly alert."""
        anomaly_data = {
            "severity": "low",
            "description": "Minor irregularity detected",
        }

        notification = await service.send_anomaly_alert("user-123", anomaly_data)

        assert notification.level == NotificationLevel.INFO
        assert "LOW" in notification.title

    @pytest.mark.asyncio
    async def test_send_anomaly_alert_medium(self, service):
        """Test medium severity anomaly alert."""
        anomaly_data = {
            "severity": "medium",
            "description": "Potential issue found",
        }

        notification = await service.send_anomaly_alert("user-123", anomaly_data)

        assert notification.level == NotificationLevel.WARNING
        assert "MEDIUM" in notification.title

    @pytest.mark.asyncio
    async def test_send_anomaly_alert_high(self, service):
        """Test high severity anomaly alert."""
        anomaly_data = {
            "severity": "high",
            "description": "Serious anomaly detected",
        }

        notification = await service.send_anomaly_alert("user-123", anomaly_data)

        assert notification.level == NotificationLevel.ERROR

    @pytest.mark.asyncio
    async def test_send_anomaly_alert_critical(self, service):
        """Test critical severity anomaly alert."""
        anomaly_data = {
            "severity": "critical",
            "description": "Critical issue requires immediate attention",
        }

        notification = await service.send_anomaly_alert("user-123", anomaly_data)

        assert notification.level == NotificationLevel.CRITICAL


class TestSendInvestigationComplete:
    """Tests for send_investigation_complete method."""

    @pytest.fixture
    def service(self):
        """Create notification service for testing."""
        return NotificationService()

    @pytest.mark.asyncio
    async def test_investigation_complete_no_anomalies(self, service):
        """Test investigation complete with no anomalies."""
        results = {"anomalies_count": 0, "confidence_score": 95.5}

        notification = await service.send_investigation_complete(
            "user-123", "inv-456", results
        )

        assert notification.level == NotificationLevel.INFO
        assert "Anomalias" not in notification.title
        assert "95.5%" in notification.message

    @pytest.mark.asyncio
    async def test_investigation_complete_with_anomalies(self, service):
        """Test investigation complete with anomalies."""
        results = {"anomalies_count": 3, "confidence_score": 87.2}

        notification = await service.send_investigation_complete(
            "user-123", "inv-789", results
        )

        assert notification.level == NotificationLevel.WARNING
        assert "3 Anomalias" in notification.title


class TestSendReportReady:
    """Tests for send_report_ready method."""

    @pytest.fixture
    def service(self):
        """Create notification service for testing."""
        return NotificationService()

    @pytest.mark.asyncio
    async def test_send_report_ready(self, service):
        """Test report ready notification."""
        notification = await service.send_report_ready(
            user_id="user-123",
            report_id="rpt-456",
            report_type="Mensal",
            download_url="https://example.com/download",
        )

        assert notification.type == NotificationType.REPORT_READY
        assert "Mensal" in notification.title
        assert notification.metadata["report_id"] == "rpt-456"
        assert notification.metadata["download_url"] == "https://example.com/download"


class TestGetNotifications:
    """Tests for get_notifications method."""

    @pytest.fixture
    def service(self):
        """Create notification service with test data."""
        service = NotificationService()
        # Add some test notifications
        service._notifications = [
            Notification(
                id="n1",
                type=NotificationType.SYSTEM_ALERT,
                level=NotificationLevel.INFO,
                title="Alert 1",
                message="Message 1",
                read=False,
            ),
            Notification(
                id="n2",
                type=NotificationType.ANOMALY_DETECTED,
                level=NotificationLevel.WARNING,
                title="Alert 2",
                message="Message 2",
                read=True,
            ),
            Notification(
                id="n3",
                type=NotificationType.SYSTEM_ALERT,
                level=NotificationLevel.ERROR,
                title="Alert 3",
                message="Message 3",
                read=False,
            ),
        ]
        return service

    def test_get_all_notifications(self, service):
        """Test getting all notifications."""
        notifications = service.get_notifications()

        assert len(notifications) == 3

    def test_get_unread_only(self, service):
        """Test getting unread notifications only."""
        notifications = service.get_notifications(unread_only=True)

        assert len(notifications) == 2
        assert all(not n.read for n in notifications)

    def test_get_by_type(self, service):
        """Test filtering by notification type."""
        notifications = service.get_notifications(type=NotificationType.SYSTEM_ALERT)

        assert len(notifications) == 2
        assert all(n.type == NotificationType.SYSTEM_ALERT for n in notifications)

    def test_get_by_level(self, service):
        """Test filtering by notification level."""
        notifications = service.get_notifications(level=NotificationLevel.WARNING)

        assert len(notifications) == 1
        assert notifications[0].level == NotificationLevel.WARNING

    def test_get_with_limit(self, service):
        """Test limiting results."""
        notifications = service.get_notifications(limit=2)

        assert len(notifications) == 2


class TestMarkAsRead:
    """Tests for mark_as_read method."""

    @pytest.fixture
    def service(self):
        """Create notification service with test data."""
        service = NotificationService()
        service._notifications = [
            Notification(
                id="n1",
                type=NotificationType.SYSTEM_ALERT,
                level=NotificationLevel.INFO,
                title="Test",
                message="Test",
                read=False,
            ),
        ]
        return service

    def test_mark_as_read_success(self, service):
        """Test marking notification as read."""
        result = service.mark_as_read("n1")

        assert result is True
        assert service._notifications[0].read is True

    def test_mark_as_read_not_found(self, service):
        """Test marking non-existent notification."""
        result = service.mark_as_read("nonexistent")

        assert result is False


class TestMarkAllAsRead:
    """Tests for mark_all_as_read method."""

    @pytest.fixture
    def service(self):
        """Create notification service with test data."""
        service = NotificationService()
        service._notifications = [
            Notification(
                id="n1",
                type=NotificationType.SYSTEM_ALERT,
                level=NotificationLevel.INFO,
                title="Test 1",
                message="Test",
                read=False,
            ),
            Notification(
                id="n2",
                type=NotificationType.SYSTEM_ALERT,
                level=NotificationLevel.INFO,
                title="Test 2",
                message="Test",
                read=True,
            ),
            Notification(
                id="n3",
                type=NotificationType.SYSTEM_ALERT,
                level=NotificationLevel.INFO,
                title="Test 3",
                message="Test",
                read=False,
            ),
        ]
        return service

    def test_mark_all_as_read(self, service):
        """Test marking all notifications as read."""
        count = service.mark_all_as_read()

        assert count == 2  # Only 2 were unread
        assert all(n.read for n in service._notifications)


class TestDeleteNotification:
    """Tests for delete_notification method."""

    @pytest.fixture
    def service(self):
        """Create notification service with test data."""
        service = NotificationService()
        service._notifications = [
            Notification(
                id="n1",
                type=NotificationType.SYSTEM_ALERT,
                level=NotificationLevel.INFO,
                title="Test",
                message="Test",
            ),
            Notification(
                id="n2",
                type=NotificationType.SYSTEM_ALERT,
                level=NotificationLevel.INFO,
                title="Test 2",
                message="Test 2",
            ),
        ]
        return service

    def test_delete_notification_success(self, service):
        """Test deleting notification."""
        result = service.delete_notification("n1")

        assert result is True
        assert len(service._notifications) == 1
        assert service._notifications[0].id == "n2"

    def test_delete_notification_not_found(self, service):
        """Test deleting non-existent notification."""
        result = service.delete_notification("nonexistent")

        assert result is False
        assert len(service._notifications) == 2


class TestUserPreferences:
    """Tests for user preferences methods."""

    @pytest.fixture
    def service(self):
        """Create notification service for testing."""
        return NotificationService()

    @pytest.mark.asyncio
    async def test_set_user_preferences(self, service):
        """Test setting user preferences."""
        preferences = {"email": True, "push": False, "webhook": True}

        await service.set_user_preferences("user-123", preferences)

        assert service._preferences["user-123"] == preferences

    def test_get_user_preferences_exists(self, service):
        """Test getting existing preferences."""
        service._preferences["user-123"] = {"email": True}

        result = service.get_user_preferences("user-123")

        assert result == {"email": True}

    def test_get_user_preferences_not_exists(self, service):
        """Test getting non-existent preferences."""
        result = service.get_user_preferences("user-456")

        assert result == {}


class TestGetUserChannels:
    """Tests for _get_user_channels method."""

    @pytest.fixture
    def service(self):
        """Create notification service for testing."""
        return NotificationService()

    @pytest.mark.asyncio
    async def test_get_channels_critical(self, service):
        """Test channels for critical level."""
        channels = await service._get_user_channels(
            "user-123",
            NotificationType.SYSTEM_ALERT,
            NotificationLevel.CRITICAL,
        )

        assert "email" in channels
        assert "webhook" in channels
        assert "push" in channels

    @pytest.mark.asyncio
    async def test_get_channels_error(self, service):
        """Test channels for error level."""
        channels = await service._get_user_channels(
            "user-123",
            NotificationType.AGENT_ERROR,
            NotificationLevel.ERROR,
        )

        assert "email" in channels
        assert "webhook" in channels

    @pytest.mark.asyncio
    async def test_get_channels_warning(self, service):
        """Test channels for warning level."""
        channels = await service._get_user_channels(
            "user-123",
            NotificationType.ANOMALY_DETECTED,
            NotificationLevel.WARNING,
        )

        assert channels == ["email"]

    @pytest.mark.asyncio
    async def test_get_channels_info(self, service):
        """Test channels for info level."""
        channels = await service._get_user_channels(
            "user-123",
            NotificationType.REPORT_READY,
            NotificationLevel.INFO,
        )

        assert channels == ["email"]


class TestTrimNotifications:
    """Tests for _trim_notifications method."""

    def test_trim_removes_old_notifications(self):
        """Test trimming removes oldest notifications."""
        service = NotificationService()
        service._max_notifications = 3

        # Add notifications with different timestamps
        for i in range(5):
            service._notifications.append(
                Notification(
                    id=f"n{i}",
                    type=NotificationType.SYSTEM_ALERT,
                    level=NotificationLevel.INFO,
                    title=f"Test {i}",
                    message=f"Message {i}",
                )
            )

        service._trim_notifications()

        assert len(service._notifications) == 3

    def test_trim_does_nothing_under_limit(self):
        """Test trim does nothing when under limit."""
        service = NotificationService()
        service._max_notifications = 100

        service._notifications = [
            Notification(
                id=f"n{i}",
                type=NotificationType.SYSTEM_ALERT,
                level=NotificationLevel.INFO,
                title=f"Test {i}",
                message=f"Message {i}",
            )
            for i in range(5)
        ]

        initial_count = len(service._notifications)
        service._trim_notifications()

        assert len(service._notifications) == initial_count
