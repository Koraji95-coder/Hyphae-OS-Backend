import asyncio
import logging
from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    📡 Manages WebSocket connections, broadcasting, and heartbeat tasks
    across connected clients in the system.
    
    Features:
    - 🔌 Tracks active client sockets
    - 🫀 Sends periodic heartbeats for liveness
    - 📊 Maintains connection stats
    - 📢 Broadcasts messages to all clients (with exclusions)
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_stats: Dict[str, Dict[str, Any]] = {}
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """
        🔌 Accept and register a new WebSocket connection.
        - Starts heartbeat loop per connection.
        - Stores connection metadata for visibility/debugging.
        """
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            self.connection_stats[client_id] = {
                "connected_at": datetime.utcnow(),
                "messages_received": 0,
                "messages_sent": 0,
                "last_heartbeat": datetime.utcnow()
            }

            # 🚀 Launch heartbeat coroutine for this client
            self.heartbeat_tasks[client_id] = asyncio.create_task(
                self._heartbeat_loop(client_id)
            )

            logger.info(f"[WebSocket] New connection: {client_id}")

        except Exception as e:
            logger.error(f"[WebSocket] Connection error: {e}")
            await self.disconnect(client_id)

    async def disconnect(self, client_id: str):
        """
        ❌ Disconnect a client and clean up resources.
        - Cancels the heartbeat.
        - Removes from stats and connection pools.
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].close()
            except Exception as e:
                logger.error(f"[WebSocket] Error closing {client_id}: {e}")
            finally:
                if client_id in self.heartbeat_tasks:
                    self.heartbeat_tasks[client_id].cancel()
                    del self.heartbeat_tasks[client_id]
                del self.active_connections[client_id]
                del self.connection_stats[client_id]
                logger.info(f"[WebSocket] Client disconnected: {client_id}")

    async def broadcast(self, message: Dict[str, Any], exclude: Set[str] = None):
        """
        📢 Send a message to all connected clients.
        - Skips clients in the `exclude` list.
        - Handles cleanup of disconnected clients.
        """
        exclude = exclude or set()
        disconnected = []

        for client_id, websocket in self.active_connections.items():
            if client_id not in exclude:
                try:
                    await websocket.send_json(message)
                    self.connection_stats[client_id]["messages_sent"] += 1
                except Exception as e:
                    logger.error(f"[WebSocket] Broadcast error for {client_id}: {e}")
                    disconnected.append(client_id)

        # 🧹 Remove any dead connections
        for client_id in disconnected:
            await self.disconnect(client_id)

    async def _heartbeat_loop(self, client_id: str):
        """
        🫀 Periodically send a heartbeat to a connected client.
        - Ensures clients remain active.
        - Helps frontend detect disconnection/liveness.
        """
        while True:
            try:
                if client_id not in self.active_connections:
                    break

                websocket = self.active_connections[client_id]
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })

                self.connection_stats[client_id]["last_heartbeat"] = datetime.utcnow()
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"[WebSocket] Heartbeat error for {client_id}: {e}")
                await self.disconnect(client_id)
                break

    def get_connection_stats(self) -> Dict[str, Any]:
        """
        📊 Return live WebSocket connection stats for diagnostics.
        """
        return {
            "total_connections": len(self.active_connections),
            "connections": self.connection_stats
        }

# 🧠 Singleton WebSocket connection manager
manager = ConnectionManager()
