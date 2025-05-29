"""
📁 rootbloom_routes.py

Provides the endpoint for RootBloom, the creative content generation agent.

Features:
- Accepts prompt input for generative creativity
- Returns synthetic output from the agent
- Tracks metrics with Prometheus
- Uses AGENT_REGISTRY for flexible agent injection
"""


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import logging

from backend.app.core.utils.logger import get_request_log_context
from backend.app.core.monitoring.agent_tracker import track_agent
from backend.app.core.utils.validators import PromptRequest
from backend.app.shared.workflows.agent_chain_executor import AGENT_REGISTRY


router = APIRouter()
logger = logging.getLogger("rootbloom")

class RootBloomResponse(BaseModel):
    """
    🌸 Structured response from RootBloom agent.

    Fields:
    - agent: The identifier for the responding generation agent
    - response: The generated creative content as a string
    """
    agent: str
    response: str

@router.post("/rootbloom/generate", response_model=RootBloomResponse, tags=["rootbloom"])
async def generate_rootbloom(input: PromptRequest):
    logger.info(f"[rootbloom] Prompt: {input.prompt}", extra=get_request_log_context())
    try:
        result = AGENT_REGISTRY["rootbloom"].ask(input.prompt)
        return {"agent": "RootBloom", "response": result}
    except Exception as e:
        logger.error(f"RootBloom error: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="RootBloom failed")

@router.post("/agent/generate", response_model=RootBloomResponse, tags=["rootbloom"])
@track_agent("rootbloom")
async def tracked_generate_rootbloom(input: PromptRequest):
    logger.info(f"[rootbloom][tracked] Prompt: {input.prompt}", extra=get_request_log_context())
    try:
        result = AGENT_REGISTRY["rootbloom"].ask(input.prompt)
        return {"agent": "RootBloom", "response": result}
    except Exception as e:
        logger.error(f"RootBloom tracked error: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Agent failed to respond")

@router.get("/rootbloom/test", tags=["rootbloom"])
async def test_rootbloom():
    return {"status": "ok", "agent": "rootbloom"}