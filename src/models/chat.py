"""
Chat persistence models.

Stores chat sessions and messages in PostgreSQL so conversations
survive deploys and restarts.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, JSON, String, Text

from src.models.base import BaseModel


class ChatSession(BaseModel):
    """Persistent chat session."""

    __tablename__ = "chat_sessions"

    # User (nullable for anonymous)
    user_id = Column(String(255), nullable=True, index=True)

    # Session metadata
    title = Column(String(500), nullable=True)
    agent_id = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="active", index=True)
    current_investigation_id = Column(String(36), nullable=True)
    context = Column(JSON, default=dict)
    last_message_at = Column(DateTime, nullable=True)
    message_count = Column(Integer, default=0)

    __table_args__ = (
        Index("idx_chat_sessions_user_status", "user_id", "status"),
        Index("idx_chat_sessions_last_message", "last_message_at"),
    )

    @property
    def last_activity(self) -> datetime:
        """Backward-compatible alias used by CachedChatService."""
        return self.updated_at or self.created_at

    def to_dict(self) -> dict[str, Any]:
        activity = self.updated_at or self.created_at
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "agent_id": self.agent_id,
            "status": self.status,
            "current_investigation_id": self.current_investigation_id,
            "context": self.context or {},
            "message_count": self.message_count,
            "last_message_at": (
                self.last_message_at.isoformat() if self.last_message_at else None
            ),
            "last_activity": activity.isoformat() if activity else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ChatMessage(BaseModel):
    """Individual chat message."""

    __tablename__ = "chat_messages"

    # Session reference
    session_id = Column(
        String(36),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Message content
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # Agent info
    agent_id = Column(String(100), nullable=True, index=True)
    intent = Column(String(100), nullable=True)

    # References
    investigation_id = Column(String(36), nullable=True)

    # Extra data (column named "metadata" in DB, mapped as message_metadata to
    # avoid collision with SQLAlchemy's reserved .metadata attribute)
    message_metadata = Column("metadata", JSON, default=dict)

    __table_args__ = (
        Index("idx_chat_messages_session_created", "session_id", "created_at"),
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "agent_id": self.agent_id,
            "intent": self.intent,
            "investigation_id": self.investigation_id,
            "metadata": self.message_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
