import json
from typing import Dict, Set
from fastapi import WebSocket
from app.schemas import WebSocketMessage, VoteUpdateMessage, SuggestionUpdateMessage


class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages"""
    
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a new WebSocket client"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a WebSocket client"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket client"""
        await websocket.send_text(message)
    
    async def broadcast_vote_update(self, vote_update: VoteUpdateMessage):
        """Broadcast vote update to all connected clients"""
        message = WebSocketMessage(
            type="vote_update",
            data=vote_update.dict()
        )
        
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_text(message.json())
                except Exception:
                    # Connection might be closed, ignore
                    pass
    
    async def broadcast_suggestion_update(self, suggestion_update: SuggestionUpdateMessage):
        """Broadcast suggestion update to all connected clients"""
        message = WebSocketMessage(
            type="suggestion_update",
            data=suggestion_update.dict()
        )
        
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_text(message.json())
                except Exception:
                    # Connection might be closed, ignore
                    pass
    
    async def broadcast_new_suggestion(self, suggestion_data: dict):
        """Broadcast new suggestion to all connected clients"""
        message = WebSocketMessage(
            type="new_suggestion",
            data=suggestion_data
        )
        
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_text(message.json())
                except Exception:
                    # Connection might be closed, ignore
                    pass


# Global connection manager instance
manager = ConnectionManager() 