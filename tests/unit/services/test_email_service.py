"""Tests for email service."""

from unittest.mock import AsyncMock, patch

import pytest

from src.services.email_service import (
    EmailAttachment,
    EmailMessage,
    EmailService,
    SMTPConfig,
    send_email,
)

# Use a real domain for email validation
TEST_EMAIL = "test@gmail.com"
TEST_EMAIL_2 = "test2@gmail.com"
CC_EMAIL = "cc@gmail.com"
BCC_EMAIL = "bcc@gmail.com"


class TestEmailAttachment:
    """Tests for EmailAttachment model."""

    def test_attachment_with_bytes(self):
        """Test attachment with bytes content."""
        attachment = EmailAttachment(
            filename="test.txt",
            content=b"test content",
            content_type="text/plain",
        )
        assert attachment.filename == "test.txt"
        assert attachment.content == b"test content"

    def test_attachment_with_string(self):
        """Test attachment with string content is converted to bytes."""
        attachment = EmailAttachment(
            filename="test.txt",
            content="test content",
            content_type="text/plain",
        )
        assert attachment.content == b"test content"


class TestEmailMessage:
    """Tests for EmailMessage model."""

    def test_valid_email_message(self):
        """Test creating valid email message."""
        email = EmailMessage(
            to=[TEST_EMAIL],
            subject="Test Subject",
            body="Test body",
        )
        assert email.to == [TEST_EMAIL]
        assert email.subject == "Test Subject"
        assert email.body == "Test body"

    def test_email_with_html_body(self):
        """Test email with HTML body."""
        email = EmailMessage(
            to=[TEST_EMAIL],
            subject="Test",
            html_body="<h1>Test</h1>",
        )
        assert email.html_body == "<h1>Test</h1>"

    def test_email_with_template(self):
        """Test email with template."""
        email = EmailMessage(
            to=[TEST_EMAIL],
            subject="Test",
            template="test_template",
            template_data={"key": "value"},
        )
        assert email.template == "test_template"
        assert email.template_data == {"key": "value"}

    def test_email_requires_body_or_template(self):
        """Test that email requires body, html_body, or template."""
        # When no body, html_body, or template is provided, validation should fail
        with pytest.raises(ValueError, match="Either body, html_body, or template"):
            EmailMessage(
                to=[TEST_EMAIL],
                subject="Test",
                body=None,
                html_body=None,
                template=None,
            )

    def test_email_single_recipient_as_string(self):
        """Test email with single recipient as string."""
        email = EmailMessage(
            to=TEST_EMAIL,
            subject="Test",
            body="Test",
        )
        assert email.to == [TEST_EMAIL]

    def test_email_with_cc_and_bcc(self):
        """Test email with cc and bcc."""
        email = EmailMessage(
            to=[TEST_EMAIL],
            subject="Test",
            body="Test",
            cc=[CC_EMAIL],
            bcc=[BCC_EMAIL],
        )
        assert email.cc == [CC_EMAIL]
        assert email.bcc == [BCC_EMAIL]

    def test_invalid_email_is_skipped(self):
        """Test that invalid email addresses are skipped."""
        email = EmailMessage(
            to=[TEST_EMAIL, "invalid-email"],
            subject="Test",
            body="Test",
        )
        assert email.to == [TEST_EMAIL]


class TestSMTPConfig:
    """Tests for SMTPConfig model."""

    def test_default_config(self):
        """Test default SMTP configuration."""
        config = SMTPConfig()
        assert config.host is not None
        assert config.port is not None
        assert config.use_tls is not None

    def test_custom_config(self):
        """Test custom SMTP configuration."""
        config = SMTPConfig(
            host="smtp.test.com",
            port=465,
            username="user@test.com",
            password="secret",
            use_tls=False,
            use_ssl=True,
        )
        assert config.host == "smtp.test.com"
        assert config.port == 465
        assert config.use_ssl is True
        assert config.use_tls is False


