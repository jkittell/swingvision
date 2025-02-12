import torch
from transformers import AutoProcessor, RTDetrForObjectDetection, VitPoseForPoseEstimation, DetrImageProcessor, DetrForObjectDetection
import cv2
import numpy as np
from PIL import Image
from src.config import logger
from src.schemas import PoseResult

class PoseProcessor:
    def __init__(self):
        # Check if MPS is available and set the device
        self.device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")

        # Load the models
        self.person_image_processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
        self.person_model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50", device_map=self.device)

        self.processor = AutoProcessor.from_pretrained("stanfordmimi/synthpose-vitpose-huge-hf")
        self.model = VitPoseForPoseEstimation.from_pretrained("stanfordmimi/synthpose-vitpose-huge-hf", device_map=self.device)

    def calculate_boxes(self, frames):
        boxes = []
        for frame in frames:
            # Ensure frame is a valid NumPy array
            if not isinstance(frame, np.ndarray):
                continue  # Skip invalid frames

            # Convert frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Apply GaussianBlur to reduce noise and improve contour detection
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            # Perform edge detection
            edged = cv2.Canny(blurred, 50, 150)
            # Find contours
            contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find the largest contour and use it as the bounding box
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                boxes.append((x, y, w, h))
            else:
                boxes.append((0, 0, frame.shape[1], frame.shape[0]))  # Use the whole frame if no contour is found
        
        return boxes

    def process_frames(self, frames):
        pose_results = []
        boxes = self.calculate_boxes(frames)
        logger.info(f"Extracted {len(frames)} frames from the video")
        logger.info(f"Found {len(boxes)} boxes for each frame")
        for frame, person_boxes in zip(frames, boxes):
            # Convert frame to PIL Image
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Detect humans
            inputs = self.person_image_processor(images=image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.person_model(**inputs)
            results = self.person_image_processor.post_process_object_detection(
                outputs, target_sizes=torch.tensor([(image.height, image.width)]), threshold=0.3
            )
            result = results[0]
            person_boxes = result["boxes"][result["labels"] == 1].cpu().numpy()
            scores = result["scores"][result["labels"] == 1].cpu().numpy()

            # Filter boxes to find the golfer
            if len(person_boxes) > 0:
                # Convert boxes format
                person_boxes_xywh = person_boxes.copy()
                person_boxes_xywh[:, 2] = person_boxes_xywh[:, 2] - person_boxes_xywh[:, 0]  # width
                person_boxes_xywh[:, 3] = person_boxes_xywh[:, 3] - person_boxes_xywh[:, 1]  # height

                # Calculate center points
                centers = person_boxes_xywh[:, :2] + person_boxes_xywh[:, 2:] / 2
                
                # Score each person based on:
                # 1. Distance from center of frame
                # 2. Size of bounding box (golfer usually takes up more space)
                # 3. Original detection confidence
                frame_center = np.array([image.width/2, image.height/2])
                center_distances = np.linalg.norm(centers - frame_center, axis=1)
                box_sizes = person_boxes_xywh[:, 2] * person_boxes_xywh[:, 3]
                
                # Normalize scores (lower distance is better)
                center_scores = 1 - (center_distances / np.max(center_distances))
                size_scores = box_sizes / np.max(box_sizes)
                
                # Combine scores (equal weights)
                combined_scores = 0.4 * center_scores + 0.3 * size_scores + 0.3 * scores
                
                # Select the person with highest score (likely the golfer)
                golfer_idx = np.argmax(combined_scores)
                person_boxes = person_boxes_xywh[golfer_idx:golfer_idx+1]
            else:
                # If no person detected, use the whole frame
                person_boxes = np.array([[0, 0, image.width, image.height]])

            # Pose estimation for the selected person
            inputs = self.processor(image, boxes=[person_boxes], return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)
            pose_results_list = self.processor.post_process_pose_estimation(outputs, boxes=[person_boxes])
            
            for person_data in pose_results_list:
                for data in person_data:
                    pose_result = PoseResult(
                        keypoints=data['keypoints'],
                        scores=data['scores'],
                        labels=data['labels'],
                        bbox=data['bbox']
                    )
                    pose_results.append(pose_result)
        return pose_results
