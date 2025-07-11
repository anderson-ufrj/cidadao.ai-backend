"""
WebSocket routes for real-time communication
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, Depends
from typing import Optional

from ..websocket import connection_manager, websocket_handler, WebSocketMessage
from ..auth import auth_manager

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    connection_type: str = Query("general")
):
    """
    Main WebSocket endpoint for real-time communication
    
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
        user = auth_manager.get_current_user(token)
        user_id = user.id
        
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {e}")
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Connect user
    await connection_manager.connect(websocket, user_id, connection_type)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await websocket_handler.handle_message(websocket, message)
                
            except json.JSONDecodeError:
                error_msg = WebSocketMessage(
                    type="error",
                    data={"message": "Invalid JSON format"}
                )
                await connection_manager.send_personal_message(websocket, error_msg)
                
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                error_msg = WebSocketMessage(
                    type="error", 
                    data={"message": f"Error processing message: {str(e)}"}
                )
                await connection_manager.send_personal_message(websocket, error_msg)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: user_id={user_id}")
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        
    finally:
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
        user = auth_manager.get_current_user(token)
        user_id = user.id
        
    except Exception as e:
        logger.error(f"Investigation WebSocket authentication failed: {e}")
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Connect and subscribe to investigation
    await connection_manager.connect(websocket, user_id, f"investigation_{investigation_id}")
    await connection_manager.subscribe_to_investigation(websocket, investigation_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await websocket_handler.handle_message(websocket, message)
                
            except json.JSONDecodeError:
                error_msg = WebSocketMessage(
                    type="error",
                    data={"message": "Invalid JSON format"}
                )
                await connection_manager.send_personal_message(websocket, error_msg)
                
    except WebSocketDisconnect:
        logger.info(f"Investigation WebSocket disconnected: user_id={user_id}, investigation_id={investigation_id}")
        
    except Exception as e:
        logger.error(f"Investigation WebSocket error: {e}")
        
    finally:
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
        user = auth_manager.get_current_user(token)
        user_id = user.id
        
    except Exception as e:
        logger.error(f"Analysis WebSocket authentication failed: {e}")
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Connect and subscribe to analysis
    await connection_manager.connect(websocket, user_id, f"analysis_{analysis_id}")
    await connection_manager.subscribe_to_analysis(websocket, analysis_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await websocket_handler.handle_message(websocket, message)
                
            except json.JSONDecodeError:
                error_msg = WebSocketMessage(
                    type="error", 
                    data={"message": "Invalid JSON format"}
                )
                await connection_manager.send_personal_message(websocket, error_msg)
                
    except WebSocketDisconnect:
        logger.info(f"Analysis WebSocket disconnected: user_id={user_id}, analysis_id={analysis_id}")
        
    except Exception as e:
        logger.error(f"Analysis WebSocket error: {e}")
        
    finally:
        await connection_manager.unsubscribe_from_analysis(websocket, analysis_id)
        connection_manager.disconnect(websocket)