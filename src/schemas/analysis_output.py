from pydantic import BaseModel

class AnalysisOutput(BaseModel):
    video_hash: str
    analysis_results: dict
    feedback: str