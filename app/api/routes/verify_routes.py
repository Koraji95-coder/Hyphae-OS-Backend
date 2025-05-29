"""
verify_routes.py 🔐
---------------------
Routes for verifying user identity via PIN or TOTP (2FA).

Features:
- ✳️ Basic mock verification endpoints
- 🔐 Supports both static PIN and dynamic TOTP codes
- 🧪 Setup for TOTP secret provisioning (e.g., Google Authenticator)
- 📛 Rate limiting + lockout placeholders for production security
"""


from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBeare
from pydantic import BaseModel
import pyotp, time, secrets, logging
from typing import Optional
from sqlalchemy.orm import Session
from back

from backend.app.services.database import get_db
from backend.app.services.token_service import verify_token

router = APIRouter()
logger = logging.getLogger("verify")
security = HTTPBearer()

# 💥 Brute force lockout check
key = f"verify:lockout:{user_id}"
attempts_key = f"verify:attempts:{user_id}"
if redis_client.get(key):
    raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")

# Constants for brute force mitigation
MAX_ATTEMPTS = 5
LOCKOUT_DURATION = 600  # 10 minutes

# 🔢 Verification input payload
class VerifyRequest(BaseModel):
    code: str
    type: str = "pin"  # Options: "pin" or "totp"

# ✅ Response schema for verification attempts
class VerifyResponse(BaseModel):
    success: bool
    message: Optional[str] = None

@router.post("/verify", response_model=VerifyResponse, tags=["verify"])
async def verify_code(request: VerifyRequest, token=Depends(security), db: Session = Depends(get_db)):
    """
    🔐 Verify a 6-digit PIN or TOTP code.

    - Static PIN check: code == 123456 (demo)
    - TOTP check: dynamically generated secret (from DB)
    - Redis-powered rate limiting + lockout
    """
    try:
        if len(request.code) != 6:
            raise HTTPException(status_code=400, detail="Invalid code format")

        payload = verify_token(token.credentials)
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 💥 Redis brute-force protection
        key = f"verify:lockout:{user_id}"
        attempts_key = f"verify:attempts:{user_id}"

        if redis_client.get(key):
            raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")

        # 🔑 Actual verification
        if request.type == "pin":
            success = request.code == "123456"
        elif request.type == "totp":
            if not user.totp_secret:
                raise HTTPException(status_code=400, detail="TOTP not configured for user")
            totp = pyotp.TOTP(user.totp_secret)
            success = totp.verify(request.code)
        else:
            raise HTTPException(status_code=400, detail="Invalid verification type")

        # 🧠 Redis tracking
        if success:
            redis_client.delete(attempts_key)
            redis_client.delete(key)
        else:
            attempts = redis_client.incr(attempts_key)
            if attempts == 1:
                redis_client.expire(attempts_key, LOCKOUT_DURATION)
            if attempts >= MAX_ATTEMPTS:
                redis_client.set(key, "1", ex=LOCKOUT_DURATION)

        logger.info(f"[verify] user={user_id} success={success}")
        return VerifyResponse(
            success=success,
            message="Verification successful" if success else "Invalid code"
        )

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")
    
@router.post("/verify/setup", tags=["verify"])
async def setup_verification(token=Depends(security), db: Session = Depends(get_db)):
    """
    🧪 Setup new TOTP secret for a user and return the URI.
    """
    try:
        payload = verify_token(token.credentials)
        user_id = payload.get("sub")

        secret = pyotp.random_base32()
        uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=payload.get("email"),
            issuer_name="HyphaeOS"
        )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.totp_secret = secret
        db.commit()

        logger.info(f"TOTP secret set for user {user_id}")
        return {"secret": secret, "uri": uri}

    except Exception as e:
        logger.error(f"TOTP setup failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to setup verification")