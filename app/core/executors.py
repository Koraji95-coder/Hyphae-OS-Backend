"""
executors.py ⚙️
────────────────────────────────────────────
Handles agent and plugin chain execution via shared base executor.
Includes agent registry, plugin resolver, and safety logic.
"""

from shared.state.session_manager import session
from backend.app.agents.mycocore_agent import Mycocore
from backend.app.agents.core.base_chain_executor import BaseChainExecutor
from backend.app.core.plugins.plugin_executor import execute_plugin

# ⬇️ Consolidated Agent Registry (No separate registry.py)
from backend.agents.neuroweave_agent import NeuroweaveAgent
from backend.agents.sporelink_agent import SporelinkAgent
from backend.agents.rootbloom_agent import RootbloomAgent

AGENT_REGISTRY = {
    "neuroweave": NeuroweaveAgent(),
    "rootbloom": RootbloomAgent(),
    "sporelink": SporelinkAgent(),
}


class AgentChainExecutor(BaseChainExecutor):
    """
    AgentChainExecutor 🧠
    Executes a sequence of prompts across registered agents.
    """
    def __init__(self):
        super().__init__()
        self.core = Mycocore()

    def execute_step(self, step: dict) -> dict:
        if not self.core.is_safe():
            return {
                "agent": "mycocore",
                "input": step.get("prompt"),
                "output": "🚫 System in safe mode."
            }

        agent_name = step.get("agent")
        prompt = step.get("prompt")
        agent = AGENT_REGISTRY.get(agent_name.lower())

        if not agent:
            return {
                "agent": agent_name,
                "input": prompt,
                "output": f"❌ Unknown agent: {agent_name}"
            }

        try:
            output = agent.ask(prompt)
            return {
                "agent": agent.name,
                "input": prompt,
                "output": output
            }
        except Exception as e:
            return {
                "agent": agent_name,
                "input": prompt,
                "output": f"❌ Error: {e}"
            }


class PluginChainExecutor(BaseChainExecutor):
    """
    PluginChainExecutor 🔌
    Handles execution of plugin chains (plugin steps in order).
    """
    def execute_step(self, step: dict) -> dict:
        plugin_name = step.get("plugin")
        input_text = step.get("input")
        result = execute_plugin(plugin_name, input_text)

        # Optionally store in session memory
        session.get_memory()["last_plugin_chain"] = result
        return result