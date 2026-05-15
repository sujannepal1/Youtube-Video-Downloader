from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DownloadRequest(BaseModel):
    url: str
    labels: List[str] = []


class DownloadResponse(BaseModel):
    task_id: str
    status: str


class BulkDownloadRequest(BaseModel):
    items: List[DownloadRequest] = Field(..., min_length=1, max_length=100)


class BulkDownloadResponse(BaseModel):
    enqueued: List[DownloadResponse]
    total: int


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None


class SongResponse(BaseModel):
    id: int
    title: Optional[str] = None
    artist: Optional[str] = None
    duration: Optional[int] = None
    url: str
    file_path: Optional[str] = None
    labels: Optional[list] = None
    created_at: datetime

    class Config:
        from_attributes = True
