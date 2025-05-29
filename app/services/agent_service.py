
from typing import Dict, List, Optional
from datetime import datetime
import logging
from shared.agents.agent_base import AgentBase
from shared.agents.cortexa_agent import CortexaAgent
from shared.agents.daphne_agent import DaphneAgent
from core.cache.redis_cache import cache
from core.monitoring.metrics import AGENT_REQUESTS, AGENT_LATENCY
import time

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self):
        self._agents: Dict[str, AgentBase] = {
            "cortexa": CortexaAgent(),
            "daphne": DaphneAgent()
        }
        
    async def process_request(
        self, 
        agent_id: str, 
        prompt: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process a request for a specific agent
        
        Args:
            agent_id: The ID of the agent to use
            prompt: The input prompt
            context: Optional context data
            
        Returns:
            Dict containing the response and metadata
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"agent:{agent_id}:prompt:{hash(prompt)}"
            cached_response = cache.get(cache_key)
            if cached_response:
                AGENT_REQUESTS.labels(agent=agent_id, status="cache_hit").inc()
                return cached_response
            
            # Get agent instance
            agent = self._agents.get(agent_id)
            if not agent:
                AGENT_REQUESTS.labels(agent=agent_id, status="not_found").inc()
                raise ValueError(f"Unknown agent: {agent_id}")
            
            # Process request
            response = await agent.ask(prompt)
            
            # Prepare result
            result = {
                "agent_id": agent_id,
                "prompt": prompt,
                "response": response,
                "timestamp": datetime.utcnow().isoformat(),
                "processing_time": time.time() - start_time
            }
            
            # Cache successful response
            cache.set(cache_key, result, expire=3600)
            
            # Record metrics
            AGENT_REQUESTS.labels(agent=agent_id, status="success").inc()
            AGENT_LATENCY.labels(agent=agent_id).observe(time.time() - start_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Agent processing error: {e}", exc_info=True)
            AGENT_REQUESTS.labels(agent=agent_id, status="error").inc()
            raise

    async def get_agent_status(self, agent_id: str) -> Dict:
        """Get current status of an agent"""
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_id}")
            
        return {
            "id": agent_id,
            "name": agent.name,
            "active": agent.active,
            "context": agent.context
        }

# Global service instance
agent_service = AgentService()
```