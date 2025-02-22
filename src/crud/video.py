from sqlalchemy.orm import Session
from src.models.video import Video
from src.schemas.video import VideoCreate
from datetime import datetime

def create_video(db: Session, video: VideoCreate) -> Video:
    db_video = Video(**video.model_dump())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def get_video(db: Session, video_id: str) -> Video:
    return db.query(Video).filter(Video.id == video_id).first()

def list_videos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Video).offset(skip).limit(limit).all()

def delete_video(db: Session, video_id: str) -> bool:
    video = db.query(Video).filter(Video.id == video_id).first()
    if video:
        db.delete(video)
        db.commit()
        return True
    return False

def update_video(db: Session, video_id: str, **kwargs) -> Video:
    video = db.query(Video).filter(Video.id == video_id).first()
    if video:
        for key, value in kwargs.items():
            setattr(video, key, value)
        video.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(video)
    return video