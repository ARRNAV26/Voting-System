import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from app.auth import get_current_user
from app.websocket_manager import manager
from app.database import get_db

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    
    try:
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": "Connected to voting system"
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                }))
            elif message.get("type") == "subscribe":
                # Client wants to subscribe to updates
                await websocket.send_text(json.dumps({
                    "type": "subscribed",
                    "message": "Subscribed to real-time updates"
                }))
            else:
                # Unknown message type
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Unknown message type"
                }))
                
    except WebSocketDisconnect:
        # Handle client disconnection
        pass
    except Exception as e:
        # Handle other errors
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Error: {str(e)}"
            }))
        except:
            pass


@router.websocket("/ws/{user_id}")
async def authenticated_websocket_endpoint(websocket: WebSocket, user_id: int):
    """Authenticated WebSocket endpoint for real-time communication"""
    await websocket.accept()
    
    try:
        # Connect to manager with user ID
        await manager.connect(websocket, user_id)
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": f"Connected as user {user_id}",
            "user_id": user_id
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": message.get("timestamp"),
                    "user_id": user_id
                }))
            elif message.get("type") == "subscribe":
                # Client wants to subscribe to updates
                await websocket.send_text(json.dumps({
                    "type": "subscribed",
                    "message": "Subscribed to real-time updates",
                    "user_id": user_id
                }))
            else:
                # Unknown message type
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Unknown message type",
                    "user_id": user_id
                }))
                
    except WebSocketDisconnect:
        # Handle client disconnection
        manager.disconnect(websocket, user_id)
    except Exception as e:
        # Handle other errors
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Error: {str(e)}",
                "user_id": user_id
            }))
        except:
            pass
        finally:
            manager.disconnect(websocket, user_id) 