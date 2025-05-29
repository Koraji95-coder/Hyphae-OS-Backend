import jwt, os
from fastapi import Request, HTTPException

from backend.app.core.users.roles import get_user_role, is_authorized

JWT_SECRET = os.environ.get("JWT_SECRET")

def get_current_email(request: Request) -> str:
    """
    Extract and validate JWT token from Authorization header.
    Returns email encoded in token.
    """
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid token.")

    try:
        token = auth.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("email")
    except Exception:
        raise HTTPException(401, "Invalid or expired token.")
    
def require_role(required: str = "admin"):
    def role_checker(request: Request):
        email = get_current_email(request)
        if not is_authorized(email, required):
            raise HTTPException(403, "Forbidden: insufficient privileges.")
        return email
    return role_checker