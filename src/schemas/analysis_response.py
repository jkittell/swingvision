from pydantic import BaseModel
from typing import List

class SwingAnalysisResponse(BaseModel):
    video_hash: str
    analysis_results: dict
    feedback: str
    annotated_frames: List[str]  # List of base64 encoded images