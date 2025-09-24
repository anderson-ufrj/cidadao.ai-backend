"""
WebSocket routes for real-time communication with message batching.
"""

from src.core import json_utils
import asyncio
import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from src.core import get_logger
from src.api.auth import verify_token
from src.infrastructure.websocket.message_batcher import websocket_manager
from src.infrastructure.events.event_bus import get_event_bus, EventType
from ..websocket import connection_manager, websocket_handler, WebSocketMessage

logger = get_logger(__name__)

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    connection_type: str = Query("general")
):
    """
    Main WebSocket endpoint for real-time communication with message batching.
    
    Query parameters:
    - token: JWT access token for authentication
    - connection_type: Type of connection (general, investigation, analysis)
    """
    
    # Authenticate user
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return
    
    try:
        # Verify token and get user
        user_payload = verify_token(token)
        user_id = user_payload["sub"]
        
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {e}")
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Accept connection
    await websocket.accept()
    
    # Generate connection ID
    connection_id = f"{user_id}:{connection_type}:{uuid.uuid4().hex[:8]}"
    
    # Connect with batching manager
    await websocket_manager.connect(connection_id, websocket)
    
    # Connect with legacy manager
    await connection_manager.connect(websocket, user_id, connection_type)
    
    # Join appropriate room
    if connection_type != "general":
        await websocket_manager.join_room(connection_id, connection_type)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                message = json_utils.loads(data)
                
                # Handle ping for keepalive
                if message.get("type") == "ping":
                    await websocket_manager.send_message(
                        connection_id,
                        {
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        priority=10
                    )
                else:
                    # Process with legacy handler
                    await websocket_handler.handle_message(websocket, message)
                
            except json_utils.JSONDecodeError:
                await websocket_manager.send_message(
                    connection_id,
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    priority=8
                )
                
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket_manager.send_message(
                    connection_id,
                    {
                        "type": "error",
                        "message": f"Error processing message: {str(e)}",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    priority=8
                )
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: user_id={user_id}")
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        
    finally:
        await websocket_manager.disconnect(connection_id)
        connection_manager.disconnect(websocket)

@router.websocket("/ws/investigations/{investigation_id}")
async def investigation_websocket(
    websocket: WebSocket,
    investigation_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for specific investigation updates
    """
    
    # Authenticate user
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return
    
    try:
        user_payload = verify_token(token)
        user_id = user_payload["sub"]
        
    except Exception as e:
        logger.error(f"Investigation WebSocket authentication failed: {e}")
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Accept connection
    await websocket.accept()
    
    # Generate connection ID
    connection_id = f"{user_id}:inv:{investigation_id}:{uuid.uuid4().hex[:8]}"
    
    # Connect with batching manager
    await websocket_manager.connect(connection_id, websocket)
    
    # Join investigation room
    await websocket_manager.join_room(connection_id, f"investigation:{investigation_id}")
    
    # Connect and subscribe with legacy manager
    await connection_manager.connect(websocket, user_id, f"investigation_{investigation_id}")
    await connection_manager.subscribe_to_investigation(websocket, investigation_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json_utils.loads(data)
                await websocket_handler.handle_message(websocket, message)
                
            except json_utils.JSONDecodeError:
                error_msg = WebSocketMessage(
                    type="error",
                    data={"message": "Invalid JSON format"}
                )
                await websocket_manager.send_message(
                    connection_id,
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    priority=8
                )
                
    except WebSocketDisconnect:
        logger.info(f"Investigation WebSocket disconnected: user_id={user_id}, investigation_id={investigation_id}")
        
    except Exception as e:
        logger.error(f"Investigation WebSocket error: {e}")
        
    finally:
        await websocket_manager.disconnect(connection_id)
        await connection_manager.unsubscribe_from_investigation(websocket, investigation_id)
        connection_manager.disconnect(websocket)

@router.websocket("/ws/analysis/{analysis_id}")
async def analysis_websocket(
    websocket: WebSocket,
    analysis_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for specific analysis updates
    """
    
    # Authenticate user
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return
    
    try:
        user_payload = verify_token(token)
        user_id = user_payload["sub"]
        
    except Exception as e:
        logger.error(f"Analysis WebSocket authentication failed: {e}")
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Accept connection
    await websocket.accept()
    
    # Generate connection ID
    connection_id = f"{user_id}:ana:{analysis_id}:{uuid.uuid4().hex[:8]}"
    
    # Connect with batching manager
    await websocket_manager.connect(connection_id, websocket)
    
    # Join analysis room
    await websocket_manager.join_room(connection_id, f"analysis:{analysis_id}")
    
    # Connect and subscribe with legacy manager
    await connection_manager.connect(websocket, user_id, f"analysis_{analysis_id}")
    await connection_manager.subscribe_to_analysis(websocket, analysis_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json_utils.loads(data)
                await websocket_handler.handle_message(websocket, message)
                
            except json_utils.JSONDecodeError:
                error_msg = WebSocketMessage(
                    type="error", 
                    data={"message": "Invalid JSON format"}
                )
                await websocket_manager.send_message(
                    connection_id,
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    priority=8
                )
                
    except WebSocketDisconnect:
        logger.info(f"Analysis WebSocket disconnected: user_id={user_id}, analysis_id={analysis_id}")
        
    except Exception as e:
        logger.error(f"Analysis WebSocket error: {e}")
        
    finally:
        await websocket_manager.disconnect(connection_id)
        await connection_manager.unsubscribe_from_analysis(websocket, analysis_id)
        connection_manager.disconnect(websocket)