from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from PIL import Image
import numpy as np
from src.schemas import PoseResult

@dataclass
class FrameData:
    """
    Represents the data for a single frame as it moves through the processing pipeline.
    Each stage of the pipeline can add its data to this object.
    """
    # Raw frame data
    frame: np.ndarray
    
    # Converted PIL Image
    pil_image: Optional[Image.Image] = None
    
    # Pose estimation results
    pose_result: Optional[PoseResult] = None
    
    # Swing phase data
    swing_phase: Optional[str] = None
    
    # Frame index in the sequence
    frame_index: int = 0
    
    # Analysis results specific to this frame
    frame_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Base64 encoded image with pose estimation drawn
    annotated_image_base64: Optional[str] = None

@dataclass
class SwingSequence:
    """
    Represents a sequence of frames from a golf swing video.
    """
    frames: List[FrameData]
    video_path: str
    metadata: dict = field(default_factory=dict)
    
    # Overall swing analysis results
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    
    # Generated feedback
    feedback: str = ""
    
    # Video hash for identification
    video_hash: str = ""
