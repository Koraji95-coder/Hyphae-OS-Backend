"""
📁 user_routes.py

Provides endpoints for managing user accounts.

Features:
- Admin-only full user list query
- Self + Admin access to individual profiles
- Role-based JWT enforcement
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import logging

from backend.app.services.dependencies import require_role
from backend.app.services.database import get_db
from backend.app.services.token_service import verify_token
from backend.app.api.models.user_model import User
from backend.app.core.utils.logger import get_request_log_context

router = APIRouter()
logger = logging.getLogger("users")
security = HTTPBearer()
DB = Depends(get_db)

class UserProfile(BaseModel):
    """
    🧑 User profile schema returned from API.
    """
    id: str
    username: str
    email: EmailStr
    role: str
    verified: bool
    last_login: Optional[str] = None

class UserList(BaseModel):
    """
    📋 List of user profiles.
    """
    users: List[UserProfile]


@router.get("/users", response_model=UserList, tags=["users"])
async def list_users(user=Depends(require_role("admin")), db: Session = DB):
    """
    🔍 Get list of system users (Admin-Only)

    - Requires admin role via JWT
    - Returns full list of registered users
    - Queries actual database using SQLAlchemy
    """
    try:
        users = db.query(User).all()
        return {"users": [UserProfile(
            id=u.id,
            username=u.username,
            email=u.email,
            role=u.role,
            verified=u.verified,
            last_login=u.last_login.isoformat() if u.last_login else None
        ) for u in users]}
    except Exception as e:
        logger.error(f"Failed to list users: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Failed to fetch users")


@router.get("/users/{user_id}", response_model=UserProfile, tags=["users"])
async def get_user(user_id: str, requester=Depends(security), db: Session = DB):
    """
    🧑‍💼 Retrieve a user profile by ID

    - Allows access if requester is the user OR has admin role
    - Uses JWT access token from Authorization header
    - Returns user profile data for valid requests
    - Returns 403 if access is denied
    - Returns 404 if user not found
    """
    payload = verify_token(requester.credentials)

    if payload["role"] != "admin" and payload["sub"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            verified=user.verified,
            last_login=user.last_login.isoformat() if user.last_login else None
        )

    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail="Failed to fetch user")
