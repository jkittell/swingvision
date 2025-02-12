from pydantic import BaseModel
from typing import List, Dict, Optional

class CLIPPrediction(BaseModel):
    score: float
    label: str

class CLIPResponse(BaseModel):
    predictions: List[CLIPPrediction]

    @classmethod
    def parse_raw_response(cls, response_bytes: bytes) -> Dict[str, float]:
        """Parse the raw response from CLIP API and return a dictionary of label:score pairs"""
        import json
        predictions = [CLIPPrediction(**pred) for pred in json.loads(response_bytes)]
        return {pred.label: pred.score for pred in predictions}

class PhaseAnalysis(BaseModel):
    strengths: List[str]
    areas_for_improvement: List[str]
    confidence: float
    all_scores: Dict[str, float]

class SwingAnalysis(BaseModel):
    clip_analysis: Dict[str, PhaseAnalysis]
    phase_analysis: Dict[str, int]