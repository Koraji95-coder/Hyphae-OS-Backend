"""
agent_routes.py 🤖
────────────────────────────────────────────
Universal REST API for agent interaction.

Endpoints:
- /agent/ask: Unified agent prompt processor
- /agent/respond: Raw agent responder
"""

from fastapi import APIRouter, HTTPException

from backend.app.agents.core.executors import AgentChainExecutor
from backend.app.agents.core.registry import AGENT_REGISTRY

from backend.app.core.utils.logger import get_request_log_context
from backend.app.core.utils.validators import PromptRequest

from pydantic import BaseModel

from typing import List


import logging

router = APIRouter()
logger = logging.getLogger("agent")

class AgentResponse(BaseModel):
    agent: str
    response: str

@router.post("/agent/ask", response_model=AgentResponse, tags=["agent"])
async def ask_any_agent(agent: str, input: PromptRequest):
    """
    🔮 Universal agent prompt entrypoint.

    Args:
    - agent (str): agent key name (e.g. neuroweave, sporelink)
    - input (PromptRequest): prompt input

    Returns:
    - Standardized agent response
    """
    agent_obj = AGENT_REGISTRY.get(agent.lower())
    if not agent_obj:
        raise HTTPException(status_code=404, detail=f"Agent '{agent}' not found")

    try:
        reply = agent_obj.ask(input.prompt)
        return {"agent": agent, "response": reply}
    except Exception as e:
        logger.error(f"[{agent}] Agent error: {e}")
        raise HTTPException(status_code=500, detail=f"Agent '{agent}' failed to respond")

class ChainStep(BaseModel):
    agent: str
    prompt: str

@router.post("/agent/chain", tags=["agent"])
async def execute_agent_chain_endpoint(steps: List[ChainStep]):
    """
    🧠 Run a chain of agents with ordered prompts.
    """
    try:
        executor = AgentChainExecutor()
        result = executor.run([step.dict() for step in steps])
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chain execution failed: {e}")