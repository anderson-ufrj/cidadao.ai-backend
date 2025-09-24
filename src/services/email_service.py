"""Email service for sending notifications via SMTP.

This service provides async email sending capabilities with support for:
- HTML and plain text emails
- Attachments
- Multiple recipients (to, cc, bcc)
- Email templates using Jinja2
- Retry logic with exponential backoff
- Connection pooling
"""

import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import aiosmtplib
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, EmailStr, Field, validator
from jinja2 import Environment, FileSystemLoader, select_autoescape
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class EmailAttachment(BaseModel):
    """Email attachment model."""
    filename: str
    content: Union[bytes, str]
    content_type: str = "application/octet-stream"
    
    @validator("content")
    def validate_content(cls, v):
        """Ensure content is bytes."""
        if isinstance(v, str):
            return v.encode()
        return v


class EmailMessage(BaseModel):
    """Email message model with validation."""
    to: List[EmailStr]
    subject: str
    body: Optional[str] = None
    html_body: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    reply_to: Optional[EmailStr] = None
    attachments: Optional[List[EmailAttachment]] = None
    headers: Optional[Dict[str, str]] = None
    template: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    
    @validator("to", "cc", "bcc", pre=True)
    def validate_emails(cls, v):
        """Validate email addresses."""
        if v is None:
            return v
        if isinstance(v, str):
            v = [v]
        validated = []
        for email in v:
            try:
                validated_email = validate_email(email)
                validated.append(validated_email.email)
            except EmailNotValidError as e:
                logger.warning(f"Invalid email address: {email} - {e}")
                continue
        return validated
    
    @validator("body", always=True)
    def validate_body(cls, v, values):
        """Ensure at least one body type is provided."""
        if not v and not values.get("html_body") and not values.get("template"):
            raise ValueError("Either body, html_body, or template must be provided")
        return v


class SMTPConfig(BaseModel):
    """SMTP configuration model."""
    host: str = Field(default_factory=lambda: settings.smtp_host)
    port: int = Field(default_factory=lambda: settings.smtp_port)
    username: Optional[str] = Field(default_factory=lambda: settings.smtp_username)
    password: Optional[str] = Field(default_factory=lambda: settings.smtp_password.get_secret_value() if settings.smtp_password else None)
    use_tls: bool = Field(default_factory=lambda: settings.smtp_use_tls)
    use_ssl: bool = Field(default_factory=lambda: settings.smtp_use_ssl)
    timeout: int = Field(default=30)
    from_email: EmailStr = Field(default_factory=lambda: settings.smtp_from_email)
    from_name: str = Field(default_factory=lambda: settings.smtp_from_name)


