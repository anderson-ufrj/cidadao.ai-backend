"""Notification models for database persistence."""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import (
    Column, String, Boolean, DateTime, JSON, Text,
    Integer, ForeignKey, Table, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class NotificationChannel(str, Enum):
    """Available notification channels."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    PUSH = "push"
    SMS = "sms"
    SLACK = "slack"


class NotificationFrequency(str, Enum):
    """Notification frequency preferences."""
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    NEVER = "never"


# Association table for user notification preferences
user_notification_channels = Table(
    'user_notification_channels',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('channel', SQLEnum(NotificationChannel)),
    Column('notification_type', String),
    Column('enabled', Boolean, default=True)
)


class NotificationPreferenceDB(Base):
    """Notification preferences database model."""
    __tablename__ = 'notification_preferences'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Global preferences
    enabled = Column(Boolean, default=True)
    frequency = Column(SQLEnum(NotificationFrequency), default=NotificationFrequency.IMMEDIATE)
    
    # Channel-specific settings
    email_enabled = Column(Boolean, default=True)
    webhook_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=False)
    sms_enabled = Column(Boolean, default=False)
    
    # Type-specific preferences (JSON)
    type_preferences = Column(JSON, default={})
    
    # Contact information
    email_addresses = Column(JSON, default=[])  # List of emails
    webhook_urls = Column(JSON, default=[])     # List of webhook configs
    phone_numbers = Column(JSON, default=[])    # List of phone numbers
    push_tokens = Column(JSON, default=[])      # List of push tokens
    
    # Time preferences
    quiet_hours_start = Column(String)  # HH:MM format
    quiet_hours_end = Column(String)    # HH:MM format
    timezone = Column(String, default='America/Sao_Paulo')
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class NotificationPreference(BaseModel):
    """Notification preferences Pydantic model."""
    user_id: str
    enabled: bool = True
    frequency: NotificationFrequency = NotificationFrequency.IMMEDIATE
    
    # Channel settings
    email_enabled: bool = True
    webhook_enabled: bool = False
    push_enabled: bool = False
    sms_enabled: bool = False
    
    # Type-specific preferences
    type_preferences: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Contact information
    email_addresses: List[EmailStr] = Field(default_factory=list)
    webhook_urls: List[Dict[str, Any]] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    push_tokens: List[str] = Field(default_factory=list)
    
    # Time preferences
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: str = "America/Sao_Paulo"
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "enabled": True,
                "frequency": "immediate",
                "email_enabled": True,
                "webhook_enabled": True,
                "type_preferences": {
                    "anomaly_detected": {
                        "enabled": True,
                        "channels": ["email", "webhook"],
                        "min_severity": "medium"
                    },
                    "investigation_complete": {
                        "enabled": True,
                        "channels": ["email"],
                        "frequency": "daily"
                    }
                },
                "email_addresses": ["user@example.com"],
                "webhook_urls": [
                    {
                        "url": "https://example.com/webhook",
                        "secret": "webhook_secret",
                        "events": ["anomaly_detected"]
                    }
                ]
            }
        }


class NotificationHistoryDB(Base):
    """Notification history database model."""
    __tablename__ = 'notification_history'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Notification details
    type = Column(String, nullable=False)
    level = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    
    # Delivery status
    channels_requested = Column(JSON, default=[])
    channels_delivered = Column(JSON, default=[])
    delivery_status = Column(JSON, default={})  # Channel -> status mapping
    
    # Metadata (renamed to avoid SQLAlchemy reserved word)
    notification_metadata = Column('metadata', JSON, default={})
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    read_at = Column(DateTime, nullable=True)
    
    # Error tracking
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)


class NotificationHistory(BaseModel):
    """Notification history Pydantic model."""
    id: str
    user_id: str
    type: str
    level: str
    title: str
    message: str
    channels_requested: List[str] = Field(default_factory=list)
    channels_delivered: List[str] = Field(default_factory=list)
    delivery_status: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    read_at: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None


class WebhookConfigDB(Base):
    """Webhook configuration database model."""
    __tablename__ = 'webhook_configs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Webhook details
    url = Column(String, nullable=False)
    secret = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    # Event filtering
    events = Column(JSON, default=[])  # List of event types
    active = Column(Boolean, default=True)
    
    # Headers and authentication
    headers = Column(JSON, default={})
    auth_type = Column(String, nullable=True)  # 'basic', 'bearer', 'custom'
    auth_value = Column(String, nullable=True)
    
    # Retry configuration
    max_retries = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=30)
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_triggered_at = Column(DateTime, nullable=True)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)


class WebhookConfig(BaseModel):
    """Webhook configuration Pydantic model."""
    id: Optional[int] = None
    user_id: str
    url: str
    secret: Optional[str] = None
    description: Optional[str] = None
    events: List[str] = Field(default_factory=list)
    active: bool = True
    headers: Dict[str, str] = Field(default_factory=dict)
    auth_type: Optional[str] = None
    auth_value: Optional[str] = None
    max_retries: int = 3
    timeout_seconds: int = 30