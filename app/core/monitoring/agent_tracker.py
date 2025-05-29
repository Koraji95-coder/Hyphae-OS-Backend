"""
# agent_tracker.py 📡
# -------------------
# Decorator for capturing per-agent Prometheus metrics
"""
from functools import wraps
from time import time
from backend.app.core.monitoring import AGENT_REQUESTS, AGENT_LATENCY

def track_agent(agent_name: str):
    """
    Decorator to track Prometheus metrics for a specific agent.

    Args:
        agent_name (str): Identifier of the agent being tracked.

    Returns:
        function: Wrapped function with metrics logging.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            """
            Wrapped function to record metrics around agent execution.
            """
            start = time()
            try:
                result = await func(*args, **kwargs)
                AGENT_REQUESTS.labels(agent=agent_name, status="success").inc()
                return result
            except Exception as e:
                AGENT_REQUESTS.labels(agent=agent_name, status="error").inc()
                raise e
            finally:
                AGENT_LATENCY.labels(agent=agent_name).observe(time() - start)
        return wrapper
    return decorator
