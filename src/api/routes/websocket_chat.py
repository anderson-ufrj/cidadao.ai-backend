"""
WebSocket endpoints for real-time bidirectional chat communication.

This module provides WebSocket connections for:
- Real-time chat with agents
- Live investigation status updates
- Anomaly detection notifications
- Multi-user collaboration
"""

import asyncio
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

from src.core import get_logger
from src.services.chat_service import ChatService

logger = get_logger(__name__)
router = APIRouter()

# Security
security = HTTPBearer(auto_error=False)


class WebSocketMessage(BaseModel):
    """WebSocket message structure."""

    type: str = Field(..., description="Message type")
    data: dict[str, Any] = Field(default_factory=dict, description="Message data")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    id: str = Field(default_factory=lambda: str(uuid4()))


class ConnectionManager:
    """Manages WebSocket connections and broadcasting."""

    def __init__(self):
        # Active connections by session_id
        self.active_connections: dict[str, list[WebSocket]] = {}
        # User subscriptions to investigations
        self.investigation_subscriptions: dict[str, set[str]] = {}
        # Connection metadata
        self.connection_metadata: dict[str, dict[str, Any]] = {}

    async def connect(
        self, websocket: WebSocket, session_id: str, metadata: dict[str, Any] = None
    ):
        """Accept and register new WebSocket connection."""
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(websocket)
        self.connection_metadata[id(websocket)] = metadata or {}

        logger.info(
            f"WebSocket connected: session={session_id}, total_connections={len(self.active_connections[session_id])}"
        )

        # Send welcome message
        await self.send_personal_message(
            WebSocketMessage(
                type="connection",
                data={
                    "status": "connected",
                    "session_id": session_id,
                    "message": "Conectado ao Cidadão.AI em tempo real",
                },
            ),
            websocket,
        )

    async def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove WebSocket connection."""
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

        # Clean up metadata
        if id(websocket) in self.connection_metadata:
            del self.connection_metadata[id(websocket)]

        # Remove from investigation subscriptions
        for investigation_id, subscribers in self.investigation_subscriptions.items():
            if session_id in subscribers:
                subscribers.remove(session_id)

        logger.info(f"WebSocket disconnected: session={session_id}")

    async def send_personal_message(
        self, message: WebSocketMessage, websocket: WebSocket
    ):
        """Send message to specific WebSocket."""
        try:
            await websocket.send_json(message.model_dump(mode="json"))
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")

    async def broadcast_to_session(self, message: WebSocketMessage, session_id: str):
        """Broadcast message to all connections in a session."""
        if session_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[session_id]:
                try:
                    await websocket.send_json(message.model_dump(mode="json"))
                except Exception as e:
                    logger.error(f"Error broadcasting to session {session_id}: {e}")
                    disconnected.append(websocket)

            # Clean up disconnected websockets
            for ws in disconnected:
                await self.disconnect(ws, session_id)

    async def broadcast_to_investigation(
        self, message: WebSocketMessage, investigation_id: str
    ):
        """Broadcast message to all subscribers of an investigation."""
        if investigation_id in self.investigation_subscriptions:
            for session_id in self.investigation_subscriptions[investigation_id]:
                await self.broadcast_to_session(message, session_id)

    def subscribe_to_investigation(self, session_id: str, investigation_id: str):
        """Subscribe session to investigation updates."""
        if investigation_id not in self.investigation_subscriptions:
            self.investigation_subscriptions[investigation_id] = set()
        self.investigation_subscriptions[investigation_id].add(session_id)
        logger.info(
            f"Session {session_id} subscribed to investigation {investigation_id}"
        )

    def unsubscribe_from_investigation(self, session_id: str, investigation_id: str):
        """Unsubscribe session from investigation updates."""
        if investigation_id in self.investigation_subscriptions:
            self.investigation_subscriptions[investigation_id].discard(session_id)
            if not self.investigation_subscriptions[investigation_id]:
                del self.investigation_subscriptions[investigation_id]


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket, session_id: str, token: str | None = Query(None)
):
    """
    WebSocket endpoint for real-time chat.

    Features:
    - Bidirectional communication with agents
    - Real-time streaming responses
    - Investigation status updates
    - Anomaly notifications

    Message Types:
    - chat: User messages and agent responses
    - status: Investigation status updates
    - notification: Anomaly alerts and notifications
    - subscribe/unsubscribe: Investigation subscriptions
    - ping/pong: Keep-alive messages
    """
    # Optional authentication
    user = None
    if token:
        try:
            # Validate token (simplified for example)
            # In production, properly validate JWT token
            user = {"id": "user-123", "name": "User"}
        except Exception:
            await websocket.close(code=1008, reason="Invalid authentication")
            return

    # Connect
    await manager.connect(websocket, session_id, {"user": user})
    chat_service = ChatService()

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = WebSocketMessage(**data)

            logger.info(
                f"WebSocket message received: type={message.type}, session={session_id}"
            )

            # Handle different message types
            if message.type == "chat":
                # Process chat message
                user_message = message.data.get("message", "")

                # Send typing indicator
                await manager.broadcast_to_session(
                    WebSocketMessage(type="typing", data={"agent": "processing"}),
                    session_id,
                )

                # Get response from chat service
                try:
                    response = await chat_service.process_message(
                        message=user_message, session_id=session_id, stream=True
                    )

                    # Stream response chunks
                    async for chunk in response:
                        await manager.broadcast_to_session(
                            WebSocketMessage(
                                type="chat",
                                data={
                                    "role": "assistant",
                                    "content": chunk.get("content", ""),
                                    "agent_id": chunk.get("agent_id"),
                                    "agent_name": chunk.get("agent_name"),
                                    "chunk": True,
                                },
                            ),
                            session_id,
                        )

                    # Send completion
                    await manager.broadcast_to_session(
                        WebSocketMessage(
                            type="chat_complete", data={"status": "completed"}
                        ),
                        session_id,
                    )

                except Exception as e:
                    logger.error(f"Error processing chat message: {e}")
                    await manager.broadcast_to_session(
                        WebSocketMessage(
                            type="error", data={"message": "Erro ao processar mensagem"}
                        ),
                        session_id,
                    )

            elif message.type == "subscribe":
                # Subscribe to investigation updates
                investigation_id = message.data.get("investigation_id")
                if investigation_id:
                    manager.subscribe_to_investigation(session_id, investigation_id)
                    await manager.send_personal_message(
                        WebSocketMessage(
                            type="subscribed",
                            data={
                                "investigation_id": investigation_id,
                                "message": f"Inscrito para atualizações da investigação {investigation_id}",
                            },
                        ),
                        websocket,
                    )

            elif message.type == "unsubscribe":
                # Unsubscribe from investigation
                investigation_id = message.data.get("investigation_id")
                if investigation_id:
                    manager.unsubscribe_from_investigation(session_id, investigation_id)
                    await manager.send_personal_message(
                        WebSocketMessage(
                            type="unsubscribed",
                            data={"investigation_id": investigation_id},
                        ),
                        websocket,
                    )

            elif message.type == "ping":
                # Keep-alive ping
                await manager.send_personal_message(
                    WebSocketMessage(type="pong", data={}), websocket
                )

    except WebSocketDisconnect:
        await manager.disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket, session_id)


@router.websocket("/ws/investigations/{investigation_id}")
async def websocket_investigation_endpoint(
    websocket: WebSocket, investigation_id: str, token: str | None = Query(None)
):
    """
    WebSocket endpoint for investigation-specific updates.

    Receives real-time updates for:
    - Investigation progress
    - Anomaly detections
    - Agent findings
    - Report generation status
    """
    session_id = f"investigation-{investigation_id}-{uuid4()}"

    await manager.connect(websocket, session_id)
    manager.subscribe_to_investigation(session_id, investigation_id)

    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(30)
            await manager.send_personal_message(
                WebSocketMessage(
                    type="heartbeat", data={"investigation_id": investigation_id}
                ),
                websocket,
            )
    except WebSocketDisconnect:
        await manager.disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"Investigation WebSocket error: {e}")
        await manager.disconnect(websocket, session_id)


# Helper functions for sending notifications from other parts of the app


async def notify_investigation_update(
    investigation_id: str, update_type: str, data: dict[str, Any]
):
    """Send investigation update to all subscribers."""
    await manager.broadcast_to_investigation(
        WebSocketMessage(
            type=f"investigation_{update_type}",
            data={
                "investigation_id": investigation_id,
                "update_type": update_type,
                **data,
            },
        ),
        investigation_id,
    )


async def notify_anomaly_detected(investigation_id: str, anomaly_data: dict[str, Any]):
    """Notify subscribers of detected anomaly."""
    await manager.broadcast_to_investigation(
        WebSocketMessage(
            type="anomaly_detected",
            data={
                "investigation_id": investigation_id,
                "severity": anomaly_data.get("severity", "medium"),
                "description": anomaly_data.get("description"),
                "details": anomaly_data,
            },
        ),
        investigation_id,
    )


async def notify_chat_session(session_id: str, notification: dict[str, Any]):
    """Send notification to chat session."""
    await manager.broadcast_to_session(
        WebSocketMessage(type="notification", data=notification), session_id
    )
