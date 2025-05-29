from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from backend.app.services.token_service import verify_token

security = HTTPBearer()

def require_role(required_role: str):
    def role_guard(token=Depends(security)):
        payload = verify_token(token.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or missing token")

        role = payload.get("role")
        if role != required_role:
            raise HTTPException(status_code=403, detail="Forbidden: insufficient privileges")
        return payload
    return role_guard
