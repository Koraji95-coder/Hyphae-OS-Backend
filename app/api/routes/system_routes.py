"""
system_routes.py 🧠
--------------------
Endpoints related to the core system state and operational mode.

Features:
- 🔍 Admin-only retrieval of system runtime state
- 🔧 Mode switching for runtime behavior
- 🧠 Integrated logging for audit visibility
"""

from fastapi.responses import FileResponse
from fastapi import APIRouter, HTTPException, Depends

from pydantic import BaseModel
from typing import Dict, Any

import logging, json, tempfile

from backend.app.utils.pdf_exporter import PDFExporter
from backend.app.services.dependencies import require_role
from backend.app.agents.mycocore_agent import Mycocore

from backend.app.core.registry.agents import get_registered_agents
from backend.app.core.utils.logger import get_request_log_context
from backend.app.core.cache.redis_cache import get_redis_client  # or directly use RedisMemoryEngine
from backend.app.core.memory.redis_memory_engine import RedisMemoryEngine


router = APIRouter()
logger = logging.getLogger("system")
core = Mycocore()

# 🧠 Represents current system state snapshot
class SystemState(BaseModel):
    mode: str
    flags: Dict[str, Any]
    memory: Dict[str, Any]

@router.get("/system/state", response_model=SystemState, tags=["system"])
async def get_system_state(user=Depends(require_role("admin"))):
    """
    🔍 Get current system state (Admin-only)

    - Returns operational mode, flags, memory
    - Requires admin-level access via token
    """
    try:
        system_state = {
            "mode": "operational",
            "flags": {},
            "memory": {}
        }
        logger.info("System state retrieved", extra=get_request_log_context())
        return system_state
    except Exception as e:
        logger.error(f"Failed to get system state: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Failed to get system state")

@router.post("/system/mode", tags=["system"])
async def set_system_mode(mode: str, user=Depends(require_role("admin"))):
    """
    🔧 Set the system's operational mode (Admin-only)

    - Logs the mode change for audit tracking
    """
    try:
        logger.info(f"System mode set to: {mode}", extra=get_request_log_context())
        return {"status": "ok", "mode": mode}
    except Exception as e:
        logger.error(f"Failed to set system mode: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Failed to set system mode")

@router.get("/core/status", tags=["system"])
def get_core_status():
    """
    🧠 MycoCore Status Endpoint
    ──────────────────────────────────────
    Returns:
    - Safe mode status (True if system is in restricted state)
    - Registered agents
    - Current system flags
    """
    return {
        "safe_mode": not core.is_safe(),
        "active_agents": list(core.get_active_agents()),
        "flags": core._system_flags  # ⚠️ Optional: sanitize if needed
    }

@router.post("/core/safe-mode/toggle", tags=["system"])
def toggle_safe_mode():
    """
    🔁 Toggle MycoCore Safe Mode
    ──────────────────────────────────────
    Enables or disables safe mode.

    Used for:
    - Emergency halts
    - System maintenance
    - Developer control
    """
    if core.is_safe():
        core.enable_safe_mode()
    else:
        core.disable_safe_mode()

@router.get("/system/memory/{user}", tags=["system"])
def view_redis_memory(user: str, actor=Depends(require_role("admin"))):
    """
    🧠 View all Redis memory for a specific user.
    Admin-only endpoint. Used for debugging and trace inspection.
    """
    try:
        memory_engine = RedisMemoryEngine()
        keys = memory_engine.redis.keys(f"{user}:*")
        memory_dump = {}
        for key in keys:
            val = memory_engine.redis.get(key)
            try:
                memory_dump[key] = json.loads(val)
            except Exception:
                memory_dump[key] = val
        return memory_dump
    except Exception as e:
        logger.error(f"Failed to read Redis memory for {user}: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Unable to access memory state.")
    
@router.get("/system/rbac", tags=["system"])
def get_all_roles(actor=Depends(require_role("admin"))):
    """
    📜 Get current role assignments (Admin only)
    """
    return load_roles()

class RoleUpdateRequest(BaseModel):
    email: str
    role: str

@router.post("/system/rbac/update", tags=["system"])
def update_user_role(update: RoleUpdateRequest, actor=Depends(require_role("owner"))):
    """
    ✏️ Update a user's role (Owner only)

    - Accepts email + new role
    - Persists to roles.json
    """
    roles = load_roles()
    roles[update.email] = update.role

    try:
        with open(ROLES_FILE, "w") as f:
            json.dump(roles, f, indent=2)
        return {"status": "updated", "user": update.email, "role": update.role}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update roles: {str(e)}")
    
@router.get("/system/dashboard", tags=["system"])
def get_dashboard_summary(actor=Depends(require_role("admin"))):
    """
    📊 HyphaeOS Global System Dashboard
    ------------------------------------
    Returns:
    - Active agents
    - Registered users
    - Memory key counts
    - Safe mode flag
    - Role assignments
    """
    try:
        redis_engine = RedisMemoryEngine()
        keys = redis_engine.redis.keys("*")
        key_summary = {}

        for key in keys:
            user_prefix = key.split(":")[0]
            key_summary[user_prefix] = key_summary.get(user_prefix, 0) + 1

        return {
            "safe_mode": not core.is_safe(),
            "active_agents": list(core.get_active_agents()),
            "registered_agents": get_registered_agents(),
            "memory_key_counts": key_summary,
            "roles": load_roles()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Dashboard error: " + str(e))

@router.get("/system/export/pdf/{user}", tags=["system"])
def export_user_memory_pdf(user: str, actor=Depends(require_role("admin"))):
    """
    🖨️ Export a user's memory chain into a structured PDF report.
    """
    try:
        redis_engine = RedisMemoryEngine()
        keys = redis_engine.redis.keys(f"*{user}:last_*")
        entries = []

        for key in keys:
            raw = redis_engine.redis.get(key)
            try:
                data = json.loads(raw)
                if isinstance(data, dict):
                    entries.append(data)
            except Exception:
                continue

        entries.sort(key=lambda x: x.get("timestamp", ""))

        pdf = PDFExporter(title=f"HyphaeOS Memory Export for {user}")
        pdf.add_header()

        for entry in entries:
            block = (
                f"[{entry['timestamp']}] {entry['type'].upper()} - {entry['agent']}\n"
                f"Mood: {entry.get('mood', 'N/A')}\n\n{entry['content']}\n"
            )
            pdf.add_section(entry['type'].capitalize(), block)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            path = pdf.generate(tmp.name)
            return FileResponse(path, filename=f"{user}_memory_export.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")