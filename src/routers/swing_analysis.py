from fastapi import APIRouter, File, UploadFile
from src.schemas import SwingInput, AnalysisOutput
from src.utils.video_processing import process_video
from src.models.action_recognition import analyze_swing_poses
from src.utils.feedback_generation import generate_feedback

router = APIRouter(prefix="/swing", tags=["Swing Analysis"])

@router.post("/analyze/", response_model=AnalysisOutput)
async def analyze_swing(file: UploadFile = File(...)):
    # Process the video and extract poses
    poses = process_video(file.file)

    # Analyze the swing using the action recognition model
    analysis_results = analyze_swing_poses(poses)

    # Generate feedback based on the analysis results
    feedback = generate_feedback(analysis_results)

    return {"video_hash": file.filename, "analysis_results": analysis_results, "feedback": feedback}