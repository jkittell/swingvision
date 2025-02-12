from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List, Dict, Any
import json
from src.config import logger
from src.pipeline.swing_pipeline import create_default_pipeline
from pathlib import Path
import uuid
import shutil
from datetime import datetime, timedelta

router = APIRouter(prefix="/swing", tags=["Swing Analysis"])

@router.post("/analyze/media")
async def analyze_swing_media(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Process a golf swing video and store results in the media directory structure.
    
    Args:
        file: Uploaded video file (must be MP4 or QuickTime)
        
    Returns:
        Dict containing analysis metadata and file locations
        
    Raises:
        HTTPException: If file validation fails or processing error occurs
    """
    # Validate file type
    validate_video_file(file)
    
    # Create unique analysis ID
    analysis_id = str(uuid.uuid4())
    
    # Create directories
    upload_dir = Path("media/uploads") / analysis_id
    frames_dir = Path("media/frames") / analysis_id
    upload_dir.mkdir(parents=True)
    frames_dir.mkdir(parents=True)
    
    try:
        # Save original video
        video_path = upload_dir / "original.mp4"
        with video_path.open("wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process video
        pipeline = create_default_pipeline()
        sequence = pipeline.process(str(video_path))
        
        if not sequence.frames:
            raise HTTPException(
                status_code=400,
                detail="No frames could be extracted from the video"
            )
        
        # Save frames and collect URLs
        frame_urls = []
        annotated_frame_urls = []
        for i, frame in enumerate(sequence.frames):
            if frame.pil_image:
                # Save original frame
                frame_path = frames_dir / f"frame_{i}.jpg"
                frame.pil_image.save(frame_path)
                frame_urls.append(f"/media/frames/{analysis_id}/frame_{i}.jpg")
            
            # Save annotated frame URL if it exists
            if hasattr(frame, 'annotated_frame_url'):
                annotated_frame_urls.append(frame.annotated_frame_url)
        
        if not frame_urls or not annotated_frame_urls:
            raise HTTPException(
                status_code=400,
                detail="No valid frames could be processed from the video"
            )
        
        # Create metadata
        metadata = {
            "analysis_id": analysis_id,
            "created_at": datetime.now().isoformat(),
            "original_video": f"/media/uploads/{analysis_id}/original.mp4",
            "frames": frame_urls,
            "annotated_frames": annotated_frame_urls,
            "frame_count": len(frame_urls),
            "analysis_results": sequence.analysis_results if hasattr(sequence, 'analysis_results') else None,
            "feedback": sequence.feedback if hasattr(sequence, 'feedback') else None
        }
        
        # Save metadata
        metadata_path = Path("media/analyses") / f"{analysis_id}.json"
        with metadata_path.open("w") as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"Successfully processed video for analysis {analysis_id}")
        return metadata
        
    except HTTPException:
        # Cleanup and re-raise HTTP exceptions
        shutil.rmtree(upload_dir, ignore_errors=True)
        shutil.rmtree(frames_dir, ignore_errors=True)
        raise
        
    except Exception as e:
        # Cleanup on error
        shutil.rmtree(upload_dir, ignore_errors=True)
        shutil.rmtree(frames_dir, ignore_errors=True)
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error processing video. Please try again or contact support."
        )

def validate_video_file(file: UploadFile) -> None:
    """Validate uploaded video file."""
    allowed_types = ["video/mp4", "video/quicktime"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Must be one of: {', '.join(allowed_types)}"
        )

@router.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: str) -> Dict[str, Any]:
    """Retrieve analysis metadata by ID."""
    try:
        metadata_path = Path("media/analyses") / f"{analysis_id}.json"
        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="Analysis not found")
            
        with metadata_path.open() as f:
            metadata = json.load(f)
            
        # Verify all referenced files exist
        video_path = Path("media") / metadata["original_video"].lstrip("/media/")
        if not video_path.exists():
            logger.warning(f"Original video missing for analysis {analysis_id}")
            metadata["original_video_available"] = False
            
        # Check frame availability
        available_frames = []
        for frame_url in metadata["frames"]:
            frame_path = Path("media") / frame_url.lstrip("/media/")
            if frame_path.exists():
                available_frames.append(frame_url)
        metadata["frames"] = available_frames
            
        return metadata
        
    except json.JSONDecodeError:
        logger.error(f"Corrupted metadata file for analysis {analysis_id}")
        raise HTTPException(status_code=500, detail="Error reading analysis metadata")
    except Exception as e:
        logger.error(f"Error retrieving analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving analysis")

@router.get("/analyses")
async def list_analyses(skip: int = 0, limit: int = 10) -> Dict[str, Any]:
    """List all analyses with pagination."""
    try:
        analyses_dir = Path("media/analyses")
        analyses = []
        total_count = 0
        
        if analyses_dir.exists():
            metadata_files = list(analyses_dir.glob("*.json"))
            total_count = len(metadata_files)
            
            # Apply pagination
            paginated_files = metadata_files[skip:skip + limit]
            
            for metadata_file in paginated_files:
                try:
                    with metadata_file.open() as f:
                        metadata = json.load(f)
                        # Add file availability information
                        video_path = Path("media") / metadata["original_video"].lstrip("/media/")
                        metadata["original_video_available"] = video_path.exists()
                        analyses.append(metadata)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Error reading metadata file {metadata_file}: {str(e)}")
                    continue
        
        return {
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "analyses": sorted(analyses, key=lambda x: x["created_at"], reverse=True)
        }
        
    except Exception as e:
        logger.error(f"Error listing analyses: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving analyses list")

@router.delete("/analyses/{analysis_id}")
async def delete_analysis(analysis_id: str) -> Dict[str, str]:
    """Delete an analysis and all associated media files."""
    try:
        metadata_path = Path("media/analyses") / f"{analysis_id}.json"
        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Read metadata before deleting to get all file references
        try:
            with metadata_path.open() as f:
                metadata = json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Corrupted metadata file for analysis {analysis_id}")
            metadata = {}
        
        # Remove all associated directories and files
        upload_dir = Path("media/uploads") / analysis_id
        frames_dir = Path("media/frames") / analysis_id
        
        if upload_dir.exists():
            shutil.rmtree(upload_dir)
            logger.info(f"Removed upload directory for analysis {analysis_id}")
            
        if frames_dir.exists():
            shutil.rmtree(frames_dir)
            logger.info(f"Removed frames directory for analysis {analysis_id}")
            
        metadata_path.unlink()
        logger.info(f"Removed metadata file for analysis {analysis_id}")
        
        return {"status": "deleted", "analysis_id": analysis_id}
        
    except Exception as e:
        logger.error(f"Error deleting analysis {analysis_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting analysis: {str(e)}"
        )

async def cleanup_old_analyses():
    """Cleanup analyses older than 24 hours"""
    max_age = timedelta(hours=24)
    current_time = datetime.now()
    
    analyses_dir = Path("media/analyses")
    if not analyses_dir.exists():
        return
    
    for metadata_file in analyses_dir.glob("*.json"):
        try:
            with metadata_file.open() as f:
                metadata = json.load(f)
            
            created_at = datetime.fromisoformat(metadata["created_at"])
            if current_time - created_at > max_age:
                analysis_id = metadata["analysis_id"]
                await delete_analysis(analysis_id)
                
        except Exception as e:
            logger.error(f"Error cleaning up analysis {metadata_file}: {str(e)}")
            continue