class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self, config: Optional[SMTPConfig] = None):
        """Initialize email service.
        
        Args:
            config: SMTP configuration. If not provided, uses settings.
        """
        self.config = config or SMTPConfig()
        self._template_env = self._setup_template_environment()
        self._connection_lock = asyncio.Lock()
        self._smtp_client: Optional[aiosmtplib.SMTP] = None
        
    def _setup_template_environment(self) -> Environment:
        """Setup Jinja2 template environment."""
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        return Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            enable_async=True
        )
    
    async def _get_smtp_client(self) -> aiosmtplib.SMTP:
        """Get or create SMTP client with connection pooling."""
        async with self._connection_lock:
            if self._smtp_client is None or not self._smtp_client.is_connected:
                self._smtp_client = aiosmtplib.SMTP(
                    hostname=self.config.host,
                    port=self.config.port,
                    timeout=self.config.timeout,
                    use_tls=self.config.use_ssl
                )
                
                await self._smtp_client.connect()
                
                if self.config.use_tls and not self.config.use_ssl:
                    await self._smtp_client.starttls()
                
                if self.config.username and self.config.password:
                    await self._smtp_client.login(
                        self.config.username,
                        self.config.password
                    )
                    
            return self._smtp_client
    
    async def _render_template(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> tuple[str, str]:
        """Render email template.
        
        Args:
            template_name: Name of the template file
            context: Template context data
            
        Returns:
            Tuple of (html_body, text_body)
        """
        # Add default context
        default_context = {
            "app_name": "Cidadão.AI",
            "app_url": settings.app_url,
            "support_email": settings.support_email,
        }
        context = {**default_context, **context}
        
        # Render HTML template
        html_template = self._template_env.get_template(f"{template_name}.html")
        html_body = await html_template.render_async(**context)
        
        # Try to render text template, fallback to HTML strip
        try:
            text_template = self._template_env.get_template(f"{template_name}.txt")
            text_body = await text_template.render_async(**context)
        except Exception:
            # Simple HTML to text conversion
            import re
            text_body = re.sub(r"<[^>]+>", "", html_body)
            text_body = re.sub(r"\s+", " ", text_body).strip()
        
        return html_body, text_body
    
    def _create_message(self, email: EmailMessage) -> MIMEMultipart:
        """Create MIME message from EmailMessage."""
        msg = MIMEMultipart("alternative")
        
        # Set headers
        msg["Subject"] = email.subject
        msg["From"] = f"{self.config.from_name} <{self.config.from_email}>"
        msg["To"] = ", ".join(email.to)
        
        if email.cc:
            msg["Cc"] = ", ".join(email.cc)
        
        if email.reply_to:
            msg["Reply-To"] = email.reply_to
        
        # Add custom headers
        if email.headers:
            for key, value in email.headers.items():
                msg[key] = value
        
        # Add text part
        if email.body:
            msg.attach(MIMEText(email.body, "plain"))
        
        # Add HTML part
        if email.html_body:
            msg.attach(MIMEText(email.html_body, "html"))
        
        # Add attachments
        if email.attachments:
            for attachment in email.attachments:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.content)
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={attachment.filename}"
                )
                msg.attach(part)
        
        return msg
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def send_email(self, email: EmailMessage) -> bool:
        """Send an email message.
        
        Args:
            email: Email message to send
            
        Returns:
            True if email was sent successfully
        """
        try:
            # Render template if specified
            if email.template:
                html_body, text_body = await self._render_template(
                    email.template,
                    email.template_data or {}
                )
                email.html_body = html_body
                email.body = text_body
            
            # Create MIME message
            msg = self._create_message(email)
            
            # Get SMTP client
            smtp = await self._get_smtp_client()
            
            # Prepare recipients
            recipients = email.to.copy()
            if email.cc:
                recipients.extend(email.cc)
            if email.bcc:
                recipients.extend(email.bcc)
            
            # Send email
            await smtp.send_message(msg)
            
            logger.info(
                "Email sent successfully",
                subject=email.subject,
                recipients=len(recipients),
                has_attachments=bool(email.attachments)
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to send email",
                subject=email.subject,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def send_batch(
        self,
        emails: List[EmailMessage],
        max_concurrent: int = 5
    ) -> List[bool]:
        """Send multiple emails concurrently.
        
        Args:
            emails: List of email messages
            max_concurrent: Maximum concurrent sends
            
        Returns:
            List of success status for each email
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def send_with_semaphore(email: EmailMessage) -> bool:
            async with semaphore:
                try:
                    return await self.send_email(email)
                except Exception:
                    return False
        
        tasks = [send_with_semaphore(email) for email in emails]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if isinstance(result, bool) else False
            for result in results
        ]
    
    async def close(self):
        """Close SMTP connection."""
        if self._smtp_client and self._smtp_client.is_connected:
            await self._smtp_client.quit()
            self._smtp_client = None


# Singleton instance
email_service = EmailService()


# Convenience functions
async def send_email(
    to: Union[str, List[str]],
    subject: str,
    body: Optional[str] = None,
    html_body: Optional[str] = None,
    template: Optional[str] = None,
    template_data: Optional[Dict[str, Any]] = None,
    attachments: Optional[List[EmailAttachment]] = None,
    **kwargs
) -> bool:
    """Send an email using the default email service.
    
    Args:
        to: Recipient email address(es)
        subject: Email subject
        body: Plain text body
        html_body: HTML body
        template: Template name to render
        template_data: Data for template rendering
        attachments: List of attachments
        **kwargs: Additional email fields (cc, bcc, reply_to, headers)
        
    Returns:
        True if email was sent successfully
    """
    if isinstance(to, str):
        to = [to]
    
    email = EmailMessage(
        to=to,
        subject=subject,
        body=body,
        html_body=html_body,
        template=template,
        template_data=template_data,
        attachments=attachments,
        **kwargs
    )
    
    return await email_service.send_email(email)


async def send_template_email(
    to: Union[str, List[str]],
    subject: str,
    template: str,
    template_data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> bool:
    """Send an email using a template.
    
    Args:
        to: Recipient email address(es)
        subject: Email subject
        template: Template name
        template_data: Template context data
        **kwargs: Additional email fields
        
    Returns:
        True if email was sent successfully
    """
    return await send_email(
        to=to,
        subject=subject,
        template=template,
        template_data=template_data,
        **kwargs
    )