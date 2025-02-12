from abc import ABC, abstractmethod
from typing import List
from src.models.frame_data import FrameData, SwingSequence
from src.utils.golf_swing_detection import is_golf_swing
from src.utils.video_processing import extract_frames
from src.utils.image_conversion import convert_frames_to_images
from src.utils.pose_processor import PoseProcessor
from src.utils.swing_phases import SwingPhase, PHASE_DESCRIPTIONS
from src.utils.feedback_generation import generate_feedback
from huggingface_hub import InferenceClient 
import os
import time
import json
import logging

class PipelineStage(ABC):
    """Abstract base class for pipeline stages"""
    
    @abstractmethod
    def process(self, sequence: SwingSequence) -> SwingSequence:
        """Process the swing sequence and return the modified sequence"""
        pass

class SwingValidationStage(PipelineStage):
    def process(self, sequence: SwingSequence) -> SwingSequence:
        if not is_golf_swing(sequence.video_path):
            raise ValueError("The video does not contain a golf swing")
        return sequence

class FrameExtractionStage(PipelineStage):
    def process(self, sequence: SwingSequence) -> SwingSequence:
        frames = extract_frames(sequence.video_path, fps=1)
        sequence.frames = [FrameData(frame=frame, frame_index=i) 
                         for i, frame in enumerate(frames)]
        return sequence

class ImageConversionStage(PipelineStage):
    def process(self, sequence: SwingSequence) -> SwingSequence:
        images = convert_frames_to_images([frame.frame for frame in sequence.frames])
        for frame_data, pil_image in zip(sequence.frames, images):
            frame_data.pil_image = pil_image
        return sequence

class PoseProcessingStage(PipelineStage):
    def process(self, sequence: SwingSequence) -> SwingSequence:
        pose_processor = PoseProcessor()
        frames = [frame.frame for frame in sequence.frames]
        pose_results = pose_processor.process_frames(frames)
        
        # Assuming pose_results maintains frame order
        for frame_data, pose_result in zip(sequence.frames, pose_results):
            frame_data.pose_result = pose_result
        return sequence

class VisualizationStage(PipelineStage):
    def process(self, sequence: SwingSequence) -> SwingSequence:
        """
        Draw pose estimations on images and save them to disk.
        """
        from src.utils.visualization_utils import draw_pose_on_image, keypoint_edges, keypoint_colors, link_colors
        import cv2
        import base64
        import io
        import numpy as np
        from PIL import Image
        from pathlib import Path
        
        for i, frame in enumerate(sequence.frames):
            if frame.pose_result and frame.pil_image:
                # Convert PIL Image to numpy array for drawing
                img_array = np.array(frame.pil_image)
                
                # Draw pose on image
                annotated_img = draw_pose_on_image(
                    img_array, 
                    [frame.pose_result],
                    keypoint_edges=keypoint_edges,
                    keypoint_colors=keypoint_colors,
                    link_colors=link_colors
                )
                
                # Convert BGR to RGB for PIL
                annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
                
                # Convert numpy array back to PIL Image
                pil_image = Image.fromarray(annotated_img)
                
                # Save annotated frame
                analysis_id = Path(sequence.video_path).parent.name
                annotated_frames_dir = Path("media/frames") / analysis_id / "annotated"
                annotated_frames_dir.mkdir(parents=True, exist_ok=True)
                
                frame_path = annotated_frames_dir / f"frame_{i}_annotated.jpg"
                pil_image.save(frame_path)
                
                # Add URL to frame data
                frame.annotated_frame_url = f"/media/frames/{analysis_id}/annotated/frame_{i}_annotated.jpg"
                
                # Also store base64 for potential direct use
                buffered = io.BytesIO()
                pil_image.save(buffered, format="JPEG")
                frame.annotated_image_base64 = base64.b64encode(buffered.getvalue()).decode()
                
        return sequence

