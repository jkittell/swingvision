from pydantic import BaseModel
from typing import List

class PoseResult(BaseModel):
    keypoints: List[List[float]]
    scores: List[float]
    labels: List[int]
    bbox: List[float]