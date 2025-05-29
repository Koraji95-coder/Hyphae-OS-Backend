"""MycocoreAgent 🌐
────────────────────────────────────────────
Central coordinator for the entire agent ecosystem.
Responsible for:
- System-wide state management
- Agent registration and lifecycle
- Safety controls and system flags
- Cross-agent communication
- System health monitoring

This singleton class serves as the "nervous system" 
connecting all specialized agents.
"""

import logging
from typing import Dict, Any
import threading

from backend.app.core.utils.ai_helpers import truncate_text, extract_json_from_response


logger = logging.getLogger(__name__)

class Mycocore:
    """Central coordinator for the entire agent ecosystem.
    
    This singleton class manages system-wide state, agent registration,
    safety controls, and cross-agent communication.
    
    Attributes:
        _instance: Singleton instance reference
        _lock: Thread synchronization lock
        _safe_mode (bool): System safety mode flag
        _system_flags (Dict): System-wide flags and settings
        _active_agents (Set): Currently registered agents
        _agent_health (Dict): Health status of all agents
        _startup_time: System startup timestamp
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern implementation.
        
        Returns:
            Mycocore: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_mycocore()
            return cls._instance

    def _init_mycocore(self):
        """Initialize the Mycocore system.
        
        Sets up initial state for the system coordinator.
        """
        self._safe_mode = False
        self._system_flags: Dict[str, Any] = {}
        self._active_agents = set()
        logger.info("Mycocore initialized")

    def is_safe(self) -> bool:
        """Check if the system is in normal operating mode.
        
        Returns:
            bool: True if system is NOT in safe mode
        """
        return not self._safe_mode

    def enable_safe_mode(self):
        """Enable safe mode across the system.
        
        This restricts potentially dangerous operations.
        """
        self._safe_mode = True
        logger.warning("Mycocore safe mode enabled")

    def disable_safe_mode(self):
        """Disable safe mode across the system.
        
        Returns system to normal operation.
        """
        self._safe_mode = False
        logger.info("Mycocore safe mode disabled")

    def set_flag(self, key: str, value: Any):
        """Set a system-wide flag or setting.
        
        Args:
            key (str): Flag identifier
            value (Any): Flag value
        """
        self._system_flags[key] = value

    def get_flag(self, key: str, default: Any = None) -> Any:
        """Get a system-wide flag or setting.
        
        Args:
            key (str): Flag identifier
            default (Any, optional): Default value if flag not found
            
        Returns:
            Any: The flag value or default
        """
        return self._system_flags.get(key)

    def register_agent(self, agent_id: str):
        """Register an agent with the system.
        
        Args:
            agent_id (str): Unique agent identifier
        """
        self._active_agents.add(agent_id)
        logger.info(f"Agent registered: {agent_id}")

    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the system.
        
        Args:
            agent_id (str): Unique agent identifier
        """
        self._active_agents.discard(agent_id)
        logger.info(f"Agent unregistered: {agent_id}")

    def get_active_agents(self) -> Set[str]:
        """Get the set of currently active agents.
        
        Returns:
            Set[str]: Set of active agent identifiers
        """
        return self._active_agents.copy()