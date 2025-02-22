from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VideoBase(BaseModel):
    filename: str
    content_type: str
    size: int
    bucket: str
    object_name: str

class VideoCreate(VideoBase):
    id: str

class Video(VideoBase):
    id: str
    created_at: datetime
    updated_at: datetime
    video_url: Optional[str] = None

    class Config:
        from_attributes = True