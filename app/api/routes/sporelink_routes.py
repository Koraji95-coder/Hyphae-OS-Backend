"""
📁 sporelink_routes.py

Provides the endpoint for SporeLink, the financial news + stock tagging agent.

Features:
- Accepts structured prompt input for analysis
- Returns categorized, stock-linked summaries
- Prometheus metrics + structured response
- Powered via centralized AGENT_REGISTRY
"""


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import logging

from backend.app.core.utils.logger import get_request_log_context
from backend.app.core.monitoring.agent_tracker import track_agent
from backend.app.core.utils.validators import PromptRequest
from backend.app.shared.workflows.agent_chain_executor import AGENT_REGISTRY


router = APIRouter()
logger = logging.getLogger("sporelink")

class SporeLinkResponse(BaseModel):
    """
    📈 Structured response from the SporeLink agent.

    Fields:
    - agent: Identifier of the responding analysis agent
    - response: Processed analysis result as a string
    """
    agent: str
    response: str

@router.post("/sporelink/analyze", response_model=SporeLinkResponse, tags=["sporelink"])
async def analyze_with_sporelink(input: PromptRequest):
    logger.info(f"[sporelink] Analyzing: {input.prompt}", extra=get_request_log_context())
    try:
        result = AGENT_REGISTRY["sporelink"].ask(input.prompt)
        return {"agent": "SporeLink", "response": result}
    except Exception as e:
        logger.error(f"SporeLink error: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="SporeLink failed")

@router.post("/agent/analyze", response_model=SporeLinkResponse, tags=["sporelink"])
@track_agent("sporelink")
async def tracked_analyze_with_sporelink(input: PromptRequest):
    logger.info(f"[sporelink][tracked] Analyzing: {input.prompt}", extra=get_request_log_context())
    try:
        result = AGENT_REGISTRY["sporelink"].ask(input.prompt)
        return {"agent": "SporeLink", "response": result}
    except Exception as e:
        logger.error(f"SporeLink tracked error: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Agent failed")

@router.get("/sporelink/test", tags=["sporelink"])
async def test_sporelink():
    return {"status": "ok", "agent": "sporelink"}
