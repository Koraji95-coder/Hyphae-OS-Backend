# app/main.py 🌐
"""
Entry point for the HyphaeOS FastAPI backend.
"""

import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi_utils.tasks import repeat_every

from .version import __version__
from .core.utils.error_handlers import setup_error_handlers
from .core.utils.logger import setup_logging
from .core.utils.rate_limiter import rate_limit_middleware
from .core.middleware.metrics_middleware import MetricsMiddleware
from .core.config.env_loader import get_env_variable
from .core.utils.dropbox_backup import backup_latest_logs

# Routes
from .api.routes import (
    auth_routes, chain_routes, log_routes, mycocore_routes, neuroweave_routes,
    plugin_routes, rootbloom_routes, sporelink_routes, state_routes,
    system_routes, user_routes, verify_routes, agent_routes
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HyphaeOS API",
    description="🧠 HyphaeOS Multi-Agent Intelligence System API",
    version=__version__,
    docs_url=None,
    redoc_url=None
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# CORS
ALLOWED_ORIGINS = get_env_variable("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Real-IP"],
    expose_headers=["X-Request-ID"],
    max_age=3600,
)

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.middleware("http")(rate_limit_middleware)

# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            "duration_ms": round(duration * 1000, 2),
            "status_code": response.status_code,
            "client_ip": request.client.host,
        }
    )
    return response

# Custom OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="HyphaeOS API",
        version=__version__,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    openapi_schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Docs
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="HyphaeOS API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

# Routes
app.include_router(agent_routes.router, prefix="/api", tags=["agent"])
app.include_router(auth_routes.router, prefix="/api", tags=["auth"])
app.include_router(chain_routes.router, prefix="/api", tags=["chain"])
app.include_router(log_routes.router, prefix="/api", tags=["logs"])
app.include_router(mycocore_routes.router, prefix="/api", tags=["mycocore"])
app.include_router(neuroweave_routes.router, prefix="/api", tags=["neuroweave"])
app.include_router(plugin_routes.router, prefix="/api", tags=["plugins"])
app.include_router(rootbloom_routes.router, prefix="/api", tags=["rootbloom"])
app.include_router(sporelink_routes.router, prefix="/api", tags=["sporelink"])
app.include_router(state_routes.router, prefix="/api", tags=["state"])
app.include_router(system_routes.router, prefix="/api", tags=["system"])
app.include_router(user_routes.router, prefix="/api", tags=["users"])
app.include_router(verify_routes.router, prefix="/api", tags=["verify"])

# Static files
BASE_DIR = Path(__file__).resolve().parent
app.mount("/", StaticFiles(directory=BASE_DIR / "static", html=True), name="static")

# Healthcheck
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}

# Rate limit test
@app.get("/rate-test")
@limiter.limit("5/minute")
async def rate_limited_route(request: Request):
    return {"message": "You're within the limit"}

# Cron jobs
@app.on_event("startup")
@repeat_every(seconds=3600)
def hourly_log_backup():
    backup_latest_logs()

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting HyphaeOS API v{__version__}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down HyphaeOS API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
