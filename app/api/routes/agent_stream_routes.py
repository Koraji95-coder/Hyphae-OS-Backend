"""
agent_stream_routes.py 📡
--------------------------
Handles WebSocket streams for live agent communication.

- Manages per-client connections with unique client IDs
- Integrates with ConnectionManager for scalable broadcasting
- Enables real-time updates in the frontend dashboard
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.core.websocket_manager import manager
import logging


router = APIRouter()
logger = logging.getLogger("agent_stream")

@router.websocket("/agents/{client_id}")
async def agent_log_stream(websocket: WebSocket, client_id: str):
    """
    Establishes a WebSocket connection for a specific client.

    - Adds client to active connection pool
    - Waits for incoming messages (e.g. pings)
    - Cleans up on disconnect
    - Logs connection and disconnection of each client_id
    """
    await manager.connect(websocket, client_id)
    logger.info(f"🟢 Client connected: {client_id}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(client_id)
        logger.info(f"🔴 Client disconnected: {client_id}")