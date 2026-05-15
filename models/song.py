from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, JSON, String
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


def save_song(metadata: dict, labels: list, file_path: str) -> Song:
    """Persist a downloaded song record to the database."""
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
