import logging
from typing import List

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
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
from models.song import Song, get_all_songs, get_song_by_id
from worker.celery_app import celery_app
from worker.tasks import download_task

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/download", response_model=DownloadResponse, status_code=202)
async def submit_download(request: DownloadRequest):
    """Enqueue a YouTube audio download job."""
    logger.info("submit_download: url=%s labels=%s", request.url, request.labels)
    task = download_task.delay(request.url, request.labels)
    logger.info("submit_download: task_id=%s status=queued", task.id)
    return DownloadResponse(task_id=task.id, status="queued")


@router.post("/bulk-download", response_model=BulkDownloadResponse, status_code=202)
async def submit_bulk_download(request: BulkDownloadRequest):
    """Enqueue multiple YouTube audio download jobs in a single request (max 100)."""
    logger.info("submit_bulk_download: total_items=%d", len(request.items))
    enqueued = []
    for idx, item in enumerate(request.items):
        try:
            task = download_task.delay(item.url, item.labels)
            logger.debug("bulk item[%d]: url=%s task_id=%s labels=%s", idx, item.url, task.id, item.labels)
            enqueued.append(DownloadResponse(task_id=task.id, status="queued"))
        except Exception:
            logger.exception("bulk item[%d]: failed to enqueue url=%s", idx, item.url)
            enqueued.append(DownloadResponse(task_id="", status="enqueue_failed"))
    logger.info("submit_bulk_download: queued=%d", len(enqueued))
    return BulkDownloadResponse(enqueued=enqueued, total=len(enqueued))


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Check the status of a previously submitted download task."""
    logger.debug("get_task_status: task_id=%s", task_id)
    result = AsyncResult(task_id, app=celery_app)
    logger.info("get_task_status: task_id=%s status=%s ready=%s", task_id, result.status, result.ready())
    return TaskStatusResponse(
        task_id=task_id,
        status=result.status,
        result=result.result if result.ready() else None,
    )


@router.get("/songs", response_model=List[SongResponse])
async def list_songs(db: AsyncSession = Depends(get_db)):
    """Return all downloaded songs stored in the database."""
    logger.debug("list_songs: querying all songs")
    songs = await get_all_songs(db)
    logger.info("list_songs: returned %d songs", len(songs))
    return songs


@router.get("/songs/{song_id}", response_model=SongResponse)
async def get_song(song_id: int, db: AsyncSession = Depends(get_db)):
    """Return a single song by its database ID."""
    logger.debug("get_song: song_id=%d", song_id)
    song = await get_song_by_id(db, song_id)
    if not song:
        logger.warning("get_song: song_id=%d not found", song_id)
        raise HTTPException(status_code=404, detail="Song not found")
    logger.info("get_song: song_id=%d title=%r artist=%r", song_id, song.title, song.artist)
    return song
