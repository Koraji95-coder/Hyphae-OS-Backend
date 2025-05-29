"""SystemLog Model 📝
────────────────────────────────────────────
Database model for system-wide event logging.

Tracks:
- Agent activities and interactions
- System events and state changes
- Diagnostic data and debugging info
- Performance metrics and analytics
"""

from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class SystemLog(Base):
    """System-wide event logging model.
    
    Captures all significant system events with associated metadata,
    enabling comprehensive system monitoring and debugging.
    
    Attributes:
        id (str): Unique identifier (UUID4)
        agent (str): Name of the agent that triggered the event
        event (str): Type/description of the event
        data (JSON): Additional event-specific data/payload
        timestamp (DateTime): When the event occurred (UTC)
    """
    __tablename__ = "system_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent = Column(String, nullable=False)
    event = Column(String, nullable=False)
    data = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)