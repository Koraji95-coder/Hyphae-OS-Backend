"""
📁 mycocore_routes.py

Defines the endpoints for MycoCore system status and real-time WebSocket streaming.

Features:
- 📊 System snapshot reporting (uptime, CPU, memory, agents)
- 🌐 WebSocket support for real-time log/event streaming
- 🧩 Includes broadcast and disconnect handling
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from typing import List

import logging, asyncio, psutil

from datetime import datetime, timedelta

from backend.app.core.websocket_manager import manager

router = APIRouter()
logger = logging.getLogger("mycocore")

# 🧬 Response schema for system snapshot
class Snapshot(BaseModel):
    status: str
    uptime: str
    memory_usage: float
    cpu_usage: float
    agents: List[str]

# 📡 Real-time system event model
class SystemEvent(BaseModel):
    type: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# 📊 Snapshot endpoint for CPU, memory, uptime, etc.
@router.get("/mycocore/snapshot", response_model=Snapshot, tags=["mycocore"])
async def get_mycocore_snapshot():
    """
    📊 Get system performance snapshot

    Returns uptime, CPU%, memory%, and active agent list.
    """
    try:
        uptime_seconds = datetime.utcnow().timestamp() - psutil.boot_time()
        uptime = str(timedelta(seconds=int(uptime_seconds)))
        memory = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent(interval=0.5)

        return Snapshot(
            status="ok",
            uptime=uptime,
            memory_usage=memory,
            cpu_usage=cpu,
            agents=["neuroweave", "rootbloom", "sporelink"]  # TODO: Replace with dynamic agent fetch
        )
    except Exception as e:
        logger.error(f"MycoCore snapshot error: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch MycoCore data.")

# 🌐 WebSocket endpoint for real-time streaming
@router.websocket("/mycocore/stream")
async def agent_log_stream(websocket: WebSocket):
    """
    🌐 WebSocket endpoint for real-time system event streaming
    """
    await websocket.accept()
    logger.info("WebSocket connection established for /mycocore/stream")

    try:
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to MycoCore stream",
            "timestamp": datetime.utcnow().isoformat()
        })

        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=30)

                if msg.lower() == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })

            except asyncio.TimeoutError:
                # 🔁 Send heartbeat every 30s
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected from /mycocore/stream")
        await handle_disconnect(websocket)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await handle_disconnect(websocket)

# 🔌 Disconnect handler
async def handle_disconnect(websocket: WebSocket):
    """
    Handle WebSocket disconnection cleanup
    """
    try:
        logger.info("Cleaning up disconnected WebSocket")
        await websocket.close()
    except Exception as e:
        logger.warning(f"Error during WebSocket cleanup: {e}")

# 📡 Broadcast helper
async def broadcast_event(event: SystemEvent):
    """
    Broadcast a system event to all connected clients via manager
    """
    try:
        await manager.broadcast(event.dict())
    except Exception as e:
        logger.error(f"Failed to broadcast event: {e}")
