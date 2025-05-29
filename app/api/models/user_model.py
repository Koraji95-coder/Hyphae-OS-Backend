"""User Model 👤
────────────────────────────────────────────
Core user identity and authentication model.

Manages:
- User authentication and identity
- Role-based access control
- Email verification workflow
- Multi-factor authentication
- Session and device tracking
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User account and authentication model.
    
    Manages user identities with comprehensive security features
    including email verification, MFA, and role-based access.
    
    Attributes:
        id (str): Unique identifier (UUID4)
        username (str): Unique login name
        email (str): Verified email address
        hashed_password (str): Bcrypt-hashed password
        role (str): Access control role
        last_login (DateTime): Most recent login timestamp
        device_id (str): Associated device identifier
        totp_secret (str): Time-based OTP secret for 2FA
        verified (bool): Email verification status
        verification_token (str): One-time email verification code
        token_expiry (DateTime): Verification token expiration
    """
    __tablename__ = "users"

    # Core identity
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Access control
    role = Column(String, default="user")
    last_login = Column(DateTime, default=datetime.utcnow)
    device_id = Column(String, nullable=True)
    
    # Multi-factor authentication
    totp_secret = Column(String, nullable=True)

    # Email verification
    verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True)