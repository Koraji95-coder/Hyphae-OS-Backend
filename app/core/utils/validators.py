from pydantic import BaseModel, Field, EmailStr, constr
from typing import Optional, List
from datetime import datetime

# Auth Validators
#class UserCredentials(BaseModel):
#   username: constr(min_length=3, max_length=50)
# #  password: constr(min_length=6, max_length=100)
# pin: Optional[constr(regex=r'^\d{6}$')] = None

#class TokenData(BaseModel):
 #   token: str
 #   expires_at: datetime

# Agent Validators
class PromptRequest(BaseModel):
    prompt: constr(min_length=1, max_length=1000)
    context: Optional[dict] = None

class AgentResponse(BaseModel):
    agent: str
    response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Chain Validators
class ChainStep(BaseModel):
    agent: constr(regex=r'^[a-zA-Z0-9_-]+$')
    prompt: constr(min_length=1, max_length=1000)

class ChainRequest(BaseModel):
    chain: List[ChainStep]
    input: Optional[str] = None

# Plugin Validators
class PluginRequest(BaseModel):
    name: constr(regex=r'^[a-zA-Z0-9_-]+$')
    input: dict

# System Validators
class SystemState(BaseModel):
    mode: constr(regex=r'^(development|production|maintenance)$')
    flags: dict = Field(default_factory=dict)
    memory: dict = Field(default_factory=dict)

# User Profile Validators
#class UserProfile(BaseModel):
 #   username: constr(min_length=3, max_length=50)
 #   email: EmailStr
  #  role: constr(regex=r'^(owner|admin|user)$')
   # device_id: Optional[str] = None

# Log Entry Validator
class LogEntry(BaseModel):
    level: constr(regex=r'^(debug|info|warning|error|critical)$')
    message: str
    metadata: Optional[dict] = None