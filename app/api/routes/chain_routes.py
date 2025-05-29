"""
📦 chain_routes.py

This module defines the `/chain/execute` API endpoint used to orchestrate
multi-agent task execution chains in sequence. Each agent receives the user input
and processes it according to its prompt and parameters.

Main Features:
- Validates and executes up to 10 chained agent steps
- Logs execution metadata and timing
- Supports future integration with dynamic agent backends
"""


from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, constr
from typing import List, Dict, Any
import logging, secrets
from datetime import datetime

router = APIRouter()
logger = logging.getLogger("chain")

class AgentStep(BaseModel):
    """
    🧠 Represents a single step in the agent chain.

    Attributes:
    - agent: Identifier of the agent to invoke (validated with regex)
    - prompt: Instructional string sent to the agent
    - parameters: Optional config dictionary passed to agent execution
    """
    agent: constr(pattern=r'^[a-zA-Z0-9_-]+$', min_length=1, max_length=50)
    prompt: str = Field(..., min_length=1, max_length=1000, description="Natural language question or command")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AgentChainRequest(BaseModel):
    """
    🔗 Defines a chain of agents to process input sequentially.

    Fields:
    - chain: Ordered list of agent identifiers (e.g., ["neuroweave", "rootbloom"])
    - input: Prompt or query to be shared across the chain
    """
    chain: List[str]
    input: str
    
class ChainRequest(BaseModel):
    """
    📤 Schema for incoming chain execution request.

    Attributes:
    - chain: Ordered list of AgentStep instructions (1–10)
    - input: Raw input string (max 2000 characters)
    - metadata: Arbitrary metadata used for custom routing/tracking
    """
    chain: List[AgentStep] = Field(..., min_items=1, max_items=10)
    input: constr(min_length=1, max_length=2000) = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChainResponse(BaseModel):
    """
    📦 Output schema returned after executing the agent chain.

    Attributes:
    - request_id: Unique ID for this execution request
    - timestamp: UTC time the request started
    - chain: Echoed chain structure for reference
    - results: List of step outputs, each with agent, input, and output
    - execution_time: Time (in seconds) taken to execute full chain
    """
    request_id: str
    timestamp: datetime
    chain: List[AgentStep]
    results: List[Dict[str, Any]]
    execution_time: float

@router.post("/chain/execute", response_model=ChainResponse, tags=["chain"])
async def execute_chain(request: ChainRequest):
    """
    🔄 Execute a sequence of agent operations
    
    - Minimum 1 and maximum 10 steps in chain
    - Each prompt limited to 1000 characters
    - Input text limited to 2000 characters
    - Agent names must be alphanumeric with underscores/hyphens
    """
    logger.info(f"Executing chain with {len(request.chain)} steps", extra=get_request_log_context())
    start_time = datetime.utcnow()
    
    try:
        results = []
        for step in request.chain:
            # Validate agent exists
            if step.agent not in ["neuroweave", "rootbloom", "sporelink"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid agent: {step.agent}"
                )
            
            # Stubbed execution - replace with actual agent routing
            execution = dispatch_to_agent(step.agent, step.prompt, step.parameters)
            execution.update({
                "agent": step.agent,
                "input": step.prompt
            })
            results.append(execution)
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ChainResponse(
            request_id=secrets.token_hex(8),
            timestamp=start_time,
            chain=request.chain,
            results=results,
            execution_time=execution_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chain execution error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to execute agent chain"
        )
    
def dispatch_to_agent(agent: str, prompt: str, params: dict) -> dict:
    """
    🚀 Routes prompt and parameters to a specific agent's backend.

    This is currently a stubbed placeholder that simulates agent execution.
    In production, replace with:
    - RPC call to agent microservice
    - HTTP request to external LLM API
    - Local function dispatch per agent name

    Returns:
    - dict with output and timestamp
    """
    return {
        "output": f"{agent} processed: {prompt}",
        "timestamp": datetime.utcnow().isoformat()
    }
    