class CLIPAnalysisStage(PipelineStage):
    def __init__(self):
        """
        Initialize CLIP analysis stage with HuggingFace API token.
        """    
        # Get API token from environment variable
        self.api_token = os.getenv('HF_TOKEN')
        if not self.api_token:
            raise ValueError("Please set the HF_TOKEN environment variable")
            
        # Initialize the inference client
        self.client = InferenceClient(token=self.api_token)
        
        # Store swing phases and their descriptions
        self.swing_phases = SwingPhase
        self.phase_descriptions = PHASE_DESCRIPTIONS

    def _call_clip_api(self, image_path: str, descriptions: list, max_retries: int = 3, retry_delay: float = 1.0) -> dict:
        """
        Call the CLIP API with retry logic using image data.
        Args:
            image_path: Path to the image file
            descriptions: List of descriptions to classify against
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
        Returns:
            A dictionary with scores mapped to labels.
        """
        import json
        from PIL import Image
        import base64
        import io
        
        for attempt in range(max_retries):
            try:
                # Open and encode image
                with Image.open(image_path) as img:
                    # Convert to RGB if needed
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                        
                    # Convert to base64
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    response = self.client.post(
                        json={
                            "parameters": {
                                "candidate_labels": descriptions
                            },
                            "inputs": img_base64,
                            "task": "zero-shot-image-classification"
                        },
                        model="openai/clip-vit-large-patch14"
                    )
                
                # Parse the response
                if isinstance(response, (dict, list)):
                    # Response is already parsed JSON
                    if isinstance(response, list):
                        return {pred["label"]: pred["score"] for pred in response}
                    return response
                elif isinstance(response, bytes):
                    response_json = json.loads(response)
                    return {pred["label"]: pred["score"] for pred in response_json}
                else:
                    logging.error(f"Unexpected CLIP API response format: {type(response)}")
                    return {}
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    logging.error(f"CLIP API attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logging.error(f"All CLIP API attempts failed: {str(e)}")
                    raise
        
        return {}

    def process(self, sequence: SwingSequence) -> SwingSequence:
        """
        Analyze the annotated images using CLIP via HuggingFace Inference API.
        Groups frames by swing phase and analyzes each phase separately.
        """
        import numpy as np
        import io
        import base64
        from PIL import Image
        from src.utils.swing_phases import SwingPhase
        
        if not sequence.frames:
            if logging.getLogger().isEnabledFor(logging.WARNING):
                logging.warning("No frames found in sequence")
            return sequence
            
        # First, assign phases to frames based on their position in the sequence
        total_frames = len(sequence.frames)
        frames_per_phase = max(1, total_frames // 10)
        
        # Map phase indices to SwingPhase enum values
        phase_map = {
            0: SwingPhase.P1_ADDRESS,
            1: SwingPhase.P2_TAKEAWAY,
            2: SwingPhase.P3_HALFWAY_BACK,
            3: SwingPhase.P4_TOP,
            4: SwingPhase.P5_EARLY_DOWN,
            5: SwingPhase.P6_PRE_IMPACT,
            6: SwingPhase.P7_IMPACT,
            7: SwingPhase.P8_RELEASE,
            8: SwingPhase.P9_FOLLOW,
            9: SwingPhase.P10_FINISH
        }
        
        for i, frame in enumerate(sequence.frames):
            phase_index = min(9, i // frames_per_phase)
            frame.swing_phase = phase_map[phase_index]
        
        # Store analysis for each phase
        clip_analysis = {}
        phase_analysis = {}
        
        # Group frames by swing phase
        phase_frames = {}
        for frame in sequence.frames:
            try:
                if not frame.annotated_image_base64:
                    continue
                    
                # Convert base64 to PIL Image
                try:
                    img_data = base64.b64decode(frame.annotated_image_base64)
                    img = Image.open(io.BytesIO(img_data))
                except Exception as e:
                    if logging.getLogger().isEnabledFor(logging.ERROR):
                        logging.error(f"Failed to decode image data: {str(e)}")
                    continue
                
                # Initialize list for this phase if needed
                if frame.swing_phase not in phase_frames:
                    phase_frames[frame.swing_phase] = []
                    
                phase_frames[frame.swing_phase].append(img)
                
            except Exception as e:
                if logging.getLogger().isEnabledFor(logging.ERROR):
                    logging.error(f"Error processing frame: {str(e)}")
                continue
        
        # Process each swing phase
        for phase in SwingPhase:
            phase_name = phase.value
            descriptions = self.phase_descriptions.get(phase, [])
            
            if not descriptions:
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug(f"No descriptions for {phase_name}")
                continue
                
            # Skip if no frames for this phase
            if phase not in phase_frames:
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug(f"No frames for {phase_name}")
                phase_analysis[phase.name] = 0  # Mark as not detected
                continue
                
            all_scores = []
            
            # Process each image in this phase
            for img in phase_frames[phase]:
                try:
                    # Save image to a temporary file
                    img_path = f"temp_{phase_name}.jpg"
                    img.save(img_path)
                    
                    # Call the CLIP endpoint with retry logic
                    response = self._call_clip_api(img_path, descriptions)
                    
                    # Extract scores from response
                    if response:
                        all_scores.append(response)
                    
                    # Remove temporary file
                    import os
                    os.remove(img_path)
                    
                except Exception as e:
                    if logging.getLogger().isEnabledFor(logging.ERROR):
                        logging.error(f"Error analyzing {phase_name}: {str(e)}")
                    continue
            
            # Analyze scores for this phase
            if all_scores:
                try:
                    # Average scores for each description
                    avg_scores = {}
                    for desc in descriptions:
                        scores_for_desc = [score_dict.get(desc, 0) for score_dict in all_scores]
                        avg_scores[desc] = float(np.mean(scores_for_desc))
                    
                    # Analyze the phase
                    phase_result = self._analyze_phase_scores(avg_scores)
                    clip_analysis[phase_name] = phase_result
                    phase_analysis[phase.name] = 1  # Mark as detected
                    
                except Exception as e:
                    if logging.getLogger().isEnabledFor(logging.ERROR):
                        logging.error(f"Error analyzing scores for {phase_name}: {str(e)}")
                    phase_analysis[phase.name] = 0  # Mark as failed
                    continue
            else:
                phase_analysis[phase.name] = 0  # Mark as no scores
        
        # Store both analyses in the sequence
        sequence.analysis_results = {
            'clip_analysis': clip_analysis,
            'phase_analysis': phase_analysis
        }
        
        return sequence
        
    def _analyze_phase_scores(self, scores: dict) -> dict:
        """
        Analyze scores for a phase and provide feedback.
        """
        # Sort descriptions by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Identify top positive and negative aspects
        positives = [desc for desc, score in sorted_scores 
                    if score > 0.3 and not any(neg in desc.lower() 
                    for neg in ['poor', 'too', 'improper', 'incorrect', 'loss', 
                               'early', 'lifting', 'incomplete', 'unstable'])]
        
        negatives = [desc for desc, score in sorted_scores 
                    if score > 0.3 and any(neg in desc.lower() 
                    for neg in ['poor', 'too', 'improper', 'incorrect', 'loss', 
                               'early', 'lifting', 'incomplete', 'unstable'])]
        
        return {
            'strengths': positives[:2],  # Top 2 positive aspects
            'areas_for_improvement': negatives[:2],  # Top 2 areas for improvement
            'confidence': sorted_scores[0][1] if sorted_scores else 0.0,  # Highest confidence score
            'all_scores': dict(sorted_scores)  # All scores for reference
        }

class FeedbackGenerationStage(PipelineStage):
    def __init__(self):
        from huggingface_hub import InferenceClient
        import os
        
        self.api_token = os.getenv('HF_TOKEN')
        if not self.api_token:
            raise ValueError("Please set the HF_TOKEN environment variable")
            
        self.client = InferenceClient(token=self.api_token)

    def process(self, sequence: SwingSequence) -> SwingSequence:
        """Generate natural language feedback using Mistral."""
        clip_analysis = sequence.analysis_results.get('clip_analysis', {})
        
        if not clip_analysis:
            sequence.feedback = "No swing analysis available."
            return sequence
            
        # Create a conversational prompt
        prompt = """As a friendly golf instructor having a one-on-one session with your student, provide encouraging feedback on their swing. Write in a natural, conversational tone as if you're speaking directly to them:

Start with a warm greeting and highlight what they're doing well. Focus on their natural strengths and how these will help their game. Be specific with your praise.

Then, gently transition into a couple of helpful adjustments they can make. Explain these in simple terms, using relatable "feel cues" that make sense. Help them understand how these changes will improve their game.

Finally, share two fun practice drills they can try. For each drill:
- Explain why you chose it and how it helps
- Walk them through the setup and steps
- Share what success feels like
- Offer ways to make it easier or more challenging
- Give them clear signs of progress to look for

Here's what I noticed in their swing:\n\n"""
        
        for phase_name, phase_data in clip_analysis.items():
            strengths = phase_data.get('strengths', [])
            improvements = phase_data.get('areas_for_improvement', [])
            
            if strengths or improvements:
                prompt += f"{phase_name}:\n"
                if strengths:
                    prompt += f"Strengths: {', '.join(strengths)}\n"
                if improvements:
                    prompt += f"Opportunities: {', '.join(improvements)}\n"
                prompt += "\n"
        
        prompt += "\nWrite as if you're having a friendly conversation at the driving range. Keep the tone warm and encouraging, while making sure they have all the details they need to improve. Make them feel excited about practicing these changes!"
        
        try:
            response = self.client.post(
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 750,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "do_sample": True,
                        "return_full_text": False
                    }
                },
                model="mistralai/Mistral-7B-Instruct-v0.3"
            )
            
            # Clean up the response
            import json
            if isinstance(response, bytes):
                response = response.decode('utf-8')
            if isinstance(response, str):
                try:
                    response = json.loads(response)
                except json.JSONDecodeError:
                    pass
                
            # Extract the feedback text
            if isinstance(response, list) and response:
                feedback = response[0].get('generated_text', '')
            elif isinstance(response, dict):
                feedback = response.get('generated_text', '')
            else:
                feedback = str(response)
            
            # Clean up the feedback text
            feedback = feedback.strip()
            feedback = feedback.replace('\\n', '\n')  # Convert escaped newlines
            feedback = feedback.replace('\\', '')     # Remove other escape chars
            
            sequence.feedback = feedback
            
        except Exception as e:
            logger.error(f"Error generating feedback: {str(e)}")
            sequence.feedback = "Unable to generate detailed feedback at this time. Please try again."
            
        return sequence

class SwingPipeline:
    """
    Main pipeline class that orchestrates the processing of a golf swing video
    through various stages.
    """
    
    def __init__(self):
        self.stages: List[PipelineStage] = []
        
    def add_stage(self, stage: PipelineStage) -> 'SwingPipeline':
        """Add a processing stage to the pipeline"""
        self.stages.append(stage)
        return self  # Enable method chaining
        
    def process(self, video_path: str) -> SwingSequence:
        """
        Process a video through all pipeline stages
        """
        # Initialize sequence with video path
        sequence = SwingSequence(frames=[], video_path=video_path)
        
        # Process through each stage
        for stage in self.stages:
            try:
                sequence = stage.process(sequence)
            except Exception as e:
                # In a production environment, you might want to add logging here
                raise Exception(f"Pipeline failed at stage {stage.__class__.__name__}: {str(e)[:100]}")  # Truncate long error messages
                
        return sequence

def create_default_pipeline() -> SwingPipeline:
    """
    Factory method to create a pipeline with the default stages
    """
    return (SwingPipeline()
            .add_stage(SwingValidationStage())
            .add_stage(FrameExtractionStage())
            .add_stage(ImageConversionStage())
            .add_stage(PoseProcessingStage())
            .add_stage(VisualizationStage())
            .add_stage(CLIPAnalysisStage())  # This handles phase analysis
            .add_stage(FeedbackGenerationStage()))
