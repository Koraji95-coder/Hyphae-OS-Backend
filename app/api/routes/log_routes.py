"""
📁 log_routes.py

Defines the endpoints for logging and querying system events.

Features:
- Admin-only structured log saving to DB + file
- Log querying for dashboard analytics
- Enforces JWT-based access control for all operations
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from backend.app.core.utils.logger import get_request_log_context
from backend.app.api.models.system_log_model import SystemLog
from backend.app.services.database import get_db
from backend.app.services.token_service import verify_token

router = APIRouter()
logger = logging.getLogger("logs")
security = HTTPBearer()

class LogEntry(BaseModel):
    """
    📝 Represents a structured system log entry.

    Fields:
    - agent: Identifier for the agent or service generating the log
    - event: Event type or short description
    - data: Flexible dictionary containing event metadata or state
    """
    agent: str
    event: str
    data: Dict[str, Any]

@router.post("/logs/save", tags=["logs"])
async def save_log(entry: LogEntry, token=Depends(security), db: Session = Depends(get_db)):
    """
    📝 Save a structured system log entry (Admin-Only)

    - Requires JWT access token
    - Logs to DB and to file via Python logger
    - Broadcasts event to connected WebSocket clients
    """
    payload = verify_token(token.credentials)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: insufficient privileges")

    try:
        # 🧠 Save to database
        db_log = SystemLog(agent=entry.agent, event=entry.event, data=entry.data)
        db.add(db_log)
        db.commit()

        # 📡 Broadcast event to WebSocket clients
        event = SystemEvent(type=entry.event, message=str(entry.data))
        await manager.broadcast(event.dict())

        # 🗂️ Also write to file
        logger.info(f"[{entry.agent}] {entry.event}: {entry.data}", extra=get_request_log_context())
        return {"status": "ok", "log_id": db_log.id}

    except Exception as e:
        logger.error(f"Failed to save log: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Failed to save log entry")

    
@router.get("/logs/query", tags=["logs"])
async def query_logs(limit: int = 100, db: Session = Depends(get_db), token=Depends(security)):
    """
    🔎 Query system logs (Admin-Only)

    - Returns recent logs ordered by timestamp
    - Accessible from admin dashboard
    """
    payload = verify_token(token.credentials)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: insufficient privileges")

    try:
        logs = db.query(SystemLog).order_by(SystemLog.timestamp.desc()).limit(limit).all()
        logger.info(f"Queried last {limit} logs", extra=get_request_log_context())
        return JSONResponse(content=[
            {
                "id": log.id,
                "agent": log.agent,
                "event": log.event,
                "data": log.data,
                "timestamp": log.timestamp.isoformat()
            }
            for log in logs
        ])
    except Exception as e:
        logger.error(f"Failed to query logs: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Failed to fetch logs")