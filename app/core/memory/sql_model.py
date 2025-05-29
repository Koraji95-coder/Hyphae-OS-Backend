# sql_model.py

import os
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# --- Database URL ---
DATABASE_URL = os.environ.get("MEMORY_DB_URL", "sqlite:///data/hyphaeos_memory.db")
os.makedirs("data", exist_ok=True)

engine = create_engine(DATABASE_URL, future=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class MemoryRecord(Base):
    __tablename__ = "memory"
    user = Column(String, primary_key=True)
    key = Column(String, primary_key=True)
    value = Column(Text)

Base.metadata.create_all(engine)
