from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# ---------------------------------------------------------------------------
# Async engine + session – used by FastAPI route handlers
# ---------------------------------------------------------------------------
_async_url = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://", 1
).replace(
    "postgres://", "postgresql+asyncpg://", 1
)
async_engine = create_async_engine(_async_url, echo=False)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

# ---------------------------------------------------------------------------
# Sync engine + session – used by Celery workers (save_song, etc.)
# ---------------------------------------------------------------------------
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


async def get_db() -> AsyncSession:
    """FastAPI async dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_db():
    """Synchronous dependency for non-async contexts (e.g. Celery workers)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
