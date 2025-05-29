"""
BaseChainExecutor 🧠
────────────────────────────────────────────
Abstract base class for agent + plugin chain executors.
Supports stepwise execution with shared context.

Use:
- Subclass this for agent/plugin chain runners
- Add persistence, memory, logging, etc. hooks
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseChainExecutor(ABC):
    def __init__(self):
        self.context: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []

    @abstractmethod
    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Override: Logic for one step in the chain"""
        pass

    def run(self, chain: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Executes a sequence of steps using the `execute_step` logic.

        Args:
            chain (list): List of steps (agent or plugin)

        Returns:
            list: Result history
        """
        for step in chain:
            try:
                result = self.execute_step(step)
                self.history.append(result)
            except Exception as e:
                self.history.append({
                    "step": step,
                    "error": str(e)
                })
        return self.history
