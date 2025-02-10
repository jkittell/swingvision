import cv2
import numpy as np
import tempfile
from src.utils.pose_extraction import extract_pose

def process_video(file):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # Write the uploaded file to the temporary file
        temp_file.write(file.read())
        temp_path = temp_file.name
    
    cap = cv2.VideoCapture(temp_path)
    frame_count = 0
    poses = []

    while cap.isOpened():
        # Read a chunk of frames (e.g., 10 frames at a time)
        for _ in range(10):
            ret, frame = cap.read()
            if not ret:
                break

            # Process the frame and extract poses (using your preferred pose estimation method)
            pose = extract_pose(frame)
            poses.append(pose)

            frame_count += 1

    cap.release()

    return poses