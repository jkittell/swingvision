from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from src.crud import video as video_crud
from src.schemas.video import VideoCreate
from src.config import get_minio_client, MINIO_BUCKET
import uuid
from datetime import datetime
import io

async def save_uploaded_video(file: UploadFile, db: Session):
    """Save uploaded video to MinIO and metadata to database"""
    upload_id = str(uuid.uuid4())
    minio_client = get_minio_client()
    
    try:
        # Read file content
        content = await file.read()
        content_length = len(content)
        
        # Create object name in MinIO
        object_name = f"{upload_id}/original.mp4"
        
        # Upload to MinIO
        result = minio_client.put_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_name,
            data=io.BytesIO(content),
            length=content_length,
            content_type=file.content_type
        )
        
        # Create video record
        video_data = VideoCreate(
            filename=file.filename,
            content_type=file.content_type,
            size=content_length
        )
        
        # Generate presigned URL for video access
        url = minio_client.presigned_get_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_name,
            expires=7*24*60*60  # URL expires in 7 days
        )
        
        metadata = {
            "upload_id": upload_id,
            "created_at": datetime.now().isoformat(),
            "bucket": MINIO_BUCKET,
            "object_name": object_name,
            "etag": result.etag,
            "presigned_url": url
        }
        
        return video_crud.create_video(
            db=db,
            video=video_data,
            file_path=f"minio://{MINIO_BUCKET}/{object_name}",
            metadata=metadata
        )
        
    except Exception as e:
        # Try to clean up the object if it was created
        try:
            minio_client.remove_object(MINIO_BUCKET, object_name)
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))

async def get_video_url(video_id: str, db: Session) -> str:
    """Get a presigned URL for video access"""
    video = video_crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    # Parse object name from file_path
    object_name = video.file_path.split("minio://")[1].split("/", 1)[1]
    
    # Generate new presigned URL
    minio_client = get_minio_client()
    url = minio_client.presigned_get_object(
        bucket_name=MINIO_BUCKET,
        object_name=object_name,
        expires=7*24*60*60  # URL expires in 7 days
    )
    
    return url