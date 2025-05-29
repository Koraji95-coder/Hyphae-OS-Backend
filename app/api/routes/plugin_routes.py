"""
plugin_routes.py 🔌
--------------------
Routes for executing plugins and plugin chains in HyphaeOS.

Features:
- 🔁 Execute individual plugins with flexible input schemas
- 🔗 Batch execution support via plugin chains
- 🧠 Logging for each execution step
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging


from backend.app.agents.core.plugins import PluginChainExecutor
from backend.app.core.utils.logger import get_request_log_context

router = APIRouter()
logger = logging.getLogger("plugins")

class PluginRequest(BaseModel):
    """
    🔧 Defines a single plugin execution request.

    Fields:
    - name: The plugin identifier or handler
    - input: A dictionary of parameters for plugin execution
    """
    name: str
    input: Dict[str, Any]


class PluginChain(BaseModel):
    """
    🔗 Defines a chain of plugin executions.

    Each item in the list will be executed in order.
    """
    plugins: List[PluginRequest]

@router.post("/plugins/execute", tags=["plugins"])
async def execute_plugin(request: PluginRequest):
    """
    🔧 Execute a single plugin

    - Logs and simulates a plugin execution.
    """
    try:
        logger.info(f"Executing plugin: {request.name}", extra=get_request_log_context())
        # Plugin execution logic here
        return {"status": "ok", "result": f"Executed {request.name}"}
    except Exception as e:
        logger.error(f"Plugin execution failed: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Plugin execution failed")


@router.post("/plugins/chain", tags=["plugins"])
async def execute_chain(chain: PluginChain):
    """
    🔗 Execute a chain of plugins in sequence

    - Executes plugins via PluginChainExecutor
    - Returns individual result statuses
    """
    try:
        executor = PluginChainExecutor()
        steps = [{"plugin": p.name, "input": p.input} for p in chain.plugins]
        results = executor.run(steps)
        return {"status": "ok", "results": results}
    except Exception as e:
        logger.error(f"Plugin execution failed: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Plugin chain execution failed")