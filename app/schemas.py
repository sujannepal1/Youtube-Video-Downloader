from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DownloadRequest(BaseModel):
    url: str
    labels: List[str] = []


class DownloadResponse(BaseModel):
    task_id: str
    status: str


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
