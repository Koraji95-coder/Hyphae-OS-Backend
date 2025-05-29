from typing import Dict, Any, Optional
import logging
from datetime import datetime
from core.cache.redis_cache import cache
from core.monitoring.metrics import MEMORY_USAGE, CPU_USAGE
import psutil

logger = logging.getLogger(__name__)

class SystemService:
    def __init__(self):
        self._system_flags: Dict[str, Any] = {}
        
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # Try cache first
            cache_key = "system:metrics"
            cached_metrics = cache.get(cache_key)
            if cached_metrics:
                return cached_metrics
                
            # Calculate metrics
            metrics = {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Update Prometheus metrics
            MEMORY_USAGE.set(metrics["memory_usage"])
            CPU_USAGE.set(metrics["cpu_usage"])
            
            # Cache for 1 minute
            cache.set(cache_key, metrics, expire=60)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                "error": "Failed to get system metrics",
                "timestamp": datetime.utcnow().isoformat()
            }
            
    async def get_system_flags(self) -> Dict[str, Any]:
        """Get current system flags"""
        return self._system_flags
        
    async def set_system_flag(self, key: str, value: Any):
        """Set a system flag"""
        self._system_flags[key] = value
        logger.info(f"System flag set: {key}={value}")
        
    async def clear_system_flag(self, key: str):
        """Clear a system flag"""
        if key in self._system_flags:
            del self._system_flags[key]
            logger.info(f"System flag cleared: {key}")

# Global service instance
system_service = SystemService()