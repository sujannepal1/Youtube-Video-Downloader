from typing import List

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import DownloadRequest, DownloadResponse, SongResponse, TaskStatusResponse
from models.song import Song
from worker.celery_app import celery_app
from worker.tasks import download_task

router = APIRouter()


@router.post("/download", response_model=DownloadResponse, status_code=202)
def submit_download(request: DownloadRequest):
    """Enqueue a YouTube audio download job."""
    task = download_task.delay(request.url, request.labels)
    return DownloadResponse(task_id=task.id, status="queued")


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    """Check the status of a previously submitted download task."""
    result = AsyncResult(task_id, app=celery_app)
    return TaskStatusResponse(
        task_id=task_id,
        status=result.status,
        result=result.result if result.ready() else None,
    )


@router.get("/songs", response_model=List[SongResponse])
def list_songs(db: Session = Depends(get_db)):
    """Return all downloaded songs stored in the database."""
    return db.query(Song).all()


@router.get("/songs/{song_id}", response_model=SongResponse)
def get_song(song_id: int, db: Session = Depends(get_db)):
    """Return a single song by its database ID."""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song
