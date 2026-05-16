import logging
from typing import List

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    BulkDownloadRequest,
    BulkDownloadResponse,
    DownloadRequest,
    DownloadResponse,
    SongResponse,
    TaskStatusResponse,
)
from models.song import Song
from worker.celery_app import celery_app
from worker.tasks import download_task

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/download", response_model=DownloadResponse, status_code=202)
async def submit_download(request: DownloadRequest):
    """Enqueue a YouTube audio download job."""
    task = download_task.delay(request.url, request.labels)
    return DownloadResponse(task_id=task.id, status="queued")


@router.post("/bulk-download", response_model=BulkDownloadResponse, status_code=202)
async def submit_bulk_download(request: BulkDownloadRequest):
    """Enqueue multiple YouTube audio download jobs in a single request (max 100)."""
    enqueued = []
    for item in request.items:
        try:
            task = download_task.delay(item.url, item.labels)
            enqueued.append(DownloadResponse(task_id=task.id, status="queued"))
        except Exception:
            logger.exception("Failed to enqueue URL: %s", item.url)
            enqueued.append(DownloadResponse(task_id="", status="enqueue_failed"))
    return BulkDownloadResponse(enqueued=enqueued, total=len(enqueued))


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Check the status of a previously submitted download task."""
    result = AsyncResult(task_id, app=celery_app)
    return TaskStatusResponse(
        task_id=task_id,
        status=result.status,
        result=result.result if result.ready() else None,
    )


@router.get("/songs", response_model=List[SongResponse])
async def list_songs(db: AsyncSession = Depends(get_db)):
    """Return all downloaded songs stored in the database."""
    result = await db.execute(select(Song))
    return result.scalars().all()


@router.get("/songs/{song_id}", response_model=SongResponse)
async def get_song(song_id: int, db: AsyncSession = Depends(get_db)):
    """Return a single song by its database ID."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song
