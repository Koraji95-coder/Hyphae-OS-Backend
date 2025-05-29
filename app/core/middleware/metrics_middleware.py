# metrics_middleware.py 🧠📈
# --------------------------
# Middleware to capture metrics for every HTTP request using Prometheus client.
# Tracks:
# - Request count (method, endpoint, status)
# - Latency (method, endpoint)
# These feed into /metrics endpoint for observability dashboards (e.g., Grafana)

from starlette.middleware.base import BaseHTTPMiddleware
import time
from backend.app.core.monitoring import REQUEST_COUNT, REQUEST_LATENCY

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    📊 Middleware that injects request metrics collection into every FastAPI request.
    """
    async def dispatch(self, request, call_next):
        # ⏱️ Capture request start time
        start = time.time()

        # 🧪 Let request continue through pipeline
        response = await call_next(request)

        # 🧮 Calculate elapsed time
        duration = time.time() - start

        # 📈 Increment request counter for Prometheus
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        # ⌛ Record request latency
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        return response
