"""Tests for alert service."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.services.alert_service import AlertService, alert_service


class TestAlertService:
    """Tests for AlertService class."""

    @pytest.fixture
    def service(self):
        """Create alert service for testing."""
        return AlertService()

    @pytest.fixture
    def sample_anomaly_data(self):
        """Create sample anomaly data."""
        return {
            "id": str(uuid4()),
            "title": "Test Anomaly",
            "severity": "high",
            "anomaly_score": 0.95,
            "source": "test_source",
            "anomaly_type": "suspicious_value",
            "description": "Test anomaly description",
            "indicators": ["indicator1", "indicator2"],
            "recommendations": ["rec1", "rec2"],
            "contract_data": {"contract_id": "123"},
        }

    def test_service_initialization(self, service):
        """Test alert service initialization."""
        assert service.webhook_urls == []
        assert service.alert_emails == []

    def test_parse_webhook_urls_empty(self, service):
        """Test parsing empty webhook URLs."""
        urls = service._parse_webhook_urls()
        assert urls == []

    def test_parse_alert_emails_empty(self, service):
        """Test parsing empty alert emails."""
        emails = service._parse_alert_emails()
        assert emails == []

    def test_format_list_with_items(self, service):
        """Test formatting list with items."""
        items = ["item1", "item2", "item3"]
        result = service._format_list(items)
        assert "- item1" in result
        assert "- item2" in result
        assert "- item3" in result

    def test_format_list_empty(self, service):
        """Test formatting empty list."""
        result = service._format_list([])
        assert result == "- Nenhum"

    def test_generate_alert_message(self, service, sample_anomaly_data):
        """Test alert message generation."""
        message = service._generate_alert_message(sample_anomaly_data)
        assert "HIGH" in message
        assert "Test Anomaly" in message
        assert "0.9500" in message
        assert "test_source" in message
        assert "indicator1" in message
        assert "rec1" in message

    def test_get_severity_color_critical(self, service):
        """Test getting critical severity color."""
        color = service._get_severity_color("CRITICAL")
        assert color == "#dc3545"

    def test_get_severity_color_high(self, service):
        """Test getting high severity color."""
        color = service._get_severity_color("HIGH")
        assert color == "#fd7e14"

    def test_get_severity_color_medium(self, service):
        """Test getting medium severity color."""
        color = service._get_severity_color("MEDIUM")
        assert color == "#ffc107"

    def test_get_severity_color_low(self, service):
        """Test getting low severity color."""
        color = service._get_severity_color("LOW")
        assert color == "#28a745"

    def test_get_severity_color_unknown(self, service):
        """Test getting unknown severity color."""
        color = service._get_severity_color("UNKNOWN")
        assert color == "#6c757d"

    @pytest.mark.asyncio
    async def test_send_webhook_alert(self, service, sample_anomaly_data):
        """Test sending webhook alert."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_client.return_value.__aexit__ = AsyncMock()

            await service._send_webhook_alert(
                "https://example.com/webhook", sample_anomaly_data
            )

            mock_instance.post.assert_called_once()
            call_args = mock_instance.post.call_args
            assert call_args[0][0] == "https://example.com/webhook"
            assert "anomaly" in call_args[1]["json"]

    @pytest.mark.asyncio
    async def test_send_email_alert_disabled(self, service, sample_anomaly_data):
        """Test email alert when email is disabled."""
        # By default email_enabled is False
        with patch("src.services.alert_service.settings") as mock_settings:
            mock_settings.email_enabled = False
            # Should not raise, just log
            await service._send_email_alert("test@gmail.com", sample_anomaly_data)

    @pytest.mark.asyncio
    async def test_send_anomaly_alert_dashboard_only(
        self, service, sample_anomaly_data
    ):
        """Test sending dashboard alert only."""
        with (
            patch.object(service, "_send_webhook_alert", new_callable=AsyncMock),
            patch(
                "src.services.alert_service.supabase_anomaly_service"
            ) as mock_supabase,
        ):
            mock_supabase.create_alert = AsyncMock(return_value={"id": str(uuid4())})

            result = await service.send_anomaly_alert(
                anomaly_id=uuid4(),
                anomaly_data=sample_anomaly_data,
                alert_types=["dashboard"],
            )

            assert "alerts_sent" in result
            assert len(result["alerts_sent"]) == 1
            assert result["alerts_sent"][0]["type"] == "dashboard"

    @pytest.mark.asyncio
    async def test_send_anomaly_alert_webhook(self, service, sample_anomaly_data):
        """Test sending webhook alert."""
        service.webhook_urls = ["https://example.com/webhook"]

        with (
            patch.object(
                service, "_send_webhook_alert", new_callable=AsyncMock
            ) as mock_webhook,
            patch(
                "src.services.alert_service.supabase_anomaly_service"
            ) as mock_supabase,
        ):
            mock_supabase.create_alert = AsyncMock(return_value={"id": str(uuid4())})

            result = await service.send_anomaly_alert(
                anomaly_id=uuid4(),
                anomaly_data=sample_anomaly_data,
                alert_types=["webhook"],
            )

            mock_webhook.assert_called_once()
            assert "alerts_sent" in result

    @pytest.mark.asyncio
    async def test_send_critical_alert_summary_no_anomalies(self, service):
        """Test critical alert summary with no anomalies."""
        with patch(
            "src.services.alert_service.supabase_anomaly_service"
        ) as mock_supabase:
            mock_supabase.get_anomalies = AsyncMock(return_value=[])

            result = await service.send_critical_alert_summary()

            assert result["summary_sent"] is False
            assert "No critical anomalies" in result["reason"]


class TestAlertServiceSingleton:
    """Tests for alert service singleton."""

    def test_singleton_instance_exists(self):
        """Test singleton instance exists."""
        assert alert_service is not None
        assert isinstance(alert_service, AlertService)
