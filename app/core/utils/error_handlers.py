"""
error_handlers.py 🚨
---------------------
Global exception handling for FastAPI.

Features:
- Centralized handler for custom AppError
- Handles common exception classes: validation, JWT, SQLAlchemy
- Unified logging output with contextual metadata
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from jose.exceptions import JWTError
from typing import Dict, Any
import logging

# Global logger for error tracking
logger = logging.getLogger(__name__)

# 💥 Custom exception type for app-specific error handling
class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

# 🔧 Hook into FastAPI to register custom handlers
def setup_error_handlers(app: FastAPI):

    # 🧠 Handles custom AppError exceptions
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        logger.error(
            f"[AppError] {exc.message} (status {exc.status_code}) for {request.method} {request.url.path}",
            extra={
                "status_code": exc.status_code,
                "details": exc.details,
                "path": request.url.path
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "details": exc.details,
                "status_code": exc.status_code
            }
        )

    # 📋 Handles pydantic validation failures
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        logger.warning("Validation error", extra={
            "errors": exc.errors(),
            "path": request.url.path
        })
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation error",
                "details": exc.errors(),
                "status_code": 422
            }
        )

    # 🔐 Handles authentication token (JWT) errors
    @app.exception_handler(JWTError)
    async def jwt_error_handler(request: Request, exc: JWTError):
        logger.warning(f"JWT error: {str(exc)}", extra={
            "path": request.url.path
        })
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Invalid authentication credentials",
                "status_code": 401
            }
        )

    # 🧱 Handles database-related exceptions
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error: {str(exc)}", extra={
            "path": request.url.path
        })
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database error occurred",
                "status_code": 500
            }
        )

    # 🧨 Global fallback for unhandled exceptions
    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {str(exc)}", exc_info=True, extra={
            "path": request.url.path
        })
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "status_code": 500
            }
        )
