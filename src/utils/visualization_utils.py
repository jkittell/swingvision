import cv2
import numpy as np
import math
from typing import List
from src.schemas import PoseResult
import logging

# Define keypoint connections for golf pose
keypoint_edges = [
    # Torso
    (11, 12), (12, 14), (14, 16),  # Right side
    (11, 13), (13, 15), (15, 17),  # Left side
    # Arms
    (23, 25), (25, 27),  # Right arm
    (24, 26), (26, 28),  # Left arm
    # Legs
    (11, 23), (23, 25), (25, 27), (27, 29), (29, 31),  # Right leg
    (12, 24), (24, 26), (26, 28), (28, 30), (30, 32)   # Left leg
]

# Define color palette
palette = np.array([
    [255, 128, 0],   # Orange
    [255, 153, 51],  # Light orange
    [255, 178, 102], # Pale orange
    [230, 230, 0],   # Yellow
    [255, 153, 255], # Pink
    [153, 204, 255], # Light blue
    [255, 102, 255], # Magenta
    [255, 51, 255],  # Bright magenta
    [102, 178, 255], # Sky blue
    [51, 153, 255],  # Blue
    [255, 153, 153], # Light red
    [255, 102, 102], # Red
    [255, 51, 51],   # Bright red
    [153, 255, 153], # Light green
    [102, 255, 102], # Green
    [51, 255, 51],   # Bright green
    [0, 255, 0],     # Pure green
    [0, 0, 255],     # Pure blue
    [255, 0, 0],     # Pure red
    [255, 255, 255]  # White
])

# Create colors for each keypoint edge
link_colors = np.array([
    palette[0],  # Torso - Orange
    palette[0],
    palette[0],
    palette[0],
    palette[0],
    palette[0],
    palette[9],  # Arms - Blue
    palette[9],
    palette[9],
    palette[9],
    palette[14], # Legs - Green
    palette[14],
    palette[14],
    palette[14],
    palette[14],
    palette[14],
    palette[14],
    palette[14],
    palette[14],
    palette[14]
])

# Create colors for each keypoint
keypoint_colors = np.array([palette[16] for _ in range(52)])  # All keypoints in green

# Function to draw keypoints on the image
def draw_points(image, keypoints, scores, pose_keypoint_color, keypoint_score_threshold, radius, show_keypoint_weight):
    if pose_keypoint_color is not None:
        assert len(pose_keypoint_color) == len(keypoints)
    for kid, (kpt, kpt_score) in enumerate(zip(keypoints, scores)):
        x_coord, y_coord = int(kpt[0]), int(kpt[1])
        if kpt_score > keypoint_score_threshold:
            color = tuple(int(c) for c in pose_keypoint_color[kid])
            if show_keypoint_weight:
                cv2.circle(image, (int(x_coord), int(y_coord)), radius, color, -1)
                transparency = max(0, min(1, kpt_score))
                cv2.addWeighted(image, transparency, image, 1 - transparency, 0, dst=image)
            else:
                cv2.circle(image, (int(x_coord), int(y_coord)), radius, color, -1)

# Function to draw links between keypoints on the image
def draw_links(image, keypoints, scores, keypoint_edges, link_colors, keypoint_score_threshold, thickness, show_keypoint_weight, stick_width=2):
    height, width, _ = image.shape
    if keypoint_edges is not None and link_colors is not None:
        assert len(link_colors) == len(keypoint_edges)
        for sk_id, sk in enumerate(keypoint_edges):
            x1, y1, score1 = (int(keypoints[sk[0], 0]), int(keypoints[sk[0], 1]), scores[sk[0]])
            x2, y2, score2 = (int(keypoints[sk[1], 0]), int(keypoints[sk[1], 1]), scores[sk[1]])
            if (
                x1 > 0
                and x1 < width
                and y1 > 0
                and y1 < height
                and x2 > 0
                and x2 < width
                and y2 > 0
                and y2 < height
                and score1 > keypoint_score_threshold
                and score2 > keypoint_score_threshold
            ):
                color = tuple(int(c) for c in link_colors[sk_id])
                if show_keypoint_weight:
                    X = (x1, x2)
                    Y = (y1, y2)
                    mean_x = np.mean(X)
                    mean_y = np.mean(Y)
                    length = ((Y[0] - Y[1]) ** 2 + (X[0] - X[1]) ** 2) ** 0.5
                    angle = math.degrees(math.atan2(Y[0] - Y[1], X[0] - X[1]))
                    polygon = cv2.ellipse2Poly(
                        (int(mean_x), int(mean_y)), (int(length / 2), int(stick_width)), int(angle), 0, 360, 1
                    )
                    cv2.fillConvexPoly(image, polygon, color)
                    transparency = max(0, min(1, 0.5 * (keypoints[sk[0], 2] + keypoints[sk[1], 2])))
                    cv2.addWeighted(image, transparency, image, 1 - transparency, 0, dst=image)
                else:
                    cv2.line(image, (x1, y1), (x2, y2), color, thickness=thickness)

# Update the draw_pose_on_image function to use draw_points and draw_links
def draw_pose_on_image(image, pose_results, keypoint_edges, keypoint_colors, link_colors, threshold=0.3):
    try:
        # Convert PIL image to OpenCV format if needed
        if isinstance(image, np.ndarray):
            image_cv = image.copy()
        else:
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        for pose_result in pose_results:
            try:
                keypoints = np.array(pose_result.keypoints)
                scores = np.array(pose_result.scores)

                # Draw keypoints and links
                draw_points(image_cv, keypoints, scores, keypoint_colors, threshold, radius=4, show_keypoint_weight=False)
                draw_links(image_cv, keypoints, scores, keypoint_edges, link_colors, threshold, thickness=2, show_keypoint_weight=False)
            except Exception as e:
                if logging.getLogger().isEnabledFor(logging.ERROR):
                    logging.error("Error drawing pose")
                continue

        return image_cv
    except Exception as e:
        if logging.getLogger().isEnabledFor(logging.ERROR):
            logging.error("Error in draw_pose_on_image")
        return image.copy() if isinstance(image, np.ndarray) else np.array(image)

# Update the slideshow function to use default parameters
def slideshow(images, pose_results, delay=100):
    for image, pose_results in zip(images, pose_results):
        annotated_image = draw_pose_on_image(image, pose_results, keypoint_edges, keypoint_colors, link_colors)
        cv2.imshow('Pose Slideshow', annotated_image)
        if cv2.waitKey(delay) & 0xFF == ord('q'):  # Press 'q' to exit early
            break

    cv2.destroyAllWindows()