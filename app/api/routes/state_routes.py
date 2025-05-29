"""
📁 state_routes.py

Manages endpoints for reading system-wide state and memory status.

Features:
- Return current system status and user context
- Expose runtime flags and in-memory structures
- Used by agents or UI to reflect backend brain/memory state
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import logging

from backend.app.core.utils.logger import get_request_log_context
from backend.app.core.memory.redis_memory_engine import RedisMemoryEngine

router = APIRouter()
logger = logging.getLogger("state")

class SystemState(BaseModel):
    """
    📦 Represents the full runtime system state.

    Fields:
    - user: Current active user or context actor
    - mood: Operational mood/status of the system
    - flags: Runtime flags for system control
    - memory: In-memory context or history
    """
    user: str
    mood: str
    flags: Dict[str, Any]
    memory: Dict[str, Any]

@router.get("/state", response_model=SystemState, tags=["state"])
async def get_system_state():
    """
    🔎 Get full system state including user context, mood, flags, and memory.

    - Useful for debugging or context introspection
    - Returns a static mock unless connected to real brain state
    """
    try:
        state = {
            "user": "system",
            "mood": "operational",
            "flags": {},
            "memory": {}
        }
        logger.info("System state requested", extra=get_request_log_context())
        return state
    except Exception as e:
        logger.error(f"Failed to get system state: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Failed to fetch system state")

@router.get("/state/memory", tags=["state"])
async def get_memory_state():
    """
    🧠 Get current memory and runtime flags only.

    - Focuses on lightweight memory layer view
    - Typically called more frequently than full system state
    """
    try:
        memory_snapshot = {
            "flags": {},
            "memory": {}
        }
        logger.info("Memory state requested", extra=get_request_log_context())
        return memory_snapshot
    except Exception as e:
        logger.error(f"Failed to get memory state: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Failed to fetch memory state")

class MemoryEntry(BaseModel):
    type: str
    agent: str
    user: str
    mood: Optional[str] = None
    timestamp: str
    content: str

@router.get("/state/memory/chain/{user}", response_model=List[MemoryEntry], tags=["state"])
async def get_user_memory_chain(user: str):
    """
    🧬 Visualize structured memory chain for a user.

    - Returns a time-ordered list of prompt/response entries
    - Each entry includes mood, agent, timestamp
    """
    try:
        redis_engine = RedisMemoryEngine()
        keys = redis_engine.redis.keys(f"*{user}:last_*")
        entries = []

        for key in keys:
            raw = redis_engine.redis.get(key)
            if raw:
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, dict):
                        entries.append(parsed)
                except Exception:
                    pass

        # Sort by timestamp
        entries.sort(key=lambda x: x.get("timestamp", ""))
        return entries
    except Exception as e:
        logger.error(f"Memory chain error: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Unable to visualize memory chain")