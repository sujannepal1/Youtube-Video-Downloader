from typing import List, Optional

from sqlalchemy import Column, DateTime, Integer, JSON, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.database import Base, SessionLocal


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    artist = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)
    url = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    labels = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ---------------------------------------------------------------------------
# Async queries — used by FastAPI route handlers
# ---------------------------------------------------------------------------


async def get_all_songs(db: AsyncSession) -> List[Song]:
    """Return all song records ordered by creation date descending."""
    result = await db.execute(select(Song).order_by(Song.created_at.desc()))
    return result.scalars().all()


async def get_song_by_id(db: AsyncSession, song_id: int) -> Optional[Song]:
    """Return a single song by primary key, or None if not found."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    return result.scalar_one_or_none()


async def get_songs_by_label(db: AsyncSession, label: str) -> List[Song]:
    """Return all songs whose labels JSON array contains the given label."""
    result = await db.execute(
        select(Song)
        .where(Song.labels.contains([label]))
        .order_by(Song.created_at.desc())
    )
    return result.scalars().all()


# ---------------------------------------------------------------------------
# Sync write — used by Celery workers (no async event loop available)
# ---------------------------------------------------------------------------


def save_song(metadata: dict, labels: list, file_path: str) -> Song:
    """Persist a downloaded song record to the database (sync, for Celery)."""
    db = SessionLocal()
    try:
        song = Song(
            title=metadata.get("title"),
            artist=metadata.get("artist"),
            duration=metadata.get("duration"),
            url=metadata.get("url"),
            file_path=file_path,
            labels=labels,
        )
        db.add(song)
        db.commit()
        db.refresh(song)
        return song
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
