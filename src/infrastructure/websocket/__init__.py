"""WebSocket infrastructure for Cidadão.AI."""

from .message_batcher import MessageBatcher, WebSocketManager, websocket_manager

__all__ = ["MessageBatcher", "WebSocketManager", "websocket_manager"]
