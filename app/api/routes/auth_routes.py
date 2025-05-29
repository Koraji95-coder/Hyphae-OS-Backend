# backend/app/api/routes/auth_routes.py

from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends, Response, Request, Cookie, Query, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
from limits import RateLimitItemPerMinute
from limits.aio.storage.memory import MemoryStorage
import secrets, logging

from backend.app.api.models.user_model import User
from backend.app.services.database import get_db
from backend.app.services.dependencies import require_role
from backend.app.services.token_service import (
    create_access_token,
    create_refresh_token,
    verify_token
)
from backend.app.services.cookie_utils import (
    set_refresh_cookie,
    clear_refresh_cookie
)

router = APIRouter()
security = HTTPBearer()

# 🔐 Password encryption context using bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger("auth")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """🔒 Verifies that a plaintext password matches a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """🔑 Hashes a plaintext password using bcrypt"""
    return pwd_context.hash(password)

# 📦 Input model for user registration
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

# 📦 Input model for user login
class UserLogin(BaseModel):
    username: str
    password: str
    pin: Optional[str] = None  # Reserved for optional PIN authentication

# 📦 Response model for successful auth
class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    token: str

# 🔐 Register new user    
@router.post("/auth/register", status_code=status.HTTP_201_CREATED, tags=["auth"])
async def register_user(user: UserRegister, db: Session = Depends(get_db)):
    """
    🔐 Register a new user with hashed password
    
    - Checks for duplicate username/email
    - Hashes the password using bcrypt
    - Generates a verification token for email verification
    """
    try:
        existing_user = db.query(User).filter(
            (User.username == user.username) | (User.email == user.email)
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or email already exists.")

        hashed_pw = pwd_context.hash(user.password)
        verification_token = secrets.token_urlsafe(32)

        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_pw,
            role="user",
            verified=False,
            verification_token=verification_token
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"User {new_user.username} registered successfully", extra=get_request_log_context())

        return {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role
        }

    except Exception as e:
        logger.error(f"Registration failed : {e}", extra=get_request_log_context())
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

# 🔓 Login + JWT Issuance
@router.post("/auth/login", response_model=UserResponse, tags=["auth"])
async def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    """
    🔓 Authenticate a user using username and password

    - Validates credentials against stored hashed password
    - Issues a short-lived JWT access token
    - Applies rate limiting before validation (brute-force protection)
    """
    await check_rate_limit(request)
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        logger.warning(f"Login failed for user: {credentials.username}", extra=get_request_log_context(request))
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username, "role": user.role})
    logger.info(f"User {user.username} logged in successfully", extra=get_request_log_context(request))
    
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        token=token
    )

# 🔚 Logout (clear refresh token)
@router.post("/auth/logout", tags=["auth"])
async def logout(response: Response):
    """
    🚪 Logout the user by clearing their refresh token cookie

    - Invalidates refresh session client-side
    """
    clear_refresh_cookie(response)
    logger.info("User logged out (refresh cookie cleared)", extra=get_request_log_context())
    return {"message": "Logged out successfully"}

# 🙋‍♂️ Fetch current user from token
@router.get("/auth/me", tags=["auth"])
async def get_current_user(token=Depends(security)):
    """
    🙋‍♂️ Retrieve the current authenticated user's info

    - Requires valid JWT access token in Authorization header
    - Returns username and role
    """
    payload = verify_token(token.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {
        "username": payload["sub"],
        "role": payload.get("role", "user")
    }

# 🔁 Refresh access token using refresh cookie
@router.post("/auth/refresh", tags=["auth"])
async def refresh_access_token(refresh_token: Optional[str] = Cookie(None)):
    """
    🔁 Refresh access token using a valid refresh token

    - Looks for refresh token in cookies
    - Returns new short-lived access token
    """
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    access_token = create_access_token({
        "sub": payload["sub"], 
        "role": payload.get("role", "user")
    })
    logger.info(f"Token refreshed for user {payload['sub']}", extra=get_request_log_context())
    return {"access_token": access_token}

# 🚪 Auto login via refresh token
@router.get("/auth/auto_login", tags=["auth"])
async def auto_login(refresh_token: Optional[str] = Cookie(None)):
    """
    Attempts to re-authenticate the user using their refresh token.
    """
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    logger.info(f"Token refreshed for user {payload['sub']}", extra=get_request_log_context())
    return {
        "username": payload["sub"],
        "role": payload.get("role", "user")
    }

# ✅ Email verification endpoint
@router.get("/auth/verify_email", tags=["auth"])
async def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    """
    Verifies user's email using a token from the verification link.
    """
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid verification token.")

    if user.verified:
        return {"message": "Account already verified."}

    user.verified = True
    user.verification_token = None
    db.commit()
    logger.info(f"Email verified for user {user.username}", extra=get_request_log_context())
    return {"message": "Email successfully verified. You may now log in."}

# Authentication Status
@router.get("/auth/status", tags=["auth"])
async def auth_status(token=Depends(security)):
    """
    🔎 Check authentication status using access token

    - Validates JWT and returns user status & role
    - Use this to validate if the current token is still active
    """
    payload = verify_token(token.credentials)
    if not payload:
        return HTTPException(status_code=401, detail="Token is invalid or expired")
    logger.debug(f"Auth status check for {payload['sub']}", extra=get_request_log_context())
    return {"status": "authenticated", "username": payload["sub"], "role": payload["role"]}

# 🔒 Admin-only route example
@router.get("/auth/admin_only", tags=["auth"])
async def admin_check(user=Depends(require_role("admin"))):
    """
    👑 Check if the current user has admin privileges

    - Requires valid access token with `role="admin"`
    - Demonstrates role-based access control (RBAC)
    - Used for admin dashboard gating
    """
    return {"message": f"Hello, {user['sub']} 👑 You have admin access."}

# 🚦 Create an in-memory rate limiter
storage = MemoryStorage()
rate_limit = RateLimitItemPerMinute(5)

async def check_rate_limit(request: Request):
    """
    🚨 Check and enforce IP-based rate limit

    - Limits to 5 login attempts per minute per IP
    - Returns 429 Too Many Requests if limit exceeded
    - Prevents brute-force login attacks
    """
    client_ip = request.client.host
    if not await storage.acquire_entry(f"login:{client_ip}", rate_limit):
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.")
