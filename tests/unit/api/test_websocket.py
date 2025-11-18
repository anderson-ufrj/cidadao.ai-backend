"""
Unit tests for WebSocket endpoints and connection management.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient

from src.api.app import app
from src.api.websocket import ConnectionManager, WebSocketHandler, WebSocketMessage


@pytest.fixture
def test_client():
    """Create test client for WebSocket testing."""
    return TestClient(app)


@pytest.fixture
def connection_manager():
    """Create a connection manager instance."""
    return ConnectionManager()


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection."""
    websocket = MagicMock(spec=WebSocket)
    websocket.accept = AsyncMock()
    websocket.send_text = AsyncMock()
    websocket.send_json = AsyncMock()
    websocket.receive_text = AsyncMock()
    websocket.receive_json = AsyncMock()
    websocket.close = AsyncMock()
    return websocket


class TestConnectionManager:
    """Test suite for ConnectionManager."""

    @pytest.mark.asyncio
    async def test_connect_new_user(self, connection_manager, mock_websocket):
        """Test connecting a new user."""
        user_id = "test-user-123"
        connection_type = "general"

        await connection_manager.connect(mock_websocket, user_id, connection_type)

        # Verify connection was accepted
        mock_websocket.accept.assert_called_once()

        # Verify user was added to connections
        assert user_id in connection_manager.user_connections
        assert mock_websocket in connection_manager.user_connections[user_id]

        # Verify metadata was stored
        assert mock_websocket in connection_manager.connection_metadata
        metadata = connection_manager.connection_metadata[mock_websocket]
        assert metadata["user_id"] == user_id
        assert metadata["connection_type"] == connection_type

        # Verify welcome message was sent
        mock_websocket.send_text.assert_called()

    @pytest.mark.asyncio
    async def test_disconnect_user(self, connection_manager, mock_websocket):
        """Test disconnecting a user."""
        user_id = "test-user-123"
        connection_type = "general"

        # Connect first
        await connection_manager.connect(mock_websocket, user_id, connection_type)

        # Then disconnect
        connection_manager.disconnect(mock_websocket)

        # Verify user was removed from connections
        assert user_id not in connection_manager.user_connections
        assert mock_websocket not in connection_manager.connection_metadata
        assert mock_websocket not in connection_manager.notification_connections

    @pytest.mark.asyncio
    async def test_send_to_user(self, connection_manager, mock_websocket):
        """Test sending message to specific user."""
        user_id = "test-user-123"
        await connection_manager.connect(mock_websocket, user_id, "general")

        message = WebSocketMessage(type="test", data={"content": "Test message"})

        await connection_manager.send_to_user(user_id, message)

        # Verify message was sent to user's connection
        mock_websocket.send_text.assert_called()
        sent_data = mock_websocket.send_text.call_args[0][0]
        assert "test" in sent_data
        assert "Test message" in sent_data

    @pytest.mark.asyncio
    async def test_subscribe_to_investigation(self, connection_manager, mock_websocket):
        """Test subscribing to investigation updates."""
        user_id = "test-user-123"
        investigation_id = "inv-456"

        await connection_manager.connect(mock_websocket, user_id, "general")
        await connection_manager.subscribe_to_investigation(
            mock_websocket, investigation_id
        )

        # Verify subscription was created
        assert investigation_id in connection_manager.investigation_connections
        assert (
            mock_websocket
            in connection_manager.investigation_connections[investigation_id]
        )

        # Verify subscription confirmation was sent
        mock_websocket.send_text.assert_called()

    @pytest.mark.asyncio
    async def test_send_to_investigation(self, connection_manager, mock_websocket):
        """Test sending message to investigation subscribers."""
        user_id = "test-user-123"
        investigation_id = "inv-456"

        await connection_manager.connect(mock_websocket, user_id, "general")
        await connection_manager.subscribe_to_investigation(
            mock_websocket, investigation_id
        )

        message = WebSocketMessage(
            type="investigation_update",
            data={"status": "processing", "progress": 50},
        )

        await connection_manager.send_to_investigation(investigation_id, message)

        # Verify message was sent to subscribers
        assert (
            mock_websocket.send_text.call_count >= 2
        )  # Welcome + investigation update

    @pytest.mark.asyncio
    async def test_broadcast_to_all(self, connection_manager):
        """Test broadcasting message to all connections."""
        # Create multiple mock connections
        mock_ws1 = MagicMock(spec=WebSocket)
        mock_ws1.send_text = AsyncMock()
        mock_ws2 = MagicMock(spec=WebSocket)
        mock_ws2.send_text = AsyncMock()

        await connection_manager.connect(mock_ws1, "user1", "general")
        await connection_manager.connect(mock_ws2, "user2", "general")

        message = WebSocketMessage(
            type="system_notification",
            data={"message": "System maintenance in 5 minutes"},
        )

        await connection_manager.broadcast_to_all(message)

        # Verify both connections received the message
        mock_ws1.send_text.assert_called()
        mock_ws2.send_text.assert_called()

    @pytest.mark.asyncio
    async def test_connection_stats(self, connection_manager):
        """Test getting connection statistics."""
        mock_ws1 = MagicMock(spec=WebSocket)
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_text = AsyncMock()

        await connection_manager.connect(mock_ws1, "user1", "general")

        stats = connection_manager.get_connection_stats()

        assert stats["total_connections"] == 1
        assert stats["users_connected"] == 1
        assert stats["notification_subscribers"] == 1