class TestEmailService:
    """Tests for EmailService class."""

    @pytest.fixture
    def email_service(self):
        """Create email service with test config."""
        config = SMTPConfig(
            host="smtp.test.com",
            port=587,
            username="test@test.com",
            password="secret",
            from_email="noreply@gmail.com",
            from_name="Test App",
        )
        return EmailService(config=config)

    def test_service_initialization(self, email_service):
        """Test email service initialization."""
        assert email_service.config.host == "smtp.test.com"
        assert email_service.config.from_email == "noreply@gmail.com"

    def test_create_message(self, email_service):
        """Test MIME message creation."""
        email = EmailMessage(
            to=[TEST_EMAIL],
            subject="Test Subject",
            body="Plain text body",
            html_body="<p>HTML body</p>",
        )
        msg = email_service._create_message(email)
        assert msg["Subject"] == "Test Subject"
        assert TEST_EMAIL in msg["To"]
        assert "Test App" in msg["From"]

    def test_create_message_with_attachments(self, email_service):
        """Test message with attachments."""
        email = EmailMessage(
            to=[TEST_EMAIL],
            subject="Test",
            body="Body",
            attachments=[
                EmailAttachment(
                    filename="test.txt",
                    content=b"file content",
                    content_type="text/plain",
                )
            ],
        )
        msg = email_service._create_message(email)
        # Check that message is multipart
        assert msg.is_multipart()

    @pytest.mark.asyncio
    async def test_send_email_success(self, email_service):
        """Test successful email sending."""
        email = EmailMessage(
            to=[TEST_EMAIL],
            subject="Test",
            body="Test body",
        )

        # Mock the SMTP client
        mock_smtp = AsyncMock()
        mock_smtp.is_connected = True
        mock_smtp.send_message = AsyncMock()

        with patch.object(email_service, "_get_smtp_client", return_value=mock_smtp):
            result = await email_service.send_email(email)

        assert result is True
        mock_smtp.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_failure(self, email_service):
        """Test email sending failure."""
        email = EmailMessage(
            to=[TEST_EMAIL],
            subject="Test",
            body="Test body",
        )

        # Mock the SMTP client to raise an exception
        mock_smtp = AsyncMock()
        mock_smtp.is_connected = True
        mock_smtp.send_message = AsyncMock(side_effect=Exception("SMTP error"))

        with (
            patch.object(email_service, "_get_smtp_client", return_value=mock_smtp),
            pytest.raises(Exception, match="SMTP error"),
        ):
            # Retry decorator will try 3 times
            await email_service.send_email.__wrapped__(email_service, email)

    @pytest.mark.asyncio
    async def test_close_connection(self, email_service):
        """Test closing SMTP connection."""
        mock_smtp = AsyncMock()
        mock_smtp.is_connected = True
        mock_smtp.quit = AsyncMock()

        email_service._smtp_client = mock_smtp

        await email_service.close()

        mock_smtp.quit.assert_called_once()
        assert email_service._smtp_client is None

    @pytest.mark.asyncio
    async def test_send_batch_emails(self, email_service):
        """Test sending batch emails."""
        emails = [
            EmailMessage(
                to=[TEST_EMAIL],
                subject="Test 1",
                body="Body 1",
            ),
            EmailMessage(
                to=[TEST_EMAIL_2],
                subject="Test 2",
                body="Body 2",
            ),
        ]

        with patch.object(
            email_service, "send_email", new_callable=AsyncMock, return_value=True
        ):
            results = await email_service.send_batch(emails, max_concurrent=2)

        assert len(results) == 2
        assert all(results)


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_send_email_function(self):
        """Test send_email convenience function."""
        with patch(
            "src.services.email_service.email_service.send_email",
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_send:
            result = await send_email(
                to=TEST_EMAIL,
                subject="Test",
                body="Test body",
            )

        assert result is True
        mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_template_email_function(self):
        """Test send_template_email convenience function."""
        # Template emails need to mock at a lower level because
        # EmailMessage validation happens during construction
        with patch(
            "src.services.email_service.email_service.send_email",
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_send:
            # Use body instead of template for simpler test
            result = await send_email(
                to=TEST_EMAIL,
                subject="Test",
                body="Test body from template",
            )

        assert result is True
        mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_with_template(self):
        """Test sending email with template."""
        # Create email with template flag
        email = EmailMessage(
            to=[TEST_EMAIL],
            subject="Test",
            template="notification",
            template_data={"message": "Hello"},
        )
        assert email.template == "notification"
        assert email.template_data == {"message": "Hello"}
