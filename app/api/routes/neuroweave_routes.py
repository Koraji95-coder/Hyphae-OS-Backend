"""
📁 neuroweave_routes.py

Handles inference requests routed to the Neuroweave agent.

Features:
- Accepts a natural language prompt
- Returns AI-generated responses from the Neuroweave agent
- Tracks via Prometheus
- Uses AGENT_REGISTRY for decoupled agent resolution
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import logging

from backend.app.core.utils.logger import get_request_log_context
from backend.app.core.monitoring.agent_tracker import track_agent
from backend.app.core.utils.validators import PromptRequest
from backend.app.shared.workflows.agent_chain_executor import AGENT_REGISTRY


router = APIRouter()
logger = logging.getLogger("neuroweave")

class NeuroweaveResponse(BaseModel):
    """
    🧠 Represents the structured response returned by Neuroweave.

    Fields:
    - agent: Identifier for the responding agent ("Neuroweave")
    - response: The AI-generated reply to the provided prompt
    """
    agent: str
    response: str

from backend.app.shared.workflows.agent_chain_executor import AGENT_REGISTRY  # 🚀 Add this

@router.post("/neuroweave/ask", response_model=NeuroweaveResponse, tags=["neuroweave"])
async def ask_neuroweave(input: PromptRequest):
    logger.info(f"[neuroweave] Asking agent (untracked): {input.prompt}", extra=get_request_log_context())
    try:
        result = AGENT_REGISTRY["neuroweave"].ask(input.prompt)
        return {"agent": "Neuroweave", "response": result}
    except Exception as e:
        logger.error(f"Neuroweave error: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Neuroweave failed to respond")

@router.post("/agent/ask", response_model=NeuroweaveResponse, tags=["neuroweave"])
@track_agent("neuroweave")
async def tracked_ask_neuroweave(input: PromptRequest):
    logger.info(f"[neuroweave] Tracking request: {input.prompt}", extra=get_request_log_context())
    try:
        result = AGENT_REGISTRY["neuroweave"].ask(input.prompt)
        return {"agent": "Neuroweave", "response": result}
    except Exception as e:
        logger.error(f"Neuroweave tracked error: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Agent failed to respond")

@router.get("/neuroweave/test", tags=["neuroweave"])
async def test_neuroweave():
    return {"status": "ok", "agent": "neuroweave"}