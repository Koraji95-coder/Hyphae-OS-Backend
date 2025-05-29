# app/services/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from shared.config.env_loader import get_env_variable

# Determine which DB to use via env
DB_ENGINE = get_env_variable("DB_ENGINE", "sqlite")

if DB_ENGINE == "postgres":
    DATABASE_URL = get_env_variable("POSTGRES_URL", optional=False)
else:
    DATABASE_URL = get_env_variable("SQLITE_URL", optional=False)

# Create async engine and session
engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
