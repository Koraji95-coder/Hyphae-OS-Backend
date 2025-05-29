"""
main.py 🌐
-----------
Entry point for the HyphaeOS FastAPI backend.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import time

from .version import __version__
from .core.utils.error_handlers import setup_error_handlers
from .core.utils.logger import setup_logging
from .core.utils.rate_limiter import rate_limit_middleware
from .core.middleware.metrics_middleware import MetricsMiddleware

# Import all routes
from .api.routes import (
    auth_routes,
    chain_routes,
    log_routes,
    mycocore_routes,
    neuroweave_routes,
    plugin_routes,
    rootbloom_routes,
    sporelink_routes,
    state_routes,
    system_routes,
    user_routes,
    verify_routes
)

# Initialize logging
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

# Secure CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not ALLOWED_ORIGINS:
    ALLOWED_ORIGINS = ["http://localhost:3000"]  # Default for development

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Request-ID",
        "X-Real-IP"
    ],
    max_age=3600,  # Cache preflight requests for 1 hour
    expose_headers=["X-Request-ID"]
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Request logging middleware
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

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="HyphaeOS API",
        version=__version__,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Apply security globally
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Custom documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="HyphaeOS API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

# Register error handlers
setup_error_handlers(app)

# Register routes
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

# Mount static files (if needed)
BASE_DIR = Path(__file__).resolve().parent
app.mount("/", StaticFiles(directory=BASE_DIR / "static", html=True), name="static")

@app.on_event("startup")
@repeat_every(seconds=3600)
def hourly_log_backup() -> None:
    backup_latest_logs()# every hour
async def startup_event():
    logger.info(f"Starting HyphaeOS API v{__version__}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down HyphaeOS API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)