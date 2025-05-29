from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# System metrics
MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)

# Agent metrics
AGENT_REQUESTS = Counter(
    'agent_requests_total',
    'Total agent requests',
    ['agent', 'status']
)

AGENT_LATENCY = Histogram(
    'agent_request_duration_seconds',
    'Agent request latency',
    ['agent']
)

def track_request_metrics():
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                response = await func(*args, **kwargs)
                REQUEST_COUNT.labels(
                    method=args[0].method,
                    endpoint=args[0].url.path,
                    status=response.status_code
                ).inc()
                return response
            finally:
                REQUEST_LATENCY.labels(
                    method=args[0].method,
                    endpoint=args[0].url.path
                ).observe(time.time() - start_time)
        return wrapper
    return decorator