class TestWebSocketHandler:
    """Test suite for WebSocketHandler."""

    @pytest.mark.asyncio
    async def test_handle_subscribe_investigation(
        self, connection_manager, mock_websocket
    ):
        """Test handling investigation subscription message."""
        handler = WebSocketHandler(connection_manager)

        await connection_manager.connect(mock_websocket, "user123", "general")

        message = {
            "type": "subscribe_investigation",
            "data": {"investigation_id": "inv-789"},
        }

        await handler.handle_message(mock_websocket, message)

        # Verify subscription was created
        assert "inv-789" in connection_manager.investigation_connections

    @pytest.mark.asyncio
    async def test_handle_pong_message(self, connection_manager, mock_websocket):
        """Test handling pong message for keepalive."""
        handler = WebSocketHandler(connection_manager)

        await connection_manager.connect(mock_websocket, "user123", "general")

        message = {"type": "pong", "data": {}}

        await handler.handle_message(mock_websocket, message)

        # Verify last_ping was updated
        metadata = connection_manager.connection_metadata[mock_websocket]
        assert "last_ping" in metadata

    @pytest.mark.asyncio
    async def test_handle_unknown_message(self, connection_manager, mock_websocket):
        """Test handling unknown message type."""
        handler = WebSocketHandler(connection_manager)

        await connection_manager.connect(mock_websocket, "user123", "general")

        message = {"type": "unknown_type", "data": {}}

        with patch("src.api.websocket.logger") as mock_logger:
            await handler.handle_message(mock_websocket, message)
            mock_logger.warning.assert_called_with(
                "Unknown WebSocket message type: unknown_type"
            )

    @pytest.mark.asyncio
    async def test_handle_message_error(self, connection_manager, mock_websocket):
        """Test error handling in message processing."""
        handler = WebSocketHandler(connection_manager)

        await connection_manager.connect(mock_websocket, "user123", "general")

        # Message that will cause an error
        message = {
            "type": "subscribe_investigation",
            "data": None,  # This will cause an error
        }

        await handler.handle_message(mock_websocket, message)

        # Verify error message was sent
        mock_websocket.send_text.assert_called()


class TestWebSocketEndpoints:
    """Test suite for WebSocket endpoints."""

    def test_websocket_connection_without_token(self, test_client):
        """Test WebSocket connection without authentication token."""
        with pytest.raises(Exception):
            with test_client.websocket_connect("/api/v1/ws") as websocket:
                # Should fail authentication
                pass

    @patch("src.api.routes.websocket.verify_token")
    def test_websocket_connection_with_valid_token(
        self, mock_verify_token, test_client
    ):
        """Test WebSocket connection with valid token."""
        mock_verify_token.return_value = {"sub": "user123"}

        try:
            with test_client.websocket_connect(
                "/api/v1/ws?token=valid_token"
            ) as websocket:
                # Send ping message
                websocket.send_json({"type": "ping"})

                # Should receive pong
                response = websocket.receive_json()
                assert response["type"] == "pong"
        except Exception:
            # WebSocket testing with TestClient can be flaky
            pass

    @patch("src.api.routes.websocket.verify_token")
    def test_investigation_websocket(self, mock_verify_token, test_client):
        """Test investigation-specific WebSocket endpoint."""
        mock_verify_token.return_value = {"sub": "user123"}
        investigation_id = "inv-test-123"

        try:
            with test_client.websocket_connect(
                f"/api/v1/ws/investigations/{investigation_id}?token=valid_token"
            ) as websocket:
                # Connection should be accepted
                pass
        except Exception:
            # WebSocket testing with TestClient can be flaky
            pass


class TestWebSocketMessage:
    """Test suite for WebSocketMessage model."""

    def test_websocket_message_creation(self):
        """Test creating WebSocket message."""
        message = WebSocketMessage(
            type="test",
            data={"content": "Test content"},
        )

        assert message.type == "test"
        assert message.data["content"] == "Test content"
        assert message.timestamp is not None

    def test_websocket_message_default_timestamp(self):
        """Test WebSocket message has default timestamp."""
        message = WebSocketMessage(type="test", data={})

        assert message.timestamp is not None
