"""Conversational memory for chat contexts."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .base import BaseMemory


@dataclass
class ConversationContext:
    """Context information for conversations."""

    session_id: str
    user_id: str | None = None
    user_profile: dict[str, Any] | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ConversationalMemory(BaseMemory):
    """Memory for conversational contexts and chat history."""

    def __init__(self, max_messages: int = 100):
        super().__init__()
        self._messages: list[dict] = []
        self._max_messages = max_messages
        self._context: dict[str, Any] = {}

    async def store(self, key: str, value: Any, metadata: dict | None = None) -> bool:
        """Store a conversational item."""
        message = {
            "key": key,
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "role": metadata.get("role", "user") if metadata else "user",
        }

        self._messages.append(message)

        # Keep only recent messages
        if len(self._messages) > self._max_messages:
            self._messages = self._messages[-self._max_messages :]

        self._storage[key] = message
        return True

    async def retrieve(self, key: str) -> Any | None:
        """Retrieve a message by key."""
        message = self._storage.get(key)
        return message["value"] if message else None

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search conversation history by query."""
        matching_messages = []
        query_lower = query.lower()

        for message in self._messages[-limit * 2 :]:  # Search in recent messages
            message_text = str(message.get("value", "")).lower()
            if query_lower in message_text:
                matching_messages.append(message)
                if len(matching_messages) >= limit:
                    break

        return matching_messages

    async def clear(self) -> bool:
        """Clear conversation history."""
        self._messages.clear()
        self._context.clear()
        self._storage.clear()
        return True

    def get_conversation_history(self, limit: int | None = None) -> list[dict]:
        """Get conversation history."""
        if limit:
            return self._messages[-limit:]
        return self._messages

    async def get_recent_messages(self, session_id: str, limit: int = 10) -> list[dict]:
        """
        Get recent messages for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return

        Returns:
            List of recent messages with role and content
        """
        # Return recent messages in simplified format
        recent = self._messages[-limit:] if self._messages else []
        return [
            {
                "role": msg.get("role", "user"),
                "content": msg.get("value", ""),
                "timestamp": msg.get("timestamp"),
            }
            for msg in recent
        ]

    async def add_message(
        self,
        role: str = None,
        content: str = None,
        session_id: str = None,
        metadata: dict | None = None,
    ) -> None:
        """Add a message to conversation history (async version)."""
        await self.store(
            f"msg_{len(self._messages)}", content, {**(metadata or {}), "role": role}
        )

    def set_context(self, key: str, value: Any) -> None:
        """Set conversation context."""
        self._context[key] = value

    def get_context(self, key: str) -> Any:
        """Get conversation context."""
        return self._context.get(key)
