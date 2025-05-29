from fastapi import Response
from datetime import datetime, timedelta

def set_refresh_cookie(response: Response, token: str):
    """Set refresh token cookie"""
    expires = datetime.utcnow() + timedelta(days=7)
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=True,
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        samesite="lax"
    )

def clear_refresh_cookie(response: Response):
    """Clear refresh token cookie"""
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )