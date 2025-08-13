"""
WebSocket manager for real-time communication in Cidadão.AI
Handles investigation streaming, analysis updates, and notifications
"""

import json
import asyncio
import logging
from typing import Dict, List, Set, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class WebSocketMessage(BaseModel):
    """Standard WebSocket message format"""
    type: str
    data: dict
    timestamp: datetime = None
    user_id: str = None
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)

class ConnectionManager:
    """Manages WebSocket connections and message broadcasting"""
    
    def __init__(self):
        # Active connections by user ID
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        
        # Connections by investigation ID
        self.investigation_connections: Dict[str, Set[WebSocket]] = {}
        
        # Connections by analysis ID  
        self.analysis_connections: Dict[str, Set[WebSocket]] = {}
        
        # Global notification connections
        self.notification_connections: Set[WebSocket] = set()
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, connection_type: str = "general"):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        # Store connection metadata
        self.connection_metadata[websocket] = {
            'user_id': user_id,
            'connection_type': connection_type,
            'connected_at': datetime.utcnow(),
            'last_ping': datetime.utcnow()
        }
        
        # Add to user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        
        # Add to notification connections
        self.notification_connections.add(websocket)
        
        logger.info(f"WebSocket connected: user_id={user_id}, type={connection_type}")
        
        # Send welcome message
        await self.send_personal_message(websocket, WebSocketMessage(
            type="connection_established",
            data={
                "message": "WebSocket connection established",
                "user_id": user_id,
                "connection_type": connection_type
            }
        ))
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket not in self.connection_metadata:
            return
        
        metadata = self.connection_metadata[websocket]
        user_id = metadata['user_id']
        
        # Remove from all connection sets
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        self.notification_connections.discard(websocket)
        
        # Remove from investigation/analysis connections
        for connections in self.investigation_connections.values():
            connections.discard(websocket)
        
        for connections in self.analysis_connections.values():
            connections.discard(websocket)
        
        # Clean up metadata
        del self.connection_metadata[websocket]
        
        logger.info(f"WebSocket disconnected: user_id={user_id}")
    
    async def send_personal_message(self, websocket: WebSocket, message: WebSocketMessage):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(message.json())
        except Exception as e:
            logger.error(f"Failed to send message to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def send_to_user(self, user_id: str, message: WebSocketMessage):
        """Send message to all connections of a specific user"""
        if user_id not in self.user_connections:
            return
        
        message.user_id = user_id
        disconnected = set()
        
        for websocket in self.user_connections[user_id].copy():
            try:
                await websocket.send_text(message.json())
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_to_all(self, message: WebSocketMessage):
        """Broadcast message to all connected users"""
        disconnected = set()
        
        for websocket in self.notification_connections.copy():
            try:
                await websocket.send_text(message.json())
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def subscribe_to_investigation(self, websocket: WebSocket, investigation_id: str):
        """Subscribe WebSocket to investigation updates"""
        if investigation_id not in self.investigation_connections:
            self.investigation_connections[investigation_id] = set()
        
        self.investigation_connections[investigation_id].add(websocket)
        
        await self.send_personal_message(websocket, WebSocketMessage(
            type="subscribed_to_investigation",
            data={
                "investigation_id": investigation_id,
                "message": f"Subscribed to investigation {investigation_id}"
            }
        ))
    
    async def unsubscribe_from_investigation(self, websocket: WebSocket, investigation_id: str):
        """Unsubscribe WebSocket from investigation updates"""
        if investigation_id in self.investigation_connections:
            self.investigation_connections[investigation_id].discard(websocket)
            
            if not self.investigation_connections[investigation_id]:
                del self.investigation_connections[investigation_id]
    
    async def send_to_investigation(self, investigation_id: str, message: WebSocketMessage):
        """Send message to all subscribers of an investigation"""
        if investigation_id not in self.investigation_connections:
            return
        
        disconnected = set()
        
        for websocket in self.investigation_connections[investigation_id].copy():
            try:
                await websocket.send_text(message.json())
            except Exception as e:
                logger.error(f"Failed to send investigation update: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def subscribe_to_analysis(self, websocket: WebSocket, analysis_id: str):
        """Subscribe WebSocket to analysis updates"""
        if analysis_id not in self.analysis_connections:
            self.analysis_connections[analysis_id] = set()
        
        self.analysis_connections[analysis_id].add(websocket)
        
        await self.send_personal_message(websocket, WebSocketMessage(
            type="subscribed_to_analysis", 
            data={
                "analysis_id": analysis_id,
                "message": f"Subscribed to analysis {analysis_id}"
            }
        ))
    
    async def send_to_analysis(self, analysis_id: str, message: WebSocketMessage):
        """Send message to all subscribers of an analysis"""
        if analysis_id not in self.analysis_connections:
            return
        
        disconnected = set()
        
        for websocket in self.analysis_connections[analysis_id].copy():
            try:
                await websocket.send_text(message.json())
            except Exception as e:
                logger.error(f"Failed to send analysis update: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def send_system_notification(self, notification_type: str, data: dict):
        """Send system-wide notification"""
        message = WebSocketMessage(
            type="system_notification",
            data={
                "notification_type": notification_type,
                **data
            }
        )
        
        await self.broadcast_to_all(message)
    
    def get_connection_stats(self) -> dict:
        """Get WebSocket connection statistics"""
        return {
            "total_connections": len(self.connection_metadata),
            "users_connected": len(self.user_connections),
            "active_investigations": len(self.investigation_connections),
            "active_analyses": len(self.analysis_connections),
            "notification_subscribers": len(self.notification_connections)
        }
    
    async def ping_all_connections(self):
        """Send ping to all connections to keep them alive"""
        ping_message = WebSocketMessage(
            type="ping",
            data={"timestamp": datetime.utcnow().isoformat()}
        )
        
        disconnected = set()
        
        for websocket in list(self.connection_metadata.keys()):
            try:
                await websocket.send_text(ping_message.json())
                self.connection_metadata[websocket]['last_ping'] = datetime.utcnow()
            except Exception:
                disconnected.add(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)

# Global connection manager instance
connection_manager = ConnectionManager()

class WebSocketHandler:
    """Handles WebSocket message processing"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def handle_message(self, websocket: WebSocket, message: dict):
        """Process incoming WebSocket message"""
        message_type = message.get('type')
        data = message.get('data', {})
        
        try:
            if message_type == "subscribe_investigation":
                investigation_id = data.get('investigation_id')
                if investigation_id:
                    await self.connection_manager.subscribe_to_investigation(websocket, investigation_id)
            
            elif message_type == "unsubscribe_investigation":
                investigation_id = data.get('investigation_id')
                if investigation_id:
                    await self.connection_manager.unsubscribe_from_investigation(websocket, investigation_id)
            
            elif message_type == "subscribe_analysis":
                analysis_id = data.get('analysis_id')
                if analysis_id:
                    await self.connection_manager.subscribe_to_analysis(websocket, analysis_id)
            
            elif message_type == "pong":
                # Handle pong response
                if websocket in self.connection_manager.connection_metadata:
                    self.connection_manager.connection_metadata[websocket]['last_ping'] = datetime.utcnow()
            
            else:
                logger.warning(f"Unknown WebSocket message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            
            error_message = WebSocketMessage(
                type="error",
                data={
                    "message": f"Failed to process message: {str(e)}",
                    "original_type": message_type
                }
            )
            
            await self.connection_manager.send_personal_message(websocket, error_message)

# Global WebSocket handler
websocket_handler = WebSocketHandler(connection_manager)

# Background task for connection maintenance
async def connection_maintenance_task():
    """Background task to maintain WebSocket connections"""
    while True:
        try:
            await connection_manager.ping_all_connections()
            await asyncio.sleep(30)  # Ping every 30 seconds
        except Exception as e:
            logger.error(f"Error in connection maintenance: {e}")
            await asyncio.sleep(60)  # Wait longer on error