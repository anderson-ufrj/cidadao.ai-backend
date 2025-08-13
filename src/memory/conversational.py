"""Conversational memory for chat contexts."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from .base import BaseMemory


class ConversationalMemory(BaseMemory):
    """Memory for conversational contexts and chat history."""
    
    def __init__(self, max_messages: int = 100):
        super().__init__()
        self._messages: List[Dict] = []
        self._max_messages = max_messages
        self._context: Dict[str, Any] = {}
    
    async def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """Store a conversational item."""
        message = {
            "key": key,
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "role": metadata.get("role", "user") if metadata else "user"
        }
        
        self._messages.append(message)
        
        # Keep only recent messages
        if len(self._messages) > self._max_messages:
            self._messages = self._messages[-self._max_messages:]
        
        self._storage[key] = message
        return True
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a message by key."""
        message = self._storage.get(key)
        return message["value"] if message else None
    
    async def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search conversation history by query."""
        matching_messages = []
        query_lower = query.lower()
        
        for message in self._messages[-limit*2:]:  # Search in recent messages
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
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history."""
        if limit:
            return self._messages[-limit:]
        return self._messages
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to conversation history."""
        import asyncio
        asyncio.create_task(self.store(
            f"msg_{len(self._messages)}",
            content,
            {**(metadata or {}), "role": role}
        ))
    
    def set_context(self, key: str, value: Any) -> None:
        """Set conversation context."""
        self._context[key] = value
    
    def get_context(self, key: str) -> Any:
        """Get conversation context."""
        return self._context.get(key)