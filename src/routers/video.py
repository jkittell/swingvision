from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from src.config import get_db, get_minio_client, MINIO_BUCKET, MINIO_SECURE, logger
from src.crud import video as video_crud
from src.schemas.video import Video, VideoCreate
import uuid
import io
from datetime import datetime, timedelta
from typing import List

router = APIRouter(prefix="/videos", tags=["Videos"])

def validate_video_file(file: UploadFile) -> None:
    """Validate uploaded video file."""
    allowed_types = ["video/mp4", "video/quicktime"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not allowed. Must be one of: {allowed_types}"
        )

@router.post("/", response_model=Video)
async def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Video:
    """Upload a video file"""
    # Validate file type
    validate_video_file(file)
    
    # Create unique ID
    video_id = str(uuid.uuid4())
    minio_client = None
    
    try:
        # Connect to MinIO
        try:
            minio_client = get_minio_client()
        except Exception as e:
            logger.error(f"Failed to connect to MinIO: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="Storage service is currently unavailable"
            )
        
        # Upload to MinIO
        object_name = f"{video_id}/{file.filename}"
        content = await file.read()
        minio_client.put_object(
            MINIO_BUCKET,
            object_name,
            io.BytesIO(content),
            len(content),
            file.content_type
        )
        
        # Create database entry
        video_data = VideoCreate(
            id=video_id,
            filename=file.filename,
            content_type=file.content_type,
            size=len(content),
            bucket=MINIO_BUCKET,
            object_name=object_name
        )
        
        db_video = video_crud.create_video(db, video_data)
        
        # Generate presigned URL with explicit HTTP scheme
        video_url = minio_client.presigned_get_object(
            MINIO_BUCKET,
            object_name,
            expires=timedelta(hours=1)  # Shorter expiry for testing
        )
        
        # Ensure the URL has the correct scheme
        if not video_url.startswith(('http://', 'https://')):
            video_url = f"http://{video_url}" if not MINIO_SECURE else f"https://{video_url}"
        
        # Log the URL for debugging
        logger.info(f"Generated video URL: {video_url}")
        
        return {**db_video.__dict__, "video_url": video_url}
        
    except Exception as e:
        # Cleanup on error
        if minio_client and video_id:
            try:
                minio_client.remove_object(MINIO_BUCKET, object_name)
            except:
                pass
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading video: {str(e)}"
        )

@router.get("/{video_id}", response_model=Video)
def get_video(video_id: str, db: Session = Depends(get_db)) -> Video:
    """Get video by ID"""
    db_video = video_crud.get_video(db, video_id)
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Generate presigned URL
    try:
        minio_client = get_minio_client()
        video_url = minio_client.presigned_get_object(
            db_video.bucket,
            db_video.object_name,
            expires=timedelta(days=7)
        )
        return {**db_video.__dict__, "video_url": video_url}
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        return db_video

@router.get("/", response_model=List[Video])
def list_videos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[Video]:
    """List all videos"""
    videos = video_crud.list_videos(db, skip, limit)
    
    # Generate presigned URLs
    try:
        minio_client = get_minio_client()
        for video in videos:
            try:
                video.video_url = minio_client.presigned_get_object(
                    video.bucket,
                    video.object_name,
                    expires=timedelta(days=7)
                )
            except:
                video.video_url = None
    except Exception as e:
        logger.error(f"Error generating presigned URLs: {str(e)}")
    
    return videos

@router.delete("/{video_id}")
def delete_video(video_id: str, db: Session = Depends(get_db)):
    """Delete a video"""
    db_video = video_crud.get_video(db, video_id)
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    try:
        # Delete from MinIO
        minio_client = get_minio_client()
        minio_client.remove_object(db_video.bucket, db_video.object_name)
        
        # Delete from database
        video_crud.delete_video(db, video_id)
        
        return {"message": "Video deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting video: {str(e)}"
        )